# OCR 텍스트를 LLM으로 요약
import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from typing import Dict, List, Tuple

from product_type_detector import (
    ProductType,
    detect_product_type,
    get_keywords_for_type,
    get_type_description,
    is_keyword_valid_for_type
)

try:
    from .utils import compute_summary_hash, load_summary_cache, save_summary_cache
except ImportError:
    from utils import compute_summary_hash, load_summary_cache, save_summary_cache

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print("경고: python-dotenv가 설치되지 않았습니다.")

DEFAULT_INPUT = os.path.join("output", "샴푸_res_texts.json")
DEFAULT_OUTPUT = os.path.join("output", "샴푸_texts_summary.json")

try:
    from ocr_text_preprocessor import load_and_preprocess_ocr_json
    PREPROCESSOR_AVAILABLE = True
except ImportError:
    PREPROCESSOR_AVAILABLE = False
    print("경고: ocr_text_preprocessor 모듈을 찾을 수 없습니다.")


def _load_ocr_texts(path: str, preprocess: bool = True) -> Tuple[List[str], Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if preprocess and PREPROCESSOR_AVAILABLE:
        texts, stats = load_and_preprocess_ocr_json(data, min_score=0.7, min_length=2, verbose=True)
    else:
        texts = data.get("rec_texts") or []
        texts = [t.strip() for t in texts if isinstance(t, str) and t.strip()]
    
    return texts, data


def _build_prompt(texts: List[str], product_type: ProductType) -> Dict[str, str]:
    numbered = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(texts))
    keywords = get_keywords_for_type(product_type)
    type_desc = get_type_description(product_type)
    
    # 프롬프트 간소화: 첫 키워드만 전체 예시, 나머지는 생략
    first_keyword = keywords[0] if keywords else "예시"
    keyword_schema = f'    "{first_keyword}": {{ "answer": "...", "status": "found|not_found" }},\n    // 나머지 {len(keywords)-1}개 키워드도 동일 형식'
    
    system = (
        "당신은 시각장애인을 위해 한국어 OCR 텍스트를 요약하고 분석하는 어시스턴트입니다. "
        "반드시 유효한 JSON 형식으로만 응답하세요."
    )
    
    instructions = (
        f"당신은 지금 '{type_desc} ({product_type.value})' 제품을 분석하고 있습니다.\n"
        f"다음 키워드들에 대한 정보를 추출하세요: {', '.join(keywords)}\n\n"
        "반드시 제공된 OCR 텍스트 내용에 기반해서만 답해야 합니다. "
        "만약 해당 키워드에 대한 정보가 텍스트에 없다면, status를 \"not_found\"로 하고 "
        "answer를 \"OCR 텍스트에 없음\"이라고 적으세요.\n\n"
        "출력할 JSON 형식:\n"
        "{\n"
        f'  "product_type": "{product_type.value}",\n'
        '  "product_name": "제품명",\n'
        '  "confidence": 0.0-1.0,\n'
        '  "summary": ["핵심 요약 문장 1", "핵심 요약 문장 2", "핵심 요약 문장 3"],\n'
        '  "keywords": {\n'
        f"{keyword_schema}\n"
        "  }\n"
        "}\n"
        "요약(summary)은 3-5문장으로 작성하세요. 시각장애인을 위한 정보를 제공해야 합니다."
    )
    
    user = "분석할 OCR 텍스트:\n" + numbered
    
    return {"system": system, "instructions": instructions, "user": user}


def _call_openai(prompt: Dict[str, str], max_retries: int = 3) -> Dict:
    api_key = os.environ.get("GMS_KEY")
    if not api_key:
        raise RuntimeError("GMS_KEY 환경변수가 설정되지 않았습니다.")

    model = os.environ.get("OPENAI_MODEL", "gpt-5-mini")
    url = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"

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
                timeout=(10, 120),
            )
            if response.status_code >= 400:
                print(f"\n[DEBUG] HTTP {response.status_code} 에러")
                print(f"[DEBUG] 응답 본문: {response.text}")
            response.raise_for_status()
            raw = response.json()

            choices = raw.get("choices", [])
            if not choices:
                raise RuntimeError("LLM 응답에 choices가 없습니다.")
            
            output_text = choices[0].get("message", {}).get("content", "")
            if not output_text:
                raise RuntimeError("LLM 응답 내용이 비어있습니다.")

            if output_text.strip().startswith("```"):
                lines = output_text.strip().split("\n")
                output_text = "\n".join(lines[1:-1])

            try:
                return json.loads(output_text)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"LLM 응답이 유효한 JSON이 아닙니다: {exc}") from exc

        except requests.exceptions.RequestException as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"API 요청 실패 (시도 {attempt + 1}/{max_retries}): {e}")
                print(f"{wait_time}초 후 재시도합니다...")
                time.sleep(wait_time)
            else:
                raise RuntimeError(f"LLM 요청이 {max_retries}회 재시도 후에도 실패했습니다: {last_error}") from last_error


