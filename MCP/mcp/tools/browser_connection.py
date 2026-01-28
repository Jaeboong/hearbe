"""
브라우저 연결 관리 모듈

Playwright를 사용하여 CDP로 브라우저 연결 및 페이지 관리
"""

import logging
from typing import Optional

from playwright.async_api import async_playwright, Browser, Page, Playwright
from core.event_bus import publish_sync, EventType

logger = logging.getLogger(__name__)


class BrowserConnectionMixin:
    """브라우저 연결 관리를 담당하는 Mixin 클래스"""

    def __init__(self):
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
        self._cdp_url: Optional[str] = None
        self._tracked_pages: set[int] = set()
        self._last_published_url: Optional[str] = None

    @property
    def is_connected(self) -> bool:
        """브라우저 연결 상태"""
        return self._browser is not None and self._browser.is_connected()

    async def connect(self, cdp_url: str) -> bool:
        """
        CDP URL로 브라우저에 연결

        Args:
            cdp_url: Chrome DevTools Protocol WebSocket URL

        Returns:
            연결 성공 여부
        """
        if self.is_connected:
            logger.warning("Already connected to browser")
            return True

        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.connect_over_cdp(cdp_url)
            self._cdp_url = cdp_url

            # 기존 페이지가 있으면 가장 최근 탭 사용, 없으면 새로 생성
            contexts = self._browser.contexts
            open_pages = []
            if contexts:
                for context in contexts:
                    for page in context.pages:
                        if not page.is_closed():
                            open_pages.append(page)

            if open_pages:
                self._page = open_pages[-1]
            else:
                context = contexts[0] if contexts else await self._browser.new_context()
                self._page = await context.new_page()

            self._attach_browser_listeners()
            logger.info(f"Connected to browser via CDP: {cdp_url}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to browser: {e}")
            await self.disconnect()
            return False

    def _attach_browser_listeners(self):
        if not self._browser:
            return
        for context in self._browser.contexts:
            try:
                context.on("page", self._on_new_page)
                for page in context.pages:
                    if not page.is_closed():
                        self._attach_page_listeners(page)
            except Exception as e:
                logger.debug(f"Failed to attach context listeners: {e}")

    def _on_new_page(self, page: Page):
        self._attach_page_listeners(page)
        self._publish_page_url(page)

    def _attach_page_listeners(self, page: Page):
        page_id = id(page)
        if page_id in self._tracked_pages:
            return
        self._tracked_pages.add(page_id)

        def on_frame_navigated(frame):
            try:
                if frame == page.main_frame:
                    self._publish_page_url(page)
            except Exception:
                pass

        def on_load():
            self._publish_page_url(page)

        try:
            page.on("framenavigated", on_frame_navigated)
            page.on("load", on_load)
        except Exception as e:
            logger.debug(f"Failed to attach page listeners: {e}")

    def _publish_page_url(self, page: Page):
        try:
            url = page.url or ""
            if not url or url == self._last_published_url:
                return
            self._last_published_url = url
            publish_sync(
                EventType.PAGE_URL_UPDATED,
                data={"url": url},
                source="browser"
            )
        except Exception:
            pass

    async def _get_active_page(self) -> Optional[Page]:
        """
        현재 활성 페이지 가져오기

        기존 페이지가 닫혔거나 없으면 새로 생성

        Returns:
            활성 Page 객체 또는 None
        """
        if not self.is_connected:
            return None

        try:
            contexts = self._browser.contexts

            # Return the most recently opened page if available.
            if contexts:
                open_pages = []
                for context in contexts:
                    for page in context.pages:
                        if not page.is_closed():
                            open_pages.append(page)
                if open_pages:
                    return open_pages[-1]

            # 유효한 페이지가 없으면 새로 생성
            logger.info("No active page found, creating new one")
            if contexts:
                context = contexts[0]
            else:
                context = await self._browser.new_context()

            page = await context.new_page()
            return page

        except Exception as e:
            logger.error(f"Failed to get active page: {e}")
            return None

    async def disconnect(self):
        """브라우저 연결 해제"""
        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass
            self._browser = None

        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                pass
            self._playwright = None

        self._cdp_url = None
        self._tracked_pages.clear()
        logger.info("Disconnected from browser")
