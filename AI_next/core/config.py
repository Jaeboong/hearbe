"""
설정 관리 모듈

환경 변수 및 설정 파일 로드
(LLM/NLU/Flow 제거 — AI_next 경량 버전)
"""

import os
import sys
import logging
import logging.handlers
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass
class ASRConfig:
    """ASR (음성 인식) 설정"""
    provider: str = "whisper"
    device: str = "cuda"
    language: str = "ko"
    model_name: str = "large-v3-turbo"
    compute_type: str = "float16"
    beam_size: int = 5
    qwen3_model_name: str = "Qwen/Qwen3-ASR-0.6B"
    qwen3_max_batch_size: int = 32
    qwen3_max_new_tokens: int = 256


@dataclass
class TTSConfig:
    """TTS (음성 합성) 설정 - Google Cloud TTS"""
    sample_rate: int = 24000
    streaming: bool = True
    speaking_rate: float = 1.0
    google_credentials_path: Optional[str] = None
    google_voice_name: str = "ko-KR-Chirp3-HD-Leda"


@dataclass
class OCRConfig:
    """OCR (이미지 인식) 설정"""
    provider: str = "openai"
    api_key: Optional[str] = None
    language: str = "kor+eng"
    device: str = "cpu"
    http_timeout_seconds: int = 45
    http_max_upload_mb: int = 20


@dataclass
class ServerConfig:
    """서버 설정"""
    host: str = "0.0.0.0"
    port: int = 8000
    ws_path: str = "/ws"
    cors_origins: str = "*"
    debug: bool = False
    public_base_url: Optional[str] = None
    public_ws_url: Optional[str] = None


@dataclass
class LogConfig:
    """로깅 설정"""
    level: str = "INFO"
    console_level: Optional[str] = None
    file_level: Optional[str] = None
    log_dir: str = "logs"
    log_file: str = "ai_server.log"
    rotate_when: str = "midnight"
    rotate_interval: int = 1
    backup_count: int = 5
    rotate_utc: bool = False


@dataclass
class AppConfig:
    """전체 애플리케이션 설정"""
    asr: ASRConfig
    tts: TTSConfig
    ocr: OCRConfig
    server: ServerConfig
    log: LogConfig


