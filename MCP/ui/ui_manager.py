"""
UI 관리자

UI 모듈의 통합 관리
"""

import logging
import threading
from typing import Optional

from core.interfaces import IUIManager, AppStatus
from core.event_bus import subscribe, publish_sync, EventType, Event
from ui.mini_window import MiniWindow

logger = logging.getLogger(__name__)


class UIManager(IUIManager):
    """UI 관리자 - 최소 상태 창 표시"""

    def __init__(self):
        self.mini_window: Optional[MiniWindow] = None
        self.ui_thread: Optional[threading.Thread] = None
        self.running = False

        logger.info("UIManager initialized")

    def start(self):
        """UI 시작 (별도 스레드에서 실행)"""
        if self.running:
            logger.warning("UIManager already running")
            return

        self.running = True

        # UI를 별도 스레드에서 실행
        self.ui_thread = threading.Thread(target=self._run_ui, daemon=True)
        self.ui_thread.start()

        logger.info("UIManager started in background thread")

    def _run_ui(self):
        """UI 메인 루프 (별도 스레드)"""
        try:
            self.mini_window = MiniWindow()
            self.mini_window.set_exit_callback(self._on_exit_requested)
            self.mini_window.show()
            self.mini_window.run()
        except Exception as e:
            logger.error(f"Error in UI thread: {e}", exc_info=True)

    def show_tray_icon(self):
        """시스템 트레이 아이콘 표시 (미구현)"""
        logger.info("Tray icon not implemented yet")
        pass

    def hide_tray_icon(self):
        """시스템 트레이 아이콘 숨김 (미구현)"""
        pass

    def update_status(self, status: AppStatus):
        """
        앱 상태 업데이트

        Args:
            status: 새로운 앱 상태
        """
        if self.mini_window:
            message = status.message or ""
            self.mini_window.update_status(status.status, message)
            logger.debug(f"UI status updated: {status.status}")

    def show_notification(self, title: str, message: str):
        """
        시스템 알림 표시

        Args:
            title: 알림 제목
            message: 알림 메시지
        """
        logger.info(f"Notification: {title} - {message}")
        # TODO: 시스템 알림 구현

    def request_exit(self):
        """앱 종료 요청"""
        logger.info("Exit requested from UI")
        self.stop()

    def stop(self):
        """UI 종료"""
        self.running = False

        if self.mini_window:
            self.mini_window.destroy()
            logger.info("Mini window destroyed")

        logger.info("UIManager stopped")

    # ========================================================================
    # 이벤트 핸들러 등록 헬퍼
    # ========================================================================

    def setup_event_handlers(self):
        """이벤트 핸들러 등록"""
        subscribe(EventType.HOTKEY_PRESSED, self._on_hotkey_pressed)
        subscribe(EventType.RECORDING_STARTED, self._on_recording_started)
        subscribe(EventType.RECORDING_STOPPED, self._on_recording_stopped)
        subscribe(EventType.STT_RESULT_RECEIVED, self._on_stt_result)
        subscribe(EventType.TTS_PLAYBACK_FINISHED, self._on_playback_finished)
        subscribe(EventType.ERROR_OCCURRED, self._on_error)

        logger.info("UI event handlers registered")

    # ========================================================================
    # 이벤트 핸들러
    # ========================================================================

    def _on_hotkey_pressed(self, event: Event):
        """핫키 눌림"""
        self.update_status(AppStatus(status="준비", message="음성 명령을 말하세요"))

    def _on_recording_started(self, event: Event):
        """녹음 시작"""
        self.update_status(AppStatus(status="녹음 중", message="말씀하세요..."))

    def _on_recording_stopped(self, event: Event):
        """녹음 종료"""
        self.update_status(AppStatus(status="처리 중", message="음성 인식 중..."))

    def _on_stt_result(self, event: Event):
        """STT 결과 수신"""
        text = event.data if event.data else "음성 인식 완료"
        self.update_status(AppStatus(status="처리 중", message=f"명령: {text[:20]}..."))

    def _on_playback_finished(self, event: Event):
        """재생 완료"""
        self.update_status(AppStatus(status="대기 중", message="Hotkey: V키"))

    def _on_error(self, event: Event):
        """오류 발생"""
        error_msg = event.data if event.data else "오류 발생"
        self.update_status(AppStatus(status="오류", message=str(error_msg)[:30]))

    def _on_exit_requested(self):
        """UI에서 종료 요청"""
        logger.info("Application exit requested from UI")
        publish_sync(EventType.APP_SHUTDOWN, source="ui")
