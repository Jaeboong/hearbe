# -*- coding: utf-8 -*-
"""
Order detail handler.

Extracts and announces order detail info on order detail pages,
and answers user questions using extracted data.
"""

import asyncio
import json
import logging
import re
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from core.interfaces import MCPCommand
from api.order.order_client import OrderClient, OrderItem, COUPANG_PLATFORM_ID
from services.llm.generators.llm_generator import LLMGenerator

logger = logging.getLogger(__name__)

CTX_ORDER_DETAIL_LAST_URL = "order_detail_last_url"
CTX_ORDER_DETAIL_REQUEST_TYPE = "order_detail_request_type"
CTX_ORDER_DETAIL_PENDING_QUESTION = "order_detail_pending_question"
CTX_ORDER_DETAIL_REQUESTED = "order_detail_requested"
CTX_ORDER_DETAIL_DATA = "order_detail_data"
CTX_ORDER_DETAIL_API_SENT_ID = "order_detail_api_sent_id"
CTX_ORDER_DETAIL_API_RETRY = "order_detail_api_retry"
CTX_ORDER_DETAIL_API_PENDING_ID = "order_detail_api_pending_id"

REQUEST_SUMMARY = "summary"
REQUEST_QUESTION = "question"

ORDER_DETAIL_PROMPT = "주문 상세 페이지에 있는 정보 중 어떤걸 읽어드릴까요?"
ORDER_DETAIL_LOADING_TTS = "주문 상세 정보를 불러오는 중입니다. 잠시만 기다려주세요."
ORDER_DETAIL_NOT_FOUND_TTS = "주문 상세 페이지에서 해당 정보를 찾지 못했어요."

ACTION_LABELS = [
    "장바구니 담기",
    "배송 조회",
    "주문, 배송 취소",
    "주문내역 삭제",
    "주문목록 돌아가기",
]


