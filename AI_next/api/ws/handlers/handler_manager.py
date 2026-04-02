# -*- coding: utf-8 -*-
"""
Handler manager: orchestrates WS handlers and session lifecycle.

ASR 결과 또는 텍스트 입력 → IntentRouter로 의도 분류 → MCP 커맨드/TTS 응답
"""

import base64
import logging

from .audio_handler import AudioHandler

logger = logging.getLogger(__name__)


class HandlerManager:
    """Coordinates handlers and shared dependencies."""

    def __init__(
        self,
        asr_service=None,
        tts_service=None,
        session_manager=None,
        sender=None,
        intent_router=None,
    ):
        self._sender = sender
        self._session = session_manager
        self._intent_router = intent_router

        self._audio_handler = AudioHandler(
            asr_service=asr_service,
            sender=sender,
            on_transcription=self._on_asr_text,
        )

    async def _on_asr_text(self, session_id: str, text: str):
        """ASR 결과 텍스트 수신 콜백 → IntentRouter로 처리"""
        logger.info("[ASR -> TEXT] session=%s text=%s", session_id, text)
        await self._process_text(session_id, text)

    async def _process_text(self, session_id: str, text: str):
        """공통 텍스트 처리: 분류 → 액션 실행 → 응답"""
        if not self._intent_router:
            logger.warning("[STUB] No intent router configured")
            return

        session = self._session.get_session(session_id) if self._session else None
        if not session:
            logger.warning("No session found: %s", session_id)
            return

        result = await self._intent_router.process(text, session)

        logger.info(
            "[INTENT] intent=%s conf=%.3f site=%s page=%s cmds=%d tts='%s'",
            result.intent, result.confidence, result.site_id,
            result.page_type, len(result.commands),
            (result.tts_text[:60] + "...") if len(result.tts_text) > 60 else result.tts_text,
        )

        # MCP 커맨드 전송
        if result.commands and self._sender:
            await self._sender.send_tool_calls(session_id, result.commands)

        # TTS 응답
        if result.tts_text and self._sender:
            await self._sender.send_tts_response(session_id, result.tts_text)

    # ── session lifecycle ──────────────────────────────────────────

    async def create_session(self, session_id: str):
        await self._audio_handler.create_session(session_id)
        if self._sender:
            logger.info("[TEST] TTS 테스트 전송: session=%s", session_id)
            await self._sender.send_tts_response(session_id, "연결되었습니다.")

    async def cleanup_session(self, session_id: str):
        await self._audio_handler.cleanup_session(session_id)

    # ── audio ──────────────────────────────────────────────────────

    async def handle_audio_chunk(self, session_id: str, data: dict):
        audio_data = base64.b64decode(data.get("audio", ""))
        seq = data.get("seq", 0)
        is_final = data.get("is_final", False)
        await self._audio_handler.handle_audio_chunk(session_id, audio_data, seq, is_final)

    async def handle_binary_audio(self, session_id: str, data: bytes):
        await self._audio_handler.handle_binary_audio(session_id, data)

    # ── user text input ────────────────────────────────────────────

    async def handle_user_input(self, session_id: str, data: dict):
        text = data.get("text", "")
        if text.strip():
            logger.info("[INPUT] Text: %s", text.strip())
            await self._process_text(session_id, text.strip())

    # ── MCP result ─────────────────────────────────────────────────

    async def handle_mcp_result(self, session_id: str, data: dict):
        tool_name = data.get("tool_name")
        success = data.get("success", False)
        result_data = data.get("result", {})
        error = data.get("error")

        logger.info("[MCP_RESULT] tool=%s success=%s session=%s", tool_name, success, session_id)

        session = self._session.get_session(session_id) if self._session else None
        if not session:
            return

        # extract 결과를 세션 컨텍스트에 저장
        if tool_name == "extract" and success and result_data:
            if not hasattr(session, "context"):
                session.context = {}

            site = None
            if self._intent_router:
                site = self._intent_router._site_manager.get_site_by_url(
                    getattr(session, "current_url", "")
                )
            page_type = site.detect_page_type(session.current_url) if site else None

            if page_type == "search":
                session.context["search_results"] = result_data
                logger.info("Stored %d search results", len(result_data) if isinstance(result_data, list) else 1)
            elif page_type == "cart":
                session.context["cart_items"] = result_data
            elif page_type == "product":
                session.context["product_detail"] = result_data
            elif page_type == "orderlist":
                session.context["order_list"] = result_data

        if error and self._sender:
            await self._sender.send_tts_response(session_id, "작업 중 오류가 발생했습니다.")

    # ── page update ───────────────────────────────────────────────

    async def handle_page_update(self, session_id: str, data: dict):
        url = data.get("url") or data.get("page_url") or data.get("current_url")
        logger.info("handle_page_update: session=%s url=%s", session_id, url)
        if not url:
            return
        session = self._session.get_session(session_id) if self._session else None
        if session:
            session.current_url = url

        # iframe 감지 정보 저장
        iframes = data.get("iframes")
        if iframes and session:
            if not hasattr(session, "context"):
                session.context = {}
            session.context["iframes"] = iframes
            logger.info("Detected %d iframes", len(iframes))

    # ── cancel / interrupt ────────────────────────────────────────

    async def handle_cancel(self, session_id: str):
        await self._audio_handler.clear_audio(session_id)
        logger.info("Session cancelled: %s", session_id)

    async def handle_interrupt(self, session_id: str):
        await self._audio_handler.clear_audio(session_id)
        if self._sender:
            await self._sender.cancel_tts(session_id)
        logger.info("Session interrupted: %s", session_id)

    # ── error ─────────────────────────────────────────────────────

    async def handle_invalid_message(self, session_id: str, error: str):
        await self._sender.send_error(session_id, error)
