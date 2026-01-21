"""
명령 생성기 모듈

자연어 입력을 MCP 브라우저 자동화 명령으로 변환합니다.
context_rules의 빌더 함수를 사용하여 명령을 생성합니다.
"""

import logging
from typing import List, Optional
from dataclasses import dataclass

from .site_manager import get_site_manager, get_current_site, SiteConfig
from .context_rules import (
    # 데이터 클래스
    GeneratedCommand,
    # 상수
    SITE_KEYWORDS,
    SITE_ACCESS_TRIGGERS,
    CART_ADD_TRIGGERS,
    CART_GO_TRIGGERS,
    LOGIN_SUBMIT_TRIGGERS,
    CHECKOUT_TRIGGERS,
    CLICK_TRIGGERS,
    # 빌더 함수
    build_site_access_commands,
    build_search_with_navigation_commands,
    build_add_to_cart_commands,
    build_go_to_cart_commands,
    build_login_page_commands,
    build_login_submit_commands,
    build_generic_click_commands,
    # 유틸리티
    extract_search_query,
    detect_target_site,
    extract_click_target,
)

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """명령 생성 결과"""
    commands: List[GeneratedCommand]
    response_text: str
    matched_rule: str = ""
    requires_flow: bool = False
    flow_type: Optional[str] = None


