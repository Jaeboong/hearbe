"""
브라우저 데이터 추출 모듈

텍스트 추출, 구조화된 데이터 추출, 버튼 조회 등
"""

import logging
from typing import Any, Dict, Optional

from browser.action_utils import get_visible_buttons as get_visible_buttons_util
from browser.extractors import extract_cart_dynamic
from browser.fallbacks.detail_fallback import apply_detail_option_fallback
from browser.fallbacks.search_fallback import build_search_fallback_result
from mcp.tool_utils import resolve_frame_context

logger = logging.getLogger(__name__)


class BrowserExtractionMixin:
    """브라우저에서 데이터를 추출하는 기능을 담당하는 Mixin 클래스"""

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
        field_attributes: Optional[Dict[str, str]] = None,
        limit: int = 20,
        frame_selector: Optional[str] = None,
        frame_name: Optional[str] = None,
        frame_url: Optional[str] = None,
        frame_index: Optional[int] = None,
        fallback_dynamic: bool = False,
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
                if fallback_dynamic:
                    fallback = await build_search_fallback_result(page, limit)
                    if fallback:
                        return fallback
                return {"success": False, "error": "Element not found", "products": []}

            max_items = count if limit <= 0 else min(limit, count)
            fields = fields or ["name"]
            field_selectors = field_selectors or {}
            field_attributes = field_attributes or {}
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
                            attr = field_attributes.get(field)
                            if attr:
                                value = await target.first.get_attribute(attr)
                                text = value.strip() if value else ""
                            else:
                                value = await target.first.text_content()
                                text = value.strip() if value else ""
                    elif field in ("name", "title"):
                        value = await item.text_content()
                        text = value.strip() if value else ""

                    item_data[field] = text

                products.append(item_data)

            # Fallback if price/name missing
            if fallback_dynamic and fields and "price" in fields:
                missing_price = all(not p.get("price") for p in products)
                if missing_price:
                    fallback = await build_search_fallback_result(page, limit)
                    if fallback:
                        return fallback

            return {
                "success": True,
                "products": products,
                "count": len(products),
                "total_count": count,
                "page_url": page.url,
            }

        except Exception as e:
            logger.error(f"Extract failed: {e}")
            return {"success": False, "error": str(e), "products": []}

    async def extract_detail(
        self,
        fields: Optional[list] = None,
        field_selectors: Optional[Dict[str, str]] = None,
        field_attributes: Optional[Dict[str, str]] = None,
        image_selector: Optional[str] = None,
        image_attribute: str = "src",
        image_limit: int = 60,
        frame_selector: Optional[str] = None,
        frame_name: Optional[str] = None,
        frame_url: Optional[str] = None,
        frame_index: Optional[int] = None,
        fallback_dynamic: bool = False,
    ) -> Dict[str, Any]:
        """
        Extract detail fields from a product page.

        Args:
            fields: Field names to extract
            field_selectors: field -> selector mapping
            field_attributes: field -> attribute mapping (e.g., value)
            image_selector: selector for detail images
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

            field_selectors = field_selectors or {}
            field_attributes = field_attributes or {}
            fields = fields or list(field_selectors.keys())
            detail: Dict[str, Any] = {}

            for field in fields:
                field_selector = field_selectors.get(field)
                if not field_selector:
                    continue

                target = context.locator(field_selector) if context_type == "frame_locator" else context.locator(field_selector)
                if await target.count() == 0:
                    continue

                attr = field_attributes.get(field)
                if attr:
                    if attr == "value":
                        try:
                            value = await target.first.input_value()
                        except Exception:
                            value = await target.first.get_attribute(attr)
                    else:
                        value = await target.first.get_attribute(attr)
                    detail[field] = (value or "").strip()
                else:
                    value = await target.first.text_content()
                    detail[field] = (value or "").strip()

            images: list[str] = []
            if image_selector:
                img_locator = context.locator(image_selector) if context_type == "frame_locator" else context.locator(image_selector)
                count = await img_locator.count()
                max_items = min(count, image_limit) if image_limit > 0 else count
                for i in range(max_items):
                    item = img_locator.nth(i)
                    src = await item.get_attribute(image_attribute)
                    if not src:
                        continue
                    src = src.strip()
                    if src.startswith("//"):
                        src = f"https:{src}"
                    images.append(src)

            # 동적 fallback: 옵션 필드가 없거나 실패한 경우
            if fallback_dynamic:
                page_url = page.url or ""
                if "coupang.com" in page_url:
                    try:
                        dynamic_options = await apply_detail_option_fallback(page, detail)
                        if dynamic_options:
                            logger.info(f"Dynamic option extraction succeeded: {dynamic_options}")
                    except Exception as e:
                        logger.warning(f"Dynamic option extraction failed: {e}")

            return {
                "success": True,
                "detail": detail,
                "detail_images": images,
                "images": images,
                "count": len(images),
                "page_url": page.url,
            }
        except Exception as e:
            logger.error(f"Extract detail failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_visible_buttons(self, max_items: int = 200) -> Dict[str, Any]:
        """
        페이지에서 보이는 버튼 요소 조회

        Args:
            max_items: 최대 반환 개수
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

    async def get_dom_snapshot(
        self,
        include_frames: bool = True,
        max_chars: int = 200000,
        frame_max_chars: int = 80000,
    ) -> Dict[str, Any]:
        """
        Return DOM snapshot for the current page.

        Args:
            include_frames: include iframe contents
            max_chars: max characters for main DOM
            frame_max_chars: max characters per frame
        """
        page = await self._get_active_page()
        if not page:
            return {"success": False, "error": "Not connected to browser"}

        def _truncate(text: str, limit: int) -> str:
            if not text:
                return ""
            return text if len(text) <= limit else text[:limit]

        try:
            dom = await page.content()
            dom = _truncate(dom, max_chars)
            frames: list[Dict[str, Any]] = []
            if include_frames:
                for frame in page.frames:
                    if frame == page.main_frame:
                        continue
                    try:
                        content = await frame.content()
                        frames.append(
                            {
                                "url": frame.url or "",
                                "name": frame.name or "",
                                "content": _truncate(content, frame_max_chars),
                            }
                        )
                    except Exception:
                        frames.append({"url": frame.url or "", "name": frame.name or "", "content": ""})
            return {
                "success": True,
                "dom": dom,
                "frames": frames,
                "current_url": page.url,
            }
        except Exception as e:
            logger.error(f"Get DOM snapshot failed: {e}")
            return {"success": False, "error": str(e)}

    async def extract_cart(self) -> Dict[str, Any]:
        """
        Extract cart items and summary from cart page.
        """
        page = await self._get_active_page()
        if not page:
            return {"success": False, "error": "Not connected to browser"}

        try:
            try:
                await page.wait_for_selector(
                    "#mainContent [id^='item_'] input[type='checkbox']",
                    timeout=3000
                )
            except Exception:
                pass
            data = await extract_cart_dynamic(page)
            items = data.get("items") if isinstance(data, dict) else []
            summary = data.get("summary") if isinstance(data, dict) else {}
            return {
                "success": True,
                "cart_items": items,
                "cart_summary": summary,
                "page_url": page.url,
            }
        except Exception as e:
            logger.error(f"Extract cart failed: {e}")
            return {"success": False, "error": str(e), "cart_items": []}
