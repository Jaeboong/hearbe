"""
Chrome 브라우저 실행 모듈

CDP(Chrome DevTools Protocol) 모드로 Chrome 자동 실행
"""

import asyncio
import logging
import subprocess
import sys
from pathlib import Path
from typing import Optional
import aiohttp

from core.config import get_config
from core.event_bus import EventType, publish

logger = logging.getLogger(__name__)


class ChromeLauncher:
    """
    Chrome 브라우저 실행 관리자

    CDP 모드로 Chrome을 실행하고 WebSocket URL을 획득
    """

    # Windows Chrome 기본 설치 경로
    CHROME_PATHS = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "Application" / "chrome.exe",
    ]

    def __init__(self):
        self._config = get_config().browser
        self._process: Optional[subprocess.Popen] = None
        self._cdp_url: Optional[str] = None

    @property
    def is_running(self) -> bool:
        """브라우저 실행 중인지 확인"""
        return self._process is not None and self._process.poll() is None

    @property
    def cdp_url(self) -> Optional[str]:
        """CDP WebSocket URL"""
        return self._cdp_url

    @property
    def process_id(self) -> Optional[int]:
        """브라우저 프로세스 ID"""
        return self._process.pid if self._process else None

    def _find_chrome_path(self) -> Optional[str]:
        """Chrome 실행 파일 경로 탐색"""
        # 환경 변수로 지정된 경로 우선
        if self._config.chrome_path:
            path = Path(self._config.chrome_path)
            if path.exists():
                return str(path)
            logger.warning(f"Configured Chrome path not found: {self._config.chrome_path}")

        # 기본 경로 탐색
        for path in self.CHROME_PATHS:
            path = Path(path)
            if path.exists():
                logger.info(f"Found Chrome at: {path}")
                return str(path)

        return None

    def _build_chrome_args(self, chrome_path: str) -> list:
        """Chrome 실행 인자 생성"""
        args = [
            chrome_path,
            f"--remote-debugging-port={self._config.debugging_port}",
            f"--user-data-dir={self._config.user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            f"--window-size={self._config.window_width},{self._config.window_height}",
        ]

        if self._config.headless:
            args.append("--headless=new")

        return args

    async def start(self) -> bool:
        """
        Chrome 브라우저 시작

        Returns:
            bool: 시작 성공 여부
        """
        if self.is_running:
            logger.warning("Chrome is already running")
            return False

        # Chrome 경로 탐색
        chrome_path = self._find_chrome_path()
        if not chrome_path:
            logger.error("Chrome executable not found")
            await publish(
                EventType.BROWSER_ERROR,
                data={"error": "Chrome executable not found"},
                source="browser.launcher"
            )
            return False

        # 사용자 프로필 디렉토리 생성
        user_data_dir = Path(self._config.user_data_dir)
        user_data_dir.mkdir(parents=True, exist_ok=True)

        # Chrome 실행
        args = self._build_chrome_args(chrome_path)
        logger.info(f"Starting Chrome with args: {' '.join(args)}")

        try:
            self._process = subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            logger.info(f"Chrome started with PID: {self._process.pid}")

        except Exception as e:
            logger.error(f"Failed to start Chrome: {e}")
            await publish(
                EventType.BROWSER_ERROR,
                data={"error": str(e)},
                source="browser.launcher"
            )
            return False

        # CDP 연결 대기
        cdp_url = await self._wait_for_cdp()
        if not cdp_url:
            logger.error("Failed to get CDP URL")
            await self.stop()
            return False

        self._cdp_url = cdp_url

        # 브라우저 준비 완료 이벤트
        await publish(
            EventType.BROWSER_READY,
            data={
                "cdp_url": self._cdp_url,
                "process_id": self._process.pid
            },
            source="browser.launcher"
        )

        logger.info(f"Chrome ready - CDP URL: {self._cdp_url}")
        return True

    async def _wait_for_cdp(self, timeout: int = 10) -> Optional[str]:
        """
        CDP 연결 대기

        Args:
            timeout: 대기 시간 (초)

        Returns:
            CDP WebSocket URL 또는 None
        """
        cdp_http_url = f"http://127.0.0.1:{self._config.debugging_port}/json/version"

        for _ in range(timeout * 2):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(cdp_http_url, timeout=aiohttp.ClientTimeout(total=1)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data.get("webSocketDebuggerUrl")
            except Exception:
                pass

            await asyncio.sleep(0.5)

        return None

    async def stop(self):
        """Chrome 브라우저 종료"""
        if not self._process:
            return

        logger.info("Stopping Chrome...")

        try:
            self._process.terminate()
            self._process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("Chrome did not terminate gracefully, killing...")
            self._process.kill()
        except Exception as e:
            logger.error(f"Error stopping Chrome: {e}")

        self._process = None
        self._cdp_url = None
        logger.info("Chrome stopped")
