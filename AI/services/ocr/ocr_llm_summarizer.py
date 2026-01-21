import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from typing import Dict, List, Tuple

# Import product type module
from product_type_detector import (
    ProductType,
    detect_product_type,
    get_keywords_for_type,
    get_type_description,
    is_keyword_valid_for_type,
)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env from the same directory as this script
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")
    print("Falling back to system environment variables only.")


DEFAULT_INPUT = os.path.join("output", "오겹살_res_texts.json")
DEFAULT_OUTPUT = os.path.join("output", "오겹살_texts_summary.json")

# Import text preprocessor
try:
    from ocr_text_preprocessor import load_and_preprocess_ocr_json
    PREPROCESSOR_AVAILABLE = True
except ImportError:
    PREPROCESSOR_AVAILABLE = False
    print("Warning: ocr_text_preprocessor module not found. OCR texts will not be preprocessed.")


def _load_ocr_texts(path: str, preprocess: bool = True) -> Tuple[List[str], Dict]:
    """
    Load OCR texts from JSON file with optional preprocessing.
    
    Args:
        path: Path to OCR JSON file
        preprocess: Whether to apply text preprocessing (default: True)
        
    Returns:
        Tuple of (cleaned_texts, original_data)
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if preprocess and PREPROCESSOR_AVAILABLE:
        # Use preprocessor to clean texts
        texts, stats = load_and_preprocess_ocr_json(data, min_score=0.7, min_length=2, verbose=True)
    else:
        # Fallback: basic cleaning without preprocessing
        texts = data.get("rec_texts") or []
        texts = [t.strip() for t in texts if isinstance(t, str) and t.strip()]
    
    return texts, data


def _build_prompt(texts: List[str], product_type: ProductType) -> Dict[str, str]:
    """Build LLM prompt with type-specific keywords."""
    numbered = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(texts))
    
    # Get keywords for this product type
    keywords = get_keywords_for_type(product_type)
    type_desc = get_type_description(product_type)
    
    # Build keyword schema dynamically
    keyword_lines = []
    for i, kw in enumerate(keywords):
        if i == 0:
            keyword_lines.append(f'    "{kw}": {{"answer": "...", "evidence": ["..."], "status": "found|not_found"}}')
        else:
            keyword_lines.append(f'    "{kw}": {{...}}')
    keyword_schema = ",\n".join(keyword_lines)
    
    system = (
        "You summarize Korean OCR text for visually impaired users. "
        "Return ONLY valid JSON. Do not add any commentary."
    )
    instructions = (
        f"You are analyzing a {type_desc} ({product_type.value}) product.\n"
        f"Extract these keywords: {', '.join(keywords)}\n\n"
        "You must only use the provided OCR lines. "
        "If a keyword is missing, mark status as \"not_found\" and answer "
        "as \"OCR 텍스트에 없음\".\n\n"
        "Output JSON schema:\n"
        "{\n"
        f'  "product_type": "{product_type.value}",\n'
        '  "product_name": "...",\n'
        '  "confidence": 0.0-1.0,\n'
        '  "summary": ["...", "..."],\n'
        '  "keywords": {\n'
        f"{keyword_schema}\n"
        "  }\n"
        "}\n"
        "Keep summary to 3-5 short sentences. "
        "Set confidence (0.0-1.0) based on OCR text quality and completeness."
    )
    user = "OCR lines:\n" + numbered
    return {"system": system, "instructions": instructions, "user": user}


def _call_openai(prompt: Dict[str, str], max_retries: int = 3) -> Dict:
    """Call SSAFY GMS API (OpenAI-compatible Chat Completions) with retry logic."""
    api_key = os.environ.get("GMS_KEY")
    if not api_key:
        raise RuntimeError("GMS_KEY is not set. Set the GMS_KEY environment variable.")

    model = os.environ.get("OPENAI_MODEL", "gpt-5-mini")
    url = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"

    # Build messages using Chat Completions format
    messages = [
        {
            "role": "developer",
            "content": prompt["system"] + "\n\n" + prompt["instructions"]
        },
        {
            "role": "user",
            "content": prompt["user"]
        }
    ]

    payload = {
        "model": model,
        "messages": messages,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    last_error = None
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=(10, 120),  # (connection timeout, read timeout)
            )
            response.raise_for_status()
            raw = response.json()

            # Extract response text from Chat Completions API format
            choices = raw.get("choices", [])
            if not choices:
                raise RuntimeError("LLM returned no choices.")
            
            output_text = choices[0].get("message", {}).get("content", "")
            if not output_text:
                raise RuntimeError("LLM returned no content.")

            try:
                return json.loads(output_text)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"LLM output is not valid JSON: {exc}") from exc

        except requests.exceptions.RequestException as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise RuntimeError(f"LLM request failed after {max_retries} retries: {last_error}") from last_error


def _write_json(path: str, data: Dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _normalize(text: str) -> str:
    return "".join(text.lower().split())


def _build_keyword_aliases() -> Dict[str, List[str]]:
    return {
        "가격": ["가격", "price", "값", "얼마"],
        "제품명": ["제품명", "상품명", "이름", "product", "name"],
        "특징": ["특징", "특성", "설명", "소개", "맛", "식감"],
        "브랜드/캐릭터": ["브랜드", "캐릭터", "브랜드/캐릭터", "브랜드캐릭터"],
        "섭취방법": ["섭취", "먹는법", "먹는 방법", "조리", "전자레인지"],
        "중량/용량": ["중량", "용량", "그램", "g", "ml", "리터"],
        "원재료/성분": ["원재료", "성분", "재료", "ingredient"],
        "알레르기": ["알레르기", "알러지", "allergy"],
        "보관방법": ["보관", "보관방법", "보관법", "보관 온도"],
        "유통기한": ["유통기한", "소비기한", "기한", "expiry"],
        "영양정보": ["영양", "영양정보", "칼로리", "kcal"],
        "주의사항": ["주의", "주의사항", "경고"],
        "기타": ["기타", "참고"],
    }


def _find_keyword_key(question: str, keywords: Dict[str, Dict]) -> str:
    normalized = _normalize(question)
    aliases = _build_keyword_aliases()
    for key, tokens in aliases.items():
        for token in tokens:
            if _normalize(token) in normalized:
                return key if key in keywords else ""
    return ""


def _answer_query(summary: Dict, question: str) -> str:
    """Answer user query with type-aware validation."""
    product_type_str = summary.get("product_type", "OTHER")
    try:
        product_type = ProductType(product_type_str)
    except ValueError:
        product_type = ProductType.OTHER
    
    keywords = summary.get("keywords", {})
    key = _find_keyword_key(question, keywords)
    
    if not key:
        available = ", ".join(keywords.keys())
        return f"질문과 일치하는 키워드를 찾지 못했습니다. 사용 가능한 키워드: {available}"
    
    # Type-aware validation
    if not is_keyword_valid_for_type(product_type, key):
        type_desc = get_type_description(product_type)
        return f"이 제품은 {type_desc}이므로 '{key}' 정보가 없을 수 있습니다."
    
    item = keywords.get(key, {})
    status = item.get("status", "not_found")
    answer = item.get("answer", "OCR 텍스트에 없음")
    if status != "found":
        return f"{key}: OCR 텍스트에 없음"
    return f"{key}: {answer}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize OCR output into keyword JSON.")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Path to OCR JSON.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Path to write summary JSON.")
    parser.add_argument("--query", default="", help="Question to answer from the summary JSON.")
    args = parser.parse_args()

    if args.query:
        if not os.path.exists(args.output):
            print(f"Summary JSON not found: {args.output}")
            return 1
        with open(args.output, "r", encoding="utf-8") as f:
            summary = json.load(f)
        print(_answer_query(summary, args.query))
        return 0

    texts, _ = _load_ocr_texts(args.input)
    if not texts:
        print("No OCR texts found.")
        return 1

    # Detect product type
    product_type = detect_product_type(texts)
    type_desc = get_type_description(product_type)
    print(f"Detected product type: {product_type.value} ({type_desc})")
    print(f"Keywords to extract: {', '.join(get_keywords_for_type(product_type))}")

    # Build prompt with type-specific keywords
    prompt = _build_prompt(texts, product_type)
    summary = _call_openai(prompt)
    summary["source_file"] = args.input
    _write_json(args.output, summary)
    print(f"Summary written to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
