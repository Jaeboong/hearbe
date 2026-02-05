"""
Login rules (ASCII-only).
"""

import re
from typing import Optional

from . import BaseRule, RuleResult
from ..context.context_rules import (
    LOGIN_SUBMIT_TRIGGERS,
    build_click_command,
    build_fill_command,
    build_login_page_commands,
    build_press_command,
    build_wait_for_selector_command,
    detect_target_site,
)
from ..sites.site_manager import get_page_type, get_selector


class LoginRule(BaseRule):
    """Login rule: navigate or submit."""

    def check(self, text: str, current_url: str, current_site) -> Optional[RuleResult]:
        if get_page_type(current_url) == "login":
            return None
        target_site = current_site or detect_target_site(text, self.site_manager, current_site)
        phone = _extract_phone_number(text)
        if phone and get_page_type(current_url) != "login":
            commands = build_login_page_commands(target_site)
            return RuleResult(
                matched=True,
                commands=commands,
                response_text="로그인 페이지로 이동합니다.",
                rule_name="login",
            )

        if "로그인" not in text and "login" not in text.lower():
            return None

        if any(kw in text for kw in LOGIN_SUBMIT_TRIGGERS):
            commands = build_login_page_commands(target_site)
            return RuleResult(
                matched=True,
                commands=commands,
                response_text="로그인 페이지로 이동합니다.",
                rule_name="login",
            )

        commands = build_login_page_commands(target_site)
        return RuleResult(
            matched=True,
            commands=commands,
            response_text="로그인 페이지로 이동합니다.",
            rule_name="login",
        )


class LoginPhoneRule(BaseRule):
    """Phone number input on login page."""

    def check(self, text: str, current_url: str, current_site) -> Optional[RuleResult]:
        if get_page_type(current_url) != "login":
            return None

        phone_digits = _extract_phone_digits(text)
        if not phone_digits:
            return None

        phone_selector = get_selector(current_url, "phone_input") if current_url else None
        if not phone_selector and current_site:
            phone_selector = current_site.get_selector("login", "phone_input")
        if not phone_selector:
            phone_selector = "input._phoneInput, input[type='tel']"

        submit_selector = get_selector(current_url, "phone_submit_button") if current_url else None
        if not submit_selector and current_site:
            submit_selector = current_site.get_selector("login", "phone_submit_button")

        commands = [
            build_wait_for_selector_command(
                phone_selector,
                state="visible",
                timeout=8000,
                description="휴대폰 번호 입력칸 대기",
            ),
            build_fill_command(phone_selector, phone_digits, "휴대폰 번호 입력"),
        ]
        if submit_selector:
            commands.append(
                build_wait_for_selector_command(
                    submit_selector,
                    state="visible",
                    timeout=8000,
                    description="인증번호 요청 버튼 대기",
                )
            )
            commands.append(build_click_command(submit_selector, "인증번호 요청"))

        return RuleResult(
            matched=True,
            commands=commands,
            response_text="휴대폰 번호를 입력하고 인증번호를 요청합니다.",
            rule_name="login",
        )


class LoginPhoneTabRule(BaseRule):
    """Switch to phone login tab on login page."""

    def check(self, text: str, current_url: str, current_site) -> Optional[RuleResult]:
        if get_page_type(current_url) != "login":
            return None

        if "휴대폰" not in text:
            return None

        tab_selector = get_selector(current_url, "tab_phone_login") if current_url else None
        if not tab_selector and current_site:
            tab_selector = current_site.get_selector("login", "tab_phone_login")
        if not tab_selector:
            return None

        phone_selector = get_selector(current_url, "phone_input") if current_url else None
        if not phone_selector and current_site:
            phone_selector = current_site.get_selector("login", "phone_input")
        if not phone_selector:
            phone_selector = "input._phoneInput, input[type='tel']"

        commands = [
            build_click_command(tab_selector, "휴대폰 로그인 탭 전환"),
            build_wait_for_selector_command(
                phone_selector,
                state="visible",
                timeout=8000,
                description="휴대폰 번호 입력칸 대기",
            ),
        ]
        return RuleResult(
            matched=True,
            commands=commands,
            response_text="휴대폰 로그인 탭으로 전환합니다, 휴대폰 번호를 불러주시면 대신 입력해 드릴게요.",
            rule_name="login",
        )


class LoginOtpRule(BaseRule):
    """OTP code input on login page."""

    def check(self, text: str, current_url: str, current_site) -> Optional[RuleResult]:
        if get_page_type(current_url) != "login":
            return None

        code = _extract_otp_code(text)
        if not code:
            return None

        selector = get_selector(current_url, "otp_input") if current_url else None
        if not selector and current_site:
            selector = current_site.get_selector("login", "otp_input")
        if not selector:
            selector = (
                "input[autocomplete='one-time-code'], "
                "input[name*='otp' i], input[id*='otp' i], "
                "input[name*='code' i], input[id*='code' i], "
                "input[placeholder*='인증'], "
                "input[type='text']"
            )

        commands = [
            build_wait_for_selector_command(
                selector,
                state="visible",
                timeout=8000,
                description="인증번호 입력칸 대기",
            ),
            build_fill_command(selector, code, "인증번호 입력"),
            build_press_command(selector, "Enter", "인증번호 적용"),
        ]
        return RuleResult(
            matched=True,
            commands=commands,
            response_text="인증번호를 입력합니다.",
            rule_name="login",
        )


def _extract_otp_code(text: str) -> Optional[str]:
    if not text:
        return None
    keywords = ("인증", "번호", "코드", "otp", "입력")
    lowered = text.lower()
    has_keyword = any((k in lowered) if k == "otp" else (k in text) for k in keywords)

    digits = _extract_all_digits(text)
    if 4 <= len(digits) <= 8:
        # Accept if keywords present or text is mostly digits/spaces/hyphens
        if has_keyword or re.fullmatch(r"[0-9\\s\\-]+", text.strip()):
            return digits
    return None


def _extract_phone_number(text: str) -> Optional[str]:
    if not text:
        return None
    match = re.search(r"(010|011|016|017|018|019)[\\s\\-]?[0-9]{3,4}[\\s\\-]?[0-9]{4}", text)
    if not match:
        return None
    return match.group(0)


def _extract_phone_digits(text: str) -> Optional[str]:
    digits = _extract_all_digits(text)
    if len(digits) in (10, 11):
        if digits.startswith(("010", "011", "016", "017", "018", "019")):
            return digits
        return digits
    return None


def _extract_all_digits(text: str) -> str:
    return re.sub(r"\\D", "", text or "")
