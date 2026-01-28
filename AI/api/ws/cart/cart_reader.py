# -*- coding: utf-8 -*-
"""
Cart reader utilities.
"""

from typing import List, Dict


def build_cart_read_tts(
    items: List[Dict],
    summary: Dict[str, str]
) -> str:
    if not items:
        return "장바구니에 담긴 상품이 없습니다."

    lines = []
    for idx, item in enumerate(items[:4]):
        name = item.get("name") or "상품"
        option = item.get("option") or ""
        arrival = item.get("arrival") or ""
        price = item.get("price") or ""
        quantity = item.get("quantity") or ""
        selected = item.get("selected")
        parts = [f"{idx + 1}번 {name}"]
        if selected is True:
            parts.append("선택됨")
        if option:
            parts.append(f"옵션 {option}")
        if arrival:
            parts.append(f"{arrival} 도착")
        if price:
            parts.append(f"가격 {price}")
        if quantity:
            parts.append(f"수량 {quantity}")
        lines.append(". ".join(parts))

    tts_text = ". ".join(lines) + "."

    total_price = summary.get("total_product_price") or ""
    shipping_fee = summary.get("shipping_fee") or ""
    if total_price or shipping_fee:
        tts_text += " 총액 정보입니다."
        if total_price:
            tts_text += f" 총 상품 가격 {total_price}."
        if shipping_fee:
            tts_text += f" 총 배송비 {shipping_fee}."

    return tts_text
