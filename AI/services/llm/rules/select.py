"""
검색 결과 선택 규칙

검색 결과 페이지에서 "선택/열어" 등의 요청은 재검색 없이 클릭으로 처리합니다.
"""

from typing import Optional
from . import BaseRule, RuleResult
from ..context_rules import (
    build_click_text_command,
    build_click_command,
    build_wait_command,
)
from ..site_manager import get_page_type


SELECTION_TRIGGERS = ["선택", "골라", "고르", "열어", "눌러", "클릭", "열어줘", "열어봐"]
FILLER_WORDS = ["해줘", "해주세요", "해", "좀", "줘", "봐", "봐줘", "상품", "결과"]


def _extract_selection_target(text: str) -> str:
    target = text
    for kw in SELECTION_TRIGGERS:
        target = target.replace(kw, "").strip()
    for kw in FILLER_WORDS:
        target = target.replace(kw, "").strip()
    return target


class SearchSelectRule(BaseRule):
    """검색 결과 페이지 선택 규칙"""

    def check(self, text: str, current_url: str, current_site) -> Optional[RuleResult]:
        if not current_url:
            return None
        if not any(kw in text for kw in SELECTION_TRIGGERS):
            return None

        page_type = get_page_type(current_url)
        if page_type != "search":
            return None

        target = _extract_selection_target(text)

        if target:
            commands = [
                build_click_text_command(target, f"검색 결과에서 '{target}' 선택"),
                build_wait_command(1500, "상품 페이지 로딩 대기"),
            ]
            return RuleResult(
                matched=True,
                commands=commands,
                response_text=f"검색 결과에서 '{target}'을 선택합니다.",
                rule_name="search_select"
            )

        selector = None
        if current_site:
            selector = current_site.get_selector("search", "product_item")

        if selector:
            commands = [
                build_click_command(selector, "검색 결과 첫 상품 선택"),
                build_wait_command(1500, "상품 페이지 로딩 대기"),
            ]
            return RuleResult(
                matched=True,
                commands=commands,
                response_text="검색 결과에서 첫 상품을 선택합니다.",
                rule_name="search_select"
            )

        return None
