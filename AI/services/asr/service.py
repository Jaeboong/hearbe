"""
ASR 서비스 구현

Faster-Whisper(turbo) 모델을 사용한 음성 인식
"""

import logging
from typing import AsyncGenerator, Optional
from core.interfaces import IASRService, STTResult
from core.config import get_config

logger = logging.getLogger(__name__)


class ASRService(IASRService):
    """
    Faster-Whisper 기반 ASR 서비스

    Features:
    - GPU 가속 기반 빠른 인식
    - 한국어 최적화
    - 실시간 스트리밍 지원
    """

    def __init__(self):
        self._config = get_config().asr
        self._model = None
        self._ready = False

    async def initialize(self):
        """모델 초기화"""
        try:
            # TODO: Faster-Whisper 모델 로드
            # from faster_whisper import WhisperModel
            # self._model = WhisperModel(
            #     self._config.model_name,
            #     device=self._config.device,
            #     compute_type=self._config.compute_type
            # )
            self._ready = True
            logger.info(f"ASR model loaded: {self._config.model_name}")
        except Exception as e:
            logger.error(f"Failed to load ASR model: {e}")
            raise

    async def transcribe(self, audio_data: bytes) -> STTResult:
        """
        음성을 텍스트로 변환

        Args:
            audio_data: 오디오 데이터 (WAV/PCM, 16kHz, 모노)

        Returns:
            STTResult: 변환된 텍스트 결과
        """
        if not self._ready:
            raise RuntimeError("ASR model not initialized")

        try:
            # TODO: 실제 구현
            # segments, info = self._model.transcribe(
            #     audio_data,
            #     language=self._config.language,
            #     beam_size=self._config.beam_size
            # )
            # text = " ".join([segment.text for segment in segments])

            text = ""  # placeholder
            confidence = 1.0
            duration = 0.0

            logger.debug(f"Transcribed: {text[:50]}...")
            return STTResult(
                text=text,
                confidence=confidence,
                language=self._config.language,
                duration=duration
            )
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

    async def transcribe_stream(
        self,
        audio_chunks: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[STTResult, None]:
        """
        스트리밍 음성을 실시간으로 텍스트 변환

        Args:
            audio_chunks: 오디오 청크 스트림

        Yields:
            STTResult: 중간/최종 변환 결과
        """
        if not self._ready:
            raise RuntimeError("ASR model not initialized")

        # TODO: 실시간 스트리밍 구현
        # 청크를 누적하면서 VAD로 발화 구간 감지
        # 발화 종료 시점에 transcribe 호출

        buffer = b""
        async for chunk in audio_chunks:
            buffer += chunk

            # 일정 크기마다 중간 결과 생성 (예: 0.5초 분량)
            if len(buffer) >= 16000:  # 1초 분량 (16kHz, 16bit)
                result = await self.transcribe(buffer)
                yield result
                buffer = b""

        # 남은 버퍼 처리
        if buffer:
            result = await self.transcribe(buffer)
            yield result

    def is_ready(self) -> bool:
        """모델 로드 완료 여부"""
        return self._ready

    async def shutdown(self):
        """리소스 정리"""
        self._model = None
        self._ready = False
        logger.info("ASR service shutdown")
