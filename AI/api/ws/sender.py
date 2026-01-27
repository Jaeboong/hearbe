# -*- coding: utf-8 -*-
"""
WebSocket sender helpers

Centralizes outbound message formats for WS responses.
"""

import logging
from typing import Optional

from core.interfaces import ASRResult
from .models import MessageType, WSMessage
from .tts_normalizer import normalize_tts_text

logger = logging.getLogger(__name__)


class WSSender:
    """WS message sender with optional TTS streaming support."""

    def __init__(self, connection_manager, tts_service=None):
        self._connections = connection_manager
        self._tts = tts_service

    async def send_status(self, session_id: str, status: str, message: str):
        msg = WSMessage(
            type=MessageType.STATUS,
            data={"status": status, "message": message},
            session_id=session_id
        )
        await self._connections.send_message(session_id, msg)

    async def send_error(self, session_id: str, error: str):
        msg = WSMessage(
            type=MessageType.ERROR,
            data={"error": error},
            session_id=session_id
        )
        await self._connections.send_message(session_id, msg)

    async def send_asr_result(self, session_id: str, result: ASRResult):
        msg = WSMessage(
            type=MessageType.ASR_RESULT,
            data={
                "text": result.text,
                "confidence": result.confidence,
                "language": result.language,
                "duration": result.duration,
                "is_final": result.is_final,
                "segment_id": result.segment_id
            },
            session_id=session_id
        )
        await self._connections.send_message(session_id, msg)

    async def send_tool_calls(self, session_id: str, commands: list):
        msg = WSMessage(
            type=MessageType.TOOL_CALLS,
            data={
                "commands": [
                    {
                        "tool_name": cmd.tool_name,
                        "arguments": cmd.arguments,
                        "description": cmd.description
                    }
                    for cmd in commands
                ]
            },
            session_id=session_id
        )
        # TODO: [TEMP] Broadcasting to all clients for testing
        # In production, send only to the originating session
        logger.info(f"[BROADCAST] Sending {len(commands)} tool calls to all clients")
        await self._connections.broadcast(msg)

    async def send_flow_step(self, session_id: str, step):
        msg = WSMessage(
            type=MessageType.FLOW_STEP,
            data={
                "step_id": step.step_id,
                "prompt": step.prompt,
                "required_fields": step.required_fields,
                "action": step.action
            },
            session_id=session_id
        )
        await self._connections.send_message(session_id, msg)

    async def send_tts_response(self, session_id: str, text: str):
        if not self._tts:
            logger.warning("TTS service not available")
            return

        try:
            text = normalize_tts_text(text)
            chunk_count = 0
            async for chunk in self._tts.synthesize_stream(text):
                msg = WSMessage(
                    type=MessageType.TTS_CHUNK,
                    data={
                        "audio": chunk.audio_data.hex() if chunk.audio_data else "",
                        "is_final": chunk.is_final,
                        "sample_rate": chunk.sample_rate
                    },
                    session_id=session_id
                )
                await self._connections.send_message(session_id, msg)
                chunk_count += 1
            logger.info(f"TTS completed: {chunk_count} chunks sent for '{text[:50]}...'")
        except Exception as e:
            logger.error(f"TTS streaming failed: {e}")

    async def send_ocr_progress(
        self,
        session_id: str,
        status: str,
        progress: int,
        total_images: int,
        current_chunk: int = 0,
        total_chunks: int = 0,
        error: Optional[str] = None
    ):
        msg = WSMessage(
            type=MessageType.OCR_PROGRESS,
            data={
                "status": status,
                "progress": progress,
                "total_images": total_images,
                "current_chunk": current_chunk,
                "total_chunks": total_chunks,
                "error": error
            },
            session_id=session_id
        )
        await self._connections.send_message(session_id, msg)
