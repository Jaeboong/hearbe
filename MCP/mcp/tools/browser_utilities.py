"""
브라우저 유틸리티 모듈

네비게이션, 대기, 스크린샷, 스크롤 등 유틸리티 기능
"""

import asyncio
import base64
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class BrowserUtilitiesMixin:
    """브라우저 유틸리티 기능을 담당하는 Mixin 클래스"""

    async def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """
        URL로 이동

        Args:
            url: 이동할 URL

        Returns:
            {"success": bool, "current_url": str}
        """
        page = await self._get_active_page()
        if not page:
            return {"success": False, "error": "Not connected to browser"}

        try:
            await page.goto(url, wait_until="domcontentloaded")
            current_url = page.url
            logger.info(f"Navigated to: {current_url}")
            return {"success": True, "current_url": current_url}

        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return {"success": False, "error": str(e)}

    async def wait(self, ms: int = 1000) -> Dict[str, Any]:
        """
        대기
        Args:
            ms: 대기 시간 (ms)

        Returns:
            {"success": bool}
        """
        if ms < 0:
            return {"success": False, "error": "Invalid wait time"}
        await asyncio.sleep(ms / 1000)
        return {"success": True}

    async def take_screenshot(self, full_page: bool = False) -> Dict[str, Any]:
        """
        스크린샷 캡처

        Args:
            full_page: 전체 페이지 캡처 여부

        Returns:
            {"success": bool, "screenshot_base64": str}
        """
        page = await self._get_active_page()
        if not page:
            return {"success": False, "error": "Not connected to browser"}

        try:
            screenshot_bytes = await page.screenshot(full_page=full_page)
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
            amount: 스크롤 양(px)

        Returns:
            {"success": bool}
        """
        page = await self._get_active_page()
        if not page:
            return {"success": False, "error": "Not connected to browser"}

        try:
            delta = -amount if direction == "up" else amount
            await page.mouse.wheel(0, delta)
            logger.info(f"Scrolled {direction} by {amount}px")
            return {"success": True}

        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return {"success": False, "error": str(e)}
