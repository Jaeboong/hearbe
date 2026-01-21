"""
브라우저 제어 도구 모듈

Playwright를 사용하여 CDP로 연결된 브라우저 제어
"""

import asyncio
import base64
import logging
from typing import Any, Dict, Optional

from playwright.async_api import async_playwright, Browser, Page, Playwright

logger = logging.getLogger(__name__)


class BrowserTools:
    """
    브라우저 제어 도구

    Playwright를 통해 CDP 연결된 Chrome 브라우저 조작
    """

    def __init__(self):
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
        self._cdp_url: Optional[str] = None

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

            # 기존 페이지가 있으면 사용, 없으면 새로 생성
            contexts = self._browser.contexts
            if contexts and contexts[0].pages:
                self._page = contexts[0].pages[0]
            else:
                context = await self._browser.new_context()
                self._page = await context.new_page()

            logger.info(f"Connected to browser via CDP: {cdp_url}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to browser: {e}")
            await self.disconnect()
            return False

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

        self._page = None
        self._cdp_url = None
        logger.info("Disconnected from browser")

    async def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """
        URL로 이동

        Args:
            url: 이동할 URL

        Returns:
            {"success": bool, "current_url": str}
        """
        if not self._page:
            return {"success": False, "error": "Not connected to browser"}

        try:
            await self._page.goto(url, wait_until="domcontentloaded")
            current_url = self._page.url
            logger.info(f"Navigated to: {current_url}")
            return {"success": True, "current_url": current_url}

        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return {"success": False, "error": str(e)}

    async def click_element(self, selector: str, wait_timeout: int = 5000) -> Dict[str, Any]:
        """
        요소 클릭

        Args:
            selector: CSS 선택자
            wait_timeout: 대기 시간 (ms)

        Returns:
            {"success": bool, "element_found": bool}
        """
        if not self._page:
            return {"success": False, "error": "Not connected to browser"}

        try:
            await self._page.wait_for_selector(selector, timeout=wait_timeout)
            await self._page.click(selector)
            logger.info(f"Clicked element: {selector}")
            return {"success": True, "element_found": True}

        except Exception as e:
            logger.error(f"Click failed: {e}")
            return {"success": False, "element_found": False, "error": str(e)}

    async def fill_input(self, selector: str, value: str) -> Dict[str, Any]:
        """
        입력 필드 채우기

        Args:
            selector: CSS 선택자
            value: 입력할 값

        Returns:
            {"success": bool}
        """
        if not self._page:
            return {"success": False, "error": "Not connected to browser"}

        try:
            await self._page.fill(selector, value)
            logger.info(f"Filled input {selector} with: {value}")
            return {"success": True}

        except Exception as e:
            logger.error(f"Fill failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_text(self, selector: str) -> Dict[str, Any]:
        """
        요소의 텍스트 추출

        Args:
            selector: CSS 선택자

        Returns:
            {"success": bool, "text": str}
        """
        if not self._page:
            return {"success": False, "error": "Not connected to browser"}

        try:
            element = await self._page.query_selector(selector)
            if element:
                text = await element.text_content()
                logger.info(f"Got text from {selector}: {text[:50] if text else ''}...")
                return {"success": True, "text": text or ""}
            else:
                return {"success": False, "error": "Element not found"}

        except Exception as e:
            logger.error(f"Get text failed: {e}")
            return {"success": False, "error": str(e)}

    async def take_screenshot(self, full_page: bool = False) -> Dict[str, Any]:
        """
        스크린샷 캡처

        Args:
            full_page: 전체 페이지 캡처 여부

        Returns:
            {"success": bool, "screenshot_base64": str}
        """
        if not self._page:
            return {"success": False, "error": "Not connected to browser"}

        try:
            screenshot_bytes = await self._page.screenshot(full_page=full_page)
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
            logger.info(f"Screenshot taken (full_page={full_page})")
            return {"success": True, "screenshot_base64": screenshot_base64}

        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return {"success": False, "error": str(e)}

    async def scroll(self, direction: str, amount: int = 500) -> Dict[str, Any]:
        """
        페이지 스크롤

        Args:
            direction: 스크롤 방향 ("up" 또는 "down")
            amount: 스크롤 양 (px)

        Returns:
            {"success": bool}
        """
        if not self._page:
            return {"success": False, "error": "Not connected to browser"}

        try:
            delta = -amount if direction == "up" else amount
            await self._page.mouse.wheel(0, delta)
            logger.info(f"Scrolled {direction} by {amount}px")
            return {"success": True}

        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return {"success": False, "error": str(e)}

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        도구 실행

        Args:
            tool_name: 도구 이름
            arguments: 도구 인자

        Returns:
            도구 실행 결과
        """
        tools = {
            "navigate_to_url": self.navigate_to_url,
            "click_element": self.click_element,
            "fill_input": self.fill_input,
            "get_text": self.get_text,
            "take_screenshot": self.take_screenshot,
            "scroll": self.scroll,
        }

        if tool_name not in tools:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        tool_func = tools[tool_name]

        try:
            return await tool_func(**arguments)
        except TypeError as e:
            return {"success": False, "error": f"Invalid arguments: {e}"}
