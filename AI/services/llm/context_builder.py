"""
LLM 프롬프트용 컨텍스트 빌더

현재 페이지 정보, 대화 기록, 사용 가능한 명령어를 프롬프트로 구성합니다.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional

from .site_manager import SiteConfig, get_site_manager


# =============================================================================
# 데이터 클래스
# =============================================================================

@dataclass
class PageContext:
    """현재 페이지 컨텍스트"""
    site_name: str
    page_type: str  # home, search, product, cart, login
    available_actions: List[str]
    selectors: Dict[str, str]


# =============================================================================
# 사용 가능한 명령어 스펙
# =============================================================================

AVAILABLE_COMMANDS = {
    "goto": {
        "description": "URL로 페이지 이동",
        "args": {"url": "이동할 URL (문자열)"},
        "example": '{"action": "goto", "args": {"url": "https://www.coupang.com/"}, "desc": "쿠팡 홈으로 이동"}'
    },
    "click": {
        "description": "CSS 셀렉터로 요소 클릭",
        "args": {"selector": "CSS 셀렉터"},
        "example": '{"action": "click", "args": {"selector": "#login-btn"}, "desc": "로그인 버튼 클릭"}'
    },
    "fill": {
        "description": "입력 필드에 텍스트 입력",
        "args": {"selector": "CSS 셀렉터", "text": "입력할 텍스트"},
        "example": '{"action": "fill", "args": {"selector": "input[name=q]", "text": "생수"}, "desc": "검색어 입력"}'
    },
    "press": {
        "description": "키보드 키 입력",
        "args": {"selector": "CSS 셀렉터", "key": "키 이름 (Enter, Tab 등)"},
        "example": '{"action": "press", "args": {"selector": "input", "key": "Enter"}, "desc": "엔터 키 입력"}'
    },
    "wait": {
        "description": "지정된 시간 대기",
        "args": {"ms": "밀리초 (숫자)"},
        "example": '{"action": "wait", "args": {"ms": 1000}, "desc": "1초 대기"}'
    },
    "click_text": {
        "description": "텍스트로 요소를 찾아 클릭",
        "args": {"text": "찾을 텍스트"},
        "example": '{"action": "click_text", "args": {"text": "장바구니"}, "desc": "장바구니 텍스트 클릭"}'
    },
    "scroll": {
        "description": "페이지 스크롤",
        "args": {"direction": "up 또는 down", "amount": "픽셀 수 (선택)"},
        "example": '{"action": "scroll", "args": {"direction": "down", "amount": 500}, "desc": "아래로 스크롤"}'
    }
}

# 페이지별 사용 가능한 액션
PAGE_ACTIONS = {
    "home": ["search", "login", "navigate", "go_to_cart"],
    "search": ["select_product", "scroll", "next_page", "filter", "sort"],
    "product": ["add_to_cart", "buy_now", "view_reviews", "scroll"],
    "cart": ["checkout", "remove_item", "change_quantity", "continue_shopping"],
    "login": ["submit_login", "find_id", "find_password", "signup"],
    "unknown": ["navigate", "scroll", "click"]
}


# =============================================================================
# 페이지 타입 감지
# =============================================================================

def detect_page_type(url: str) -> str:
    """URL에서 페이지 타입 감지"""
    url_lower = url.lower()
    
    if "login" in url_lower or "signin" in url_lower:
        return "login"
    elif "/search" in url_lower or "query=" in url_lower or "keyword=" in url_lower:
        return "search"
    elif "/vp/" in url_lower or "/products/" in url_lower or "/item" in url_lower:
        return "product"
    elif "/cart" in url_lower:
        return "cart"
    elif "/checkout" in url_lower or "/order" in url_lower:
        return "checkout"
    else:
        return "home"


def get_page_context(url: str, site: Optional[SiteConfig] = None) -> PageContext:
    """URL과 사이트 정보로 페이지 컨텍스트 생성"""
    page_type = detect_page_type(url)
    
    site_name = site.name if site else "알 수 없음"
    selectors = site.selectors.get(page_type, {}) if site else {}
    available_actions = PAGE_ACTIONS.get(page_type, PAGE_ACTIONS["unknown"])
    
    return PageContext(
        site_name=site_name,
        page_type=page_type,
        available_actions=available_actions,
        selectors=selectors
    )


# =============================================================================
# 컨텍스트 빌더
# =============================================================================

class ContextBuilder:
    """LLM 프롬프트용 컨텍스트 빌더"""
    
    def build_messages(
        self,
        user_text: str,
        current_url: str,
        conversation_history: List[Dict[str, str]] = None,
        page_context: PageContext = None
    ) -> List[Dict[str, str]]:
        """
        LLM API 호출용 메시지 리스트 생성
        
        Args:
            user_text: 현재 사용자 입력
            current_url: 현재 페이지 URL
            conversation_history: 이전 대화 기록
            page_context: 페이지 컨텍스트
        
        Returns:
            OpenAI API messages 형식의 리스트
        """
        system_prompt = self._build_system_prompt(current_url, page_context)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # 최근 대화 기록 추가 (최대 5개)
        if conversation_history:
            for msg in conversation_history[-5:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # 현재 사용자 입력
        messages.append({"role": "user", "content": user_text})
        
        return messages
    
    def _build_system_prompt(
        self, 
        current_url: str, 
        page_context: PageContext = None
    ) -> str:
        """시스템 프롬프트 생성"""
        
        if page_context is None:
            site = get_site_manager().get_site_by_url(current_url)
            page_context = get_page_context(current_url, site)
        
        commands_doc = self._format_commands()
        selectors_doc = self._format_selectors(page_context.selectors)
        
        return f"""당신은 시각장애인을 위한 웹 쇼핑 도우미입니다.
사용자의 자연어 요청을 브라우저 자동화 명령으로 변환합니다.

## 현재 상황
- 사이트: {page_context.site_name}
- 페이지 타입: {page_context.page_type}
- URL: {current_url}
- 가능한 액션: {', '.join(page_context.available_actions)}

## 사용 가능한 명령어
{commands_doc}

## 현재 페이지 셀렉터 (있는 경우 우선 사용)
{selectors_doc}

## 중요 규칙
1. 반드시 아래 JSON 형식으로만 응답하세요.
2. 명령어는 순서대로 실행됩니다.
3. 셀렉터가 확실하지 않으면 click_text를 사용하세요.
4. 페이지 이동 후에는 wait 명령을 추가하세요.

## 출력 형식 (반드시 이 JSON 형식으로)
{{
  "response": "사용자에게 할 말 (한국어)",
  "commands": [
    {{"action": "명령어", "args": {{}}, "desc": "설명"}}
  ]
}}

명령이 불가능하거나 이해할 수 없으면:
{{
  "response": "죄송합니다. 요청을 이해하지 못했습니다. 다시 말씀해 주세요.",
  "commands": []
}}
"""
    
    def _format_commands(self) -> str:
        """명령어 문서 포맷"""
        lines = []
        for name, spec in AVAILABLE_COMMANDS.items():
            lines.append(f"- {name}: {spec['description']}")
            lines.append(f"  예시: {spec['example']}")
        return "\n".join(lines)
    
    def _format_selectors(self, selectors: Dict[str, str]) -> str:
        """셀렉터 문서 포맷"""
        if not selectors:
            return "(셀렉터 정보 없음 - click_text 사용 권장)"
        
        lines = []
        for name, selector in selectors.items():
            lines.append(f"- {name}: {selector}")
        return "\n".join(lines)
