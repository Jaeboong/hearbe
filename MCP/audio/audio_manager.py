"""
Audio Manager - PTT (Push-to-Talk) 녹음 관리

스페이스바를 누르고 있는 동안 녹음하고, 
3초마다 서버로 audio_chunk를 전송합니다.
"""

import asyncio
import base64
import logging
import threading
import time
from typing import Optional, Callable

try:
    import pyaudio
except ImportError:
    pyaudio = None

try:
    import keyboard
except ImportError:
    keyboard = None

from core.event_bus import subscribe, publish_sync, EventType

logger = logging.getLogger(__name__)

# Audio settings (AI 서버와 동일하게 설정)
SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16 if pyaudio else None
CHUNK_SIZE = 1024
CHUNK_DURATION_SEC = 3.0  # 3초마다 전송
MIN_RECORDING_SEC = 0.5   # 최소 녹음 시간


class AudioManager:
    """
    PTT (Push-to-Talk) 오디오 녹음 관리자
    
    스페이스바를 누르고 있는 동안 녹음하고,
    3초마다 자동으로 audio_chunk를 전송합니다.
    
    Events:
        - RECORDING_STARTED: 녹음 시작 시 발행
        - RECORDING_STOPPED: 녹음 종료 시 발행
        - AUDIO_READY: audio_chunk 데이터 준비 시 발행
    """
    
    def __init__(self, hotkey: str = "space"):
        if pyaudio is None:
            raise ImportError("pyaudio not installed. Run: pip install pyaudio")
        if keyboard is None:
            raise ImportError("keyboard not installed. Run: pip install keyboard")
        
        self.hotkey = hotkey
        self.audio: Optional[pyaudio.PyAudio] = None
        self.stream = None
        self.running = False
        self.recording = False
        
        self.audio_buffer = b""
        self.seq = 0
        self.lock = threading.Lock()
        self.record_start_time = 0
        
        self._hotkey_pressed = False
        self._audio_thread: Optional[threading.Thread] = None
        
        logger.info(f"AudioManager initialized with hotkey: {hotkey}")
    
    def _init_audio(self):
        """PyAudio 초기화"""
        if self.audio is not None:
            return
            
        self.audio = pyaudio.PyAudio()
        
        # 입력 장치 목록 출력
        info = self.audio.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        
        logger.info("Available input devices:")
        for i in range(num_devices):
            device_info = self.audio.get_device_info_by_host_api_device_index(0, i)
            if device_info.get('maxInputChannels') > 0:
                logger.info(f"  [{i}] {device_info.get('name')}")
    
    def _start_recording(self):
        """녹음 시작"""
        if self.recording:
            return
        
        with self.lock:
            self.recording = True
            self.audio_buffer = b""
            self.record_start_time = time.time()
        
        try:
            self.stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE
            )
            logger.info("Recording started")
            publish_sync(EventType.RECORDING_STARTED, source="audio")
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.recording = False
    
    def _stop_recording(self) -> Optional[bytes]:
        """녹음 종료 및 버퍼 반환"""
        if not self.recording:
            return None
        
        with self.lock:
            self.recording = False
            buffer = self.audio_buffer
            self.audio_buffer = b""
        
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                logger.warning(f"Error closing stream: {e}")
            self.stream = None
        
        duration = len(buffer) / (SAMPLE_RATE * 2)  # 2 bytes per sample
        logger.info(f"Recording stopped ({duration:.2f}s)")
        publish_sync(EventType.RECORDING_STOPPED, source="audio")
        
        return buffer
    
    def _read_audio_chunk(self) -> Optional[tuple]:
        """오디오 청크 읽기 (3초마다 반환)"""
        if not self.recording or not self.stream:
            return None
        
        try:
            data = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
            with self.lock:
                self.audio_buffer += data
            
            # 3초 경과 확인
            elapsed = time.time() - self.record_start_time
            if elapsed >= CHUNK_DURATION_SEC:
                with self.lock:
                    buffer = self.audio_buffer
                    self.audio_buffer = b""
                    self.record_start_time = time.time()
                return ("chunk", buffer)
            
            return None
        except Exception as e:
            logger.error(f"Audio read error: {e}")
            return None
    
    def _send_audio_chunk(self, audio_data: bytes, is_final: bool):
        """오디오 청크를 이벤트로 발행"""
        duration = len(audio_data) / (SAMPLE_RATE * 2) if audio_data else 0
        
        # 너무 짧은 녹음은 스킵 (Whisper 환각 방지)
        if is_final and duration < MIN_RECORDING_SEC:
            logger.info(f"Audio too short ({duration:.2f}s), sending final signal only")
            # 빈 final 시그널은 보내지 않음
            return
        
        self.seq += 1
        
        # base64 인코딩
        audio_b64 = base64.b64encode(audio_data).decode("ascii") if audio_data else ""
        
        data = {
            "audio": audio_b64,
            "seq": self.seq,
            "is_final": is_final
        }
        
        status = "FINAL" if is_final else "PARTIAL"
        logger.info(f"Sending {status} chunk #{self.seq} ({duration:.2f}s, {len(audio_data)} bytes)")
        
        publish_sync(EventType.AUDIO_READY, data=data, source="audio")
    
    def _audio_loop(self):
        """오디오 처리 메인 루프 (별도 스레드)"""
        logger.info("Audio loop started")
        
        def on_hotkey_press(e):
            if not self._hotkey_pressed:
                self._hotkey_pressed = True
                self._start_recording()
        
        def on_hotkey_release(e):
            self._hotkey_pressed = False
        
        # 핫키 등록
        keyboard.on_press_key(self.hotkey, on_hotkey_press)
        keyboard.on_release_key(self.hotkey, on_hotkey_release)
        
        logger.info(f"Hotkey registered: {self.hotkey.upper()} to record")
        
        try:
            while self.running:
                if self.recording:
                    result = self._read_audio_chunk()
                    if result and result[0] == "chunk":
                        # 3초 경과, 중간 청크 전송
                        self._send_audio_chunk(result[1], is_final=False)
                
                # 핫키 릴리즈 확인
                if not self._hotkey_pressed and self.recording:
                    buffer = self._stop_recording()
                    if buffer:
                        self._send_audio_chunk(buffer, is_final=True)
                
                time.sleep(0.01)
        except Exception as e:
            logger.error(f"Audio loop error: {e}", exc_info=True)
        finally:
            keyboard.unhook_all()
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            logger.info("Audio loop stopped")
    
    async def start(self):
        """AudioManager 시작"""
        if self.running:
            logger.warning("AudioManager already running")
            return
        
        self._init_audio()
        self.running = True
        
        # 오디오 루프를 별도 스레드에서 실행
        self._audio_thread = threading.Thread(target=self._audio_loop, daemon=True)
        self._audio_thread.start()
        
        logger.info("AudioManager started")
        logger.info(f"Hold {self.hotkey.upper()} to record, release to send")
    
    async def stop(self):
        """AudioManager 종료"""
        logger.info("Stopping AudioManager...")
        self.running = False
        
        if self.recording:
            self._stop_recording()
        
        if self._audio_thread and self._audio_thread.is_alive():
            self._audio_thread.join(timeout=2.0)
        
        if self.audio:
            self.audio.terminate()
            self.audio = None
        
        logger.info("AudioManager stopped")
    
    def setup_event_handlers(self):
        """이벤트 핸들러 등록"""
        subscribe(EventType.APP_SHUTDOWN, self._on_shutdown)
        logger.info("AudioManager event handlers registered")
    
    async def _on_shutdown(self, event):
        """종료 이벤트 핸들러"""
        await self.stop()