class OrderDetailHandler:
    def __init__(self, sender, session_manager, llm_generator: Optional[LLMGenerator] = None):
        self._sender = sender
        self._session = session_manager
        self._llm = llm_generator or LLMGenerator()

    async def handle_page_update(self, session_id: str, current_url: str) -> bool:
        if not self._sender or not self._session:
            return False
        if not _is_order_detail_url(current_url):
            return False

        last_url = self._session.get_context(session_id, CTX_ORDER_DETAIL_LAST_URL)
        if last_url == current_url and self._session.get_context(session_id, CTX_ORDER_DETAIL_DATA):
            return False

        self._session.set_context(session_id, CTX_ORDER_DETAIL_LAST_URL, current_url)
        self._session.set_context(session_id, CTX_ORDER_DETAIL_REQUEST_TYPE, REQUEST_SUMMARY)
        self._session.set_context(session_id, CTX_ORDER_DETAIL_PENDING_QUESTION, None)
        self._session.set_context(session_id, CTX_ORDER_DETAIL_REQUESTED, True)
        await self._sender.send_tool_calls(
            session_id,
            [
                MCPCommand(
                    tool_name="extract_order_detail",
                    arguments={},
                    description="extract order detail",
                )
            ],
        )
        return True

    async def ensure_context(self, session_id: str, current_url: str, session) -> bool:
        if not self._sender or not self._session:
            return False
        if not current_url or not _is_order_detail_url(current_url):
            return False
        if self._session.get_context(session_id, CTX_ORDER_DETAIL_DATA):
            return False
        if self._session.get_context(session_id, CTX_ORDER_DETAIL_REQUESTED):
            return False

        self._session.set_context(session_id, CTX_ORDER_DETAIL_REQUEST_TYPE, REQUEST_SUMMARY)
        self._session.set_context(session_id, CTX_ORDER_DETAIL_PENDING_QUESTION, None)
        self._session.set_context(session_id, CTX_ORDER_DETAIL_REQUESTED, True)
        await self._sender.send_tool_calls(
            session_id,
            [
                MCPCommand(
                    tool_name="extract_order_detail",
                    arguments={},
                    description="extract order detail",
                )
            ],
        )
        return True

    async def handle_user_text(self, session_id: str, text: str) -> bool:
        if not self._sender or not self._session:
            return False
        if not text:
            return False
        session = self._session.get_session(session_id)
        current_url = session.current_url if session else ""
        if not _is_order_detail_url(current_url):
            return False

        if self._session.get_context(session_id, CTX_ORDER_DETAIL_REQUESTED):
            await self._sender.send_tts_response(session_id, ORDER_DETAIL_LOADING_TTS)
            return True

        if _is_order_detail_question(text):
            self._session.set_context(session_id, CTX_ORDER_DETAIL_REQUEST_TYPE, REQUEST_QUESTION)
            self._session.set_context(session_id, CTX_ORDER_DETAIL_PENDING_QUESTION, text)
            self._session.set_context(session_id, CTX_ORDER_DETAIL_REQUESTED, True)
            await self._sender.send_tool_calls(
                session_id,
                [
                    MCPCommand(
                        tool_name="extract_order_detail",
                        arguments={},
                        description="extract order detail",
                    )
                ],
            )
            return True

        if _is_order_detail_read_request(text):
            self._session.set_context(session_id, CTX_ORDER_DETAIL_REQUEST_TYPE, REQUEST_SUMMARY)
            self._session.set_context(session_id, CTX_ORDER_DETAIL_PENDING_QUESTION, None)
            self._session.set_context(session_id, CTX_ORDER_DETAIL_REQUESTED, True)
            await self._sender.send_tool_calls(
                session_id,
                [
                    MCPCommand(
                        tool_name="extract_order_detail",
                        arguments={},
                        description="extract order detail",
                    )
                ],
            )
            return True

        return False

    async def handle_mcp_result(self, session_id: str, data: Dict[str, Any]) -> bool:
        if not self._sender or not self._session:
            return False
        tool_name = data.get("tool_name")
        if tool_name == "get_user_session":
            result = data.get("result") or {}
            if not isinstance(result, dict):
                return False
            access_token = result.get("access_token") or result.get("accessToken") or ""
            if access_token:
                self._session.set_context(session_id, "access_token", access_token)
            user_id = result.get("user_id") or result.get("userId") or ""
            if user_id:
                self._session.set_context(session_id, "user_id", str(user_id))
            user_type = result.get("user_type") or result.get("userType") or ""
            if user_type:
                self._session.set_context(session_id, "user_type", str(user_type))
            if access_token:
                self._session.set_context(session_id, CTX_ORDER_DETAIL_API_RETRY, False)
                pending_id = self._session.get_context(session_id, CTX_ORDER_DETAIL_API_PENDING_ID)
                if pending_id:
                    self._session.set_context(session_id, CTX_ORDER_DETAIL_API_PENDING_ID, None)
                    order_data = self._session.get_context(session_id, CTX_ORDER_DETAIL_DATA) or {}
                    await self._send_order_to_backend(session_id, str(pending_id), order_data, force_token=access_token)
            return True
        if tool_name != "extract_order_detail":
            return False

        result = data.get("result") or {}
        page_url = _resolve_page_url(self._session, session_id, data)
        if not _is_order_detail_url(page_url):
            return False

        if not self._session.get_context(session_id, CTX_ORDER_DETAIL_REQUESTED):
            return False
        self._session.set_context(session_id, CTX_ORDER_DETAIL_REQUESTED, False)

        order_data = result.get("order_detail") if isinstance(result, dict) else None
        if not isinstance(order_data, dict):
            order_data = {}

        # Do not store order_id in order detail data to avoid reading it out.

        self._session.set_context(session_id, CTX_ORDER_DETAIL_DATA, order_data)
        order_id = _extract_order_id_from_order_detail_url(page_url)
        if order_id:
            sent = self._session.get_context(session_id, CTX_ORDER_DETAIL_API_SENT_ID)
            if sent != order_id:
                asyncio.create_task(self._send_order_to_backend(session_id, order_id, order_data))

        request_type = self._session.get_context(session_id, CTX_ORDER_DETAIL_REQUEST_TYPE, REQUEST_SUMMARY)
        if request_type == REQUEST_QUESTION:
            question = self._session.get_context(session_id, CTX_ORDER_DETAIL_PENDING_QUESTION) or ""
            answer = await self._ask_order_detail_llm(question, order_data, page_url)
            await self._sender.send_tts_response(session_id, answer)
            return True

        summary = _build_order_detail_summary(order_data)
        actions = _build_order_detail_actions(order_data)
        await self._sender.send_tts_response(session_id, summary)
        await self._sender.send_tts_response(session_id, actions)
        await self._sender.send_tts_response(session_id, ORDER_DETAIL_PROMPT)
        return True

    def cleanup_session(self, session_id: str) -> None:
        if not self._session:
            return
        self._session.set_context(session_id, CTX_ORDER_DETAIL_LAST_URL, None)
        self._session.set_context(session_id, CTX_ORDER_DETAIL_REQUEST_TYPE, None)
        self._session.set_context(session_id, CTX_ORDER_DETAIL_PENDING_QUESTION, None)
        self._session.set_context(session_id, CTX_ORDER_DETAIL_REQUESTED, None)
        self._session.set_context(session_id, CTX_ORDER_DETAIL_DATA, None)
        self._session.set_context(session_id, CTX_ORDER_DETAIL_API_SENT_ID, None)
        self._session.set_context(session_id, CTX_ORDER_DETAIL_API_RETRY, None)
        self._session.set_context(session_id, CTX_ORDER_DETAIL_API_PENDING_ID, None)

    async def _send_order_to_backend(
        self,
        session_id: str,
        order_id: str,
        order_data: Dict[str, Any],
        force_token: Optional[str] = None,
    ) -> None:
        if not self._session:
            return
        token = force_token or _get_access_token(self._session, session_id)
        if not token:
            retry = bool(self._session.get_context(session_id, CTX_ORDER_DETAIL_API_RETRY))
            if not retry:
                self._session.set_context(session_id, CTX_ORDER_DETAIL_API_RETRY, True)
                self._session.set_context(session_id, CTX_ORDER_DETAIL_API_PENDING_ID, order_id)
                await self._sender.send_tool_calls(
                    session_id,
                    [
                        MCPCommand(
                            tool_name="get_user_session",
                            arguments={},
                            description="get user session from localStorage",
                        )
                    ],
                )
                logger.info("Order API token fetch requested: session=%s", session_id)
                return
            logger.info("Order API skipped: missing access token after retry (session=%s)", session_id)
            return

        items = _build_order_items(order_data)
        if not items:
            logger.warning("Order API skipped: no items extracted (session=%s)", session_id)
            return

        client = OrderClient(jwt_token=token)
        result = await client.create_order(items=items, platform_id=COUPANG_PLATFORM_ID)
        if result.get("success"):
            self._session.set_context(session_id, CTX_ORDER_DETAIL_API_SENT_ID, order_id)
            logger.info(
                "Order API sent: session=%s order_id=%s items=%d",
                session_id,
                order_id,
                len(items),
            )
        else:
            logger.warning(
                "Order API failed: session=%s order_id=%s error=%s",
                session_id,
                order_id,
                result.get("error"),
            )

    async def _ask_order_detail_llm(self, question: str, order_data: Dict[str, Any], page_url: str) -> str:
        if not question:
            return ORDER_DETAIL_NOT_FOUND_TTS
        data_text = json.dumps(_prune_data(order_data), ensure_ascii=False)
        data_text = _truncate_text(data_text, 12000)
        system_prompt = (
            "당신은 한국어 쇼핑 도우미입니다. 아래 ORDER_DETAIL_DATA만 근거로 "
            "사용자의 질문에 간결하게 답하세요. 정보가 없으면 "
            "'주문 상세 페이지에서 해당 정보를 찾지 못했어요.'라고 말하세요. "
            "반드시 JSON 객체로만 답하세요. 형식: {\"response\": \"...\", \"commands\": []}"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"ORDER_DETAIL_DATA:\n{data_text}"},
            {"role": "user", "content": question},
        ]
        result = await self._llm.generate_with_messages(messages, page_url)
        return result.response_text or ORDER_DETAIL_NOT_FOUND_TTS


