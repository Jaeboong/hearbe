# -*- coding: utf-8 -*-
"""
Order detail rules for Coupang.

Applies only on order detail pages.
"""

from typing import Optional

from . import BaseRule, RuleResult
from ..context.context_rules import GeneratedCommand
from ..sites.site_manager import get_selector, get_page_type, get_current_site


class OrderDetailRule(BaseRule):
    """주문 상세 페이지 전용 룰"""

    def check(self, text: str, current_url: str, current_site) -> Optional[RuleResult]:
        if not text:
            return None
        if not _is_coupang_site(current_url, current_site):
            return None

        page_type = get_page_type(current_url) if current_url else None
        if page_type != "orderdetail":
            return None

        normalized = _normalize(text)

        # 배송 조회
        if _contains_any(normalized, ["배송조회", "배송확인", "배송조회해"]):
            selector = get_selector(current_url, "track_delivery") if current_url else None
            commands = _build_click(selector, "배송 조회")
            return RuleResult(
                matched=True,
                commands=commands,
                response_text="배송 조회를 진행합니다.",
                rule_name="orderdetail_track_delivery",
            )

        # 장바구니 담기
        if _contains_any(normalized, ["장바구니담기", "장바구니추가", "장바구니넣"]) or "장바구니" in normalized:
            selector = get_selector(current_url, "add_to_cart") if current_url else None
            commands = _build_click(selector, "장바구니 담기")
            return RuleResult(
                matched=True,
                commands=commands,
                response_text="장바구니에 담겠습니다.",
                rule_name="orderdetail_add_to_cart",
            )

        # 주문/배송 취소
        if _contains_any(normalized, ["주문배송취소", "주문취소", "배송취소", "주문취소해", "취소"]):
            # 주문 상세 페이지 내 버튼 텍스트 기반 클릭
            commands = [
                GeneratedCommand(
                    tool_name="click_text",
                    arguments={"text": "주문 · 배송 취소"},
                    description="주문 · 배송 취소 버튼 클릭",
                )
            ]
            return RuleResult(
                matched=True,
                commands=commands,
                response_text="주문 및 배송 취소로 이동합니다.",
                rule_name="orderdetail_cancel",
            )

        # 주문목록 돌아가기
        if _contains_any(normalized, ["주문목록돌아가기", "주문목록", "목록돌아가기", "주문목록가기"]):
            selector = get_selector(current_url, "back_to_orderlist") if current_url else None
            commands = _build_click(selector, "주문목록 돌아가기")
            return RuleResult(
                matched=True,
                commands=commands,
                response_text="주문목록으로 돌아갑니다.",
                rule_name="orderdetail_back_to_list",
            )

        return None


def _normalize(text: str) -> str:
    return "".join(text.split())


def _contains_any(text: str, keys: list[str]) -> bool:
    return any(k in text for k in keys)


def _build_click(selector: Optional[str], fallback_text: str) -> list[GeneratedCommand]:
    if selector:
        return [
            GeneratedCommand(
                tool_name="click",
                arguments={"selector": selector},
                description=f"{fallback_text} 버튼 클릭",
            )
        ]
    return [
        GeneratedCommand(
            tool_name="click_text",
            arguments={"text": fallback_text},
            description=f"{fallback_text} 텍스트 클릭",
        )
    ]


def _is_coupang_site(current_url: str, current_site) -> bool:
    if current_site and getattr(current_site, "site_id", "") == "coupang":
        return True
    site = get_current_site(current_url) if current_url else None
    return bool(site and getattr(site, "site_id", "") == "coupang")


__all__ = ["OrderDetailRule"]
