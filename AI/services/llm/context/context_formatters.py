"""
Formatting helpers for LLM prompt sections.
"""

import json
from typing import Any, Dict, List, Optional

from .context_commands import AVAILABLE_COMMANDS


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


def format_cart_items_section(cart_items: List[Dict[str, Any]] = None) -> str:
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
            "selectors": build_cart_item_selectors(name) if name else {},
        }
        lines.append(json.dumps(entry, ensure_ascii=True))
    return "\n".join(lines)


def format_url_context(current_url: str, previous_url: Optional[str]) -> str:
    if not previous_url:
        return ""
    return f"- Previous URL: {previous_url}"


def build_cart_item_selectors(name: str) -> Dict[str, str]:
    safe = name.replace('"', '\\"')
    base = f'[id^="item_"]:has(a span:has-text("{safe}"))'
    return {
        "item_root": base,
        "item_checkbox": f"{base} input[type=\"checkbox\"]",
        "quantity_input": f"{base} input.cart-quantity-input",
        "quantity_plus": (
            f"{base} [data-component-id=\"quantity-input\"] .twc-bg-plus-icon, "
            f'{base} button[aria-label*="증가"], {base} button[aria-label*="더하기"]'
        ),
        "quantity_minus": (
            f"{base} [data-component-id=\"quantity-input\"] .twc-bg-minus-icon, "
            f'{base} button[aria-label*="감소"], {base} button[aria-label*="빼기"]'
        ),
    }
