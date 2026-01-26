"""
브라우저 제어 도구 모듈

Playwright를 사용하여 CDP로 연결된 브라우저 제어
"""

import logging
from typing import Any, Dict

from mcp.tool_utils import normalize_tool_call
from .browser_connection import BrowserConnectionMixin
from .browser_actions import BrowserActionsMixin
from .browser_extraction import BrowserExtractionMixin
from .browser_utilities import BrowserUtilitiesMixin
from .browser_tabs import BrowserTabsMixin

logger = logging.getLogger(__name__)


class BrowserTools(
    BrowserConnectionMixin,
    BrowserActionsMixin,
    BrowserExtractionMixin,
    BrowserUtilitiesMixin,
    BrowserTabsMixin,
):
    """
    브라우저 제어 도구

    Playwright를 통해 CDP 연결된 Chrome 브라우저 조작
    여러 Mixin 클래스를 조합하여 기능 제공
    """

    def __init__(self):
        # 모든 Mixin 초기화
        BrowserConnectionMixin.__init__(self)

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        도구 실행

        Args:
            tool_name: 도구 이름
            arguments: 도구 인자

        Returns:
            도구 실행 결과
        """
        tool_name, args = normalize_tool_call(tool_name, arguments)

        tools = {
            "navigate_to_url": self.navigate_to_url,
            "click_element": self.click_element,
            "fill_input": self.fill_input,
            "get_text": self.get_text,
            "extract": self.extract,
            "take_screenshot": self.take_screenshot,
            "scroll": self.scroll,
            "press_key": self.press_key,
            "wait": self.wait,
            "click_text": self.click_text,
            "get_visible_buttons": self.get_visible_buttons,
            "get_pages": self.get_pages,
            "wait_for_new_page": self.wait_for_new_page,
        }

        if tool_name not in tools:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        tool_func = tools[tool_name]

        try:
            result = await tool_func(**args)
            if isinstance(result, dict):
                try:
                    page = await self._get_active_page()
                    if page and page.url:
                        result.setdefault("current_url", page.url)
                except Exception:
                    pass
            return result
        except TypeError as e:
            return {"success": False, "error": f"Invalid arguments: {e}"}


__all__ = ["BrowserTools"]
