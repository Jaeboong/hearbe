"""
명령 생성기 모듈

자연어 입력을 MCP 브라우저 자동화 명령으로 변환합니다.
context_rules와 site_manager를 활용하여 컨텍스트 인식 명령을 생성합니다.
"""

import re
import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

# 상위 디렉토리의 모듈 import
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .site_manager import get_site_manager, get_current_site, SiteConfig

logger = logging.getLogger(__name__)


@dataclass
class GeneratedCommand:
    """생성된 MCP 명령"""
    tool_name: str
    arguments: Dict[str, Any]
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "description": self.description
        }


@dataclass
class CommandResult:
    """명령 생성 결과"""
    commands: List[GeneratedCommand]
    response_text: str
    matched_rule: str = ""  # 어떤 규칙으로 매칭되었는지
    requires_flow: bool = False
    flow_type: Optional[str] = None


class CommandGenerator:
    """
    자연어 → MCP 명령 변환기
    
    규칙 기반 + 컨텍스트 인식으로 명령을 생성합니다.
    """
    
    def __init__(self):
        self.site_manager = get_site_manager()
    
    def generate(
        self, 
        user_text: str, 
        current_url: str = ""
    ) -> CommandResult:
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
        
        # 현재 사이트 확인
        current_site = get_current_site(current_url)
        
        # 1. 사이트 접속 명령
        result = self._check_site_access(text)
        if result:
            return result
        
        # 2. 검색 명령
        result = self._check_search(text, current_url, current_site)
        if result:
            return result
        
        # 3. 장바구니 명령
        result = self._check_cart(text, current_url, current_site)
        if result:
            return result
        
        # 4. 로그인 명령
        result = self._check_login(text, current_site, current_url)
        if result:
            return result
        
        # 5. 결제 명령 (Flow Engine 위임)
        result = self._check_checkout(text, current_site)
        if result:
            return result
        
        # 6. 일반 클릭 (텍스트 기반)
        result = self._check_generic_click(text)
        if result:
            return result
        
        # 매칭 없음
        return CommandResult(
            commands=[],
            response_text=f"'{text}' 명령을 어떻게 처리할지 모르겠습니다.",
            matched_rule="none"
        )
    
    def _check_site_access(self, text: str) -> Optional[CommandResult]:
        """사이트 접속 명령 체크"""
        site_keywords = {
            "쿠팡": "coupang",
            "네이버": "naver",
            "11번가": "11st",
        }
        
        for keyword, site_id in site_keywords.items():
            if keyword in text and ("접속" in text or "열어" in text or "가" in text):
                site = self.site_manager.get_site(site_id)
                if site:
                    home_url = site.get_url("home")
                    return CommandResult(
                        commands=[
                            GeneratedCommand(
                                tool_name="goto",
                                arguments={"url": home_url},
                                description=f"{site.name} 접속"
                            ),
                            GeneratedCommand(
                                tool_name="wait",
                                arguments={"ms": 1000},
                                description="페이지 로딩 대기"
                            )
                        ],
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
        
        # 검색어 추출
        match = re.search(r"(.+?)\s*검색", text)
        if not match:
            return None
        
        query = match.group(1).strip()
        
        # 사이트 키워드에서 제거
        for keyword in ["쿠팡", "네이버", "11번가", "에서", "에"]:
            query = query.replace(keyword, "").strip()
        
        if not query:
            return None
        
        # 특정 사이트 지정 확인
        target_site = current_site
        if "쿠팡" in text:
            target_site = self.site_manager.get_site("coupang")
        elif "네이버" in text:
            target_site = self.site_manager.get_site("naver")
        elif "11번가" in text:
            target_site = self.site_manager.get_site("11st")
        
        if not target_site:
            target_site = self.site_manager.get_site("coupang")
        
        commands = []
        
        # 현재 사이트가 다르면 먼저 이동
        if not target_site.matches_domain(current_url):
            home_url = target_site.get_url("home")
            commands.append(GeneratedCommand(
                tool_name="goto",
                arguments={"url": home_url},
                description=f"{target_site.name} 이동"
            ))
            commands.append(GeneratedCommand(
                tool_name="wait",
                arguments={"ms": 1000},
                description="페이지 로딩 대기"
            ))
        
        # 검색 실행
        search_selectors = target_site.selectors.get("search", {})
        input_selector = search_selectors.get("input", "input[name='q']")
        submit_key = search_selectors.get("submit_key", "Enter")
        
        commands.extend([
            GeneratedCommand(
                tool_name="click",
                arguments={"selector": input_selector},
                description="검색창 클릭"
            ),
            GeneratedCommand(
                tool_name="fill",
                arguments={"selector": input_selector, "text": query},
                description=f"'{query}' 입력"
            ),
            GeneratedCommand(
                tool_name="press",
                arguments={"selector": input_selector, "key": submit_key},
                description="검색 실행"
            ),
            GeneratedCommand(
                tool_name="wait",
                arguments={"ms": 1500},
                description="검색 결과 로딩 대기"
            )
        ])
        
        return CommandResult(
            commands=commands,
            response_text=f"'{query}'를 {target_site.name}에서 검색합니다.",
            matched_rule="search"
        )
    
    def _check_cart(
        self, 
        text: str, 
        current_url: str,
        current_site: Optional[SiteConfig]
    ) -> Optional[CommandResult]:
        """장바구니 관련 명령 체크"""
        if "장바구니" not in text:
            return None
        
        # 장바구니 담기
        if any(kw in text for kw in ["담", "추가", "넣"]):
            if current_site:
                selector = current_site.get_selector("product", "add_to_cart")
                if selector:
                    return CommandResult(
                        commands=[
                            GeneratedCommand(
                                tool_name="click",
                                arguments={"selector": selector},
                                description="장바구니 담기 버튼 클릭"
                            ),
                            GeneratedCommand(
                                tool_name="wait",
                                arguments={"ms": 1000},
                                description="처리 대기"
                            )
                        ],
                        response_text="장바구니에 담고 있습니다.",
                        matched_rule="add_to_cart"
                    )
            
            # 폴백: 텍스트로 클릭
            return CommandResult(
                commands=[
                    GeneratedCommand(
                        tool_name="click_text",
                        arguments={"text": "장바구니"},
                        description="장바구니 버튼 찾아서 클릭"
                    )
                ],
                response_text="장바구니에 담고 있습니다.",
                matched_rule="add_to_cart_fallback"
            )
        
        # 장바구니 이동
        if any(kw in text for kw in ["이동", "가", "보", "열"]) or text == "장바구니":
            if current_site:
                cart_url = current_site.get_url("cart")
                if cart_url:
                    return CommandResult(
                        commands=[
                            GeneratedCommand(
                                tool_name="goto",
                                arguments={"url": cart_url},
                                description="장바구니 페이지 이동"
                            )
                        ],
                        response_text="장바구니로 이동합니다.",
                        matched_rule="go_to_cart"
                    )
            
            # 폴백
            return CommandResult(
                commands=[
                    GeneratedCommand(
                        tool_name="click_text",
                        arguments={"text": "장바구니"},
                        description="장바구니 버튼 클릭"
                    )
                ],
                response_text="장바구니로 이동합니다.",
                matched_rule="go_to_cart_fallback"
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
        
        # 이미 로그인 페이지에 있는지 확인
        is_on_login_page = "login" in current_url.lower()
        
        # 로그인 페이지에서 "로그인 버튼 클릭" 또는 "로그인 실행" 요청
        if is_on_login_page and any(kw in text for kw in ["클릭", "실행", "버튼", "하기"]):
            return CommandResult(
                commands=[
                    GeneratedCommand(
                        tool_name="click",
                        arguments={"selector": "._loginSubmitButton, .login__button--submit, button[type='submit']"},
                        description="로그인 버튼 클릭"
                    ),
                    GeneratedCommand(
                        tool_name="wait",
                        arguments={"ms": 2000},
                        description="로그인 처리 대기"
                    )
                ],
                response_text="로그인 버튼을 클릭합니다.",
                matched_rule="login_submit"
            )
        
        # 로그인 페이지로 이동
        if current_site:
            login_url = current_site.get_url("login")
            if login_url:
                return CommandResult(
                    commands=[
                        GeneratedCommand(
                            tool_name="goto",
                            arguments={"url": login_url},
                            description="로그인 페이지 이동"
                        )
                    ],
                    response_text="로그인 페이지로 이동합니다.",
                    matched_rule="login"
                )
        
        return CommandResult(
            commands=[
                GeneratedCommand(
                    tool_name="click_text",
                    arguments={"text": "로그인"},
                    description="로그인 버튼 클릭"
                )
            ],
            response_text="로그인 버튼을 찾고 있습니다.",
            matched_rule="login_fallback"
        )
    
    def _check_checkout(
        self, 
        text: str, 
        current_site: Optional[SiteConfig]
    ) -> Optional[CommandResult]:
        """결제 명령 체크 (Flow Engine 위임)"""
        checkout_keywords = ["결제", "주문", "구매하기", "바로구매"]
        
        if not any(kw in text for kw in checkout_keywords):
            return None
        
        return CommandResult(
            commands=[],
            response_text="결제를 진행하시겠습니까? 결제 과정은 단계별로 안내해 드리겠습니다.",
            matched_rule="checkout_flow",
            requires_flow=True,
            flow_type="checkout"
        )
    
    def _check_generic_click(self, text: str) -> Optional[CommandResult]:
        """일반 클릭 명령 체크"""
        generic_actions = ["클릭", "눌러", "선택"]
        
        if not any(kw in text for kw in generic_actions):
            return None
        
        # 클릭 대상 추출
        target = text
        for kw in generic_actions:
            target = target.replace(kw, "").strip()
        
        if target:
            return CommandResult(
                commands=[
                    GeneratedCommand(
                        tool_name="click_text",
                        arguments={"text": target},
                        description=f"'{target}' 클릭"
                    )
                ],
                response_text=f"'{target}'을 클릭합니다.",
                matched_rule="generic_click"
            )
        
        return None


# 편의 함수
def generate_commands(user_text: str, current_url: str = "") -> CommandResult:
    """명령 생성 편의 함수"""
    generator = CommandGenerator()
    return generator.generate(user_text, current_url)