class CommandGenerator:
    """
    자연어 → MCP 명령 변환기

    규칙 기반 + 컨텍스트 인식으로 명령을 생성합니다.
    실제 명령 생성은 context_rules의 빌더 함수에 위임합니다.
    """

    def __init__(self):
        self.site_manager = get_site_manager()

    def generate(self, user_text: str, current_url: str = "") -> CommandResult:
        """
        자연어를 MCP 명령으로 변환

        Args:
            user_text: 사용자 입력 텍스트
            current_url: 현재 브라우저 URL

        Returns:
            CommandResult: 생성된 명령 및 응답
        """
        text = user_text.strip()
        if not text:
            return CommandResult(
                commands=[],
                response_text="명령을 입력해주세요.",
                matched_rule="empty"
            )

        current_site = get_current_site(current_url)

        # 규칙 체크 순서대로 실행
        checkers = [
            lambda: self._check_site_access(text),
            lambda: self._check_search(text, current_url, current_site),
            lambda: self._check_cart(text, current_site),
            lambda: self._check_login(text, current_site, current_url),
            lambda: self._check_checkout(text, current_site),
            lambda: self._check_generic_click(text),
        ]

        for checker in checkers:
            result = checker()
            if result:
                return result

        return CommandResult(
            commands=[],
            response_text=f"'{text}' 명령을 어떻게 처리할지 모르겠습니다.",
            matched_rule="none"
        )

    def _check_site_access(self, text: str) -> Optional[CommandResult]:
        """사이트 접속 명령 체크"""
        for keyword, site_id in SITE_KEYWORDS.items():
            if keyword in text and any(t in text for t in SITE_ACCESS_TRIGGERS):
                site = self.site_manager.get_site(site_id)
                if site:
                    return CommandResult(
                        commands=build_site_access_commands(site),
                        response_text=f"{site.name}에 접속합니다.",
                        matched_rule="site_access"
                    )
        return None

    def _check_search(
        self,
        text: str,
        current_url: str,
        current_site: Optional[SiteConfig]
    ) -> Optional[CommandResult]:
        """검색 명령 체크"""
        if "검색" not in text:
            return None

        query = extract_search_query(text)
        if not query:
            return None

        target_site = detect_target_site(text, self.site_manager, current_site)
        if not target_site:
            return None

        needs_navigation = not target_site.matches_domain(current_url)
        commands = build_search_with_navigation_commands(target_site, query, needs_navigation)

        return CommandResult(
            commands=commands,
            response_text=f"'{query}'를 {target_site.name}에서 검색합니다.",
            matched_rule="search"
        )

    def _check_cart(
        self,
        text: str,
        current_site: Optional[SiteConfig]
    ) -> Optional[CommandResult]:
        """장바구니 관련 명령 체크"""
        if "장바구니" not in text:
            return None

        # 장바구니 담기
        if any(kw in text for kw in CART_ADD_TRIGGERS):
            commands = build_add_to_cart_commands(current_site)
            matched_rule = "add_to_cart" if current_site else "add_to_cart_fallback"
            return CommandResult(
                commands=commands,
                response_text="장바구니에 담고 있습니다.",
                matched_rule=matched_rule
            )

        # 장바구니 이동
        if any(kw in text for kw in CART_GO_TRIGGERS) or text == "장바구니":
            commands = build_go_to_cart_commands(current_site)
            matched_rule = "go_to_cart" if current_site else "go_to_cart_fallback"
            return CommandResult(
                commands=commands,
                response_text="장바구니로 이동합니다.",
                matched_rule=matched_rule
            )

        return None

    def _check_login(
        self,
        text: str,
        current_site: Optional[SiteConfig],
        current_url: str = ""
    ) -> Optional[CommandResult]:
        """로그인 명령 체크"""
        if "로그인" not in text:
            return None

        is_on_login_page = "login" in current_url.lower()

        # 로그인 페이지에서 버튼 클릭 요청
        if is_on_login_page and any(kw in text for kw in LOGIN_SUBMIT_TRIGGERS):
            return CommandResult(
                commands=build_login_submit_commands(),
                response_text="로그인 버튼을 클릭합니다.",
                matched_rule="login_submit"
            )

        # 로그인 페이지로 이동
        commands = build_login_page_commands(current_site)
        matched_rule = "login" if current_site else "login_fallback"
        response = "로그인 페이지로 이동합니다." if current_site else "로그인 버튼을 찾고 있습니다."

        return CommandResult(
            commands=commands,
            response_text=response,
            matched_rule=matched_rule
        )

    def _check_checkout(self, text: str, current_site: Optional[SiteConfig] = None) -> Optional[CommandResult]:
        """결제 명령 체크 - CheckoutFlowManager 사용"""
        if not any(kw in text for kw in CHECKOUT_TRIGGERS):
            return None
        
        # CheckoutFlowManager에서 설정 로드
        from services.flow.checkout_flow import get_checkout_manager
        
        manager = get_checkout_manager()
        
        # 현재 사이트 확인
        site_id = current_site.site_id if current_site else "coupang"
        config = manager.get_config(site_id)
        
        if not config:
            # 설정이 없으면 Flow Engine 위임
            return CommandResult(
                commands=[],
                response_text="결제를 진행하시겠습니까? 결제 과정은 단계별로 안내해 드리겠습니다.",
                matched_rule="checkout_flow",
                requires_flow=True,
                flow_type="checkout"
            )
        
        # 첫 번째 단계 명령 생성
        first_step = manager.get_next_step(site_id)
        if not first_step:
            return None
        
        cmd_dicts = manager.generate_step_commands(first_step)
        commands = [
            GeneratedCommand(
                tool_name=cmd["tool_name"],
                arguments=cmd["arguments"],
                description=cmd.get("description", "")
            )
            for cmd in cmd_dicts
        ]
        
        return CommandResult(
            commands=commands,
            response_text=first_step.prompt or f"{first_step.name}을(를) 진행합니다.",
            matched_rule="checkout_step",
            requires_flow=True,
            flow_type="checkout"
        )

    def _check_generic_click(self, text: str) -> Optional[CommandResult]:
        """일반 클릭 명령 체크"""
        if not any(kw in text for kw in CLICK_TRIGGERS):
            return None

        target = extract_click_target(text)
        if not target:
            return None

        return CommandResult(
            commands=build_generic_click_commands(target),
            response_text=f"'{target}'을 클릭합니다.",
            matched_rule="generic_click"
        )


# 편의 함수
def generate_commands(user_text: str, current_url: str = "") -> CommandResult:
    """명령 생성 편의 함수"""
    generator = CommandGenerator()
    return generator.generate(user_text, current_url)
