# -*- coding: utf-8 -*-
"""
Handler manager: orchestrates WS handlers and session lifecycle.
"""

import base64
import logging
import os
import time

from services.llm.sites.site_manager import get_current_site, get_page_type
from services.llm.generators.tts_generator import TTSGenerator

from .audio_handler import AudioHandler
from .text_handler import TextHandler
from .mcp_handler import MCPHandler
from .dom_fallback import DomFallbackManager
from .payment_keypad import PaymentKeypadManager
from .page_extract_manager import PageExtractManager
from ..feedback.action_feedback import ActionFeedbackManager
from ..feedback.login_guard import LoginGuard
from ..feedback.login_feedback import LoginFeedbackManager
from ..feedback.order_detail_handler import OrderDetailHandler
from ..feedback.tool_failure_notifier import ToolFailureNotifier

logger = logging.getLogger(__name__)


class HandlerManager:
    """Coordinates handlers and shared dependencies."""

    def __init__(
        self,
        asr_service=None,
        nlu_service=None,
        llm_planner=None,
        tts_service=None,
        flow_engine=None,
        session_manager=None,
        sender=None
    ):
        self._sender = sender
        self._session = session_manager
        self._tts = TTSGenerator()

        self._action_feedback = ActionFeedbackManager(sender)
        self._failure_notifier = ToolFailureNotifier(sender)
        self._login_guard = LoginGuard(session_manager, sender, self._action_feedback)
        self._login_feedback = LoginFeedbackManager(session_manager, sender)
        self._dom_fallback = DomFallbackManager(
            sender=sender,
            session_manager=session_manager,
            action_feedback=self._action_feedback,
            login_guard=self._login_guard,
            login_feedback=self._login_feedback,
        )
        self._payment_keypad = PaymentKeypadManager(
            sender=sender,
            session_manager=session_manager,
        )
        self._order_detail = OrderDetailHandler(
            sender=sender,
            session_manager=session_manager,
        )
        self._page_extract = PageExtractManager(
            sender=sender,
            session_manager=session_manager,
        )

        self._text_handler = TextHandler(
            nlu_service=nlu_service,
            llm_planner=llm_planner,
            flow_engine=flow_engine,
            session_manager=session_manager,
            sender=sender,
            action_feedback=self._action_feedback,
            login_guard=self._login_guard,
            login_feedback=self._login_feedback,
            payment_keypad=self._payment_keypad,
            order_detail_handler=self._order_detail,
            page_extract=self._page_extract,
        )
        self._audio_handler = AudioHandler(
            asr_service=asr_service,
            sender=sender,
            enqueue_text=self._text_handler.enqueue_text
        )
        self._mcp_handler = MCPHandler(
            sender=sender,
            session_manager=session_manager,
            action_feedback=self._action_feedback,
            failure_notifier=self._failure_notifier,
            login_guard=self._login_guard,
            login_feedback=self._login_feedback,
            dom_fallback=self._dom_fallback
        )

    async def create_session(self, session_id: str):
        await self._audio_handler.create_session(session_id)
        await self._text_handler.create_session(session_id)

    async def cleanup_session(self, session_id: str):
        await self._audio_handler.cleanup_session(session_id)
        await self._text_handler.cleanup_session(session_id)
        self._action_feedback.clear_pending(session_id)
        self._login_guard.clear_pending(session_id)
        self._login_feedback.clear_pending(session_id)
        self._dom_fallback.clear_pending(session_id)
        self._mcp_handler.cleanup_session(session_id)
        self._payment_keypad.cleanup_session(session_id)
        self._order_detail.cleanup_session(session_id)

    async def handle_audio_chunk(self, session_id: str, data: dict):
        audio_data = base64.b64decode(data.get("audio", ""))
        seq = data.get("seq", 0)
        is_final = data.get("is_final", False)
        await self._audio_handler.handle_audio_chunk(session_id, audio_data, seq, is_final)

    async def handle_binary_audio(self, session_id: str, data: bytes):
        await self._audio_handler.handle_binary_audio(session_id, data)

    async def handle_user_input(self, session_id: str, data: dict):
        await self._text_handler.handle_user_input(session_id, data.get("text", ""))

    async def handle_user_confirm(self, session_id: str, data: dict):
        await self._text_handler.handle_user_confirm(session_id, data)

    async def handle_cancel(self, session_id: str):
        await self._audio_handler.clear_audio(session_id)
        await self._text_handler.handle_cancel(session_id)
        self._action_feedback.clear_pending(session_id)
        self._login_guard.clear_pending(session_id)
        self._login_feedback.clear_pending(session_id)
        self._dom_fallback.clear_pending(session_id)
        self._payment_keypad.cleanup_session(session_id)
        self._order_detail.cleanup_session(session_id)

    async def handle_interrupt(self, session_id: str):
        await self._audio_handler.clear_audio(session_id)
        await self._text_handler.interrupt(session_id)
        if self._session:
            self._session.set_context(session_id, "interrupt_ts", time.time())
            try:
                suppress_sec = float(os.getenv("TTS_INTERRUPT_SUPPRESS_SEC", "3"))
            except ValueError:
                suppress_sec = 3.0
            self._session.set_context(
                session_id,
                "tts_suppress_until",
                time.time() + suppress_sec
            )
        self._action_feedback.clear_pending(session_id)
        self._login_feedback.clear_pending(session_id)
        self._dom_fallback.clear_pending(session_id)
        self._payment_keypad.cleanup_session(session_id)
        self._order_detail.cleanup_session(session_id)
        if self._sender:
            await self._sender.cancel_tts(session_id)

    async def handle_mcp_result(self, session_id: str, data: dict):
        handled = await self._payment_keypad.handle_mcp_result(session_id, data)
        if handled:
            return
        handled = await self._order_detail.handle_mcp_result(session_id, data)
        if handled:
            return
        await self._mcp_handler.handle_mcp_result(session_id, data)

    async def handle_page_update(self, session_id: str, data: dict):
        url = data.get("url") or data.get("page_url") or data.get("current_url")
        page_id = data.get("page_id")
        if not url:
            return
        session = self._session.get_session(session_id) if self._session else None
        if not session:
            return
        previous_url = session.current_url
        if previous_url and previous_url != url:
            self._session.set_context(session_id, "previous_url", previous_url)
        session.current_url = url
        site = get_current_site(url)
        if site:
            session.current_site = site.name
        await self._payment_keypad.handle_page_update(session_id, url)
        await self._order_detail.handle_page_update(session_id, url)
        await self._page_extract.handle_page_update(session_id, url, page_id)

        # One-time login page guidance after redirect
        if not previous_url or previous_url == url:
            return
        if get_page_type(url) != "login":
            return
        if get_page_type(previous_url) == "login":
            return
        if not self._session or self._session.get_context(session_id, "login_guidance_shown", False):
            return
        if self._sender:
            await self._sender.send_tts_response(
                session_id,
                self._tts.build_login_guidance()
            )
        self._session.set_context(session_id, "login_guidance_shown", True)

    async def handle_invalid_message(self, session_id: str, error: str):
        await self._sender.send_error(session_id, error)
