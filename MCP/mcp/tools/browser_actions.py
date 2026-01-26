"""
브라우저 액션 모듈

요소 클릭, 입력, 키 입력 등 브라우저 조작 기능
"""

import logging
from typing import Any, Dict, Optional

from browser.action_utils import click_text as click_text_util
from mcp.tool_utils import resolve_frame_context

logger = logging.getLogger(__name__)


class BrowserActionsMixin:
    """브라우저 액션(클릭, 입력 등)을 담당하는 Mixin 클래스"""

    async def click_element(
        self,
        selector: str,
        wait_timeout: int = 5000,
        frame_selector: Optional[str] = None,
        frame_name: Optional[str] = None,
        frame_url: Optional[str] = None,
        frame_index: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        요소 클릭

        Args:
            selector: CSS 선택자
            wait_timeout: 대기 시간 (ms)
            frame_selector: iframe CSS 선택자 (선택)
            frame_name: iframe name 속성 (선택)
            frame_url: iframe URL 일부 또는 정규식 (선택)
            frame_index: iframe index (선택)

        Returns:
            {"success": bool, "element_found": bool}
        """
        return await self._click_with_frame(
            selector,
            wait_timeout=wait_timeout,
            frame_selector=frame_selector,
            frame_name=frame_name,
            frame_url=frame_url,
            frame_index=frame_index,
        )

    async def fill_input(
        self,
        selector: str,
        value: str,
        frame_selector: Optional[str] = None,
        frame_name: Optional[str] = None,
        frame_url: Optional[str] = None,
        frame_index: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        입력 필드 채우기

        Args:
            selector: CSS 선택자
            value: 입력할 값
            frame_selector: iframe CSS 선택자 (선택)
            frame_name: iframe name 속성 (선택)
            frame_url: iframe URL 일부 또는 정규식 (선택)
            frame_index: iframe index (선택)

        Returns:
            {"success": bool}
        """
        page = await self._get_active_page()
        if not page:
            return {"success": False, "error": "Not connected to browser"}

        try:
            context_type, context, error = resolve_frame_context(
                page,
                frame_selector=frame_selector,
                frame_name=frame_name,
                frame_url=frame_url,
                frame_index=frame_index,
            )
            if error:
                return {"success": False, "error": error}

            if context_type == "frame_locator":
                locator = context.locator(selector)
                await locator.fill(value)
            else:
                await context.fill(selector, value)

            logger.info(f"Filled input {selector} with: {value}")
            return {"success": True}

        except Exception as e:
            logger.error(f"Fill failed: {e}")
            return {"success": False, "error": str(e)}

    async def press_key(
        self,
        selector: str,
        key: str = "Enter",
        frame_selector: Optional[str] = None,
        frame_name: Optional[str] = None,
        frame_url: Optional[str] = None,
        frame_index: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        키보드 키 입력

        Args:
            selector: CSS 선택자
            key: 키 이름 (Enter, Tab 등)
            frame_selector: iframe CSS 선택자 (선택)
            frame_name: iframe name 속성 (선택)
            frame_url: iframe URL 일부 또는 정규식 (선택)
            frame_index: iframe index (선택)

        Returns:
            {"success": bool}
        """
        page = await self._get_active_page()
        if not page:
            return {"success": False, "error": "Not connected to browser"}

        try:
            context_type, context, error = resolve_frame_context(
                page,
                frame_selector=frame_selector,
                frame_name=frame_name,
                frame_url=frame_url,
                frame_index=frame_index,
            )
            if error:
                return {"success": False, "error": error}

            if context_type == "frame_locator":
                locator = context.locator(selector)
                await locator.press(key)
            else:
                await context.press(selector, key)

            logger.info(f"Pressed key {key} on {selector}")
            return {"success": True}

        except Exception as e:
            logger.error(f"Press failed: {e}")
            return {"success": False, "error": str(e)}

    async def click_text(self, text: str) -> Dict[str, Any]:
        """
        텍스트로 요소 클릭 (프레임 포함)

        Args:
            text: 찾을 텍스트
        Returns:
            {"success": bool, "result": str}
        """
        page = await self._get_active_page()
        if not page:
            return {"success": False, "error": "Not connected to browser"}

        try:
            return await click_text_util(page, text)
        except Exception as e:
            logger.error(f"Click text failed: {e}")
            return {"success": False, "error": str(e)}

    async def _click_with_frame(
        self,
        selector: str,
        wait_timeout: int = 5000,
        frame_selector: Optional[str] = None,
        frame_name: Optional[str] = None,
        frame_url: Optional[str] = None,
        frame_index: Optional[int] = None,
    ) -> Dict[str, Any]:
        """프레임을 고려한 클릭 내부 구현"""
        page = await self._get_active_page()
        if not page:
            return {"success": False, "error": "Not connected to browser"}

        try:
            context_type, context, error = resolve_frame_context(
                page,
                frame_selector=frame_selector,
                frame_name=frame_name,
                frame_url=frame_url,
                frame_index=frame_index,
            )
            if error:
                return {"success": False, "element_found": False, "error": error}

            if context_type == "frame_locator":
                locator = context.locator(selector)
                await locator.wait_for(timeout=wait_timeout)
                await locator.click(timeout=wait_timeout)
            else:
                await context.wait_for_selector(selector, timeout=wait_timeout)
                await context.click(selector)

            logger.info(f"Clicked element: {selector}")
            return {"success": True, "element_found": True}

        except Exception as e:
            logger.error(f"Click failed: {e}")
            return {"success": False, "element_found": False, "error": str(e)}