def summarize_texts(
    texts: List[str],
    product_type: ProductType = None,
    verbose: bool = True,
    use_cache: bool = True,
    prompt_version: str = "v1",
) -> Dict:
    if not texts:
        return {
            "product_type": "기타",
            "product_name": "알 수 없음",
            "confidence": 0.0,
            "summary": ["텍스트가 없어 요약할 수 없습니다."],
            "keywords": {},
            "error": "입력 텍스트가 비어있습니다."
        }
    
    if product_type is None:
        product_type = detect_product_type(texts)
        if verbose:
            type_desc = get_type_description(product_type)
            print(f"    제품 타입 자동 감지: {type_desc} ({product_type.value})")
    
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    if use_cache:
        summary_hash = compute_summary_hash(
            texts=texts,
            product_type=product_type.value,
            model=model,
            prompt_version=prompt_version,
        )
        cached = load_summary_cache(summary_hash)
        if cached:
            if verbose:
                print("    LLM summary cache hit")
            return cached

    prompt = _build_prompt(texts, product_type)
    
    if verbose:
        print("    LLM API 호출 중...", end="", flush=True)
    summary = _call_openai(prompt)
    if use_cache:
        save_summary_cache(summary_hash, summary)
    if verbose:
        print(" 완료!")
    
    return summary


def _write_json(path: str, data: Dict) -> None:
    dir_path = os.path.dirname(path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _normalize(text: str) -> str:
    return "".join(text.lower().split())


def _build_keyword_aliases() -> Dict[str, List[str]]:
    return {
        "가격": ["가격", "price", "값", "얼마", "비용"],
        "제품명": ["제품명", "상품명", "이름", "product", "name", "뭐에요"],
        "특징": ["특징", "특성", "설명", "소개", "맛", "식감"],
        "브랜드/캐릭터": ["브랜드", "캐릭터", "제조사", "만든곳"],
        "섭취방법": ["섭취", "먹는법", "먹는 방법", "조리", "전자레인지", "어떻게 먹어"],
        "중량/용량": ["중량", "용량", "그램", "g", "ml", "리터", "양", "무게"],
        "원재료/성분": ["원재료", "성분", "재료", "ingredient", "뭐가 들어"],
        "알레르기": ["알레르기", "알러지", "allergy", "주의성분"],
        "보관방법": ["보관", "보관방법", "보관법", "온도", "냉장", "냉동"],
        "유통기한": ["유통기한", "소비기한", "기한", "expiry", "언제까지"],
        "영양정보": ["영양", "영양정보", "칼로리", "kcal", "열량"],
        "주의사항": ["주의", "주의사항", "경고", "조심"],
        "기타": ["기타", "참고"],
    }


def _find_keyword_key(question: str, keywords: Dict[str, Dict]) -> str:
    normalized = _normalize(question)
    aliases = _build_keyword_aliases()
    
    for key, tokens in aliases.items():
        for token in tokens:
            if _normalize(token) in normalized:
                if key in keywords:
                    return key
    return ""


def _answer_query(summary: Dict, question: str) -> str:
    product_type_str = summary.get("product_type", "기타")
    try:
        product_type = ProductType(product_type_str)
    except ValueError:
        product_type = ProductType.기타
    
    keywords = summary.get("keywords", {})
    key = _find_keyword_key(question, keywords)
    
    if not key:
        available = ", ".join(keywords.keys())
        return f"죄송합니다. 질문과 일치하는 정보를 찾지 못했습니다.\n알려드릴 수 있는 정보: {available}"
    
    if not is_keyword_valid_for_type(product_type, key):
        type_desc = get_type_description(product_type)
        return f"이 제품은 '{type_desc}'이므로 '{key}'에 대한 정보는 없습니다."
    
    item = keywords.get(key, {})
    status = item.get("status", "not_found")
    answer = item.get("answer", "OCR 텍스트에 없음")
    
    if status != "found":
        return f"죄송합니다. '{key}'에 대한 정보가 포장에 적혀있지 않습니다."
        
    return f"{key}: {answer}"


def main() -> int:
    parser = argparse.ArgumentParser(description="OCR 결과를 분석하여 JSON으로 요약")
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--query", default="")
    args = parser.parse_args()

    if args.query:
        if not os.path.exists(args.output):
            print(f"오류: 요약 파일({args.output})을 찾을 수 없습니다.")
            return 1
        with open(args.output, "r", encoding="utf-8") as f:
            summary = json.load(f)
        print(_answer_query(summary, args.query))
        return 0

    print(f"분석 시작: {args.input}")
    
    texts, _ = _load_ocr_texts(args.input)
    if not texts:
        print("오류: 유효한 OCR 텍스트가 없습니다.")
        return 1

    product_type = detect_product_type(texts)
    type_desc = get_type_description(product_type)
    print(f"감지된 제품 타입: {product_type.value} ({type_desc})")
    print(f"추출 목표 키워드: {', '.join(get_keywords_for_type(product_type))}")

    prompt = _build_prompt(texts, product_type)
    
    print("LLM 분석 중...", end="", flush=True)
    summary = _call_openai(prompt)
    print(" 완료!")
    
    summary["source_file"] = args.input
    _write_json(args.output, summary)
    print(f"요약 결과가 저장되었습니다: {args.output}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
