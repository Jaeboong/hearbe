from __future__ import annotations

import re
from typing import Optional, List, Dict

from core.interfaces import LLMResponse, MCPCommand, SessionState
from core.korean_numbers import extract_ordinal_index
from services.llm.sites.site_manager import get_page_type, get_selector


def handle_cart_action(user_text: str, session: Optional[SessionState]) -> Optional[LLMResponse]:
    if not session:
        return None

    current_url = session.current_url or ""
    if not current_url or get_page_type(current_url) != "cart":
        return None

    text = user_text.strip()
    if not text:
        return None

    items = session.context.get("cart_items") if session.context else []
    items = items if isinstance(items, list) else []

    # Select all / deselect all
    if "전체선택" in text or "전체 선택" in text or "전체해제" in text or "전체 해제" in text:
        selector = get_selector(current_url, "select_all_checkbox") or "input[type='checkbox']"
        return LLMResponse(
            text="전체 선택을 변경합니다.",
            commands=[
                MCPCommand(tool_name="click", arguments={"selector": selector}, description="toggle select all")
            ],
            requires_flow=False,
            flow_type=None,
        )

    target_name = _resolve_target_item(text, items)
    if not target_name:
        return None

    if any(word in text for word in ["선택", "체크"]):
        selector = _build_cart_item_checkbox_selector(target_name)
        return LLMResponse(
            text=f"'{target_name}' 상품을 선택합니다.",
            commands=[MCPCommand(tool_name="click", arguments={"selector": selector}, description="select cart item")],
            requires_flow=False,
            flow_type=None,
        )

    if any(word in text for word in ["해제", "취소", "체크 해제"]):
        selector = _build_cart_item_checkbox_selector(target_name)
        return LLMResponse(
            text=f"'{target_name}' 선택을 해제합니다.",
            commands=[MCPCommand(tool_name="click", arguments={"selector": selector}, description="deselect cart item")],
            requires_flow=False,
            flow_type=None,
        )

    quantity = _extract_quantity(text)
    if quantity is not None:
        selector = _build_cart_item_quantity_selector(target_name)
        commands = [
            MCPCommand(tool_name="fill", arguments={"selector": selector, "text": str(quantity)}, description="update cart quantity"),
            MCPCommand(tool_name="press", arguments={"selector": selector, "key": "Enter"}, description="apply quantity"),
        ]
        return LLMResponse(
            text=f"'{target_name}' 수량을 {quantity}개로 변경합니다.",
            commands=commands,
            requires_flow=False,
            flow_type=None,
        )

    return None


def _resolve_target_item(text: str, items: List[Dict]) -> Optional[str]:
    if not items:
        return None

    ordinal = extract_ordinal_index(text)
    if ordinal is not None and 0 <= ordinal < len(items):
        name = items[ordinal].get("name")
        if name:
            return name

    for item in items:
        name = item.get("name")
        if not name:
            continue
        if name in text:
            return name

    if len(items) == 1:
        return items[0].get("name")

    return None


def _build_cart_item_checkbox_selector(name: str) -> str:
    safe = name.replace('"', '\\"')
    return (
        '[data-component-id="non-fresh-bundle"] [id^="item_"]'
        f':has(a span:has-text("{safe}")) input[type="checkbox"]'
    )


def _build_cart_item_quantity_selector(name: str) -> str:
    safe = name.replace('"', '\\"')
    return (
        '[data-component-id="non-fresh-bundle"] [id^="item_"]'
        f':has(a span:has-text("{safe}")) input.cart-quantity-input'
    )


def _extract_quantity(text: str) -> Optional[int]:
    match = re.search(r"(\d+)\s*개", text)
    if match:
        return int(match.group(1))
    match = re.search(r"수량\s*(\d+)", text)
    if match:
        return int(match.group(1))
    return None
