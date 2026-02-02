from __future__ import annotations

import re
from typing import Optional, Dict, Any, List, Tuple

from core.interfaces import LLMResponse, MCPCommand, SessionState
from core.korean_numbers import extract_ordinal_index
from .selection_extract import build_product_extract_command
from ...sites.site_manager import get_page_type


_OPTION_KEYWORDS = (
    "옵션",
    "수량",
    "색상",
    "사이즈",
    "크기",
    "용량",
    "중량",
    "팩",
    "개",
    "변경",
    "바꿔",
    "바꾸",
    "선택",
    "고르",
    "교체",
    "수정",
)

_PURCHASE_KEYWORDS = (
    "구매",
    "주문",
    "담기",
    "결제",
    "장바구니",
    "카트",
)


def select_option_from_detail(
    user_text: str,
    session: Optional[SessionState]
) -> Optional[LLMResponse]:
    if not session or not session.context:
        return None

    current_url = session.current_url or ""
    if current_url and get_page_type(current_url) != "product":
        return None

    detail = session.context.get("product_detail")
    if not isinstance(detail, dict) or not detail:
        return None

    options_list = detail.get("options_list")
    if not isinstance(options_list, dict) or not options_list:
        return None

    target = user_text.strip()
    if not target:
        return None

    if not _is_option_request(target):
        return None

    candidates = _flatten_options(options_list)
    if not candidates:
        return None

    ordinal_index = extract_ordinal_index(target.lower())
    if ordinal_index is not None:
        keys = {key for key, _, _ in candidates}
        if len(keys) != 1:
            ordinal_index = None
    if ordinal_index is not None:
        ordinal_match = _select_by_ordinal(candidates, ordinal_index)
        if ordinal_match:
            key, name, _ = ordinal_match
            return _build_option_click_response(name, key, detail, session)

    best = _select_by_text_match(target, candidates)
    if not best:
        return None

    key, name, _ = best
    return _build_option_click_response(name, key, detail, session)


def _is_option_request(text: str) -> bool:
    lowered = text.lower()
    if any(keyword in lowered for keyword in _PURCHASE_KEYWORDS):
        return False
    return any(keyword in lowered for keyword in _OPTION_KEYWORDS)


def _flatten_options(options_list: Dict[str, Any]) -> List[Tuple[str, str, bool]]:
    flattened: List[Tuple[str, str, bool]] = []
    for key, items in options_list.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            if not name:
                continue
            selected = bool(item.get("selected"))
            flattened.append((key, str(name), selected))
    return flattened


def _select_by_ordinal(
    candidates: List[Tuple[str, str, bool]],
    ordinal_index: int
) -> Optional[Tuple[str, str, bool]]:
    if ordinal_index < 0 or ordinal_index >= len(candidates):
        return None
    return candidates[ordinal_index]


def _select_by_text_match(
    user_text: str,
    candidates: List[Tuple[str, str, bool]]
) -> Optional[Tuple[str, str, bool]]:
    query = _normalize(user_text)
    if not query:
        return None

    tokens = _extract_tokens(user_text)
    best_score = 0
    best_candidate: Optional[Tuple[str, str, bool]] = None

    for key, name, selected in candidates:
        candidate_norm = _normalize(name)
        if not candidate_norm:
            continue
        score = 0
        matched = False
        if candidate_norm in query or query in candidate_norm:
            score += 100
            matched = True
        for token in tokens:
            if token and token in name:
                score += 10
                matched = True
        if matched:
            score += min(len(candidate_norm), 30)
        if score > best_score:
            best_score = score
            best_candidate = (key, name, selected)

    return best_candidate if best_score > 0 else None


def _normalize(text: str) -> str:
    cleaned = text.lower().replace("×", "x")
    return re.sub(r"[^0-9a-zA-Z가-힣]+", "", cleaned)


def _extract_tokens(text: str) -> List[str]:
    return re.findall(r"\d+(?:[\.,]\d+)?(?:[a-zA-Z가-힣%]+)?", text)


def _build_option_click_response(
    option_name: str,
    key: str,
    detail: Dict[str, Any],
    session: SessionState
) -> Optional[LLMResponse]:
    if not option_name:
        return None

    current_options = detail.get("options")
    if isinstance(current_options, dict):
        current_value = current_options.get(key)
        if current_value and option_name in str(current_value):
            return LLMResponse(
                text=f"이미 선택된 옵션입니다: {option_name}",
                commands=[],
                requires_flow=False,
                flow_type=None,
            )

    selector = _build_option_selector(option_name)
    commands = [
        MCPCommand(
            tool_name="click",
            arguments={"selector": selector},
            description=f"select option '{option_name}' within option table"
        ),
        MCPCommand(
            tool_name="wait",
            arguments={"ms": 800},
            description="wait for option update"
        ),
    ]
    extract_command = build_product_extract_command(session)
    if extract_command:
        commands.append(extract_command)

    return LLMResponse(
        text=f"옵션을 변경합니다: {option_name}",
        commands=commands,
        requires_flow=False,
        flow_type=None,
    )


def _build_option_selector(option_name: str) -> str:
    safe_text = option_name.replace('"', '\\"')
    return (
        '.option-table-v2 '
        f'.option-table-list__option:has(.option-table-list__option-name:has-text("{safe_text}"))'
        f', .custom-scrollbar .select-item:has-text("{safe_text}")'
    )
