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
import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from dataclasses import dataclass, asdict
from enum import Enum

from core.event_bus import EventType, publish
from core.interfaces import SessionState, ASRResult

logger = logging.getLogger(__name__)


# ============================================================================
# Audio Contract Constants
# ============================================================================

AUDIO_SAMPLE_RATE = 16000          # 16kHz (Whisper requirement)
AUDIO_CHANNELS = 1                  # Mono
AUDIO_BIT_DEPTH = 16                # 16-bit
AUDIO_BYTES_PER_SAMPLE = 2          # 16-bit = 2 bytes
AUDIO_FRAME_MS = 20                 # 20ms frame (VAD compatible)
AUDIO_FRAME_BYTES = AUDIO_SAMPLE_RATE * AUDIO_BYTES_PER_SAMPLE * AUDIO_FRAME_MS // 1000  # 640 bytes

# Buffer thresholds
BUFFER_THRESHOLD_BYTES = 32000      # ~1 second of audio
BUFFER_OVERLAP_BYTES = 6400         # 200ms overlap for continuity
MAX_BUFFER_SIZE = 320000            # 10 seconds max (memory limit)
MAX_QUEUE_SIZE = 50                 # Max pending chunks per session

# PTT (Push-to-Talk) mode: client controls recording
# Server simply transcribes whatever audio chunks it receives
# No VAD needed - client sends is_final=true when recording stops


class MessageType(str, Enum):
    """WebSocket message types"""
    # Client -> Server
    AUDIO_CHUNK = "audio_chunk"
    USER_INPUT = "user_input"
    USER_CONFIRM = "user_confirm"
    CANCEL = "cancel"
    MCP_RESULT = "mcp_result"

    # Server -> Client
    ASR_RESULT = "asr_result"
    TOOL_CALLS = "tool_calls"
    FLOW_STEP = "flow_step"
    TTS_CHUNK = "tts_chunk"
    STATUS = "status"
    ERROR = "error"


@dataclass
class WSMessage:
    """WebSocket message"""
    type: MessageType
    data: Any
    session_id: Optional[str] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)


@dataclass
class AudioChunk:
    """Audio chunk with metadata"""
    data: bytes
    seq: int
    is_final: bool = False
    timestamp_ms: int = 0


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

    async def send_message(self, session_id: str, message: WSMessage) -> None:
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

    async def broadcast(self, message: WSMessage) -> None:
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

# Global ASR lock for GPU serialization
_asr_lock = asyncio.Lock()


