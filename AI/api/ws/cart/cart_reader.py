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
        return "장바구니가 비어 있어요."

    total_count = len(items)
    selected_count = sum(1 for item in items if item.get("selected") is True)

    def _normalize_quantity(value: str | int | None) -> str:
        if value is None:
            return ""
        text = str(value).strip()
        if not text:
            return ""
        return f"{text}개" if text.isdigit() else text

    lines = []
    max_read = 4
    for idx, item in enumerate(items[:max_read]):
        name = item.get("name") or "상품"
        option = item.get("option") or ""
        arrival = item.get("arrival") or ""
        price = item.get("price") or ""
        quantity = _normalize_quantity(item.get("quantity") or "")
        selected = item.get("selected")
        parts = [f"{idx + 1}번 {name}"]
        if selected is True:
            parts.append("현재 선택됨")
        if option:
            parts.append(f"옵션 {option}")
        if arrival:
            parts.append(arrival)
        if price:
            parts.append(f"가격 {price}")
        if quantity:
            parts.append(f"수량 {quantity}")
        lines.append(". ".join(parts))

    intro = f"장바구니에 상품 {total_count}개가 있어요."
    if selected_count:
        intro += f" 현재 선택된 상품은 {selected_count}개입니다."
    intro += " 주요 상품을 알려드릴게요."

    tts_text = intro + " " + ". ".join(lines) + "."

    if total_count > max_read:
        remain = total_count - max_read
        tts_text += f" 나머지 {remain}개도 읽어드릴까요?"

    total_price = summary.get("total_product_price") or ""
    shipping_fee = summary.get("shipping_fee") or ""
    if total_price or shipping_fee:
        tts_text += " 총액 정보입니다."
        if total_price:
            tts_text += f" 총 상품 가격 {total_price}."
        if shipping_fee:
            tts_text += f" 총 배송비 {shipping_fee}."

    return tts_text
