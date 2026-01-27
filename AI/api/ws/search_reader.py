# -*- coding: utf-8 -*-
"""
Search results reader utilities
"""

from typing import List, Dict, Tuple


def _get_name(item: Dict) -> str:
    return (
        item.get("name")
        or item.get("title")
        or item.get("product_name")
        or "상품"
    )


def _get_price(item: Dict) -> str:
    return item.get("price") or ""


def build_search_read_tts(
    products: List[Dict],
    start_index: int,
    count: int,
    include_total: bool = False
) -> Tuple[str, int, bool]:
    """
    Build TTS text for a slice of search results.

    Returns:
        (tts_text, next_index, has_more)
    """
    total = len(products)
    if total == 0 or start_index >= total:
        return "더 읽을 상품이 없습니다.", start_index, False

    end_index = min(start_index + count, total)
    lines = []
    for idx in range(start_index, end_index):
        item = products[idx]
        name = _get_name(item)
        price = _get_price(item)
        line = f"{idx + 1}번, {name}"
        if price:
            line += f", 가격 {price}"
        lines.append(line)

    prefix = f"총 {total}개 상품입니다. " if include_total else ""
    tts_text = prefix + ". ".join(lines) + "."
    has_more = end_index < total
    return tts_text, end_index, has_more
