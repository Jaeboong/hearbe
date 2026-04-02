"""
정규식 기반 파라미터 추출기

인텐트에 필요한 파라미터를 사용자 발화에서 추출합니다.
예: "무선 이어폰 검색해줘" → {"query": "무선 이어폰"}
"""

import re
from typing import Dict, Any, Optional


class ParamExtractor:
    """인텐트별 파라미터 추출"""

    def extract(self, intent: str, text: str) -> Dict[str, Any]:
        extractor = _EXTRACTORS.get(intent)
        if not extractor:
            return {}
        return extractor(text)


# ── 검색 쿼리 ──────────────────────────────────────────────

def _extract_search_query(text: str) -> Dict[str, Any]:
    """'무선 이어폰 검색해줘' → {'query': '무선 이어폰'}"""
    patterns = [
        r"(.+?)\s*(?:검색해줘|검색해|검색|찾아줘|찾아봐|찾아)",
        r"(?:검색|찾아)\s*(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            query = match.group(1).strip()
            for kw in ("쿠팡에서", "네이버에서", "쿠팡", "네이버", "11번가에서", "11번가", "에서"):
                query = query.replace(kw, "").strip()
            if query:
                return {"query": query}
    return {"query": text.strip()}


# ── 순번 (ordinal) ─────────────────────────────────────────

_KOREAN_ORDINALS = {"첫": 1, "두": 2, "세": 3, "네": 4, "다섯": 5, "여섯": 6, "일곱": 7, "여덟": 8, "아홉": 9, "열": 10}


def _extract_ordinal(text: str) -> Dict[str, Any]:
    """'2번 상품 열어줘' → {'ordinal': 2}"""
    match = re.search(r"(\d+)\s*번", text)
    if match:
        return {"ordinal": int(match.group(1))}
    for word, num in _KOREAN_ORDINALS.items():
        if f"{word}번째" in text or f"{word} 번째" in text:
            return {"ordinal": num}
    return {"ordinal": 1}


# ── 텍스트 입력 (아이디, 비밀번호, 이름 등) ────────────────

def _extract_text_input(text: str, labels: tuple) -> Optional[str]:
    for label in labels:
        pattern = rf"{re.escape(label)}\s*(?:은|는|이|가|:|\s)\s*(\S+)"
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def _extract_id(text: str) -> Dict[str, Any]:
    value = _extract_text_input(text, ("아이디", "id", "ID", "아이디는", "아이디가"))
    if not value:
        cleaned = re.sub(r"(아이디|입력|해줘|해|할게|로|으로|는|이|가)", "", text).strip()
        if re.fullmatch(r"[A-Za-z0-9._@]{3,50}", cleaned):
            value = cleaned
    return {"id_value": value}


def _extract_password(text: str) -> Dict[str, Any]:
    value = _extract_text_input(text, ("비밀번호", "비번", "패스워드", "password", "pw"))
    if not value:
        cleaned = re.sub(r"(비밀번호|비번|패스워드|입력|해줘|해|할게|로|으로|는|이|가)", "", text).strip()
        if cleaned and len(cleaned) >= 4:
            value = cleaned
    return {"password_value": value}


def _extract_quantity(text: str) -> Dict[str, Any]:
    match = re.search(r"(\d+)\s*(?:개|번)", text)
    if match:
        return {"quantity": int(match.group(1))}
    return {"quantity": None}


def _extract_option(text: str) -> Dict[str, Any]:
    cleaned = re.sub(r"(옵션|변경|선택|으로|로|해줘|해|바꿔|바꾸|할게)", "", text).strip()
    return {"option_text": cleaned if cleaned else None}


def _extract_name(text: str) -> Dict[str, Any]:
    value = _extract_text_input(text, ("이름", "성함", "이름은", "이름이"))
    if not value:
        cleaned = re.sub(r"(이름|성함|입력|해줘|해|할게|로|으로|는|이|가)", "", text).strip()
        if cleaned and 2 <= len(cleaned) <= 10:
            value = cleaned
    return {"name_value": value}


def _extract_email(text: str) -> Dict[str, Any]:
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    if match:
        return {"email_value": match.group(0)}
    value = _extract_text_input(text, ("이메일", "email", "메일"))
    return {"email_value": value}


def _extract_phone(text: str) -> Dict[str, Any]:
    digits = re.sub(r"\D", "", text)
    if len(digits) in (10, 11) and digits.startswith(("010", "011")):
        return {"phone_value": digits}
    return {"phone_value": None}


def _extract_password_confirm(text: str) -> Dict[str, Any]:
    result = _extract_password(text)
    return {"password_confirm_value": result.get("password_value")}


# ── 인텐트 → 추출기 매핑 ──────────────────────────────────

_EXTRACTORS = {
    "search_products": _extract_search_query,
    "select_search_result": _extract_ordinal,
    "select_cart_item": _extract_ordinal,
    "unselect_cart_item": _extract_ordinal,
    "click_order_detail": _extract_ordinal,
    "click_product_view": _extract_ordinal,
    "input_id": _extract_id,
    "input_password": _extract_password,
    "input_password_confirm": _extract_password_confirm,
    "input_name": _extract_name,
    "input_email": _extract_email,
    "input_phone_number": _extract_phone,
    "adjust_item_quantity": _extract_quantity,
    "update_product_option": _extract_option,
}
