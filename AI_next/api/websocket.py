# -*- coding: utf-8 -*-
"""
WebSocket Handler

Real-time bidirectional communication:
- Audio streaming (audio_chunk)
- ASR results (asr_result)
- MCP commands (tool_calls)
- TTS streaming (tts_chunk)

(AI_next: LLM/NLU/Flow 의존성 제거)
"""

import logging
from typing import Dict, Optional

from fastapi import WebSocket, WebSocketDisconnect

from core.event_bus import EventType, publish

from .ws.router import WebSocketRouter
from .ws.sender import WSSender
from .ws.handlers.handler_manager import HandlerManager

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager"""

    def __init__(self):
        self._connections: Dict[str, WebSocket] = {}
        self._ws_to_session: Dict[WebSocket, str] = {}

    @staticmethod
    def _is_closed_socket_error(exc: Exception) -> bool:
        if isinstance(exc, WebSocketDisconnect):
            return True
        msg = str(exc) or ""
        return (
            'Cannot call "send" once a close message has been sent.' in msg
            or 'Cannot call "receive" once a disconnect message has been received.' in msg
            or "WebSocket is not connected" in msg
            or "connection closed" in msg.lower()
        )

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        await websocket.accept()
        self._connections[session_id] = websocket
        self._ws_to_session[websocket] = session_id
        logger.info(f"WebSocket connected: session={session_id}")

    def disconnect(self, websocket: WebSocket) -> Optional[str]:
        session_id = self._ws_to_session.pop(websocket, None)
        if session_id:
            self._connections.pop(session_id, None)
            logger.info(f"WebSocket disconnected: session={session_id}")
        return session_id

    async def send_message(self, session_id: str, message) -> bool:
        ws = self._connections.get(session_id)
        if not ws:
            return False
        try:
            await ws.send_text(message.to_json())
            return True
        except Exception as e:
            if self._is_closed_socket_error(e):
                logger.warning(
                    "WebSocket send failed (closed). Disconnecting: session=%s err=%s: %s",
                    session_id, type(e).__name__, e,
                )
            else:
                logger.error(
                    "WebSocket send failed. Disconnecting: session=%s err=%s: %s",
                    session_id, type(e).__name__, e,
                )
            self.disconnect(ws)
            return False

    async def send_bytes(self, session_id: str, data: bytes) -> bool:
        ws = self._connections.get(session_id)
        if not ws:
            return False
        try:
            await ws.send_bytes(data)
            return True
        except Exception as e:
            if self._is_closed_socket_error(e):
                logger.warning(
                    "WebSocket send_bytes failed (closed). Disconnecting: session=%s",
                    session_id,
                )
            else:
                logger.error(
                    "WebSocket send_bytes failed. Disconnecting: session=%s",
                    session_id,
                )
            self.disconnect(ws)
            return False

    async def broadcast(self, message) -> None:
        for session_id, ws in list(self._connections.items()):
            try:
                await ws.send_text(message.to_json())
            except Exception as e:
                logger.error(f"Broadcast failed for {session_id}: {e}")

    def get_session_id(self, websocket: WebSocket) -> Optional[str]:
        return self._ws_to_session.get(websocket)

    def get_connection_count(self) -> int:
        return len(self._connections)

    def is_connected(self, session_id: str) -> bool:
        return session_id in self._connections


connection_manager = ConnectionManager()


class WebSocketHandler:
    """WebSocket message handler (routing + lifecycle)."""

    def __init__(
        self,
        asr_service=None,
        tts_service=None,
        session_manager=None,
        intent_router=None,
    ):
        self._session = session_manager

        self._sender = WSSender(connection_manager, tts_service=tts_service)
        self._handlers = HandlerManager(
            asr_service=asr_service,
            tts_service=tts_service,
            session_manager=session_manager,
            sender=self._sender,
            intent_router=intent_router,
        )
        self._router = WebSocketRouter(self._handlers)

    async def handle_connection(self, websocket: WebSocket, session_id: str):
        await connection_manager.connect(websocket, session_id)

        session = self._session.get_session(session_id) if self._session else None
        if not session and self._session:
            self._session.create_session(session_id=session_id)

        await self._handlers.create_session(session_id)
        await self._sender.send_status(session_id, "connected", "Connected to server")

        await publish(
            EventType.CLIENT_CONNECTED,
            data={"session_id": session_id},
            source="websocket",
        )

        try:
            while True:
                data = await websocket.receive()
                if "text" in data:
                    await self._router.handle_text(session_id, data["text"])
                elif "bytes" in data:
                    await self._router.handle_binary(session_id, data["bytes"])

        except WebSocketDisconnect:
            logger.info(f"Client disconnected: {session_id}")
        except RuntimeError as e:
            if ConnectionManager._is_closed_socket_error(e):
                logger.info(f"Client disconnected: {session_id}")
            else:
                logger.error(f"WebSocket runtime error: {e}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            await self._handlers.cleanup_session(session_id)
            connection_manager.disconnect(websocket)
            await publish(
                EventType.CLIENT_DISCONNECTED,
                data={"session_id": session_id},
                source="websocket",
            )
