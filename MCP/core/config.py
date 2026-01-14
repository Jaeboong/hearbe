"""
설정 관리 모듈

환경 변수 및 설정 파일 로드
"""

import os
import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass
class AudioConfig:
    """오디오 설정"""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    hotkey: str = "v"


@dataclass
class BrowserConfig:
    """브라우저 설정"""
    chrome_path: Optional[str] = None
    user_data_dir: Optional[str] = None
    debugging_port: int = 9222
    headless: bool = False
    window_width: int = 1280
    window_height: int = 720


@dataclass
class MCPConfig:
    """MCP 서버 설정"""
    server_script: str = "mcp/playwright_mcp_server.py"
    python_path: Optional[str] = None
    timeout: int = 30


@dataclass
class NetworkConfig:
    """네트워크 설정"""
    ws_url: str = "ws://localhost:8000/ws"
    auth_url: str = "http://localhost:8000/auth"
    reconnect_interval: int = 5
    max_reconnect_attempts: int = 10


@dataclass
class LogConfig:
    """로깅 설정"""
    level: str = "INFO"
    log_dir: str = "logs"
    log_file: str = "app.log"
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class AppConfig:
    """전체 애플리케이션 설정"""
    audio: AudioConfig
    browser: BrowserConfig
    mcp: MCPConfig
    network: NetworkConfig
    log: LogConfig
    session_file: str = "session.json"


class ConfigManager:
    """
    설정 관리자 (Singleton)

    환경 변수와 기본값을 결합하여 애플리케이션 설정 관리
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # .env 파일 로드
        self._load_env()

        # 설정 초기화
        self.config = self._create_config()

        self._initialized = True
        logger.info("ConfigManager initialized")

    def _load_env(self):
        """환경 변수 로드"""
        # 현재 파일의 부모 디렉토리(MCP/)에서 .env 파일 찾기
        current_dir = Path(__file__).parent.parent
        env_path = current_dir / ".env"

        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"Loaded .env file from {env_path}")
        else:
            logger.warning(f".env file not found at {env_path}")

    def _get_env(self, key: str, default: str = "") -> str:
        """환경 변수 가져오기"""
        return os.getenv(key, default)

    def _get_env_int(self, key: str, default: int) -> int:
        """환경 변수를 정수로 가져오기"""
        try:
            return int(self._get_env(key, str(default)))
        except ValueError:
            logger.warning(f"Invalid integer value for {key}, using default: {default}")
            return default

    def _get_env_bool(self, key: str, default: bool) -> bool:
        """환경 변수를 boolean으로 가져오기"""
        value = self._get_env(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")

    def _create_config(self) -> AppConfig:
        """환경 변수를 기반으로 설정 생성"""
        # Audio 설정
        audio = AudioConfig(
            sample_rate=self._get_env_int("AUDIO_SAMPLE_RATE", 16000),
            channels=self._get_env_int("AUDIO_CHANNELS", 1),
            chunk_size=self._get_env_int("AUDIO_CHUNK_SIZE", 1024),
            hotkey=self._get_env("AUDIO_HOTKEY", "v")
        )

        # Browser 설정
        browser = BrowserConfig(
            chrome_path=self._get_env("CHROME_PATH") or None,
            user_data_dir=self._get_env("CHROME_USER_DATA_DIR") or None,
            debugging_port=self._get_env_int("CHROME_DEBUG_PORT", 9222),
            headless=self._get_env_bool("CHROME_HEADLESS", False),
            window_width=self._get_env_int("CHROME_WINDOW_WIDTH", 1280),
            window_height=self._get_env_int("CHROME_WINDOW_HEIGHT", 720)
        )

        # MCP 설정
        mcp = MCPConfig(
            server_script=self._get_env("MCP_SERVER_SCRIPT", "mcp/playwright_mcp_server.py"),
            python_path=self._get_env("PYTHON_PATH") or None,
            timeout=self._get_env_int("MCP_TIMEOUT", 30)
        )

        # Network 설정
        network = NetworkConfig(
            ws_url=self._get_env("WS_URL", "ws://localhost:8000/ws"),
            auth_url=self._get_env("AUTH_URL", "http://localhost:8000/auth"),
            reconnect_interval=self._get_env_int("RECONNECT_INTERVAL", 5),
            max_reconnect_attempts=self._get_env_int("MAX_RECONNECT_ATTEMPTS", 10)
        )

        # Log 설정
        log = LogConfig(
            level=self._get_env("LOG_LEVEL", "INFO"),
            log_dir=self._get_env("LOG_DIR", "logs"),
            log_file=self._get_env("LOG_FILE", "app.log"),
            max_bytes=self._get_env_int("LOG_MAX_BYTES", 10 * 1024 * 1024),
            backup_count=self._get_env_int("LOG_BACKUP_COUNT", 5)
        )

        # 전체 설정
        return AppConfig(
            audio=audio,
            browser=browser,
            mcp=mcp,
            network=network,
            log=log,
            session_file=self._get_env("SESSION_FILE", "session.json")
        )

    def get(self) -> AppConfig:
        """현재 설정 반환"""
        return self.config

    def reload(self):
        """설정 다시 로드"""
        logger.info("Reloading configuration...")
        self._load_env()
        self.config = self._create_config()
        logger.info("Configuration reloaded")


# 싱글톤 인스턴스
config_manager = ConfigManager()


def get_config() -> AppConfig:
    """전역 설정 가져오기"""
    return config_manager.get()


def setup_logging(config: AppConfig):
    """로깅 설정"""
    # 로그 디렉토리 생성
    log_dir = Path(config.log.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # 로그 파일 경로
    log_file = log_dir / config.log.log_file

    # 로그 레벨 매핑
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    log_level = level_map.get(config.log.level.upper(), logging.INFO)

    # 로깅 설정
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            # 파일 핸들러 (rotating)
            logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=config.log.max_bytes,
                backupCount=config.log.backup_count,
                encoding="utf-8"
            ),
            # 콘솔 핸들러
            logging.StreamHandler()
        ]
    )

    logger.info(f"Logging configured: level={config.log.level}, file={log_file}")
