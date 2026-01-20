"""
컨텍스트 인식 규칙 엔진

현재 URL을 기반으로 사용자 명령을 해석합니다.
예: 쿠팡에 있는 상태에서 "생수 검색" → 쿠팡에서 검색 (Google X)
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from .site_manager import get_current_site, get_site_manager, SiteConfig


def build_search_commands(
    query: str, 
    site: SiteConfig
) -> List[Tuple[str, Dict[str, Any]]]:
    """해당 사이트에서 검색하는 명령 생성"""
    search_selectors = site.selectors.get("search", {})
    input_selector = search_selectors.get("input", "input[name='q']")
    submit_key = search_selectors.get("submit_key", "Enter")
    
    return [
        ("click", {"selector": input_selector}),
        ("fill", {"selector": input_selector, "text": query}),
        ("press", {"selector": input_selector, "key": submit_key}),
    ]


def build_cart_commands(site: SiteConfig) -> List[Tuple[str, Dict[str, Any]]]:
    """장바구니 이동 명령 생성"""
    cart_url = site.get_url("cart")
    if cart_url:
        return [("open_url", {"url": cart_url})]
    
    cart_selector = site.get_selector("cart", "button")
    if cart_selector:
        return [("click", {"selector": cart_selector})]
    
    # 폴백: 텍스트로 클릭 시도
    return [("click_text", {"text": "장바구니"})]


def build_add_to_cart_commands(site: SiteConfig) -> List[Tuple[str, Dict[str, Any]]]:
    """장바구니 담기 명령 생성"""
    selector = site.get_selector("product", "add_to_cart")
    if selector:
        return [("click", {"selector": selector})]
    return [("click_text", {"text": "장바구니"})]


def context_aware_commands(
    user_text: str, 
    current_url: str
) -> List[Tuple[str, Dict[str, Any]]]:
    """
    컨텍스트 인식 명령 생성
    
    현재 URL을 기반으로 사용자 명령을 해석합니다.
    
    Args:
        user_text: 사용자 입력 텍스트
        current_url: 현재 브라우저 URL
        
    Returns:
        MCP 명령 리스트 [(tool_name, arguments), ...]
    """
    text = user_text.strip()
    if not text:
        return []
    
    site = get_current_site(current_url)
    
    # 1. 검색 명령 처리 (현재 사이트에서 검색)
    if "검색" in text:
        # "생수 검색해줘" → query = "생수"
        match = re.search(r"(.+?)\s*검색", text)
        query = match.group(1).strip() if match else ""
        
        # 특정 사이트 키워드가 있으면 해당 사이트로
        if "쿠팡" in text:
            site = get_site_manager().get_site("coupang")
        elif "네이버" in text:
            site = get_site_manager().get_site("naver")
        elif "11번가" in text:
            site = get_site_manager().get_site("11st")
        
        if site and query:
            # 현재 사이트가 같으면 바로 검색
            if site.matches_domain(current_url):
                return build_search_commands(query, site)
            else:
                # 다른 사이트면 먼저 이동 후 검색
                home_url = site.get_url("home")
                commands = [("open_url", {"url": home_url}), ("wait", {"ms": 1000})]
                commands.extend(build_search_commands(query, site))
                return commands
        
        # 사이트 지정 없고 현재 사이트가 쇼핑몰이면 → 현재 사이트에서 검색
        if site and query:
            return build_search_commands(query, site)
    
    # 2. 장바구니 이동
    if "장바구니" in text and ("이동" in text or "가" in text or "보" in text or text == "장바구니"):
        if site:
            return build_cart_commands(site)
    
    # 3. 장바구니 담기
    if "장바구니" in text and ("담" in text or "추가" in text or "넣" in text):
        if site:
            return build_add_to_cart_commands(site)
    
    # 4. 로그인
    if "로그인" in text:
        if site:
            login_url = site.get_url("login")
            if login_url:
                return [("open_url", {"url": login_url})]
    
    # 매칭 없음
    return []
