"""
Helpers for building follow-up extract commands after selection.
"""

from typing import Optional, Dict

from core.interfaces import MCPCommand, SessionState
from ..sites.site_manager import get_site_manager, get_current_site


def build_product_extract_command(
    session: Optional[SessionState],
) -> Optional[MCPCommand]:
    if not session:
        return None

    current_url = session.current_url or ""
    site = None
    if session.current_site:
        site = get_site_manager().get_site(session.current_site)
    if not site and current_url:
        site = get_current_site(current_url)

    if not site:
        return None

    page = site.get_page_selectors("product")
    selectors = page.selectors if page and page.selectors else {}
    if not selectors:
        return None

    field_selectors: Dict[str, str] = {}
    title_selector = selectors.get("product_title")
    if title_selector:
        field_selectors["name"] = title_selector
    price_selector = selectors.get("price")
    if price_selector:
        field_selectors["price"] = price_selector
    original_selector = selectors.get("original_price")
    if original_selector:
        field_selectors["original_price"] = original_selector
    info_selector = selectors.get("product_info")
    if info_selector:
        field_selectors["description"] = info_selector

    if not field_selectors:
        return None

    fields = list(field_selectors.keys())
    return MCPCommand(
        tool_name="extract",
        arguments={
            "selector": "body",
            "fields": fields,
            "field_selectors": field_selectors,
            "limit": 1,
        },
        description="extract product details"
    )
