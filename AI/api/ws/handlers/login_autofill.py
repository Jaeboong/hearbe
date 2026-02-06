# -*- coding: utf-8 -*-
"""
Login autofill helper.

If the user asks to log in while on the login page, check whether
email/password fields are already filled (e.g., by browser autofill).
If filled, click the login button immediately. Otherwise, fall back to
the usual guidance prompt.
"""

import logging
import re
from typing import Any, Dict, Optional

from core.interfaces import MCPCommand
from services.llm.sites.site_manager import get_current_site, get_page_type, get_selector
from services.llm.generators.tts_generator import TTSGenerator

logger = logging.getLogger(__name__)


CTX_EMAIL_ARGS = "login_autofill_email_args"
CTX_PASS_ARGS = "login_autofill_pass_args"
CTX_EMAIL_FILLED = "login_autofill_email_filled"
CTX_PASS_FILLED = "login_autofill_pass_filled"
CTX_PENDING = "login_autofill_pending"
CTX_ATTEMPT = "login_autofill_attempt"
CTX_LAST_URL = "login_autofill_last_url"
CTX_SESSION_CHECK_PENDING = "login_autofill_session_check_pending"
CTX_SESSION_CHECK_URL = "login_autofill_session_check_url"

MAX_ATTEMPTS = 2
FOCUS_WAIT_MS = 300
RETRY_DELAY_MS = 1500


