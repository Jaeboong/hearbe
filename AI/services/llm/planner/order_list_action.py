"""
Order list action handler.

Handles order detail navigation from order list page using session context.
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List
import re

from core.interfaces import MCPCommand, LLMResponse, SessionState
from core.korean_numbers import extract_ordinal_index
from services.llm.sites.site_manager import get_page_type

DETAIL_KEYWORDS = (
    "상세",
    "상세보기",
    "주문 상세",
    "주문상세",
    "상세로",
)

READ_KEYWORDS = (
    "주문 목록",
    "주문목록",
    "주문 내역",
    "주문내역",
    "주문 리스트",
    "주문리스트",
    "읽어",
    "알려",
    "보여",
    "확인",
    "조회",
)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", "", text or "").lower()


def _find_by_title(items: List[Dict[str, Any]], text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    norm = _normalize(text)
    if not norm:
        return None
    for item in items:
        title = str(item.get("title") or "")
        if not title:
            continue
        title_norm = _normalize(title)
        if not title_norm:
            continue
        if norm in title_norm or title_norm in norm:
            return item
    return None


def _build_detail_commands(item: Dict[str, Any]) -> List[MCPCommand]:
    selector = item.get("detail_selector")
    url = item.get("detail_url")
    title = item.get("title") or ""

    commands: List[MCPCommand] = []
    if selector:
        commands.append(
            MCPCommand(
                tool_name="click",
                arguments={"selector": selector},
                description="open order detail",
            )
        )
    elif url:
        commands.append(
            MCPCommand(
                tool_name="goto",
                arguments={"url": url},
                description="go to order detail",
            )
        )
    elif title:
        commands.append(
            MCPCommand(
                tool_name="click_text",
                arguments={"text": str(title)},
                description="click order title",
            )
        )

    if commands:
        commands.append(
            MCPCommand(
                tool_name="wait",
                arguments={"ms": 1500},
                description="wait for order detail page",
            )
        )
    return commands


def _build_order_list_summary_text(items: List[Dict[str, Any]]) -> str:
    if not items:
        return "주문 목록이 비어 있어요."

    total_count = len(items)
    max_read = 4
    lines = []
    for idx, order in enumerate(items[:max_read], start=1):
        title = order.get("title") or "상품"
        ordered_at = order.get("ordered_at") or ""
        status = order.get("status") or ""
        total_price = order.get("total_price") or ""

        parts = [f"{idx}번 {title}"]
        if ordered_at:
            parts.append(f"주문일 {ordered_at}")
        if status:
            parts.append(f"상태 {status}")
        if total_price:
            parts.append(f"가격 {total_price}")
        lines.append(". ".join(parts))

    intro = f"주문 목록에 {total_count}건이 있어요. 주요 주문을 알려드릴게요."
    tts_text = intro + " " + ". ".join(lines) + "."

    if total_count > max_read:
        remain = total_count - max_read
        tts_text += f" 나머지 {remain}건도 읽어드릴까요?"

    tts_text += " 특정 주문을 보려면 'N번째 주문 상세보기'라고 말씀해 주세요."
    return tts_text


def _is_affirmative(text: str) -> bool:
    keywords = [
        "네", "응", "예", "그래", "그래요", "맞아", "맞아요", "어",
        "읽어", "읽어줘", "읽어주세요", "읽어줄래",
    ]
    return any(word in text for word in keywords)


def _is_negative(text: str) -> bool:
    keywords = [
        "아니", "아니요", "괜찮아", "괜찮아요", "싫어", "됐어", "필요없어", "필요 없어",
    ]
    return any(word in text for word in keywords)


def handle_order_list_action(user_text: str, session: Optional[SessionState]) -> Optional[LLMResponse]:
    if not session or not session.context:
        return None
    current_url = session.current_url or ""
    if not current_url or get_page_type(current_url) != "orderlist":
        return None

    text = (user_text or "").strip()
    if not text:
        return None
    order_list = session.context.get("order_list")
    items: List[Dict[str, Any]] = []
    if isinstance(order_list, dict):
        raw = order_list.get("orders") or order_list.get("items") or order_list.get("order_list")
        if isinstance(raw, list):
            items = [item for item in raw if isinstance(item, dict)]
    elif isinstance(order_list, list):
        items = [item for item in order_list if isinstance(item, dict)]

    if not items:
        return None
    ordinal_index = extract_ordinal_index(text)
    title_match = _find_by_title(items, text)
    has_read_intent = any(keyword in text for keyword in READ_KEYWORDS)
    has_detail_intent = any(keyword in text for keyword in DETAIL_KEYWORDS)

    prompt_pending = bool(session.context.get("order_list_prompt_pending"))
    if prompt_pending:
        if _is_affirmative(text):
            session.context["order_list_prompt_pending"] = False
            summary = _build_order_list_summary_text(items)
            return LLMResponse(
                text=summary,
                commands=[],
                requires_flow=False,
                flow_type=None,
            )
        if _is_negative(text):
            session.context["order_list_prompt_pending"] = False
            return LLMResponse(
                text="알겠습니다. 필요하신 내용을 말씀해 주세요.",
                commands=[],
                requires_flow=False,
                flow_type=None,
            )

    if (
        ordinal_index is None
        and not title_match
        and not has_read_intent
        and not has_detail_intent
    ):
        return None

    if ordinal_index is None and title_match is None and has_read_intent and not has_detail_intent:
        session.context["order_list_prompt_pending"] = False
        summary = _build_order_list_summary_text(items)
        return LLMResponse(
            text=summary,
            commands=[],
            requires_flow=False,
            flow_type=None,
        )

    target = None
    if ordinal_index is not None and 0 <= ordinal_index < len(items):
        target = items[ordinal_index]
    if target is None:
        target = title_match or _find_by_title(items, text)
    if target is None and len(items) == 1:
        target = items[0]

    if not target:
        return None

    commands = _build_detail_commands(target)
    if not commands:
        return None

    session.context["order_list_prompt_pending"] = False
    title = target.get("title") or ""
    label = title or "선택한 주문"

    return LLMResponse(
        text=f"{label} 상세로 이동합니다.",
        commands=commands,
        requires_flow=False,
        flow_type=None,
    )


__all__ = ["handle_order_list_action"]