def _resolve_page_url(session_manager, session_id: str, data: Dict[str, Any]) -> str:
    page_data = data.get("page_data") if isinstance(data, dict) else None
    url = page_data.get("url") if isinstance(page_data, dict) else None
    result = data.get("result") if isinstance(data, dict) else None
    if not url and isinstance(result, dict):
        url = result.get("current_url") or result.get("page_url") or result.get("url")
    if not url and session_manager:
        session = session_manager.get_session(session_id)
        if session:
            url = session.current_url
    return url or ""


def _is_order_detail_url(url: str) -> bool:
    if not url:
        return False
    try:
        parsed = urlparse(url)
        host = (parsed.netloc or "").lower()
        path = parsed.path or ""
        return "mc.coupang.com" in host and bool(re.search(r"/ssr/desktop/order/\d+", path))
    except Exception:
        return False


def _extract_order_id_from_order_detail_url(url: str) -> str:
    if not url:
        return ""
    try:
        match = re.search(r"/ssr/desktop/order/(\d+)", url)
        return match.group(1) if match else ""
    except Exception:
        return ""

def _get_access_token(session_manager, session_id: str) -> str:
    token_keys = [
        "access_token",
        "jwt_token",
        "api_access_token",
        "Authorization",
        "authorization",
        "auth_token",
    ]
    for key in token_keys:
        value = session_manager.get_context(session_id, key)
        if isinstance(value, str) and value.strip():
            token = value.strip()
            if token.lower().startswith("bearer "):
                token = token[7:].strip()
            return token
    return ""


