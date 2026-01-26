"""
Browser tab helpers.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class BrowserTabsMixin:
    """Tab detection and focus helpers."""

    async def wait_for_new_page(
        self,
        timeout_ms: int = 1500,
        focus: bool = True,
    ) -> Dict[str, Any]:
        page = await self._get_active_page()
        if not page:
            return {"success": False, "error": "Not connected to browser"}

        context = page.context
        before_pages = [p for p in context.pages if not p.is_closed()]
        before_set = set(before_pages)
        new_page = None

        try:
            new_page = await context.wait_for_event("page", timeout=timeout_ms)
        except Exception:
            new_page = None

        if not new_page:
            after_pages = [p for p in context.pages if not p.is_closed()]
            for candidate in after_pages:
                if candidate not in before_set:
                    new_page = candidate
                    break

        if not new_page:
            return {"success": True, "new_page": False}

        if focus:
            try:
                await new_page.bring_to_front()
            except Exception:
                pass

        try:
            self._page = new_page
        except Exception:
            pass

        logger.info("Detected new page and focused")
        return {"success": True, "new_page": True, "page_url": new_page.url}