class WebSocketHandler:
    """
    WebSocket message handler with Queue-based ASR processing.

    Architecture:
    - Receive loop: puts audio chunks into per-session queue (fast)
    - Worker task: pulls from queue, buffers, and triggers ASR (slow)
    - Separation prevents receive blocking during ASR inference
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

        # Per-session state
        self._audio_queues: Dict[str, asyncio.Queue] = {}
        self._audio_buffers: Dict[str, bytes] = {}
        self._worker_tasks: Dict[str, asyncio.Task] = {}
        self._chunk_counters: Dict[str, int] = {}
        self._segment_counters: Dict[str, int] = {}

    async def handle_connection(self, websocket: WebSocket, session_id: str):
        """Handle WebSocket connection lifecycle"""
        await connection_manager.connect(websocket, session_id)

        # Create or retrieve session
        session = self.session.get_session(session_id) if self.session else None
        if not session and self.session:
            session = self.session.create_session(session_id=session_id)

        # Initialize per-session state
        self._audio_queues[session_id] = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)
        self._audio_buffers[session_id] = b""
        self._chunk_counters[session_id] = 0
        self._segment_counters[session_id] = 0

        # Start ASR worker task
        self._worker_tasks[session_id] = asyncio.create_task(
            self._asr_worker(session_id)
        )

        # Send connection confirmation
        await self._send_status(session_id, "connected", "Connected to server")

        # Publish connection event
        await publish(
            EventType.CLIENT_CONNECTED,
            data={"session_id": session_id},
            source="websocket"
        )

        try:
            while True:
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
            await self._cleanup_session(session_id)
            connection_manager.disconnect(websocket)
            await publish(
                EventType.CLIENT_DISCONNECTED,
                data={"session_id": session_id},
                source="websocket"
            )

    async def _cleanup_session(self, session_id: str):
        """Clean up session resources on disconnect"""
        # Cancel worker task
        if session_id in self._worker_tasks:
            task = self._worker_tasks.pop(session_id)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Clear buffers and queues
        self._audio_queues.pop(session_id, None)
        self._audio_buffers.pop(session_id, None)
        self._chunk_counters.pop(session_id, None)
        self._segment_counters.pop(session_id, None)

        logger.debug(f"Session resources cleaned up: {session_id}")

    async def _asr_worker(self, session_id: str):
        """
        ASR worker task for PTT (Push-to-Talk) mode.

        Client controls recording start/stop:
        - Receives audio chunks and buffers them
        - Transcribes when is_final=true (user released record button)
        - Also transcribes partial results for long recordings (>3s chunks)
        """
        queue = self._audio_queues.get(session_id)
        if not queue:
            return

        logger.debug(f"ASR worker started: {session_id}")

        try:
            while True:
                try:
                    chunk: AudioChunk = await asyncio.wait_for(
                        queue.get(),
                        timeout=30.0
                    )
                except asyncio.TimeoutError:
                    continue

                # Append chunk to buffer
                buffer = self._audio_buffers.get(session_id, b"")
                buffer += chunk.data
                self._audio_buffers[session_id] = buffer

                # Check buffer size limit
                if len(buffer) > MAX_BUFFER_SIZE:
                    logger.warning(f"Buffer overflow, truncating: {session_id}")
                    buffer = buffer[-MAX_BUFFER_SIZE:]
                    self._audio_buffers[session_id] = buffer

                # Transcribe if:
                # 1. is_final=true (user released record button)
                # 2. Buffer has data and chunk signals end of a segment
                should_transcribe = chunk.is_final and len(buffer) > 0

                if should_transcribe and self.asr and self.asr.is_ready():
                    await self._process_audio_buffer(
                        session_id,
                        buffer,
                        is_final=chunk.is_final
                    )
                    # Clear buffer after transcription
                    self._audio_buffers[session_id] = b""

        except asyncio.CancelledError:
            logger.debug(f"ASR worker cancelled: {session_id}")
        except Exception as e:
            logger.error(f"ASR worker error: {session_id}: {e}")

    async def _process_audio_buffer(
        self,
        session_id: str,
        audio_data: bytes,
        is_final: bool
    ):
        """Process buffered audio through ASR pipeline"""
        try:
            # Increment segment counter
            self._segment_counters[session_id] = self._segment_counters.get(session_id, 0) + 1
            segment_id = f"seg_{self._segment_counters[session_id]}"

            # Publish processing started event
            await publish(
                EventType.ASR_PROCESSING_STARTED,
                data={"segment_id": segment_id},
                session_id=session_id
            )

            # Acquire lock for GPU serialization
            async with _asr_lock:
                asr_result = await self.asr.transcribe(
                    audio_data,
                    is_final=is_final,
                    segment_id=segment_id
                )

            # Send ASR result to client
            await self._send_asr_result(session_id, asr_result)

            # Publish result ready event
            await publish(
                EventType.ASR_RESULT_READY,
                data={
                    "text": asr_result.text,
                    "is_final": asr_result.is_final,
                    "segment_id": asr_result.segment_id
                },
                session_id=session_id
            )

            # Process through NLU/LLM pipeline only on final result
            if is_final and asr_result.text.strip():
                await self._process_text_input(session_id, asr_result.text)

        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            await publish(
                EventType.ASR_ERROR,
                data={"error": str(e)},
                session_id=session_id
            )
            await self._send_error(session_id, "Audio processing error")

    async def _handle_text_message(self, session_id: str, text: str):
        """Handle text message from client"""
        try:
            msg = json.loads(text)
            msg_type = msg.get("type")
            data = msg.get("data", {})

            logger.debug(f"Received message: type={msg_type}, session={session_id}")

            if msg_type == MessageType.AUDIO_CHUNK:
                import base64
                audio_data = base64.b64decode(data.get("audio", ""))
                seq = data.get("seq", 0)
                is_final = data.get("is_final", False)
                await self._enqueue_audio_chunk(session_id, audio_data, seq, is_final)

            elif msg_type == MessageType.USER_INPUT:
                await self._handle_user_input(session_id, data.get("text", ""))

            elif msg_type == MessageType.USER_CONFIRM:
                await self._handle_user_confirm(session_id, data)

            elif msg_type == MessageType.CANCEL:
                await self._handle_cancel(session_id)

            elif msg_type == MessageType.MCP_RESULT:
                await self._handle_mcp_result(session_id, data)

            else:
                logger.warning(f"Unknown message type: {msg_type}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            await self._send_error(session_id, "Invalid message format")

    async def _handle_binary_message(self, session_id: str, data: bytes):
        """Handle binary message (raw audio stream)"""
        counter = self._chunk_counters.get(session_id, 0) + 1
        self._chunk_counters[session_id] = counter
        await self._enqueue_audio_chunk(session_id, data, counter, False)

    async def _enqueue_audio_chunk(
        self,
        session_id: str,
        audio_data: bytes,
        seq: int,
        is_final: bool
    ):
        """Enqueue audio chunk for ASR processing"""
        queue = self._audio_queues.get(session_id)
        if not queue:
            logger.warning(f"No queue for session: {session_id}")
            return

        chunk = AudioChunk(
            data=audio_data,
            seq=seq,
            is_final=is_final,
            timestamp_ms=int(datetime.now().timestamp() * 1000)
        )

        try:
            queue.put_nowait(chunk)
        except asyncio.QueueFull:
            # Backpressure: drop oldest chunk
            logger.warning(f"Queue full, dropping chunk: {session_id}")
            try:
                queue.get_nowait()
                queue.put_nowait(chunk)
            except asyncio.QueueEmpty:
                pass

    async def _handle_user_input(self, session_id: str, text: str):
        """Handle direct text input (bypass ASR)"""
        # Send as ASR result for UI consistency
        result = ASRResult(
            text=text,
            confidence=1.0,
            language="ko",
            duration=0.0,
            is_final=True,
            segment_id="text_input"
        )
        await self._send_asr_result(session_id, result)
        await self._process_text_input(session_id, text)

    async def _process_text_input(self, session_id: str, text: str):
        """Process text through NLU -> LLM -> TTS pipeline"""
        try:
            session = self.session.get_session(session_id) if self.session else None
            if not session:
                return

            # Add to conversation history
            if self.session:
                self.session.add_to_history(session_id, "user", text)

            # Check if flow is active
            if self.flow and self.flow.is_flow_active(session_id):
                await self._handle_flow_input(session_id, text)
                return

            # Initialize defaults
            intent = None
            resolved_text = text

            # NLU: intent analysis (optional)
            if self.nlu:
                context = session.context
                intent = await self.nlu.analyze_intent(text, context)
                resolved_text = await self.nlu.resolve_reference(text, context)

            # LLM: command generation (works with or without NLU)
            if self.llm:
                response = await self.llm.generate_commands(
                    resolved_text,
                    intent,
                    session
                )

                # Check if flow delegation required
                if response.requires_flow and self.flow:
                    flow_type = response.flow_type
                    site = session.current_site or "coupang"
                    step = await self.flow.start_flow(flow_type, site, session)
                    await self._send_flow_step(session_id, step)
                else:
                    if response.commands:
                        await self._send_tool_calls(session_id, response.commands)

                # TTS response
                if response.text and self.tts:
                    await self._send_tts_response(session_id, response.text)

                # Add to conversation history
                if self.session:
                    self.session.add_to_history(session_id, "assistant", response.text)

        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            await self._send_error(session_id, "Processing error")

    async def _handle_flow_input(self, session_id: str, text: str):
        """Handle input during active flow"""
        session = self.session.get_session(session_id) if self.session else None
        if not session:
            return

        user_input = {"text": text}
        next_step = await self.flow.next_step(session, user_input)
        await self._send_flow_step(session_id, next_step)

        if next_step.prompt and self.tts:
            await self._send_tts_response(session_id, next_step.prompt)

    async def _handle_user_confirm(self, session_id: str, data: Dict[str, Any]):
        """Handle user confirmation response"""
        confirmed = data.get("confirmed", False)
        if confirmed:
            await self._process_text_input(session_id, "yes")
        else:
            await self._process_text_input(session_id, "no")

    async def _handle_cancel(self, session_id: str):
        """Handle cancel request"""
        # Clear audio buffer and queue
        self._audio_buffers[session_id] = b""
        queue = self._audio_queues.get(session_id)
        if queue:
            while not queue.empty():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

        session = self.session.get_session(session_id) if self.session else None
        if session and self.flow:
            await self.flow.cancel_flow(session)

        await self._send_status(session_id, "cancelled", "Cancelled")

        if self.tts:
            await self._send_tts_response(session_id, "Cancelled")

    async def _handle_mcp_result(self, session_id: str, data: Dict[str, Any]):
        """Handle MCP execution result from client"""
        success = data.get("success", False)
        result = data.get("result", {})
        error = data.get("error")

        await publish(
            EventType.MCP_RESULT_RECEIVED,
            data={"success": success, "result": result, "error": error},
            session_id=session_id
        )

        if self.llm:
            session = self.session.get_session(session_id) if self.session else None
            if session:
                if self.session:
                    self.session.set_context(session_id, "mcp_result", result)

                response_text = await self.llm.generate_response(session.context)

                if self.tts:
                    await self._send_tts_response(session_id, response_text)

    # ========================================================================
    # Message sending helpers
    # ========================================================================

    async def _send_status(self, session_id: str, status: str, message: str):
        """Send status message"""
        msg = WSMessage(
            type=MessageType.STATUS,
            data={"status": status, "message": message},
            session_id=session_id
        )
        await connection_manager.send_message(session_id, msg)

    async def _send_error(self, session_id: str, error: str):
        """Send error message"""
        msg = WSMessage(
            type=MessageType.ERROR,
            data={"error": error},
            session_id=session_id
        )
        await connection_manager.send_message(session_id, msg)

    async def _send_asr_result(self, session_id: str, result: ASRResult):
        """Send ASR result to client"""
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
        await connection_manager.send_message(session_id, msg)

    async def _send_tool_calls(self, session_id: str, commands: list):
        """Send MCP tool calls - broadcasts to all clients for pipeline testing"""
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
        await connection_manager.broadcast(msg)

    async def _send_flow_step(self, session_id: str, step):
        """Send flow step"""
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
        """Send TTS response (streaming)"""
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
