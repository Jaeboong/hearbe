"""
MCP 데스크탑 앱 메인 진입점

시각장애인을 위한 음성 기반 웹 쇼핑 지원 애플리케이션
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# 현재 디렉토리를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from core.config import get_config, setup_logging
from core.event_bus import event_bus, EventType, publish

logger = logging.getLogger(__name__)


class Application:
    """메인 애플리케이션 클래스"""

    def __init__(self):
        # 설정 로드
        self.config = get_config()

        # 로깅 설정
        setup_logging(self.config)

        # 모듈 인스턴스 (나중에 각 담당자가 구현)
        self.audio_recorder = None
        self.audio_player = None
        self.hotkey_manager = None
        self.browser_controller = None
        self.mcp_server_manager = None
        self.mcp_client = None
        self.ws_client = None
        self.auth_manager = None
        self.session_manager = None
        self.ui_manager = None

        # 실행 상태
        self.running = False

        logger.info("Application initialized")

    async def setup_modules(self):
        """모듈 초기화 및 설정"""
        logger.info("Setting up modules...")

        # UI 모듈 초기화 (구현 완료)
        from ui.ui_manager import UIManager
        self.ui_manager = UIManager()
        self.ui_manager.setup_event_handlers()
        self.ui_manager.start()

        # TODO: 각 담당자가 모듈 구현 후 여기서 초기화
        # 예시:
        # from audio.hotkey import HotkeyManager
        # self.hotkey_manager = HotkeyManager(self.config.audio.hotkey)

        # from browser.launcher import BrowserController
        # self.browser_controller = BrowserController(self.config.browser)

        # from mcp.server_manager import MCPServerManager
        # self.mcp_server_manager = MCPServerManager(self.config.mcp)

        # 이벤트 구독 설정
        self._setup_event_handlers()

        logger.info("Modules setup complete")

    def _setup_event_handlers(self):
        """이벤트 핸들러 등록"""
        # 시스템 이벤트
        event_bus.subscribe(EventType.APP_SHUTDOWN, self._on_shutdown)
        event_bus.subscribe(EventType.ERROR_OCCURRED, self._on_error)

        # TODO: 각 모듈별 이벤트 핸들러 등록
        # 예시:
        # event_bus.subscribe(EventType.HOTKEY_PRESSED, self._on_hotkey_pressed)
        # event_bus.subscribe(EventType.AUDIO_READY, self._on_audio_ready)

        logger.info("Event handlers registered")

    async def start(self):
        """애플리케이션 시작"""
        logger.info("Starting application...")

        # 이벤트 버스 시작
        await event_bus.start()

        # 모듈 설정
        await self.setup_modules()

        # 실행 상태 설정
        self.running = True

        # 앱 시작 이벤트 발행
        await publish(EventType.APP_STARTED, source="main")

        logger.info("Application started successfully")

        # TODO: 각 모듈 시작
        # 예시:
        # if self.browser_controller:
        #     self.browser_controller.launch_chrome(self.config.browser)
        #
        # if self.mcp_server_manager:
        #     self.mcp_server_manager.start_server()
        #
        # if self.hotkey_manager:
        #     self.hotkey_manager.start()
        #
        # if self.ui_manager:
        #     self.ui_manager.show_tray_icon()

        logger.info("=== MCP Desktop App is now running ===")
        logger.info(f"Hotkey: {self.config.audio.hotkey}")
        logger.info("Press Ctrl+C to exit")

    async def stop(self):
        """애플리케이션 종료"""
        logger.info("Stopping application...")

        self.running = False

        # 종료 이벤트 발행
        await publish(EventType.APP_SHUTDOWN, source="main")

        # UI 모듈 종료
        if self.ui_manager:
            self.ui_manager.stop()

        # TODO: 각 모듈 종료
        # 예시:
        # if self.hotkey_manager:
        #     self.hotkey_manager.stop()
        #
        # if self.mcp_server_manager:
        #     self.mcp_server_manager.stop_server()
        #
        # if self.browser_controller:
        #     self.browser_controller.close()
        #
        # if self.ws_client:
        #     await self.ws_client.disconnect()

        # 이벤트 버스 종료
        await event_bus.stop()

        logger.info("Application stopped")

    async def run(self):
        """메인 실행 루프"""
        try:
            await self.start()

            # 메인 루프 (종료 신호를 기다림)
            while self.running:
                await asyncio.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
        finally:
            await self.stop()

    # ========================================================================
    # 이벤트 핸들러
    # ========================================================================

    async def _on_shutdown(self, event):
        """앱 종료 이벤트 처리"""
        logger.info(f"Shutdown event received from {event.source}")
        self.running = False

    async def _on_error(self, event):
        """에러 이벤트 처리"""
        logger.error(f"Error event: {event.data}")

    # TODO: 각 모듈별 이벤트 핸들러 구현
    # async def _on_hotkey_pressed(self, event):
    #     """V키 눌림 이벤트 처리"""
    #     logger.info("Hotkey pressed, starting recording...")
    #     if self.audio_recorder:
    #         self.audio_recorder.start_recording()
    #
    # async def _on_audio_ready(self, event):
    #     """녹음된 오디오 준비 완료 이벤트 처리"""
    #     logger.info("Audio ready, sending to server...")
    #     audio_data = event.data
    #     if self.ws_client:
    #         await self.ws_client.send_audio(audio_data)


def setup_signal_handlers(app: Application, loop: asyncio.AbstractEventLoop):
    """시그널 핸들러 설정 (Ctrl+C 등)"""

    def signal_handler(signum, frame):
        logger.info(f"Signal {signum} received, shutting down...")
        # 이벤트 루프에서 종료 코루틴 실행
        asyncio.ensure_future(app.stop(), loop=loop)

    # Windows와 Unix 모두 지원
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """메인 함수"""
    print("=" * 60)
    print("MCP Desktop App for Visually Impaired Shopping")
    print("시각장애인을 위한 음성 기반 웹 쇼핑 지원 앱")
    print("=" * 60)
    print()

    # 애플리케이션 인스턴스 생성
    app = Application()

    # 이벤트 루프 생성
    if sys.platform == "win32":
        # Windows에서는 ProactorEventLoop 사용
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    # 시그널 핸들러 설정
    setup_signal_handlers(app, loop)

    try:
        # 애플리케이션 실행
        loop.run_until_complete(app.run())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        loop.close()
        logger.info("Event loop closed")

    print()
    print("=" * 60)
    print("Goodbye!")
    print("=" * 60)


if __name__ == "__main__":
    main()
