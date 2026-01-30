# -*- coding: utf-8 -*-
"""
WebSocket Handler

Real-time bidirectional communication:
- Audio streaming (audio_chunk)
- ASR results (asr_result)
- MCP commands (tool_calls)
- TTS streaming (tts_chunk)
- Flow progression (flow_step)
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

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        """Register new connection"""
        await websocket.accept()
        self._connections[session_id] = websocket
        self._ws_to_session[websocket] = session_id
        logger.info(f"WebSocket connected: session={session_id}")

    def disconnect(self, websocket: WebSocket) -> Optional[str]:
        """Unregister connection"""
        session_id = self._ws_to_session.pop(websocket, None)
        if session_id:
            self._connections.pop(session_id, None)
            logger.info(f"WebSocket disconnected: session={session_id}")
        return session_id

    async def send_message(self, session_id: str, message) -> None:
        """Send message to specific session"""
        ws = self._connections.get(session_id)
        if ws:
            try:
                await ws.send_text(message.to_json())
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {e}")

    async def send_bytes(self, session_id: str, data: bytes) -> None:
        """Send binary data to specific session"""
        ws = self._connections.get(session_id)
        if ws:
            try:
                await ws.send_bytes(data)
            except Exception as e:
                logger.error(f"Failed to send bytes to {session_id}: {e}")

    async def broadcast(self, message) -> None:
        """Broadcast message to all connections"""
        for session_id, ws in self._connections.items():
            try:
                await ws.send_text(message.to_json())
            except Exception as e:
                logger.error(f"Broadcast failed for {session_id}: {e}")

    def get_session_id(self, websocket: WebSocket) -> Optional[str]:
        """Get session ID from WebSocket"""
        return self._ws_to_session.get(websocket)

    def get_connection_count(self) -> int:
        """Get current connection count"""
        return len(self._connections)

    def is_connected(self, session_id: str) -> bool:
        """Check if session is connected"""
        return session_id in self._connections


# Global connection manager
connection_manager = ConnectionManager()


class WebSocketHandler:
    """WebSocket message handler (routing + lifecycle)."""

    def __init__(
        self,
        asr_service=None,
        nlu_service=None,
        llm_planner=None,
        tts_service=None,
        flow_engine=None,
        session_manager=None
    ):
        self._session = session_manager

        self._sender = WSSender(connection_manager, tts_service=tts_service)
        self._handlers = HandlerManager(
            asr_service=asr_service,
            nlu_service=nlu_service,
            llm_planner=llm_planner,
            tts_service=tts_service,
            flow_engine=flow_engine,
            session_manager=session_manager,
            sender=self._sender
        )
        self._router = WebSocketRouter(self._handlers)

    async def handle_connection(self, websocket: WebSocket, session_id: str):
        """Handle WebSocket connection lifecycle"""
        await connection_manager.connect(websocket, session_id)

        session = self._session.get_session(session_id) if self._session else None
        if not session and self._session:
            self._session.create_session(session_id=session_id)

        await self._handlers.create_session(session_id)

        await self._sender.send_status(session_id, "connected", "Connected to server")

        await publish(
            EventType.CLIENT_CONNECTED,
            data={"session_id": session_id},
            source="websocket"
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
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            await self._handlers.cleanup_session(session_id)
            connection_manager.disconnect(websocket)
            await publish(
                EventType.CLIENT_DISCONNECTED,
                data={"session_id": session_id},
                source="websocket"
            )
