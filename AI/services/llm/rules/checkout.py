"""
결제 규칙
"""

from typing import Optional
from . import BaseRule, RuleResult
from ..context.context_rules import (
    CHECKOUT_TRIGGERS,
    GeneratedCommand
)
from ..sites.site_manager import get_selector, get_page_type


class CheckoutRule(BaseRule):
    """결제 규칙: '결제하기', '바로구매' 등"""
    
    def check(self, text: str, current_url: str, current_site) -> Optional[RuleResult]:
        if not any(kw in text for kw in CHECKOUT_TRIGGERS):
            return None

        # 현재 페이지 타입 확인
        page_type = get_page_type(current_url) if current_url else None
        
        # 페이지에 따라 적절한 셀렉터 선택
        selector = None
        button_name = "결제하기"
        
        if page_type == "product":
            # 상품 페이지 → 바로구매 버튼
            selector = get_selector(current_url, "buy_now")
            button_name = "바로구매"
        elif page_type == "checkout":
            # 결제 페이지 → 결제하기 버튼
            selector = get_selector(current_url, "pay_button")
            button_name = "결제하기"
        elif page_type == "cart":
            # 장바구니 페이지 → 구매하기 버튼
            selector = get_selector(current_url, "checkout_button")
            button_name = "구매하기"
        
        # 폴백: 텍스트 기반
        if not selector:
            selector = "button:has-text('결제하기'), button:has-text('바로구매'), button:has-text('구매하기')"
        
        commands = [
            GeneratedCommand(
                tool_name="click",
                arguments={"selector": selector},
                description=f"{button_name} 버튼 클릭"
            ),
            GeneratedCommand(
                tool_name="wait",
                arguments={"ms": 2000},
                description="처리 대기"
            )
        ]

        return RuleResult(
            matched=True,
            commands=commands,
            response_text=f"{button_name}을(를) 진행합니다.",
            rule_name="checkout"
        )