class LoginAutofillManager:
    """Detects login autofill on the login page and triggers submit."""

    def __init__(self, sender, session_manager, login_feedback=None):
        self._sender = sender
        self._session = session_manager
        self._login_feedback = login_feedback
        self._tts = TTSGenerator()

    async def handle_user_text(self, session_id: str, text: str) -> bool:
        session = self._session.get_session(session_id) if self._session else None
        if not session:
            return False

        current_url = session.current_url or ""
        if get_page_type(current_url) != "login":
            return False
        if not _is_coupang_login_url(current_url):
            logger.info("login_autofill skip: not coupang login url (text)")
            return False

        if not _is_login_intent(text):
            return False

        if self._session.get_context(session_id, CTX_PENDING):
            return True

        return await self._start_probe(session_id, current_url, source="text")

    async def handle_page_update(self, session_id: str, url: str, previous_url: Optional[str] = None) -> bool:
        page_type = get_page_type(url)
        logger.info(
            "login_autofill handle_page_update: session=%s url=%s page_type=%s previous_url=%s",
            session_id, url, page_type, previous_url,
        )
        if page_type != "login":
            logger.info("login_autofill skip: page_type is not login")
            return False
        if _is_coupang_login_url(url):
            if previous_url and get_page_type(previous_url) == "login":
                logger.info("login_autofill skip: previous_url was also login (coupang)")
                return False
            if self._session.get_context(session_id, CTX_PENDING):
                logger.info("login_autofill skip: CTX_PENDING is True (coupang)")
                return True
            if self._session.get_context(session_id, CTX_SESSION_CHECK_PENDING):
                logger.info("login_autofill skip: CTX_SESSION_CHECK_PENDING is True (coupang)")
                return True
            last_url = self._session.get_context(session_id, CTX_LAST_URL)
            if last_url == url:
                logger.info("login_autofill skip: same as last_url (coupang)")
                return False
            return await self._start_probe(session_id, url, source="page")
        if not _is_hearbe_url(url):
            logger.info("login_autofill skip: login page not heabe or coupang")
            return False
        if previous_url and get_page_type(previous_url) == "login":
            logger.info("login_autofill skip: previous_url was also login")
            return False
        if self._session.get_context(session_id, CTX_PENDING):
            logger.info("login_autofill skip: CTX_PENDING is True")
            return True
        if self._session.get_context(session_id, CTX_SESSION_CHECK_PENDING):
            logger.info("login_autofill skip: CTX_SESSION_CHECK_PENDING is True")
            return True
        last_url = self._session.get_context(session_id, CTX_LAST_URL)
        if last_url == url:
            logger.info("login_autofill skip: same as last_url")
            return False

        # Check existing session before autofill probe
        return await self._start_session_check(session_id, url)

    async def handle_main_page_update(self, session_id: str, url: str) -> bool:
        """Handle main page entry - redirect logged-in users to appropriate mall."""
        logger.info(
            "login_autofill handle_main_page_update: session=%s url=%s",
            session_id, url,
        )
        if self._session.get_context(session_id, "token_recovery_in_flight"):
            logger.info("login_autofill main skip: token recovery in flight")
            return False
        if not _is_hearbe_url(url):
            logger.info("login_autofill main skip: not heabe url")
            return False
        if self._session.get_context(session_id, CTX_SESSION_CHECK_PENDING):
            logger.info("login_autofill main skip: CTX_SESSION_CHECK_PENDING is True")
            return True

        # Check existing session and redirect if logged in
        return await self._start_session_check(session_id, url)

    async def _start_session_check(self, session_id: str, url: str) -> bool:
        """Check if user already has a valid session in localStorage."""
        self._session.set_context(session_id, CTX_SESSION_CHECK_PENDING, True)
        self._session.set_context(session_id, CTX_SESSION_CHECK_URL, url)

        logger.info(
            "login session check start: session=%s url=%s",
            session_id,
            url,
        )
        await self._sender.send_tool_calls(
            session_id,
            [
                MCPCommand(
                    tool_name="get_user_session",
                    arguments={},
                    description="check existing user session",
                )
            ],
        )
        return True

    async def handle_mcp_result(self, session_id: str, data: Dict[str, Any]) -> bool:
        tool_name = data.get("tool_name")

        # Handle session check result
        if tool_name == "get_user_session":
            return await self._handle_session_check_result(session_id, data)

        if tool_name != "get_attribute_list":
            return False

        args = data.get("arguments") or {}
        result = data.get("result") or {}

        email_args = self._session.get_context(session_id, CTX_EMAIL_ARGS)
        pass_args = self._session.get_context(session_id, CTX_PASS_ARGS)
        if not email_args and not pass_args:
            return False

        if _args_match(email_args, args):
            filled = _has_non_empty_values(result)
            self._session.set_context(session_id, CTX_EMAIL_FILLED, filled)
            logger.info("login autofill email result: session=%s filled=%s", session_id, filled)
            return await self._maybe_finalize(session_id)

        if _args_match(pass_args, args):
            filled = _has_non_empty_values(result)
            self._session.set_context(session_id, CTX_PASS_FILLED, filled)
            logger.info("login autofill password result: session=%s filled=%s", session_id, filled)
            return await self._maybe_finalize(session_id)

        return False

    async def _handle_session_check_result(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Handle get_user_session result and redirect if logged in."""
        if not self._session.get_context(session_id, CTX_SESSION_CHECK_PENDING):
            return False

        self._session.set_context(session_id, CTX_SESSION_CHECK_PENDING, None)
        result = data.get("result") or {}
        logged_in = result.get("logged_in", False)
        user_type = result.get("user_type")
        check_url = self._session.get_context(session_id, CTX_SESSION_CHECK_URL) or ""

        if self._session.get_context(session_id, "token_recovery_in_flight"):
            logger.info(
                "login session check skip redirect: session=%s token recovery in flight (url=%s)",
                session_id,
                check_url,
            )
            self._session.set_context(session_id, CTX_SESSION_CHECK_URL, None)
            return False

        if logged_in and user_type:
            # Redirect based on userType
            redirect_url = self._get_redirect_url(user_type, check_url)
            logger.info(
                "login session found: session=%s user_type=%s redirect=%s",
                session_id,
                user_type,
                redirect_url,
            )
            await self._sender.send_tool_calls(
                session_id,
                [
                    MCPCommand(
                        tool_name="navigate_to_url",
                        arguments={"url": redirect_url},
                        description=f"redirect to {user_type} mall",
                    )
                ],
            )
            await self._sender.send_tts_response(
                session_id,
                "이미 로그인되어 있습니다. 쇼핑몰 페이지로 이동합니다.",
            )
            return True

        page_type = get_page_type(check_url)
        if page_type == "login":
            if _is_coupang_login_url(check_url):
                logger.info(
                    "login session not found: session=%s on coupang login, starting autofill probe",
                    session_id,
                )
                return await self._start_probe(session_id, check_url, source="page")
            logger.info(
                "login session not found: session=%s on login page, no autofill (hearbe)",
                session_id,
            )
            return False

        login_url = self._resolve_login_url(check_url, user_type=None)
        if login_url and login_url != check_url:
            logger.info(
                "login session not found: session=%s redirecting to login page=%s",
                session_id,
                login_url,
            )
            await self._sender.send_tool_calls(
                session_id,
                [
                    MCPCommand(
                        tool_name="navigate_to_url",
                        arguments={"url": login_url},
                        description="redirect to login page",
                    )
                ],
            )
            return True

        logger.info(
            "login session not found: session=%s no login redirect available (url=%s)",
            session_id,
            check_url,
        )
        return False

    def _resolve_login_url(self, current_url: str, user_type: Optional[str]) -> Optional[str]:
        """Resolve login URL for Hearbe site based on user type or current path."""
        site = get_current_site(current_url)
        urls = site.urls if site else {}
        if user_type == "BLIND":
            return urls.get("login_a") or urls.get("login_b") or urls.get("login_c")
        if user_type == "LOW_VISION":
            return urls.get("login_b") or urls.get("login_c") or urls.get("login_a")
        if user_type == "GENERAL":
            return urls.get("login_c") or urls.get("login_b") or urls.get("login_a")

        # Default to GENERAL login
        return urls.get("login_c") or urls.get("login_b") or urls.get("login_a")

    def _get_redirect_url(self, user_type: str, current_url: str) -> str:
        """Get redirect URL based on userType."""
        # Extract base URL from current login URL
        # e.g., https://i14d108.p.ssafy.io/A/login -> https://i14d108.p.ssafy.io
        base_match = re.match(r"(https?://[^/]+)", current_url)
        base_url = base_match.group(1) if base_match else "https://i14d108.p.ssafy.io"

        if user_type == "BLIND":
            return f"{base_url}/A/mall"
        elif user_type == "LOW_VISION":
            return f"{base_url}/B/mall"
        else:  # GENERAL or others
            return f"{base_url}/C/mall"

    def cleanup_session(self, session_id: str):
        if not self._session:
            return
        self._session.set_context(session_id, CTX_EMAIL_ARGS, None)
        self._session.set_context(session_id, CTX_PASS_ARGS, None)
        self._session.set_context(session_id, CTX_EMAIL_FILLED, None)
        self._session.set_context(session_id, CTX_PASS_FILLED, None)
        self._session.set_context(session_id, CTX_PENDING, None)
        self._session.set_context(session_id, CTX_ATTEMPT, None)
        self._session.set_context(session_id, CTX_LAST_URL, None)
        self._session.set_context(session_id, CTX_SESSION_CHECK_PENDING, None)
        self._session.set_context(session_id, CTX_SESSION_CHECK_URL, None)

    async def _maybe_finalize(self, session_id: str) -> bool:
        email_filled = self._session.get_context(session_id, CTX_EMAIL_FILLED)
        pass_filled = self._session.get_context(session_id, CTX_PASS_FILLED)
        if email_filled is None or pass_filled is None:
            return True

        self._session.set_context(session_id, CTX_PENDING, False)

        session = self._session.get_session(session_id) if self._session else None
        current_url = session.current_url if session else ""

        if email_filled or pass_filled:
            logger.info(
                "login autofill success: session=%s email_filled=%s pass_filled=%s",
                session_id,
                email_filled,
                pass_filled,
            )
            await self._send_login_click(session_id, current_url)
            return True

        attempt = self._session.get_context(session_id, CTX_ATTEMPT) or 1
        if attempt < MAX_ATTEMPTS:
            logger.info(
                "login autofill retry: session=%s attempt=%s/%s",
                session_id,
                attempt + 1,
                MAX_ATTEMPTS,
            )
            self._session.set_context(session_id, CTX_ATTEMPT, attempt + 1)
            self._session.set_context(session_id, CTX_PENDING, True)
            email_args = self._session.get_context(session_id, CTX_EMAIL_ARGS)
            pass_args = self._session.get_context(session_id, CTX_PASS_ARGS)
            if email_args and pass_args:
                await self._sender.send_tool_calls(
                    session_id,
                    [
                        MCPCommand(
                            tool_name="wait",
                            arguments={"ms": RETRY_DELAY_MS},
                            description="wait for login autofill",
                        ),
                        MCPCommand(
                            tool_name="get_attribute_list",
                            arguments=email_args,
                            description="check login email autofill (retry)",
                        ),
                        MCPCommand(
                            tool_name="get_attribute_list",
                            arguments=pass_args,
                            description="check login password autofill (retry)",
                        ),
                    ],
                )
                return True

        # Autofill not detected; fall back to normal guidance.
        logger.info(
            "login autofill failed: session=%s email_filled=%s pass_filled=%s",
            session_id,
            email_filled,
            pass_filled,
        )
        await self._sender.send_tts_response(session_id, self._tts.build_login_guidance())
        return True

    async def _start_probe(self, session_id: str, current_url: str, source: str) -> bool:
        if not _is_coupang_login_url(current_url):
            logger.info("login_autofill probe skip: not coupang login url")
            return False
        email_selector = get_selector(current_url, "email_input") or "#login-email-input"
        password_selector = get_selector(current_url, "password_input") or "#login-password-input"

        email_args = {"selector": email_selector, "attribute": "value"}
        pass_args = {"selector": password_selector, "attribute": "value"}

        self._session.set_context(session_id, CTX_EMAIL_ARGS, email_args)
        self._session.set_context(session_id, CTX_PASS_ARGS, pass_args)
        self._session.set_context(session_id, CTX_EMAIL_FILLED, None)
        self._session.set_context(session_id, CTX_PASS_FILLED, None)
        self._session.set_context(session_id, CTX_ATTEMPT, 1)
        self._session.set_context(session_id, CTX_PENDING, True)
        self._session.set_context(session_id, CTX_LAST_URL, current_url)

        logger.info(
            "login autofill probe start: session=%s url=%s source=%s email_selector=%s pass_selector=%s",
            session_id,
            current_url,
            source,
            email_selector,
            password_selector,
        )
        await self._send_probe(session_id, email_selector, password_selector, email_args, pass_args, with_focus=True)
        return True

    async def _send_login_click(self, session_id: str, current_url: str):
        login_selector = (
            get_selector(current_url, "login_button")
            or get_selector(current_url, "submit_button")
            or "button[type='submit']"
        )
        commands = [
            MCPCommand(
                tool_name="click",
                arguments={"selector": login_selector},
                description="login submit",
            ),
            MCPCommand(
                tool_name="wait",
                arguments={"ms": 2000},
                description="wait for login",
            ),
        ]
        if self._login_feedback:
            self._login_feedback.mark_login_submit_pending(session_id, commands, current_url or "")
        await self._sender.send_tool_calls(session_id, commands)

    async def _send_probe(
        self,
        session_id: str,
        email_selector: str,
        password_selector: str,
        email_args: Dict[str, Any],
        pass_args: Dict[str, Any],
        with_focus: bool = False,
    ):
        commands = []
        if with_focus:
            commands.extend(
                [
                    MCPCommand(
                        tool_name="click",
                        arguments={"selector": email_selector},
                        description="focus login email input",
                    ),
                    MCPCommand(
                        tool_name="click",
                        arguments={"selector": password_selector},
                        description="focus login password input",
                    ),
                    MCPCommand(
                        tool_name="wait",
                        arguments={"ms": FOCUS_WAIT_MS},
                        description="wait for autofill after focus",
                    ),
                ]
            )
        commands.extend(
            [
                MCPCommand(
                    tool_name="get_attribute_list",
                    arguments=email_args,
                    description="check login email autofill",
                ),
                MCPCommand(
                    tool_name="get_attribute_list",
                    arguments=pass_args,
                    description="check login password autofill",
                ),
            ]
        )
        await self._sender.send_tool_calls(session_id, commands)


def _has_non_empty_values(result: Dict[str, Any]) -> bool:
    values = result.get("values") if isinstance(result, dict) else None
    if not values:
        return False
    return any(v and v.strip() for v in values)


def _is_login_intent(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    if "로그인" not in text and "login" not in lowered:
        return False
    if any(k in text for k in ("휴대폰", "인증", "문자")):
        return False
    if "otp" in lowered or "code" in lowered:
        return False
    # Avoid hijacking pure OTP/phone digit inputs.
    digits = re.sub(r"\\D", "", text)
    if 4 <= len(digits) <= 8 and "로그인" not in text:
        return False
    return True


def _args_match(expected: Optional[Dict[str, Any]], actual: Dict[str, Any]) -> bool:
    if not expected:
        return False
    for key, value in expected.items():
        if actual.get(key) != value:
            return False
    return True


def _is_coupang_login_url(url: str) -> bool:
    if not url:
        return False
    lowered = url.lower()
    return "login.coupang.com" in lowered and "/login/login.pang" in lowered


def _is_hearbe_url(url: str) -> bool:
    if not url:
        return False
    lowered = url.lower()
    return (
        "i14d108.p.ssafy.io" in lowered
        or "localhost" in lowered
        or "127.0.0.1" in lowered
    )
