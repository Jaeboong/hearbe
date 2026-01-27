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


def normalize_tts_text(text: str) -> str:
    if not text:
        return text

    normalized = text
    for pattern, repl in _UNIT_PATTERNS:
        normalized = pattern.sub(repl, normalized)
    return normalized
