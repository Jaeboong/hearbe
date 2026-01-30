# -*- coding: utf-8 -*-
"""
WebSocket sender helpers

Centralizes outbound message formats for WS responses.
"""

import logging
import re
from typing import Optional, Iterable, List

from core.interfaces import ASRResult
from .models import MessageType, WSMessage
from .tts.tts_normalizer import normalize_tts_text

logger = logging.getLogger(__name__)


class WSSender:
    """WS message sender with optional TTS streaming support."""

    def __init__(self, connection_manager, tts_service=None):
        self._connections = connection_manager
        self._tts = tts_service
        self._tts_epoch = {}

    async def cancel_tts(self, session_id: str):
        """Cancel ongoing TTS streaming for a session."""
        self._tts_epoch[session_id] = self._tts_epoch.get(session_id, 0) + 1

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
            text = _strip_urls(text)
            text = _normalize_line_breaks(text)
            text = normalize_tts_text(text)
            segments = _split_tts_text(text)
            epoch = self._tts_epoch.get(session_id, 0)
            chunk_count = 0
            for segment in segments:
                if self._tts_epoch.get(session_id, 0) != epoch:
                    logger.info(f"TTS cancelled: session={session_id}")
                    break
                if not segment:
                    continue
                async for chunk in self._tts.synthesize_stream(segment):
                    if self._tts_epoch.get(session_id, 0) != epoch:
                        logger.info(f"TTS cancelled: session={session_id}")
                        break
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
            preview = segments[0][:50] if segments else ""
            logger.info(f"TTS completed: {chunk_count} chunks sent for '{preview}...'")
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


_URL_PATTERN = re.compile(r"https?://\S+")


def _strip_urls(text: str) -> str:
    if not text:
        return text
    cleaned = _URL_PATTERN.sub("", text)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _normalize_line_breaks(text: str) -> str:
    if not text:
        return text
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""
    normalized: List[str] = []
    for line in lines:
        if re.search(r"[.!?。…]$", line):
            normalized.append(line)
        else:
            normalized.append(f"{line}.")
    return " ".join(normalized)


def _split_tts_text(text: str, max_chars: int = 200) -> List[str]:
    if not text:
        return []
    # Split by sentence endings or newlines.
    parts = re.split(r"(?<=[.!?。…])\s+|\n+", text)
    segments: List[str] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(part) <= max_chars:
            segments.append(part)
            continue
        # Further split long segments by commas or spaces.
        while len(part) > max_chars:
            cut = part.rfind(",", 0, max_chars)
            if cut == -1:
                cut = part.rfind(" ", 0, max_chars)
            if cut == -1:
                cut = max_chars
            segments.append(part[:cut].strip())
            part = part[cut:].strip()
        if part:
            segments.append(part)
    return segments
