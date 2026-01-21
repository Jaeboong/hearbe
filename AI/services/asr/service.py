"""
ASR Service Implementation

Faster-Whisper (turbo) model for speech recognition.
"""

import io
import logging
from typing import AsyncGenerator, Optional

import numpy as np
import soundfile as sf

from core.interfaces import IASRService, ASRResult
from core.config import get_config

logger = logging.getLogger(__name__)


class ASRService(IASRService):
    """
    Faster-Whisper based ASR service.

    Features:
    - GPU accelerated transcription
    - Korean language optimized
    - Batch transcription (streaming support planned)
    """

    def __init__(self):
        self._config = get_config().asr
        self._model = None
        self._ready = False

    async def initialize(self):
        """Load Whisper model."""
        try:
            from faster_whisper import WhisperModel

            logger.info(
                f"Loading ASR model: {self._config.model_name} "
                f"(device={self._config.device}, compute_type={self._config.compute_type})"
            )
            self._model = WhisperModel(
                self._config.model_name,
                device=self._config.device,
                compute_type=self._config.compute_type
            )
            self._ready = True
            logger.info(f"ASR model loaded: {self._config.model_name}")
        except Exception as e:
            logger.error(f"Failed to load ASR model: {e}")
            raise

    def _preprocess_audio(self, audio_data: bytes) -> np.ndarray:
        """
        Convert raw audio bytes to numpy array for Whisper.

        Expects WAV format or raw PCM (16kHz, mono, 16-bit).
        Returns float32 numpy array normalized to [-1, 1].
        """
        try:
            # Try reading as WAV file
            audio_io = io.BytesIO(audio_data)
            audio_array, sample_rate = sf.read(audio_io, dtype="float32")

            # Convert stereo to mono if needed
            if len(audio_array.shape) > 1:
                audio_array = np.mean(audio_array, axis=1)

            # Resample to 16kHz if needed (Whisper requirement)
            if sample_rate != 16000:
                import scipy.signal as signal
                num_samples = int(len(audio_array) * 16000 / sample_rate)
                audio_array = signal.resample(audio_array, num_samples)

            return audio_array.astype(np.float32)

        except Exception:
            # Fallback: assume raw PCM (16-bit, 16kHz, mono)
            logger.debug("WAV parsing failed, treating as raw PCM")
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            return audio_array.astype(np.float32) / 32768.0

    async def transcribe(self, audio_data: bytes, is_final: bool = True, segment_id: str = None) -> ASRResult:
        """
        Transcribe audio to text.

        Args:
            audio_data: Audio bytes (WAV or raw PCM, 16kHz, mono)
            is_final: Whether this is the final transcription for the segment
            segment_id: Optional segment identifier for tracking

        Returns:
            ASRResult: Transcription result
        """
        if not self._ready:
            raise RuntimeError("ASR model not initialized")

        try:
            audio_array = self._preprocess_audio(audio_data)
            duration = len(audio_array) / 16000.0

            segments, info = self._model.transcribe(
                audio_array,
                language=self._config.language,
                beam_size=self._config.beam_size,
                word_timestamps=False
            )

            # Collect all segment texts
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text.strip())

            text = " ".join(text_parts)
            confidence = info.language_probability if hasattr(info, "language_probability") else 1.0

            logger.debug(f"Transcribed ({duration:.2f}s): {text[:80]}...")
            return ASRResult(
                text=text,
                confidence=confidence,
                language=self._config.language,
                duration=duration,
                is_final=is_final,
                segment_id=segment_id
            )
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

    async def transcribe_stream(
        self,
        audio_chunks: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[ASRResult, None]:
        """
        Stream audio chunks and yield transcription results.

        Accumulates chunks and transcribes when buffer reaches threshold.
        Future: integrate VAD for utterance boundary detection.

        Args:
            audio_chunks: Async generator of audio bytes

        Yields:
            ASRResult: Intermediate/final transcription results
        """
        if not self._ready:
            raise RuntimeError("ASR model not initialized")

        # Threshold: 1 second of audio (16kHz, 16-bit = 32000 bytes)
        CHUNK_THRESHOLD = 32000

        buffer = b""
        segment_counter = 0
        async for chunk in audio_chunks:
            buffer += chunk

            if len(buffer) >= CHUNK_THRESHOLD:
                segment_counter += 1
                result = await self.transcribe(
                    buffer,
                    is_final=False,
                    segment_id=f"seg_{segment_counter}"
                )
                yield result
                buffer = b""

        # Process remaining buffer as final
        if buffer:
            segment_counter += 1
            result = await self.transcribe(
                buffer,
                is_final=True,
                segment_id=f"seg_{segment_counter}"
            )
            yield result

    def is_ready(self) -> bool:
        """모델 로드 완료 여부"""
        return self._ready

    async def shutdown(self):
        """리소스 정리"""
        self._model = None
        self._ready = False
        logger.info("ASR service shutdown")
