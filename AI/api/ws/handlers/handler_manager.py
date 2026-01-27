# -*- coding: utf-8 -*-
"""
Handler manager: orchestrates WS handlers and session lifecycle.
"""

import base64
import logging

from .audio_handler import AudioHandler
from .text_handler import TextHandler
from .mcp_handler import MCPHandler
from ..action_feedback import ActionFeedbackManager

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

        self._action_feedback = ActionFeedbackManager(sender)

        self._text_handler = TextHandler(
            nlu_service=nlu_service,
            llm_planner=llm_planner,
            flow_engine=flow_engine,
            session_manager=session_manager,
            sender=sender,
            action_feedback=self._action_feedback
        )
        self._audio_handler = AudioHandler(
            asr_service=asr_service,
            sender=sender,
            enqueue_text=self._text_handler.enqueue_text
        )
        self._mcp_handler = MCPHandler(
            sender=sender,
            session_manager=session_manager,
            action_feedback=self._action_feedback
        )

    async def create_session(self, session_id: str):
        await self._audio_handler.create_session(session_id)
        await self._text_handler.create_session(session_id)

    async def cleanup_session(self, session_id: str):
        await self._audio_handler.cleanup_session(session_id)
        await self._text_handler.cleanup_session(session_id)
        self._action_feedback.clear_pending(session_id)

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

    async def handle_mcp_result(self, session_id: str, data: dict):
        await self._mcp_handler.handle_mcp_result(session_id, data)

    async def handle_invalid_message(self, session_id: str, error: str):
        await self._sender.send_error(session_id, error)
