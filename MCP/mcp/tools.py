"""
釉뚮씪?곗? ?쒖뼱 ?꾧뎄 紐⑤뱢

Playwright瑜??ъ슜?섏뿬 CDP濡??곌껐??釉뚮씪?곗? ?쒖뼱
"""

import asyncio
import base64
import logging
from typing import Any, Dict, Optional

from playwright.async_api import async_playwright, Browser, Page, Playwright

from browser.action_utils import (
    click_text as click_text_util,
    get_visible_buttons as get_visible_buttons_util,
)
from mcp.tool_utils import normalize_tool_call, resolve_frame_context

logger = logging.getLogger(__name__)


class BrowserTools:
    """
    釉뚮씪?곗? ?쒖뼱 ?꾧뎄

    Playwright瑜??듯빐 CDP ?곌껐??Chrome 釉뚮씪?곗? 議곗옉
    """

    def __init__(self):
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
        self._cdp_url: Optional[str] = None

    @property
    def is_connected(self) -> bool:
        """釉뚮씪?곗? ?곌껐 ?곹깭"""
        return self._browser is not None and self._browser.is_connected()

    async def connect(self, cdp_url: str) -> bool:
        """
        CDP URL濡?釉뚮씪?곗????곌껐

        Args:
            cdp_url: Chrome DevTools Protocol WebSocket URL

        Returns:
            ?곌껐 ?깃났 ?щ?
        """
        if self.is_connected:
            logger.warning("Already connected to browser")
            return True

        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.connect_over_cdp(cdp_url)
            self._cdp_url = cdp_url

            # 湲곗〈 ?섏씠吏媛 ?덉쑝硫??ъ슜, ?놁쑝硫??덈줈 ?앹꽦
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
        logger.info("Disconnected from browser")

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
        ?붿냼 ?대┃

        Args:
            selector: CSS ?좏깮??            wait_timeout: ?湲??쒓컙 (ms)
            frame_selector: iframe CSS ?좏깮??(?좏깮)
            frame_name: iframe name ?띿꽦 (?좏깮)
            frame_url: iframe URL ?쇰? ?먮뒗 ?뺢퇋??(?좏깮)
            frame_index: iframe index (?좏깮)

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

    async def get_text(
        self,
        selector: str,
        frame_selector: Optional[str] = None,
        frame_name: Optional[str] = None,
        frame_url: Optional[str] = None,
        frame_index: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        요소의 텍스트 추출

        Args:
            selector: CSS 선택자
            frame_selector: iframe CSS 선택자 (선택)
            frame_name: iframe name 속성 (선택)
            frame_url: iframe URL 일부 또는 정규식 (선택)
            frame_index: iframe index (선택)

        Returns:
            {"success": bool, "text": str}
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
                if await locator.count() == 0:
                    return {"success": False, "error": "Element not found"}
                text = await locator.first.text_content()
            else:
                element = await context.query_selector(selector)
                if not element:
                    return {"success": False, "error": "Element not found"}
                text = await element.text_content()

            logger.info(f"Got text from {selector}: {text[:50] if text else ''}...")
            return {"success": True, "text": text or ""}

        except Exception as e:
            logger.error(f"Get text failed: {e}")
            return {"success": False, "error": str(e)}

    async def extract(
        self,
        selector: str,
        fields: Optional[list] = None,
        field_selectors: Optional[Dict[str, str]] = None,
        limit: int = 20,
        frame_selector: Optional[str] = None,
        frame_name: Optional[str] = None,
        frame_url: Optional[str] = None,
        frame_index: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Extract structured items from a list.

        Args:
            selector: CSS selector for list items
            fields: Field names to extract (default: ["name"])
            field_selectors: Optional field -> selector mapping
            limit: Max number of items to extract
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

            locator = context.locator(selector)
            count = await locator.count()
            if count == 0:
                return {"success": False, "error": "Element not found", "products": []}

            max_items = min(limit, count)
            fields = fields or ["name"]
            field_selectors = field_selectors or {}
            products: list[Dict[str, Any]] = []

            for i in range(max_items):
                item = locator.nth(i)
                item_data: Dict[str, Any] = {"index": i + 1}

                for field in fields:
                    text = ""
                    field_selector = field_selectors.get(field)
                    if field_selector:
                        target = item.locator(field_selector)
                        if await target.count() > 0:
                            value = await target.first.text_content()
                            text = value.strip() if value else ""
                    elif field in ("name", "title"):
                        value = await item.text_content()
                        text = value.strip() if value else ""

                    item_data[field] = text

                products.append(item_data)

            return {
                "success": True,
                "products": products,
                "count": len(products),
                "page_url": page.url,
            }

        except Exception as e:
            logger.error(f"Extract failed: {e}")
            return {"success": False, "error": str(e), "products": []}

    async def click_text(self, text: str) -> Dict[str, Any]:
        """
        ?띿뒪?몃줈 ?붿냼 ?대┃ (?꾨젅???ы븿)

        Args:
            text: 李얠쓣 ?띿뒪??
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

    async def get_visible_buttons(self, max_items: int = 200) -> Dict[str, Any]:
        """
        ?섏씠吏?먯꽌 蹂댁씠??踰꾪듉 ?붿냼 議고쉶

        Args:
            max_items: 理쒕? ??ぉ ??
        Returns:
            {"success": bool, "buttons": list, "count": int}
        """
        page = await self._get_active_page()
        if not page:
            return {"success": False, "error": "Not connected to browser", "buttons": []}

        try:
            buttons = await get_visible_buttons_util(page, max_items=max_items)
            return {"success": True, "buttons": buttons, "count": len(buttons)}
        except Exception as e:
            logger.error(f"Get visible buttons failed: {e}")
            return {"success": False, "error": str(e), "buttons": []}

    async def wait(self, ms: int = 1000) -> Dict[str, Any]:
        """
        ?湲?
        Args:
            ms: ?湲??쒓컙 (ms)

        Returns:
            {"success": bool}
        """
        if ms < 0:
            return {"success": False, "error": "Invalid wait time"}
        await asyncio.sleep(ms / 1000)
        return {"success": True}

    async def take_screenshot(self, full_page: bool = False) -> Dict[str, Any]:
        """
        ?ㅽ겕由곗꺑 罹≪쿂

        Args:
            full_page: ?꾩껜 ?섏씠吏 罹≪쿂 ?щ?

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
        ?섏씠吏 ?ㅽ겕濡?

        Args:
            direction: ?ㅽ겕濡?諛⑺뼢 ("up" ?먮뒗 "down")
            amount: ?ㅽ겕濡???(px)

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

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        ?꾧뎄 ?ㅽ뻾

        Args:
            tool_name: ?꾧뎄 ?대쫫
            arguments: ?꾧뎄 ?몄옄

        Returns:
            ?꾧뎄 ?ㅽ뻾 寃곌낵
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
        }

        if tool_name not in tools:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        tool_func = tools[tool_name]

        try:
            return await tool_func(**args)
        except TypeError as e:
            return {"success": False, "error": f"Invalid arguments: {e}"}

    async def _click_with_frame(
        self,
        selector: str,
        wait_timeout: int = 5000,
        frame_selector: Optional[str] = None,
        frame_name: Optional[str] = None,
        frame_url: Optional[str] = None,
        frame_index: Optional[int] = None,
    ) -> Dict[str, Any]:
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
