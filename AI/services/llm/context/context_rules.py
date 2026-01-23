"""
명령 빌더 모듈

MCP 브라우저 자동화 명령을 생성하는 빌더 함수들을 정의합니다.
CommandGenerator에서 호출하여 사용합니다.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from ..sites.site_manager import SiteConfig


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


SITE_KEYWORDS = {
    "쿠팡": "coupang",
    "네이버": "naver",
    "11번가": "11st",
}

SITE_ACCESS_TRIGGERS = ["접속", "열어", "가"]
CART_ADD_TRIGGERS = ["담", "추가", "넣"]
CART_GO_TRIGGERS = ["이동", "가", "보", "열"]
LOGIN_SUBMIT_TRIGGERS = ["클릭", "실행", "버튼", "하기"]
CHECKOUT_TRIGGERS = ["결제", "주문", "구매하기", "바로구매"]
CLICK_TRIGGERS = ["클릭", "눌러", "선택"]


# =============================================================================
# 명령 빌더 함수
# =============================================================================

def build_goto_command(url: str, description: str = "") -> GeneratedCommand:
    """URL 이동 명령 생성"""
    return GeneratedCommand(
        tool_name="goto",
        arguments={"url": url},
        description=description or f"{url}로 이동"
    )


def build_wait_command(ms: int = 1000, description: str = "") -> GeneratedCommand:
    """대기 명령 생성"""
    return GeneratedCommand(
        tool_name="wait",
        arguments={"ms": ms},
        description=description or f"{ms}ms 대기"
    )


def build_click_command(selector: str, description: str = "") -> GeneratedCommand:
    """클릭 명령 생성"""
    return GeneratedCommand(
        tool_name="click",
        arguments={"selector": selector},
        description=description or f"{selector} 클릭"
    )


def build_fill_command(selector: str, text: str, description: str = "") -> GeneratedCommand:
    """텍스트 입력 명령 생성"""
    return GeneratedCommand(
        tool_name="fill",
        arguments={"selector": selector, "text": text},
        description=description or f"'{text}' 입력"
    )


def build_press_command(selector: str, key: str = "Enter", description: str = "") -> GeneratedCommand:
    """키 입력 명령 생성"""
    return GeneratedCommand(
        tool_name="press",
        arguments={"selector": selector, "key": key},
        description=description or f"{key} 키 입력"
    )


def build_click_text_command(text: str, description: str = "") -> GeneratedCommand:
    """텍스트로 요소 찾아 클릭 명령 생성"""
    return GeneratedCommand(
        tool_name="click_text",
        arguments={"text": text},
        description=description or f"'{text}' 텍스트 클릭"
    )

def build_extract_products_command(
    site: Optional[SiteConfig],
    current_url: str = "",
    limit: int = 20,
) -> Optional[GeneratedCommand]:
    """
    Build an extract command for search results.

    Intended to run after search to capture product names for follow-up selection.
    """
    from ..sites.site_manager import get_selector

    selectors: Dict[str, str] = {}
    if site:
        page = site.get_page_selectors("search")
        if page and page.selectors:
            selectors = page.selectors

    item_selector = (
        selectors.get("product_list")
        or selectors.get("product_item")
        or (get_selector(current_url, "product_list") if current_url else None)
        or (get_selector(current_url, "product_item") if current_url else None)
    )
    if not item_selector:
        return None

    field_selectors: Dict[str, str] = {}
    title_selector = selectors.get("product_title") or selectors.get("product_name")
    if title_selector:
        field_selectors["name"] = title_selector
    if selectors.get("product_price"):
        field_selectors["price"] = selectors["product_price"]
    if selectors.get("product_rating"):
        field_selectors["rating"] = selectors["product_rating"]
    if selectors.get("product_review"):
        field_selectors["review_count"] = selectors["product_review"]

    fields = list(field_selectors.keys()) or ["name"]

    return GeneratedCommand(
        tool_name="extract",
        arguments={
            "selector": item_selector,
            "fields": fields,
            "field_selectors": field_selectors,
            "limit": limit,
        },
        description="Extract search results"
    )



# =============================================================================
# 복합 명령 빌더
# =============================================================================

def build_site_access_commands(site: SiteConfig) -> List[GeneratedCommand]:
    """사이트 접속 명령 시퀀스 생성"""
    home_url = site.get_url("home")
    return [
        build_goto_command(home_url, f"{site.name} 접속"),
        build_wait_command(1000, "페이지 로딩 대기")
    ]


def build_search_commands(site: SiteConfig, query: str, current_url: str = "") -> List[GeneratedCommand]:
    """검색 명령 시퀀스 생성 (URL 기반 셀렉터 동적 로딩)"""
    from ..sites.site_manager import get_selector
    
    # URL 기반으로 현재 페이지의 검색 셀렉터 로드
    input_selector = get_selector(current_url, "search_input") if current_url else None
    button_selector = get_selector(current_url, "search_button") if current_url else None
    
    # 폴백: 기본 셀렉터
    if not input_selector:
        input_selector = "#headerSearchKeyword"  # 쿠팡 기본
    
    commands = [
        build_fill_command(input_selector, query, f"'{query}' 입력"),
    ]
    
    # 검색 버튼이 있으면 클릭, 없으면 Enter
    if button_selector:
        commands.append(build_click_command(button_selector, "검색 버튼 클릭"))
    else:
        commands.append(build_press_command(input_selector, "Enter", "검색 실행"))
    
    commands.append(build_wait_command(1500, "검색 결과 로딩 대기"))
    return commands


def build_search_with_navigation_commands(
    site: SiteConfig,
    query: str,
    needs_navigation: bool,
    current_url: str = ""
) -> List[GeneratedCommand]:
    """사이트 이동 포함 검색 명령 시퀀스 생성"""
    commands = []

    if needs_navigation:
        home_url = site.get_url("home")
        commands.append(build_goto_command(home_url, f"{site.name} 이동"))
        commands.append(build_wait_command(1000, "페이지 로딩 대기"))
        # 이동 후 URL 업데이트
        current_url = home_url

    commands.extend(build_search_commands(site, query, current_url))
    return commands


def build_add_to_cart_commands(site: Optional[SiteConfig], current_url: str = "") -> List[GeneratedCommand]:
    """장바구니 담기 명령 시퀀스 생성 (URL 기반 셀렉터 동적 로딩)"""
    from ..sites.site_manager import get_selector
    
    # URL 기반으로 셀렉터 로드 (product 페이지의 add_to_cart)
    selector = get_selector(current_url, "add_to_cart") if current_url else None
    
    # 폴백: SiteConfig에서 시도
    if not selector and site:
        selector = site.get_selector("product", "add_to_cart")
    
    if selector:
        return [
            build_click_command(selector, "장바구니 담기 버튼 클릭"),
            build_wait_command(1000, "처리 대기")
        ]

    # 최종 폴백: 텍스트 기반
    return [build_click_text_command("장바구니", "장바구니 버튼 찾아서 클릭")]


def build_go_to_cart_commands(site: Optional[SiteConfig]) -> List[GeneratedCommand]:
    """장바구니 이동 명령 시퀀스 생성"""
    if site:
        cart_url = site.get_url("cart")
        if cart_url:
            return [build_goto_command(cart_url, "장바구니 페이지 이동")]

    # 폴백
    return [build_click_text_command("장바구니", "장바구니 버튼 클릭")]


def build_login_page_commands(site: Optional[SiteConfig]) -> List[GeneratedCommand]:
    """로그인 페이지 이동 명령 생성"""
    if site:
        login_url = site.get_url("login")
        if login_url:
            return [build_goto_command(login_url, "로그인 페이지 이동")]

    # 폴백
    return [build_click_text_command("로그인", "로그인 버튼 클릭")]


def build_login_submit_commands() -> List[GeneratedCommand]:
    """로그인 버튼 클릭 명령 생성"""
    return [
        build_click_command(
            "._loginSubmitButton, .login__button--submit, button[type='submit']",
            "로그인 버튼 클릭"
        ),
        build_wait_command(2000, "로그인 처리 대기")
    ]


def build_generic_click_commands(target: str) -> List[GeneratedCommand]:
    """일반 클릭 명령 생성"""
    return [build_click_text_command(target, f"'{target}' 클릭")]


# =============================================================================
# 유틸리티 함수
# =============================================================================

def extract_search_query(text: str) -> Optional[str]:
    """텍스트에서 검색어 추출"""
    import re
    match = re.search(r"(.+?)\s*검색", text)
    if not match:
        return None

    query = match.group(1).strip()

    # 사이트 키워드 및 조사 제거
    for keyword in list(SITE_KEYWORDS.keys()) + ["에서", "에"]:
        query = query.replace(keyword, "").strip()

    return query if query else None


def detect_target_site(text: str, site_manager, current_site: Optional[SiteConfig]) -> Optional[SiteConfig]:
    """텍스트에서 대상 사이트 감지"""
    for keyword, site_id in SITE_KEYWORDS.items():
        if keyword in text:
            return site_manager.get_site(site_id)

    # 지정 없으면 현재 사이트 또는 기본값
    if current_site:
        return current_site

    return site_manager.get_site("coupang")


def extract_click_target(text: str) -> str:
    """클릭 대상 텍스트 추출"""
    target = text
    for kw in CLICK_TRIGGERS:
        target = target.replace(kw, "").strip()
    return target
