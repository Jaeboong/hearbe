# -*- coding: utf-8 -*-
"""
Login feedback manager

Tracks login submit attempts and announces successful navigation after login.
"""

from typing import Optional

from services.llm.sites.site_manager import get_page_type, get_selector, get_site_manager


class LoginFeedbackManager:
    """Login-related feedback helpers."""

    def __init__(self, session_manager, sender):
        self._session = session_manager
        self._sender = sender

    def clear_pending(self, session_id: str):
        if self._session:
            self._session.set_context(session_id, "login_submit_pending", False)

    def mark_login_submit_pending(self, session_id: str, commands, current_url: str):
        if not self._session or not commands:
            return
        if get_page_type(current_url) != "login":
            return

        login_selector = (
            get_selector(current_url, "login_button")
            or get_selector(current_url, "submit_button")
            or "button[type='submit']"
        )
        password_selector = get_selector(current_url, "password_input")

        for cmd in commands:
            try:
                tool = cmd.tool_name
                args = cmd.arguments or {}
                if tool in ("click", "click_element"):
                    selector = args.get("selector")
                    if selector and selector == login_selector:
                        self._session.set_context(session_id, "login_submit_pending", True)
                        return
                if tool == "click_text":
                    text = (args.get("text") or "").strip()
                    if text in ("로그인", "로그인하기", "로그인 버튼"):
                        self._session.set_context(session_id, "login_submit_pending", True)
                        return
                if tool in ("press", "press_key"):
                    key = args.get("key")
                    selector = args.get("selector")
                    if key == "Enter" and password_selector and selector == password_selector:
                        self._session.set_context(session_id, "login_submit_pending", True)
                        return
            except Exception:
                continue

    async def maybe_announce_login_success(
        self,
        session_id: str,
        previous_url: Optional[str],
        current_url: Optional[str],
    ):
        if not self._session or not self._sender:
            return
        if not previous_url or not current_url or previous_url == current_url:
            return
        if get_page_type(previous_url) != "login":
            return
        if get_page_type(current_url) == "login":
            return
        if not self._session.get_context(session_id, "login_submit_pending", False):
            return

        tts = self._build_login_success_tts(current_url)
        if tts:
            await self._sender.send_tts_response(session_id, tts)
        self._session.set_context(session_id, "login_submit_pending", False)

    def _build_login_success_tts(self, current_url: str) -> str:
        site = get_site_manager().get_site_by_url(current_url)
        site_name = site.name if site and site.name else ""
        page_type = get_page_type(current_url)
        page_label = {
            "home": "홈",
            "search": "검색",
            "product": "상품",
            "cart": "장바구니",
            "checkout": "결제",
            "order": "주문",
        }.get(page_type)
        if page_label:
            prefix = f"{site_name} " if site_name else ""
            return f"로그인 완료되었습니다. {prefix}{page_label} 페이지로 이동했습니다."
        return "로그인 완료되었습니다. 페이지가 이동되었습니다."
