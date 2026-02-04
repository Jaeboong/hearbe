"""
Formatting helpers for LLM prompt sections.
"""

import json
from typing import Any, Dict, List, Optional

from .context_commands import AVAILABLE_COMMANDS
from ..sites.site_manager import get_selector


def format_commands() -> str:
    """Render available commands documentation."""
    lines: List[str] = []
    for name, spec in AVAILABLE_COMMANDS.items():
        lines.append(f"- {name}: {spec['description']}")
        lines.append(f"  예시: {spec['example']}")
    return "\n".join(lines)


def format_selectors(selectors: Dict[str, str]) -> str:
    """Render selector documentation."""
    if not selectors:
        return "(선택자 정보 없음 - click_text 사용 권장)"

    lines = []
    for name, selector in selectors.items():
        lines.append(f"- {name}: {selector}")
    return "\n".join(lines)


def format_search_results_section(search_results: List[Any] = None) -> str:
    if not search_results:
        return ""

    items: List[Dict[str, Any]] = []
    for item in search_results:
        if isinstance(item, dict):
            items.append(item)

    if not items:
        return ""

    max_items = len(items)
    lines = ["## Search Results (most recent)"]
    for item in items[:max_items]:
        entry = {
            "index": item.get("index"),
            "name": item.get("name") or item.get("title") or item.get("product_name"),
            "price": item.get("price"),
            "rating": item.get("rating"),
            "review_count": item.get("review_count"),
            "discount": item.get("discount"),
            "delivery": item.get("delivery") or item.get("delivery_date"),
            "free_shipping": item.get("free_shipping"),
            "free_return": item.get("free_return"),
        }
        lines.append(json.dumps(entry, ensure_ascii=True))
    lines.append("")
    lines.append("## Selection Rule")
    lines.append("- If user text matches an item above, prefer click_text with that name.")
    lines.append("- Do not run a new search when a match exists.")
    lines.append("- If no match and the intent is search, run a new search.")
    return "\n".join(lines)


def format_product_detail_section(product_detail: Optional[Dict[str, Any]] = None) -> str:
    if not product_detail:
        return ""

    detail = {
        "name": product_detail.get("name"),
        "price": product_detail.get("price"),
        "discount": product_detail.get("discount"),
        "quantity": product_detail.get("quantity"),
        "option": product_detail.get("option"),
        "options": product_detail.get("options"),
        "options_list": product_detail.get("options_list"),
    }
    lines = ["## Product Detail (current)"]
    lines.append(json.dumps(detail, ensure_ascii=True))
    return "\n".join(lines)


def format_cart_items_section(
    cart_items: List[Dict[str, Any]] = None,
    current_url: Optional[str] = None,
) -> str:
    if not cart_items:
        return ""

    items: List[Dict[str, Any]] = []
    for item in cart_items:
        if isinstance(item, dict):
            items.append(item)

    if not items:
        return ""

    lines = ["## Cart Items (current)"]
    for idx, item in enumerate(items, start=1):
        name = item.get("name") or ""
        entry = {
            "index": idx,
            "name": name,
            "option": item.get("option"),
            "price": item.get("price"),
            "quantity": item.get("quantity"),
            "selected": item.get("selected"),
            "arrival": item.get("arrival"),
            "selectors": build_cart_item_selectors(name, current_url) if name else {},
        }
        lines.append(json.dumps(entry, ensure_ascii=True))
    return "\n".join(lines)


def format_url_context(current_url: str, previous_url: Optional[str]) -> str:
    if not previous_url:
        return ""
    return f"- Previous URL: {previous_url}"


def _wrap_is(selector: Optional[str]) -> str:
    if not selector:
        return ""
    if selector.startswith(":is("):
        return selector
    if "," in selector:
        return f":is({selector})"
    return selector


def _build_cart_item_root_selector(name: str, current_url: Optional[str]) -> str:
    safe = name.replace('"', '\\"')
    item_selector = _wrap_is(get_selector(current_url, "cart_item")) if current_url else ""
    title_selector = _wrap_is(get_selector(current_url, "item_title")) if current_url else ""
    if item_selector and title_selector:
        return f'{item_selector}:has({title_selector}:has-text("{safe}"))'
    return f'[id^="item_"]:has(a span:has-text("{safe}"))'


def build_cart_item_selectors(name: str, current_url: Optional[str] = None) -> Dict[str, str]:
    base = _build_cart_item_root_selector(name, current_url)
    checkbox_selector = _wrap_is(get_selector(current_url, "item_checkbox")) if current_url else ""
    quantity_selector = _wrap_is(get_selector(current_url, "quantity_input")) if current_url else ""
    plus_selector = _wrap_is(get_selector(current_url, "quantity_plus")) if current_url else ""
    minus_selector = _wrap_is(get_selector(current_url, "quantity_minus")) if current_url else ""

    if not checkbox_selector:
        checkbox_selector = "input[type=\"checkbox\"]"
    if not quantity_selector:
        quantity_selector = "input.cart-quantity-input"

    quantity_plus = (
        f"{base} {plus_selector}"
        if plus_selector
        else (
            f"{base} [data-component-id=\"quantity-input\"] .twc-bg-plus-icon, "
            f'{base} button[aria-label*="증가"], {base} button[aria-label*="더하기"]'
        )
    )
    quantity_minus = (
        f"{base} {minus_selector}"
        if minus_selector
        else (
            f"{base} [data-component-id=\"quantity-input\"] .twc-bg-minus-icon, "
            f'{base} button[aria-label*="감소"], {base} button[aria-label*="빼기"]'
        )
    )

    return {
        "item_root": base,
        "item_checkbox": f"{base} {checkbox_selector}",
        "quantity_input": f"{base} {quantity_selector}",
        "quantity_plus": quantity_plus,
        "quantity_minus": quantity_minus,
    }
