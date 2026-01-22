"""
로그인 규칙
"""

from typing import Optional
from . import BaseRule, RuleResult
from ..context_rules import (
    LOGIN_SUBMIT_TRIGGERS,
    build_login_page_commands,
    build_login_submit_commands
)


class LoginRule(BaseRule):
    """로그인 규칙: '로그인', '로그인 버튼 클릭' 등"""
    
    def check(self, text: str, current_url: str, current_site) -> Optional[RuleResult]:
        if "로그인" not in text:
            return None

        # 로그인 페이지 이동
        if any(kw in ["이동", "가", "열"] for kw in text.split()):
            commands = build_login_page_commands(current_site)
            return RuleResult(
                matched=True,
                commands=commands,
                response_text="로그인 페이지로 이동합니다.",
                rule_name="login_page"
            )

        # 로그인 버튼 클릭
        if any(kw in text for kw in LOGIN_SUBMIT_TRIGGERS):
            commands = build_login_submit_commands()
            return RuleResult(
                matched=True,
                commands=commands,
                response_text="로그인 버튼을 클릭합니다.",
                rule_name="login_submit"
            )

        return None
