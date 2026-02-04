"""
Audio Player - TTS audio playback

Receives TTS_AUDIO_RECEIVED events and plays PCM audio.
Publishes TTS_PLAYBACK_FINISHED when playback completes.
"""

import logging
import threading
import queue
import time
from typing import Optional

try:
    import pyaudio
except ImportError:
    pyaudio = None

from core.event_bus import subscribe, publish_sync, EventType
from core.interfaces import IAudioPlayer

logger = logging.getLogger(__name__)

# Audio settings (must match AI server TTS output)
TTS_SAMPLE_RATE = 24000  # Google TTS Chirp default
TTS_CHANNELS = 1
TTS_FORMAT = pyaudio.paInt16 if pyaudio else None
TTS_CHUNK_SIZE = 4096
_STOP_SENTINEL = object()
_FLUSH_SENTINEL = object()
_BARGE_IN_SUPPRESS_SEC = 3.0


class AudioPlayer(IAudioPlayer):
    """
    TTS Audio Player

    Subscribes to TTS_AUDIO_RECEIVED events and plays audio chunks.
    Uses a queue-based approach for streaming playback.

    Events:
        - Subscribes: TTS_AUDIO_RECEIVED
        - Publishes: TTS_PLAYBACK_FINISHED
    """

    def __init__(
        self,
        sample_rate: int = TTS_SAMPLE_RATE,
        output_device_index: Optional[int] = None
    ):
        if pyaudio is None:
            raise ImportError("pyaudio not installed. Run: pip install pyaudio")

        self.sample_rate = sample_rate
        self.audio: Optional[pyaudio.PyAudio] = None
        self.stream = None
        self._playing = False
        self._stop_requested = False
        self._suppress_until = 0.0
        self.output_device_index = output_device_index

        # Audio queue for streaming playback
        self._audio_queue: queue.Queue = queue.Queue()
        self._playback_thread: Optional[threading.Thread] = None

        logger.info(
            "AudioPlayer initialized: "
            f"sample_rate={sample_rate}, "
            f"output_device_index={output_device_index}"
        )

    def start(self):
        """Start player and register event handlers"""
        self._init_audio()
        self._register_handlers()
        self._start_playback_thread()
        logger.info("AudioPlayer started")

    def _init_audio(self):
        """Initialize PyAudio"""
        if self.audio is not None:
            return

        self.audio = pyaudio.PyAudio()

        # Log default output device (no selection logic here)
        try:
            default_output = self.audio.get_default_output_device_info()
            logger.info(
                f"Default output device: {default_output.get('name', 'unknown')}"
            )
        except Exception as e:
            logger.warning(f"Could not get default output device: {e}")

    def _register_handlers(self):
        """Register event handlers"""
        subscribe(EventType.TTS_AUDIO_RECEIVED, self._on_tts_audio_received)
        subscribe(EventType.HOTKEY_PRESSED, self._on_hotkey_pressed)
        logger.info("AudioPlayer event handlers registered")

    def _start_playback_thread(self):
        """Start background playback thread"""
        if self._playback_thread is not None and self._playback_thread.is_alive():
            return

        self._stop_requested = False
        self._playback_thread = threading.Thread(
            target=self._playback_loop,
            daemon=True,
            name="AudioPlayer-Playback"
        )
        self._playback_thread.start()
        logger.debug("Playback thread started")

    def _playback_loop(self):
        """Background thread for audio playback"""
        while not self._stop_requested:
            try:
                # Wait for audio data with timeout
                item = self._audio_queue.get(timeout=0.5)

                if item is _STOP_SENTINEL:
                    self._on_playback_finished()
                    break
                if item is _FLUSH_SENTINEL:
                    self._on_playback_finished()
                    continue

                audio_data, is_final = item
                self._play_chunk(audio_data)

                if is_final:
                    self._on_playback_finished()

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Playback error: {e}")

        logger.debug("Playback thread stopped")

    def _play_chunk(self, audio_data: bytes):
        """Play a single audio chunk"""
        if not audio_data:
            return

        try:
            self._playing = True

            # Open stream if not already open
            if self.stream is None or not self.stream.is_active():
                stream_kwargs = {
                    "format": TTS_FORMAT,
                    "channels": TTS_CHANNELS,
                    "rate": self.sample_rate,
                    "output": True,
                    "frames_per_buffer": TTS_CHUNK_SIZE
                }
                if self.output_device_index is not None:
                    stream_kwargs["output_device_index"] = self.output_device_index

                self.stream = self.audio.open(
                    **stream_kwargs
                )

            # Write audio data to stream
            self.stream.write(audio_data)

        except Exception as e:
            logger.error(f"Failed to play audio chunk: {e}")
        finally:
            self._playing = False

    def _on_tts_audio_received(self, event):
        """Handle TTS_AUDIO_RECEIVED event"""
        data = event.data
        if not data:
            return

        if time.time() < self._suppress_until:
            return

        audio_bytes = data.get("audio")
        is_final = data.get("is_final", False)

        if audio_bytes:
            self._audio_queue.put((audio_bytes, is_final))
            logger.debug(f"TTS chunk queued: {len(audio_bytes)} bytes, final={is_final}")

    def _on_playback_finished(self):
        """Called when playback of a TTS response completes"""
        # Close the stream to flush any remaining audio
        if self.stream is not None:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

        # Publish completion event
        publish_sync(
            EventType.TTS_PLAYBACK_FINISHED,
            data={},
            source="audio.player"
        )
        logger.info("TTS playback finished")

    def _on_hotkey_pressed(self, event):
        """Stop TTS playback on barge-in hotkey"""
        if self.is_playing():
            logger.info("Hotkey pressed - stopping TTS playback")
            self._suppress_until = time.time() + _BARGE_IN_SUPPRESS_SEC
            self._request_stop_playback()

    def play(self, audio_data: bytes) -> None:
        """
        Play audio data directly (IAudioPlayer interface)

        Args:
            audio_data: PCM audio data to play
        """
        self._audio_queue.put((audio_data, True))

    def stop(self) -> None:
        """Stop current playback"""
        # Clear the queue
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except queue.Empty:
                break

        # Let playback thread close the stream and publish finished.
        self._audio_queue.put(_FLUSH_SENTINEL)
        self._playing = False
        logger.info("Playback stopped")

    def _request_stop_playback(self) -> None:
        """Request playback stop via playback thread to avoid concurrent stream close."""
        # Clear the queue
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except queue.Empty:
                break
        # Let the playback thread close the stream and publish finished.
        self._audio_queue.put(_FLUSH_SENTINEL)

    def is_playing(self) -> bool:
        """Check if currently playing"""
        return self._playing or not self._audio_queue.empty()

    def shutdown(self):
        """Clean up resources"""
        logger.info("Stopping AudioPlayer...")

        self._stop_requested = True
        self._audio_queue.put(_STOP_SENTINEL)  # Sentinel to stop thread

        if self._playback_thread is not None:
            self._playback_thread.join(timeout=2.0)

        self.stop()

        if self.audio is not None:
            self.audio.terminate()
            self.audio = None

        logger.info("AudioPlayer stopped")
