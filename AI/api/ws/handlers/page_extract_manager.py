# -*- coding: utf-8 -*-
"""
Page extract manager.

Triggers extract tools on page/tab changes to align LLM context with actual browser state.
"""

import logging
import time
from typing import List, Optional

from core.interfaces import MCPCommand
from services.llm.context.context_rules import build_extract_products_command
from services.llm.sites.site_manager import get_page_type, get_current_site

logger = logging.getLogger(__name__)

AUTO_EXTRACT_MIN_INTERVAL_SEC = 1.0

CTX_LAST_URL = "auto_extract_last_url"
CTX_LAST_TS = "auto_extract_last_ts"
CTX_LAST_TYPE = "auto_extract_last_type"
CTX_LAST_PAGE_ID = "auto_extract_last_page_id"


class PageExtractManager:
    def __init__(self, sender, session_manager):
        self._sender = sender
        self._session = session_manager

    async def handle_page_update(self, session_id: str, url: Optional[str], page_id: Optional[int] = None) -> None:
        await self._trigger_extract(session_id, url, force=False, page_id=page_id)

    async def ensure_context(self, session_id: str, url: Optional[str], session) -> bool:
        if not url or not session:
            return False
        page_type = get_page_type(url)
        if not page_type:
            return False
        if not self._is_context_missing(page_type, session):
            return False
        return await self._trigger_extract(session_id, url, force=True, page_id=None)

    async def _trigger_extract(
        self,
        session_id: str,
        url: Optional[str],
        force: bool,
        page_id: Optional[int],
    ) -> bool:
        if not url or not self._sender:
            return False

        page_type = get_page_type(url)
        if not page_type:
            return False

        last_url = self._get_context(session_id, CTX_LAST_URL)
        last_page_id = self._get_context(session_id, CTX_LAST_PAGE_ID)
        if page_id is None and last_page_id is not None:
            page_id = last_page_id
        if not force and last_url == url and last_page_id == page_id:
            return False

        now = time.time()
        last_ts = self._get_context(session_id, CTX_LAST_TS) or 0.0
        if now - last_ts < AUTO_EXTRACT_MIN_INTERVAL_SEC:
            return False

        commands = self._build_extract_commands(page_type, url)
        if commands:
            await self._sender.send_tool_calls(session_id, commands)
            logger.info(
                "Auto extract triggered: session=%s type=%s url=%s force=%s",
                session_id,
                page_type,
                url,
                force,
            )

        self._set_context(session_id, CTX_LAST_URL, url)
        self._set_context(session_id, CTX_LAST_TS, now)
        self._set_context(session_id, CTX_LAST_TYPE, page_type)
        self._set_context(session_id, CTX_LAST_PAGE_ID, page_id)
        return bool(commands)

    def _build_extract_commands(self, page_type: str, url: str) -> List[MCPCommand]:
        wait_cmd = MCPCommand(
            tool_name="wait",
            arguments={"ms": 1200},
            description="wait for page to settle",
        )
        if page_type == "search":
            site = get_current_site(url)
            cmd = build_extract_products_command(site, current_url=url, limit=0)
            if not cmd:
                return []
            return [
                wait_cmd,
                MCPCommand(
                    tool_name=cmd.tool_name,
                    arguments=cmd.arguments,
                    description=cmd.description or "extract search results on page change",
                ),
            ]
        if page_type == "product":
            site = get_current_site(url)
            selectors = {}
            if site:
                page = site.get_page_selectors("product")
                if page and page.selectors:
                    selectors = page.selectors

            field_selectors = {}
            if selectors.get("product_title"):
                field_selectors["name"] = selectors["product_title"]
            if selectors.get("final_price"):
                field_selectors["price"] = selectors["final_price"]
            if selectors.get("discount_rate"):
                field_selectors["discount_rate"] = selectors["discount_rate"]
            if selectors.get("original_price"):
                field_selectors["original_price"] = selectors["original_price"]
            if selectors.get("rocket_delivery"):
                field_selectors["delivery"] = selectors["rocket_delivery"]
            if selectors.get("product_info"):
                field_selectors["description"] = selectors["product_info"]

            image_selector = selectors.get("detail_images")

            args = {"fallback_dynamic": True}
            if field_selectors:
                args["fields"] = list(field_selectors.keys())
                args["field_selectors"] = field_selectors
            if image_selector:
                args["image_selector"] = image_selector
                args["image_limit"] = 40

            if len(args) == 1:
                return []

            return [
                wait_cmd,
                MCPCommand(
                    tool_name="extract_detail",
                    arguments=args,
                    description="extract product detail on page change",
                ),
            ]
        if page_type == "cart":
            return [
                wait_cmd,
                MCPCommand(
                    tool_name="extract_cart",
                    arguments={},
                    description="extract cart summary on page change",
                ),
            ]
        if page_type == "orderlist":
            return [
                wait_cmd,
                MCPCommand(
                    tool_name="extract_order_list",
                    arguments={},
                    description="extract order list on page change",
                ),
            ]
        return []

    def _is_context_missing(self, page_type: str, session) -> bool:
        context = getattr(session, "context", {}) or {}
        if page_type == "search":
            return not context.get("search_results")
        if page_type == "product":
            return not context.get("product_detail")
        if page_type == "cart":
            return not context.get("cart_items")
        if page_type == "orderlist":
            return not context.get("order_list")
        return False

    def _get_context(self, session_id: str, key: str, default=None):
        if not self._session:
            return default
        return self._session.get_context(session_id, key, default)

    def _set_context(self, session_id: str, key: str, value) -> None:
        if not self._session:
            return
        self._session.set_context(session_id, key, value)
