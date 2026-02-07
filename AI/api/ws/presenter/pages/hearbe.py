# -*- coding: utf-8 -*-
"""
Hearbe page presenter helpers.
"""


def build_hearbe_main_guidance_tts() -> str:
    return (
        "메인 페이지입니다. "
        "'A형(음성 큰글씨 쇼핑)', 'B형(고대비 쇼핑)', 'C형(일반 쇼핑)', '공유 쇼핑' 중 "
        "어떤 모드로 진행할까요?"
    )


def build_hearbe_login_redirect_tts() -> str:
    return "로그인이 필요합니다. 로그인 페이지로 이동합니다."


def build_hearbe_mall_guidance_tts() -> str:
    # Keep this deterministic and short; this is spoken on page entry.
    return (
        "쇼핑몰 선택 페이지입니다. "
        "1번 쿠팡. 입니다. "
        "추가로 가능한 작업은 장바구니. 마이페이지 이동. 로그아웃 입니다."
    )


__all__ = [
    "build_hearbe_main_guidance_tts",
    "build_hearbe_login_redirect_tts",
    "build_hearbe_mall_guidance_tts",
]
