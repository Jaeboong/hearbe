import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path
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
    # Load .env from workspace root (새 폴더 (2))
    # Path: scripts/ocr_llm_summarizer.py -> ocr_test -> 새 폴더 (2) -> .env
    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")
    print("Falling back to system environment variables only.")


DEFAULT_INPUT = os.path.join("output", "샴푸_res.json")
DEFAULT_OUTPUT = os.path.join("output", "샴푸_summary.json")

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


def _call_openai(prompt: Dict[str, str]) -> Dict:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    model = os.environ.get("OPENAI_MODEL", "gpt-5-mini")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    url = f"{base_url.rstrip('/')}/responses"

    payload = {
        "model": model,
        "instructions": prompt["system"] + "\n\n" + prompt["instructions"],
        "input": prompt["user"],
        "reasoning": {"effort": "minimal"},
        "text": {"verbosity": "low"},
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8")
    raw = json.loads(body)

    # Extract response text from the Responses API format.
    output_text = ""
    for item in raw.get("output", []):
        if item.get("type") == "message":
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    output_text = content.get("text", "")
                    break
    if not output_text:
        raise RuntimeError("LLM returned no output_text.")

    try:
        return json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"LLM output is not valid JSON: {exc}") from exc


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
