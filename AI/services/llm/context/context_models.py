"""
Page context models and page type detection.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from ..sites.site_manager import SiteConfig


@dataclass
class PageContext:
    """Current page context."""

    site_name: str
    page_type: str  # home, search, product, cart, login
    available_actions: List[str]
    selectors: Dict[str, str]


PAGE_ACTIONS = {
    "home": ["search", "login", "navigate", "go_to_cart"],
    "search": ["select_product", "scroll", "next_page", "filter", "sort"],
    "product": ["add_to_cart", "buy_now", "view_reviews", "scroll"],
    "cart": ["checkout", "remove_item", "change_quantity", "continue_shopping"],
    "login": ["submit_login", "find_id", "find_password", "signup"],
    "unknown": ["navigate", "scroll", "click"],
}


def detect_page_type(url: str) -> str:
    """Infer page type from URL."""
    if not url:
        return "home"
    url_lower = url.lower()

    if "login" in url_lower or "signin" in url_lower:
        return "login"
    if "/search" in url_lower or "query=" in url_lower or "keyword=" in url_lower:
        return "search"
    if "/vp/" in url_lower or "/products/" in url_lower or "/item" in url_lower:
        return "product"
    if "/cart" in url_lower:
        return "cart"
    if "/checkout" in url_lower or "/order" in url_lower:
        return "checkout"
    return "home"


def get_page_context(url: str, site: Optional[SiteConfig] = None) -> PageContext:
    """Build page context from URL and site config."""
    page_type = detect_page_type(url)

    site_name = site.name if site else "unknown"

    selectors: Dict[str, str] = {}
    if site:
        page_selectors = site.get_page_selectors(page_type)
        if page_selectors:
            selectors = page_selectors.selectors

    available_actions = PAGE_ACTIONS.get(page_type, PAGE_ACTIONS["unknown"])

    return PageContext(
        site_name=site_name,
        page_type=page_type,
        available_actions=available_actions,
        selectors=selectors,
    )