def _coerce_int(value: Any, default: int = 1) -> int:
    if value is None:
        return default
    if isinstance(value, int):
        return value
    try:
        cleaned = re.sub(r"[^\d]", "", str(value))
        if not cleaned:
            return default
        return int(cleaned)
    except Exception:
        return default


def _coerce_price(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    try:
        cleaned = re.sub(r"[^\d]", "", str(value))
        if not cleaned:
            return None
        return int(cleaned)
    except Exception:
        return None


def _build_order_items(order_data: Dict[str, Any]):
    items = []
    raw_items = order_data.get("items") if isinstance(order_data, dict) else None
    if not isinstance(raw_items, list):
        return items
    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        name = raw.get("product_name") or raw.get("vendor_item_name") or raw.get("name") or ""
        name = str(name).strip()
        if not name:
            continue
        price = _coerce_price(raw.get("discounted_unit_price"))
        if price is None:
            price = _coerce_price(raw.get("unit_price"))
        if price is None:
            continue
        quantity = _coerce_int(raw.get("quantity"), default=1)
        url = raw.get("product_url") or raw.get("url") or ""
        img_url = raw.get("img_url") or raw.get("image") or ""
        deliver_url = raw.get("deliver_url") or raw.get("tracking_url") or ""
        items.append(
            OrderItem(
                name=name,
                price=price,
                quantity=quantity,
                url=url or None,
                img_url=img_url or None,
                deliver_url=deliver_url or None,
            )
        )
    return items


def _is_order_detail_question(text: str) -> bool:
    if not text:
        return False
    keywords = [
        "주문",
        "배송",
        "결제",
        "금액",
        "상품",
        "받는",
        "주소",
        "상태",
        "도착",
        "언제",
        "어디",
        "뭐",
        "정보",
        "내역",
        "상세",
        "읽어",
        "알려",
        "보여",
    ]
    return any(word in text for word in keywords)


def _is_order_detail_read_request(text: str) -> bool:
    if not text:
        return False
    patterns = [
        "주문 상세 읽어",
        "주문 상세 알려",
        "주문 상세 정보",
        "주문 정보",
        "주문 내역",
    ]
    return any(pat in text for pat in patterns)


def _build_order_detail_summary(data: Dict[str, Any]) -> str:
    order = data.get("order") or {}
    text = data.get("text") or {}
    items = data.get("items") or []
    payment = data.get("payment") or {}

    title = order.get("title") or (items[0].get("product_name") if items else "") or ""
    status = text.get("status") or ""
    eta = text.get("eta") or ""
    total = _format_won(payment.get("total_payed_amount") or text.get("total_price"))

    parts = ["주문 상세 정보를 안내합니다."]
    if status:
        parts.append(f"현재 상태는 {status}입니다.")
    if eta:
        parts.append(f"도착 예정은 {eta}입니다.")
    if title:
        parts.append(f"상품은 {title}입니다.")
    if total:
        parts.append(f"결제금액은 {total}입니다.")
    return " ".join(parts)


def _build_order_detail_actions(data: Dict[str, Any]) -> str:
    actions = data.get("actions") or list(ACTION_LABELS)
    action_text = ", ".join(actions)
    return f"가능한 작업은 {action_text} 입니다."


def _format_won(value: Any) -> str:
    if value is None:
        return ""
    try:
        if isinstance(value, str):
            cleaned = re.sub(r"[^\d]", "", value)
            if not cleaned:
                return ""
            value = int(cleaned)
        return f"{int(value):,}원"
    except Exception:
        return ""


def _truncate_text(text: str, limit: int) -> str:
    if not text:
        return ""
    return text if len(text) <= limit else text[:limit] + "..."


def _prune_data(obj: Any, depth: int = 0, max_depth: int = 4) -> Any:
    if depth >= max_depth:
        if isinstance(obj, dict):
            return {"_summary": f"{len(obj)} keys"}
        if isinstance(obj, list):
            return {"_summary": f"{len(obj)} items"}
        return obj
    if isinstance(obj, dict):
        pruned: Dict[str, Any] = {}
        for idx, (key, value) in enumerate(obj.items()):
            if idx >= 30:
                pruned["_truncated"] = True
                break
            pruned[key] = _prune_data(value, depth + 1, max_depth)
        return pruned
    if isinstance(obj, list):
        return [_prune_data(item, depth + 1, max_depth) for item in obj[:10]]
    if isinstance(obj, str):
        return obj if len(obj) <= 200 else obj[:200] + "..."
    return obj


__all__ = [
    "OrderDetailHandler",
    "ORDER_DETAIL_PROMPT",
    "ORDER_DETAIL_LOADING_TTS",
    "ORDER_DETAIL_NOT_FOUND_TTS",
    "CTX_ORDER_DETAIL_DATA",
]