class ConfigManager:
    """설정 관리자 (Singleton)"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._load_env()
        self.config = self._create_config()
        self._initialized = True
        logger.info("ConfigManager initialized")

    def _load_env(self):
        current_dir = Path(__file__).parent.parent
        env_path = current_dir / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"Loaded .env file from {env_path}")
        else:
            logger.warning(f".env file not found at {env_path}")

    def _get_env(self, key: str, default: str = "") -> str:
        return os.getenv(key, default)

    def _get_env_int(self, key: str, default: int) -> int:
        try:
            return int(self._get_env(key, str(default)))
        except ValueError:
            return default

    def _get_env_float(self, key: str, default: float) -> float:
        try:
            return float(self._get_env(key, str(default)))
        except ValueError:
            return default

    def _get_env_bool(self, key: str, default: bool) -> bool:
        value = self._get_env(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")

    def _get_env_profile(self, key: str, default: str = "") -> str:
        app_env = self._get_env("APP_ENV", "dev").strip().lower()
        profile_key = f"{app_env.upper()}_{key}"
        if os.getenv(key) is not None:
            return os.getenv(key)
        if os.getenv(profile_key) is not None:
            return os.getenv(profile_key)
        return default

    def _get_env_profile_bool(self, key: str, default: bool) -> bool:
        value = self._get_env_profile(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")

    def _get_env_profile_int(self, key: str, default: int) -> int:
        try:
            return int(self._get_env_profile(key, str(default)))
        except ValueError:
            return default

    def _create_config(self) -> AppConfig:
        asr = ASRConfig(
            provider=self._get_env("ASR_PROVIDER", "whisper"),
            device=self._get_env("ASR_DEVICE", "cuda"),
            language=self._get_env("ASR_LANGUAGE", "ko"),
            model_name=self._get_env("ASR_MODEL_NAME", "large-v3-turbo"),
            compute_type=self._get_env("ASR_COMPUTE_TYPE", "float16"),
            beam_size=self._get_env_int("ASR_BEAM_SIZE", 5),
            qwen3_model_name=self._get_env("ASR_QWEN3_MODEL_NAME", "Qwen/Qwen3-ASR-0.6B"),
            qwen3_max_batch_size=self._get_env_int("ASR_QWEN3_MAX_BATCH_SIZE", 32),
            qwen3_max_new_tokens=self._get_env_int("ASR_QWEN3_MAX_NEW_TOKENS", 256),
        )

        tts = TTSConfig(
            sample_rate=self._get_env_int("TTS_SAMPLE_RATE", 24000),
            streaming=self._get_env_bool("TTS_STREAMING", True),
            speaking_rate=self._get_env_float("TTS_SPEAKING_RATE", 1.0),
            google_credentials_path=self._get_env("GOOGLE_APPLICATION_CREDENTIALS") or None,
            google_voice_name=self._get_env("TTS_GOOGLE_VOICE", "ko-KR-Chirp3-HD-Leda"),
        )

        ocr = OCRConfig(
            provider=self._get_env("OCR_PROVIDER", "openai"),
            api_key=self._get_env("OCR_API_KEY") or self._get_env("OPENAI_API_KEY") or None,
            language=self._get_env("OCR_LANGUAGE", "kor+eng"),
            device=self._get_env("OCR_DEVICE", "cpu"),
            http_timeout_seconds=self._get_env_int("OCR_HTTP_TIMEOUT_SECONDS", 45),
            http_max_upload_mb=max(15, self._get_env_int("OCR_HTTP_MAX_UPLOAD_MB", 20)),
        )

        server = ServerConfig(
            host=self._get_env("SERVER_HOST", "0.0.0.0"),
            port=self._get_env_int("SERVER_PORT", 8000),
            ws_path=self._get_env("WS_PATH", "/ws"),
            cors_origins=self._get_env("CORS_ORIGINS", "*"),
            debug=self._get_env_profile_bool("DEBUG", False),
            public_base_url=self._get_env("PUBLIC_BASE_URL") or None,
            public_ws_url=self._get_env("PUBLIC_WS_URL") or None,
        )

        log = LogConfig(
            level=self._get_env_profile("LOG_LEVEL", "INFO"),
            console_level=self._get_env_profile("LOG_CONSOLE_LEVEL") or None,
            file_level=self._get_env_profile("LOG_FILE_LEVEL") or None,
            log_dir=self._get_env_profile("LOG_DIR", "logs"),
            log_file=self._get_env_profile("LOG_FILE", "ai_server.log"),
            rotate_when=self._get_env_profile("LOG_ROTATE_WHEN", "midnight"),
            rotate_interval=self._get_env_profile_int("LOG_ROTATE_INTERVAL", 1),
            backup_count=self._get_env_profile_int("LOG_BACKUP_COUNT", 5),
            rotate_utc=self._get_env_profile_bool("LOG_ROTATE_UTC", False),
        )

        return AppConfig(asr=asr, tts=tts, ocr=ocr, server=server, log=log)

    def get(self) -> AppConfig:
        return self.config

    def reload(self):
        logger.info("Reloading configuration...")
        self._load_env()
        self.config = self._create_config()
        logger.info("Configuration reloaded")


config_manager = ConfigManager()


def get_config() -> AppConfig:
    return config_manager.get()


def setup_logging(config: AppConfig):
    log_dir = Path(config.log.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / config.log.log_file

    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    console_level = level_map.get(
        (config.log.console_level or config.log.level).upper(), logging.INFO
    )
    file_level = level_map.get(
        (config.log.file_level or config.log.level).upper(), logging.INFO
    )
    root_level = min(console_level, file_level)

    root_logger = logging.getLogger()
    root_logger.setLevel(root_level)
    root_logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    if config.log.rotate_utc:
        formatter.converter = time.gmtime

    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file,
        when=config.log.rotate_when,
        interval=config.log.rotate_interval,
        backupCount=config.log.backup_count,
        utc=config.log.rotate_utc,
        encoding="utf-8",
    )
    file_handler.suffix = "%Y-%m-%d.log"
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logger.info(
        "Logging configured: level=%s console=%s file=%s",
        config.log.level,
        config.log.console_level or config.log.level,
        config.log.file_level or config.log.level,
    )
