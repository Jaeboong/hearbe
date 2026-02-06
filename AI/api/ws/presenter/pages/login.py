# -*- coding: utf-8 -*-
"""
Login/authorization page presenter helpers.
"""

from typing import Optional

from services.llm.sites.site_manager import get_page_type, get_site_manager


def build_login_success_tts(current_url: str) -> str:
    site = get_site_manager().get_site_by_url(current_url)
    site_name = site.name if site and site.name else ""
    page_type = get_page_type(current_url)
    page_label = {
        "home": "홈",
        "search": "검색",
        "product": "상품",
        "cart": "장바구니",
        "checkout": "결제",
        "order": "주문",
    }.get(page_type)
    if page_label:
        prefix = f"{site_name} " if site_name else ""
        return f"로그인 완료되었습니다. {prefix}{page_label} 페이지로 이동했습니다."
    return "로그인 완료되었습니다. 페이지가 이동되었습니다."


def build_login_autofill_success_tts(current_url: str) -> str:
    """TTS for successful login via browser autofill."""
    site = get_site_manager().get_site_by_url(current_url)
    site_name = site.name if site and site.name else ""
    page_type = get_page_type(current_url)
    page_label = {
        "home": "홈",
        "search": "검색",
        "product": "상품",
        "cart": "장바구니",
        "checkout": "결제",
        "order": "주문",
    }.get(page_type)
    if page_label:
        prefix = f"{site_name} " if site_name else ""
        return f"자동 로그인 되었습니다. {prefix}{page_label} 페이지로 이동했습니다."
    return "자동 로그인 되었습니다. 페이지가 이동되었습니다."


def build_login_guidance_tts() -> str:
    return "로그인 페이지입니다. 이메일+비밀번호 또는 휴대폰 번호 중 어떤 방식으로 진행할까요?"


def build_captcha_prompt_tts() -> str:
    return (
        "보안 캡차 인증이 떴습니다. 음성으로 듣기 버튼을 눌렀어요. "
        "들리는 보안문자를 입력해 주세요."
    )
