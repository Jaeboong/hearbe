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
    
    system = (
        "당신은 시각장애인 사용자에게 제품을 대신 읽어주는 **따뜻하고 친절한 쇼핑 친구**이자, "
        "안전을 책임지는 **꼼꼼한 확인자**입니다. "
        "기계적인 요약 대신 **사용자가 바로 옆에 있는 것처럼** 제품의 매력(맛, 식감, 특징)을 생생하게 설명하세요. "
        "단, 안전과 직결된 **숫자, 유통기한, 알레르기 성분은 절대로 추측하지 말고** OCR 텍스트에 적힌 그대로 정확하게 전달해야 합니다."
    )
    
    instructions = (
        "다음 OCR 텍스트를 분석하여 친구에게 말해주듯이 JSON 형식으로 응답하세요.\n\n"
        "**💡 1단계: 냉철한 팩트 체크 (Strict Check)**\n"
        "- **추측 금지**: 텍스트에 없는 내용을 상상해서 채워 넣지 마세요.\n"
        "- **숫자/단위**: 용량(g, ml), 칼로리(kcal), 개수 등은 텍스트 그대로 정확히 찾으세요.\n"
        "- **안전 정보**: 유통기한, 보관방법, 알레르기 주의사항은 **원문 그대로** 추출하세요. '밀가루'가 '말가루'로 오인식 된 것처럼 **명백한 오타만** 문맥에 맞게 수정하세요.\n\n"
        "**� 2단계: 매력 포인트 발견 (Rich Description)**\n"
        "- 딱딱한 스펙 외에, 포장지에 적힌 **설명 문구**를 적극적으로 찾으세요.\n"
        "- 예: \"진한 풍미\", \"부드러운 식감\", \"깊은 맛\", \"국산 원료 사용\" 등.\n"
        "- 단순히 \"스프입니다\"라고 하지 말고, **\"진한 버섯 풍미가 가득한 포르치니 스프\"**라고 설명해 주세요.\n\n"
        "**✍️ 3단계: 친절한 말하기 (요약 작성)**\n"
        "다음 흐름으로 **3~6문장**의 이야기를 들려주세요. (딱딱한 \"~다\"체 금지, **\"~해요/네요\"체 사용**)\n"
        "1. **첫인상**: \"이건 [브랜드]의 **[제품명]**이에요. 포장지에 [매력 포인트/수식어]라고 적혀 있네요.\"\n"
        "2. **상세 설명**: \"용량은 [용량]이고, 칼로리는 [열량]이라서 [용도추천]으로 좋을 것 같아요. [맛/식감 묘사]가 특징이라고 해요.\"\n"
        "3. **사용법**: \"조리법도 간단해요. [조리법 내용]하면 된답니다.\"\n"
        "4. **안전 챙김**: \"아, 그리고 [알레르기/주의사항]이 있으니 꼼꼼히 확인해 주세요!\" (없으면 생략)\n\n"
        "**출력 JSON 형식:**\n"
        "{\n"
        "  \"product_type\": \"자동 감지한 제품군\",\n"
        "  \"product_name\": \"제품명\",\n"
        "  \"confidence\": 1.0,\n"
        "  \"summary\": [\n"
        "    \"이야기하듯 작성한 첫 번째 문장\",\n"
        "    \"두 번째 문장\",\n"
        "    \"세 번째 문장...\"\n"
        "  ],\n"
        "  \"keywords\": {\n"
        "    \"키워드1(예: 조리법)\": { \"answer\": \"내용\", \"status\": \"found|not_found\" },\n"
        "    \"키워드2(예: 칼로리)\": { \"answer\": \"내용\", \"status\": \"found|not_found\" },\n"
        "    \"키워드3(자동생성)\": { \"answer\": \"내용\", \"status\": \"found|not_found\" }\n"
        "  }\n"
        "}\n"
    )
    
    user = "분석할 OCR 텍스트:\n" + numbered
    
    return {"system": system, "instructions": instructions, "user": user}


def _call_openai(prompt: Dict[str, str], max_retries: int = 3) -> Dict:
    api_key = os.environ.get("GMS_KEY")
    if not api_key:
        raise RuntimeError("GMS_KEY 환경변수가 설정되지 않았습니다.")

    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
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
        "temperature": 0.1,
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
