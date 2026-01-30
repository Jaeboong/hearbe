# -*- coding: utf-8 -*-
"""
TTS text normalizer

Converts unit expressions (e.g., 2L, 500ml) into Korean-friendly forms.
"""

import re


_UNIT_PATTERNS = [
    # liters
    (re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:L|l|ℓ)\b"), r"\1리터"),
    # milliliters
    (re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:mL|ml|ML|㎖)\b"), r"\1밀리리터"),
    # kilograms
    (re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:kg|Kg|kG|KG)\b"), r"\1킬로그램"),
    # grams (lowercase only to avoid 5G)
    (re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:g)\b"), r"\1그램"),
    # milligrams
    (re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:mg|mG|Mg|MG)\b"), r"\1밀리그램"),
]


_KOR_DIGITS = ["", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]
_SMALL_UNITS = ["", "십", "백", "천"]
_LARGE_UNITS = ["", "만", "억", "조", "경"]


def _int_to_korean(num: int) -> str:
    if num == 0:
        return "영"

    parts = []
    unit_index = 0
    while num > 0:
        chunk = num % 10000
        if chunk:
            chunk_text = _chunk_to_korean(chunk)
            unit = _LARGE_UNITS[unit_index]
            parts.append(chunk_text + unit)
        num //= 10000
        unit_index += 1

    return " ".join(reversed(parts)).strip()


def _chunk_to_korean(chunk: int) -> str:
    result = []
    for i in range(4):
        digit = chunk % 10
        if digit:
            digit_text = _KOR_DIGITS[digit]
            unit = _SMALL_UNITS[i]
            if digit == 1 and unit:
                digit_text = ""
            result.append(digit_text + unit)
        chunk //= 10
    return "".join(reversed(result)).strip()


def _parse_int(value: str) -> int:
    return int(value.replace(",", ""))


def _replace_percent(match: re.Match) -> str:
    value = match.group(1)
    try:
        number = _parse_int(value)
    except ValueError:
        return match.group(0)
    return f"{_int_to_korean(number)}퍼센트"


def _replace_won(match: re.Match) -> str:
    value = match.group(1)
    try:
        number = _parse_int(value)
    except ValueError:
        return match.group(0)
    return f"{_int_to_korean(number)}원"


def _replace_comma_number(match: re.Match) -> str:
    value = match.group(1)
    try:
        number = _parse_int(value)
    except ValueError:
        return match.group(0)
    return _int_to_korean(number)


_PERCENT_PATTERN = re.compile(r"(\d{1,3}(?:,\d{3})*|\d+)\s*%")
_WON_PATTERN = re.compile(r"(\d{1,3}(?:,\d{3})*|\d+)\s*원")
_COMMA_NUMBER_PATTERN = re.compile(r"(\d{1,3}(?:,\d{3})+)")
_DATE_SLASH_PATTERN = re.compile(r"(?<!\d)(1[0-2]|0?[1-9])\s*/\s*(3[01]|[12]\d|0?[1-9])(?!\d)")
_DATE_CONTEXT_PATTERN = re.compile(
    r"(도착|배송|보장|새벽|오전|오후|밤|오늘|내일|모레)"
)


def _normalize_date_slash(text: str) -> str:
    def _repl(match: re.Match) -> str:
        start, end = match.span()
        window = text[max(0, start - 10):min(len(text), end + 10)]
        if not _DATE_CONTEXT_PATTERN.search(window):
            return match.group(0)
        month = int(match.group(1))
        day = int(match.group(2))
        return f"{month}월 {day}일"

    return _DATE_SLASH_PATTERN.sub(_repl, text)


def normalize_tts_text(text: str) -> str:
    if not text:
        return text

    normalized = text
    normalized = _normalize_date_slash(normalized)
    normalized = _PERCENT_PATTERN.sub(_replace_percent, normalized)
    normalized = _WON_PATTERN.sub(_replace_won, normalized)
    normalized = _COMMA_NUMBER_PATTERN.sub(_replace_comma_number, normalized)
    for pattern, repl in _UNIT_PATTERNS:
        normalized = pattern.sub(repl, normalized)
    return normalized
