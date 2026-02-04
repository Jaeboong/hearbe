from __future__ import annotations

import re
from typing import Optional, List, Dict

from core.interfaces import LLMResponse, MCPCommand, SessionState
from core.korean_numbers import extract_ordinal_index
from .cart_item_matcher import match_cart_item_name, prefer_single_selected
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
        selector = _build_cart_item_checkbox_selector(current_url, target_name)
        return LLMResponse(
            text=f"'{target_name}' 상품을 선택합니다.",
            commands=[MCPCommand(tool_name="click", arguments={"selector": selector}, description="select cart item")],
            requires_flow=False,
            flow_type=None,
        )

    if any(word in text for word in ["해제", "취소", "체크 해제"]):
        selector = _build_cart_item_checkbox_selector(current_url, target_name)
        return LLMResponse(
            text=f"'{target_name}' 선택을 해제합니다.",
            commands=[MCPCommand(tool_name="click", arguments={"selector": selector}, description="deselect cart item")],
            requires_flow=False,
            flow_type=None,
        )

    if any(word in text for word in ["삭제", "지워", "제거", "빼줘", "빼 줘"]):
        delete_selector = _build_cart_item_delete_selector(current_url, target_name)
        if delete_selector:
            commands = [MCPCommand(tool_name="click", arguments={"selector": delete_selector}, description="delete cart item")]
        else:
            checkbox_selector = _build_cart_item_checkbox_selector(current_url, target_name)
            delete_selected = _wrap_is(get_selector(current_url, "delete_selected")) or "button:has-text(\"선택 삭제\")"
            commands = [
                MCPCommand(tool_name="click", arguments={"selector": checkbox_selector}, description="select cart item"),
                MCPCommand(tool_name="click", arguments={"selector": delete_selected}, description="delete selected items"),
            ]
        return LLMResponse(
            text=f"'{target_name}' 상품을 장바구니에서 삭제합니다.",
            commands=commands,
            requires_flow=False,
            flow_type=None,
        )

    quantity = _extract_quantity(text)
    if quantity is not None:
        current_qty = _find_current_quantity(target_name, items)
        if current_qty is None:
            selector = _build_cart_item_quantity_selector(current_url, target_name)
            commands = [
                MCPCommand(tool_name="fill", arguments={"selector": selector, "text": str(quantity)}, description="update cart quantity"),
                MCPCommand(tool_name="press", arguments={"selector": selector, "key": "Enter"}, description="apply quantity"),
            ]
        else:
            delta = quantity - current_qty
            if delta == 0:
                return LLMResponse(
                    text=f"'{target_name}' 수량은 이미 {quantity}개입니다.",
                    commands=[],
                    requires_flow=False,
                    flow_type=None,
                )
            if delta > 0:
                button_selector = _build_cart_item_plus_selector(current_url, target_name)
                cmd_desc = "increase quantity"
            else:
                button_selector = _build_cart_item_minus_selector(current_url, target_name)
                cmd_desc = "decrease quantity"
            commands = [
                MCPCommand(tool_name="click", arguments={"selector": button_selector}, description=cmd_desc)
                for _ in range(abs(delta))
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

    selected_name = prefer_single_selected(items)
    if selected_name:
        return selected_name

    match = match_cart_item_name(text, items)
    return match.name


def _wrap_is(selector: Optional[str]) -> str:
    if not selector:
        return ""
    if selector.startswith(":is("):
        return selector
    if "," in selector:
        return f":is({selector})"
    return selector


def _build_cart_item_root_selector(current_url: str, name: str) -> str:
    safe = _sanitize_selector_text(name)
    item_selector = _wrap_is(get_selector(current_url, "cart_item")) or '[id^="item_"]'
    title_selector = _wrap_is(get_selector(current_url, "item_title")) or "a span"
    return f'{item_selector}:has({title_selector}:has-text("{safe}"))'


def _build_cart_item_checkbox_selector(current_url: str, name: str) -> str:
    base = _build_cart_item_root_selector(current_url, name)
    checkbox_selector = _wrap_is(get_selector(current_url, "item_checkbox")) or "input[type=\"checkbox\"]"
    return f"{base} {checkbox_selector}"


def _build_cart_item_quantity_selector(current_url: str, name: str) -> str:
    base = _build_cart_item_root_selector(current_url, name)
    quantity_selector = _wrap_is(get_selector(current_url, "quantity_input")) or "input.cart-quantity-input"
    return f"{base} {quantity_selector}"


def _build_cart_item_plus_selector(current_url: str, name: str) -> str:
    base = _build_cart_item_root_selector(current_url, name)
    plus_selector = _wrap_is(get_selector(current_url, "quantity_plus")) or "[data-component-id='quantity-input'] .twc-bg-plus-icon"
    return f"{base} {plus_selector}"


def _build_cart_item_minus_selector(current_url: str, name: str) -> str:
    base = _build_cart_item_root_selector(current_url, name)
    minus_selector = _wrap_is(get_selector(current_url, "quantity_minus")) or "[data-component-id='quantity-input'] .twc-bg-minus-icon"
    return f"{base} {minus_selector}"


def _build_cart_item_delete_selector(current_url: str, name: str) -> str:
    base = _build_cart_item_root_selector(current_url, name)
    delete_selector = _wrap_is(get_selector(current_url, "delete_button"))
    if not delete_selector:
        return ""
    return f"{base} {delete_selector}"


def _sanitize_selector_text(text: str) -> str:
    if not text:
        return ""
    cleaned = "".join(ch for ch in text if ch >= " " and ch != '"')
    return cleaned.strip()


def _find_current_quantity(name: str, items: List[Dict]) -> Optional[int]:
    for item in items:
        if item.get("name") != name:
            continue
        qty = item.get("quantity")
        if qty is None:
            return None
        text = str(qty).strip()
        if not text:
            return None
        match = re.search(r"\d+", text)
        if not match:
            return None
        return int(match.group(0))
    return None


def _extract_quantity(text: str) -> Optional[int]:
    match = re.search(r"(\d+)\s*개", text)
    if match:
        return int(match.group(1))
    match = re.search(r"수량\s*(\d+)", text)
    if match:
        return int(match.group(1))
    return None
