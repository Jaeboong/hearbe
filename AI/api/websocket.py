"""
WebSocket 핸들러

실시간 양방향 통신 처리
- 음성 스트리밍 (audio_chunk)
- STT 결과 (stt_result)
- MCP 명령 (tool_calls)
- TTS 스트리밍 (tts_chunk)
- 플로우 진행 (flow_step)
"""

import logging
import json
import asyncio
from typing import Dict, Set, Any, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from dataclasses import dataclass, asdict
from enum import Enum

from core.event_bus import EventType, publish
from core.interfaces import SessionState

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket 메시지 타입"""
    # Client → Server
    AUDIO_CHUNK = "audio_chunk"
    USER_INPUT = "user_input"
    USER_CONFIRM = "user_confirm"
    CANCEL = "cancel"
    MCP_RESULT = "mcp_result"

    # Server → Client
    STT_RESULT = "stt_result"
    TOOL_CALLS = "tool_calls"
    FLOW_STEP = "flow_step"
    TTS_CHUNK = "tts_chunk"
    STATUS = "status"
    ERROR = "error"


@dataclass
class WSMessage:
    """WebSocket 메시지"""
    type: MessageType
    data: Any
    session_id: Optional[str] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)


class ConnectionManager:
    """WebSocket 연결 관리자"""

    def __init__(self):
        # session_id -> WebSocket
        self._connections: Dict[str, WebSocket] = {}
        # WebSocket -> session_id (역방향 조회용)
        self._ws_to_session: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        """새 연결 등록"""
        await websocket.accept()
        self._connections[session_id] = websocket
        self._ws_to_session[websocket] = session_id
        logger.info(f"WebSocket connected: session={session_id}")

    def disconnect(self, websocket: WebSocket) -> Optional[str]:
        """연결 해제"""
        session_id = self._ws_to_session.pop(websocket, None)
        if session_id:
            self._connections.pop(session_id, None)
            logger.info(f"WebSocket disconnected: session={session_id}")
        return session_id

    async def send_message(self, session_id: str, message: WSMessage) -> None:
        """특정 세션에 메시지 전송"""
        ws = self._connections.get(session_id)
        if ws:
            try:
                await ws.send_text(message.to_json())
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {e}")

    async def send_bytes(self, session_id: str, data: bytes) -> None:
        """특정 세션에 바이너리 데이터 전송"""
        ws = self._connections.get(session_id)
        if ws:
            try:
                await ws.send_bytes(data)
            except Exception as e:
                logger.error(f"Failed to send bytes to {session_id}: {e}")

    async def broadcast(self, message: WSMessage) -> None:
        """모든 연결에 메시지 전송"""
        for session_id, ws in self._connections.items():
            try:
                await ws.send_text(message.to_json())
            except Exception as e:
                logger.error(f"Broadcast failed for {session_id}: {e}")

    def get_session_id(self, websocket: WebSocket) -> Optional[str]:
        """WebSocket에서 세션 ID 조회"""
        return self._ws_to_session.get(websocket)

    def get_connection_count(self) -> int:
        """현재 연결 수"""
        return len(self._connections)

    def is_connected(self, session_id: str) -> bool:
        """세션 연결 여부"""
        return session_id in self._connections


# 전역 연결 관리자
connection_manager = ConnectionManager()


class WebSocketHandler:
    """
    WebSocket 메시지 핸들러

    클라이언트-서버 간 실시간 통신 처리
    """

    def __init__(
        self,
        asr_service=None,
        nlu_service=None,
        llm_planner=None,
        tts_service=None,
        flow_engine=None,
        session_manager=None
    ):
        self.asr = asr_service
        self.nlu = nlu_service
        self.llm = llm_planner
        self.tts = tts_service
        self.flow = flow_engine
        self.session = session_manager
        self._audio_buffers: Dict[str, bytes] = {}

    async def handle_connection(self, websocket: WebSocket, session_id: str):
        """WebSocket 연결 처리"""
        await connection_manager.connect(websocket, session_id)

        # 세션 생성 또는 조회
        session = self.session.get_session(session_id)
        if not session:
            session = self.session.create_session()

        # 연결 확인 메시지
        await self._send_status(session_id, "connected", "서버에 연결되었습니다.")

        # 이벤트 발행
        await publish(
            EventType.CLIENT_CONNECTED,
            data={"session_id": session_id},
            source="websocket"
        )

        try:
            while True:
                # 메시지 수신
                data = await websocket.receive()

                if "text" in data:
                    await self._handle_text_message(session_id, data["text"])
                elif "bytes" in data:
                    await self._handle_binary_message(session_id, data["bytes"])

        except WebSocketDisconnect:
            logger.info(f"Client disconnected: {session_id}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            connection_manager.disconnect(websocket)
            await publish(
                EventType.CLIENT_DISCONNECTED,
                data={"session_id": session_id},
                source="websocket"
            )

    async def _handle_text_message(self, session_id: str, text: str):
        """텍스트 메시지 처리"""
        try:
            msg = json.loads(text)
            msg_type = msg.get("type")
            data = msg.get("data", {})

            logger.debug(f"Received message: type={msg_type}, session={session_id}")

            if msg_type == MessageType.AUDIO_CHUNK:
                # Base64 인코딩된 오디오 청크
                import base64
                audio_data = base64.b64decode(data.get("audio", ""))
                await self._handle_audio_chunk(session_id, audio_data, data.get("is_final", False))

            elif msg_type == MessageType.USER_INPUT:
                # 사용자 텍스트 입력 (음성 대신)
                await self._handle_user_input(session_id, data.get("text", ""))

            elif msg_type == MessageType.USER_CONFIRM:
                # 사용자 확인 응답
                await self._handle_user_confirm(session_id, data)

            elif msg_type == MessageType.CANCEL:
                # 취소 요청
                await self._handle_cancel(session_id)

            elif msg_type == MessageType.MCP_RESULT:
                # MCP 실행 결과 (클라이언트에서 전송)
                await self._handle_mcp_result(session_id, data)

            else:
                logger.warning(f"Unknown message type: {msg_type}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            await self._send_error(session_id, "Invalid message format")

    async def _handle_binary_message(self, session_id: str, data: bytes):
        """바이너리 메시지 처리 (오디오 스트림)"""
        await self._handle_audio_chunk(session_id, data, False)

    async def _handle_audio_chunk(self, session_id: str, audio_data: bytes, is_final: bool):
        """오디오 청크 처리"""
        # 버퍼에 누적
        if session_id not in self._audio_buffers:
            self._audio_buffers[session_id] = b""

        self._audio_buffers[session_id] += audio_data

        # 최종 청크면 STT 처리
        if is_final and self.asr:
            buffer = self._audio_buffers.pop(session_id, b"")
            if buffer:
                await self._process_audio(session_id, buffer)

    async def _process_audio(self, session_id: str, audio_data: bytes):
        """오디오 처리 (STT → NLU → LLM → TTS)"""
        try:
            # 1. STT
            await publish(EventType.STT_PROCESSING_STARTED, session_id=session_id)
            stt_result = await self.asr.transcribe(audio_data)

            await self._send_stt_result(session_id, stt_result.text)
            await publish(
                EventType.STT_RESULT_READY,
                data={"text": stt_result.text},
                session_id=session_id
            )

            # 2. 이후 파이프라인 처리
            await self._process_text_input(session_id, stt_result.text)

        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            await self._send_error(session_id, "음성 처리 중 오류가 발생했습니다.")

    async def _handle_user_input(self, session_id: str, text: str):
        """사용자 텍스트 입력 처리"""
        await self._send_stt_result(session_id, text)
        await self._process_text_input(session_id, text)

    async def _process_text_input(self, session_id: str, text: str):
        """텍스트 입력 처리 (NLU → LLM → TTS)"""
        try:
            session = self.session.get_session(session_id)
            if not session:
                return

            # 대화 기록 추가
            self.session.add_to_history(session_id, "user", text)

            # Flow 진행 중인지 확인
            if self.flow and self.flow.is_flow_active(session_id):
                await self._handle_flow_input(session_id, text)
                return

            # 2. NLU - 의도 분석
            if self.nlu:
                context = session.context
                intent = await self.nlu.analyze_intent(text, context)

                # 참조 해석
                resolved_text = await self.nlu.resolve_reference(text, context)

                # 3. LLM - 명령 생성
                if self.llm:
                    response = await self.llm.generate_commands(
                        resolved_text,
                        intent,
                        session
                    )

                    # Flow Engine 위임 필요?
                    if response.requires_flow and self.flow:
                        flow_type = response.flow_type
                        site = session.current_site or "coupang"
                        step = await self.flow.start_flow(flow_type, site, session)
                        await self._send_flow_step(session_id, step)
                    else:
                        # MCP 명령 전송
                        if response.commands:
                            await self._send_tool_calls(session_id, response.commands)

                    # TTS 응답
                    if response.text and self.tts:
                        await self._send_tts_response(session_id, response.text)

                    # 대화 기록 추가
                    self.session.add_to_history(session_id, "assistant", response.text)

        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            await self._send_error(session_id, "처리 중 오류가 발생했습니다.")

    async def _handle_flow_input(self, session_id: str, text: str):
        """플로우 진행 중 입력 처리"""
        session = self.session.get_session(session_id)
        if not session:
            return

        # TODO: 입력 파싱 및 다음 단계 진행
        user_input = {"text": text}
        next_step = await self.flow.next_step(session, user_input)
        await self._send_flow_step(session_id, next_step)

        if next_step.prompt and self.tts:
            await self._send_tts_response(session_id, next_step.prompt)

    async def _handle_user_confirm(self, session_id: str, data: Dict[str, Any]):
        """사용자 확인 응답 처리"""
        confirmed = data.get("confirmed", False)
        if confirmed:
            await self._process_text_input(session_id, "네")
        else:
            await self._process_text_input(session_id, "아니")

    async def _handle_cancel(self, session_id: str):
        """취소 요청 처리"""
        session = self.session.get_session(session_id)
        if session and self.flow:
            await self.flow.cancel_flow(session)

        await self._send_status(session_id, "cancelled", "취소되었습니다.")

        if self.tts:
            await self._send_tts_response(session_id, "취소되었습니다.")

    async def _handle_mcp_result(self, session_id: str, data: Dict[str, Any]):
        """MCP 실행 결과 처리"""
        # 클라이언트에서 MCP 명령 실행 후 결과 전송
        success = data.get("success", False)
        result = data.get("result", {})
        error = data.get("error")

        await publish(
            EventType.MCP_RESULT_RECEIVED,
            data={"success": success, "result": result, "error": error},
            session_id=session_id
        )

        # 결과에 따라 응답 생성
        if self.llm:
            session = self.session.get_session(session_id)
            if session:
                # 컨텍스트에 결과 저장
                self.session.set_context(session_id, "mcp_result", result)

                # 응답 텍스트 생성
                response_text = await self.llm.generate_response(session.context)

                if self.tts:
                    await self._send_tts_response(session_id, response_text)

    # ========================================================================
    # 메시지 전송 헬퍼
    # ========================================================================

    async def _send_status(self, session_id: str, status: str, message: str):
        """상태 메시지 전송"""
        msg = WSMessage(
            type=MessageType.STATUS,
            data={"status": status, "message": message},
            session_id=session_id
        )
        await connection_manager.send_message(session_id, msg)

    async def _send_error(self, session_id: str, error: str):
        """에러 메시지 전송"""
        msg = WSMessage(
            type=MessageType.ERROR,
            data={"error": error},
            session_id=session_id
        )
        await connection_manager.send_message(session_id, msg)

    async def _send_stt_result(self, session_id: str, text: str):
        """STT 결과 전송"""
        msg = WSMessage(
            type=MessageType.STT_RESULT,
            data={"text": text},
            session_id=session_id
        )
        await connection_manager.send_message(session_id, msg)

    async def _send_tool_calls(self, session_id: str, commands: list):
        """MCP 명령 전송"""
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
        await connection_manager.send_message(session_id, msg)

    async def _send_flow_step(self, session_id: str, step):
        """플로우 단계 전송"""
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
        await connection_manager.send_message(session_id, msg)

    async def _send_tts_response(self, session_id: str, text: str):
        """TTS 응답 전송 (스트리밍)"""
        if not self.tts:
            return

        try:
            async for chunk in self.tts.synthesize_stream(text):
                msg = WSMessage(
                    type=MessageType.TTS_CHUNK,
                    data={
                        "audio": chunk.audio_data.hex() if chunk.audio_data else "",
                        "is_final": chunk.is_final,
                        "sample_rate": chunk.sample_rate
                    },
                    session_id=session_id
                )
                await connection_manager.send_message(session_id, msg)

        except Exception as e:
            logger.error(f"TTS streaming failed: {e}")