import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from typing import Dict, List, Tuple

# ==========================================
# 사용자 정의 모듈 임포트
# ==========================================

# 제품 타입을 감지하고 관련 키워드를 가져오는 모듈을 임포트합니다.
from product_type_detector import (
    ProductType,              # 제품 타입 열거형 (Enum)
    detect_product_type,      # 텍스트 기반 제품 타입 감지 함수
    get_keywords_for_type,    # 타입별 추출 키워드 반환 함수
    get_type_description,     # 타입별 한글 설명 반환 함수
    is_keyword_valid_for_type # 키워드 유효성 검사 함수
)

# ==========================================
# 환경 변수 로드 (.env)
# ==========================================
try:
    from dotenv import load_dotenv
    # 현재 스크립트가 있는 디렉토리의 .env 파일을 찾습니다.
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # python-dotenv 패키지가 없는 경우 경고를 출력하고 시스템 환경변수만 사용합니다.
    print("경고: python-dotenv가 설치되지 않았습니다. pip install python-dotenv 로 설치해주세요.")
    print("시스템 환경변수만 사용합니다.")


# ==========================================
# 기본 설정 상수
# ==========================================
# 입력 파일 기본 경로 (테스트용)
DEFAULT_INPUT = os.path.join("output", "샴푸_res_texts.json")
# 출력 파일 기본 경로
DEFAULT_OUTPUT = os.path.join("output", "샴푸_texts_summary.json")

# 텍스트 전처리 모듈 임포트 시도
try:
    # OCR 텍스트 전처리기를 가져옵니다. (노이즈 제거, 신뢰도 낮은 텍스트 필터링 등)
    from ocr_text_preprocessor import load_and_preprocess_ocr_json
    PREPROCESSOR_AVAILABLE = True
except ImportError:
    # 모듈이 없으면 전처리 없이 진행하도록 플래그를 설정합니다.
    PREPROCESSOR_AVAILABLE = False
    print("경고: ocr_text_preprocessor 모듈을 찾을 수 없습니다. OCR 텍스트 전처리가 건너뛰어집니다.")


def _load_ocr_texts(path: str, preprocess: bool = True) -> Tuple[List[str], Dict]:
    """
    JSON 파일에서 OCR 텍스트를 로드하고, 선택적으로 전처리를 수행합니다.
    
    Args:
        path: OCR 결과 JSON 파일 경로
        preprocess: 텍스트 전처리 수행 여부 (기본값: True)
        
    Returns:
        Tuple[List[str], Dict]: (정제된 텍스트 리스트, 원본 JSON 데이터)
    """
    # 1. JSON 파일 읽기
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 2. 전처리 수행 (모듈이 있고, 수행 옵션이 켜져 있을 때)
    if preprocess and PREPROCESSOR_AVAILABLE:
        # load_and_preprocess_ocr_json 함수를 통해 텍스트를 정제합니다.
        # min_score=0.7: 신뢰도 70% 미만 제거
        # min_length=2: 2글자 미만 제거
        texts, stats = load_and_preprocess_ocr_json(data, min_score=0.7, min_length=2, verbose=True)
    else:
        # 3. 전처리 없이 단순 로드 (Fallback)
        # rec_texts 키에서 텍스트 리스트를 가져옵니다. 없으면 빈 리스트를 반환합니다.
        texts = data.get("rec_texts") or []
        # 문자열이 아니거나 빈 문자열인 경우 제거합니다.
        texts = [t.strip() for t in texts if isinstance(t, str) and t.strip()]
    
    return texts, data


def _build_prompt(texts: List[str], product_type: ProductType) -> Dict[str, str]:
    """
    LLM(거대 언어 모델)에게 보낼 프롬프트(질문)를 구성합니다.
    제품 타입에 맞춰 추출해야 할 키워드를 동적으로 변경합니다.
    
    Args:
        texts: OCR로 추출된 텍스트 리스트
        product_type: 감지된 제품 타입 (예: FOOD_FRESH, HEALTH_MEDICINE 등)
        
    Returns:
        Dict[str, str]: 시스템 메시지, 사용자 메시지 등이 포함된 프롬프트 딕셔너리
    """
    # 텍스트 리스트를 번호를 매겨 하나의 문자열로 합칩니다.
    # 예: "1. 오겹살\n2. 100g당 2000원..."
    numbered = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(texts))
    
    # 해당 제품 타입에 맞는 키워드 리스트를 가져옵니다.
    keywords = get_keywords_for_type(product_type)
    
    # 제품 타입에 대한 한글 설명을 가져옵니다.
    type_desc = get_type_description(product_type)
    
    # 키워드 스키마(JSON 구조)를 동적으로 생성합니다.
    keyword_lines = []
    for i, kw in enumerate(keywords):
        if i == 0:
            # 첫 번째 키워드는 예시를 보여주기 위해 상세히 적습니다.
            keyword_lines.append(f'    "{kw}": {{ "answer": "...", "evidence": ["..."], "status": "found|not_found" }}')
        else:
            # 나머지 키워드는 형식만 맞춥니다.
            keyword_lines.append(f'    "{kw}": {{...}}')
    keyword_schema = ",\n".join(keyword_lines)
    
    # 시스템 프롬프트: AI의 역할과 제약조건을 정의합니다.
    system = (
        "당신은 시각장애인을 위해 한국어 OCR 텍스트를 요약하고 분석하는 어시스턴트입니다. "
        "반드시 유효한 JSON 형식으로만 응답하세요. 다른 설명이나 인사말을 추가하지 마세요."
    )
    
    # 지시사항(Instructions): 구체적으로 무엇을 해야 하는지 설명합니다.
    instructions = (
        f"당신은 지금 '{type_desc} ({product_type.value})' 제품을 분석하고 있습니다.\n"
        f"다음 키워드들에 대한 정보를 추출하세요: {', '.join(keywords)}\n\n"
        "반드시 제공된 OCR 텍스트 내용에 기반해서만 답해야 합니다. "
        "만약 해당 키워드에 대한 정보가 텍스트에 없다면, status를 \"not_found\"로 하고 "
        "answer를 \"OCR 텍스트에 없음\"이라고 적으세요.\n\n"
        "출력할 JSON 형식:\n"
        "{\n"
        f'  "product_type": "{product_type.value}",\n'
        '  "product_name": "제품명 (찾을 수 없으면 \'알 수 없음\')",\n'
        '  "confidence": 0.0-1.0 (OCR 품질 기반 신뢰도),\n'
        '  "summary": ["핵심 요약 문장 1", "핵심 요약 문장 2", "핵심 요약 문장 3"],\n'
        '  "keywords": {\n'
        f"{keyword_schema}\n"
        "  }\n"
        "}\n"
        "요약(summary)은 3-5문장으로 짧고 간결하게 작성하세요. 시각장애인이 듣기 편한 말투를 사용하세요."
    )
    
    # 사용자 메시지: 실제 분석할 데이터를 전달합니다.
    user = "분석할 OCR 텍스트:\n" + numbered
    
    return {"system": system, "instructions": instructions, "user": user}


def _call_openai(prompt: Dict[str, str], max_retries: int = 3) -> Dict:
    """
    SSAFY GMS API (OpenAI 호환)를 호출하여 LLM 응답을 받습니다.
    실패 시 재시도 로직이 포함되어 있습니다.
    
    Args:
        prompt: _build_prompt 함수에서 생성된 프롬프트
        max_retries: 최대 재시도 횟수 (기본값: 3)
        
    Returns:
        Dict: LLM이 생성한 JSON 응답 파싱 결과
    """
    # 환경변수에서 API 키를 가져옵니다.
    api_key = os.environ.get("GMS_KEY")
    if not api_key:
        raise RuntimeError("GMS_KEY 환경변수가 설정되지 않았습니다. .env 파일을 확인해주세요.")

    # 모델 설정 (기본값: gpt-5-mini)
    model = os.environ.get("OPENAI_MODEL", "gpt-5-mini")
    # SSAFY GMS API 엔드포인트 URL
    url = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"

    # API 요청 메시지 구성
    messages = [
        {
            "role": "developer", # GMS API는 developer 역할 사용
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
    # 재시도 루프
    for attempt in range(max_retries):
        try:
            # API 호출
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=(10, 120),  # (연결 타임아웃 10초, 읽기 타임아웃 120초)
            )
            if response.status_code >= 400:
                print(f"\n[DEBUG] HTTP {response.status_code} 에러")
                print(f"[DEBUG] 응답 본문: {response.text}")
            response.raise_for_status() # 4xx, 5xx 에러 발생 시 예외 송출
            raw = response.json()

            # 응답에서 내용 추출
            choices = raw.get("choices", [])
            if not choices:
                raise RuntimeError("LLM 응답에 choices가 없습니다.")
            
            output_text = choices[0].get("message", {}).get("content", "")
            if not output_text:
                raise RuntimeError("LLM 응답 내용이 비어있습니다.")

            # Markdown 코드 블록으로 감싸진 JSON 처리 (예: ```json ... ```)
            if output_text.strip().startswith("```"):
                lines = output_text.strip().split("\n")
                # 첫 줄(```json)과 마지막 줄(```) 제거
                output_text = "\n".join(lines[1:-1])

            # JSON 파싱 시도
            try:
                return json.loads(output_text)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"LLM 응답이 유효한 JSON이 아닙니다: {exc}") from exc

        except requests.exceptions.RequestException as e:
            last_error = e
            # 마지막 시도가 아니면 재시도 대기
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 지수 백오프: 1초, 2초, 4초... 대기
                print(f"API 요청 실패 (시도 {attempt + 1}/{max_retries}): {e}")
                print(f"{wait_time}초 후 재시도합니다...")
                time.sleep(wait_time)
            else:
                # 모든 시도 실패 시 예외 발생
                raise RuntimeError(f"LLM 요청이 {max_retries}회 재시도 후에도 실패했습니다: {last_error}") from last_error


def _write_json(path: str, data: Dict) -> None:
    """
    딕셔너리 데이터를 JSON 파일로 저장합니다.
    디렉토리가 없으면 자동으로 생성합니다.
    """
    dir_path = os.path.dirname(path)
    if dir_path:  # 빈 문자열이 아닐 때만 디렉토리 생성
        os.makedirs(dir_path, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        # ensure_ascii=False: 한글이 깨지지 않고 그대로 저장되도록 함
        # indent=2: 들여쓰기를 2칸으로 하여 보기 좋게 포맷팅
        json.dump(data, f, ensure_ascii=False, indent=2)


def _normalize(text: str) -> str:
    """
    문자열 정규화: 모든 공백을 제거하고 소문자로 변환합니다.
    검색이나 비교를 용이하게 하기 위함입니다.
    """
    return "".join(text.lower().split())


def _build_keyword_aliases() -> Dict[str, List[str]]:
    """
    검색 편의를 위한 키워드 별칭(Alias) 사전입니다.
    사용자가 '얼마에요?'라고 물어도 '가격' 키워드를 찾을 수 있게 합니다.
    """
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
    """
    사용자 질문에서 관련된 키워드 키(Key)를 찾습니다.
    
    Args:
        question: 사용자 질문 "이거 얼마야?"
        keywords: LLM이 추출한 키워드 데이터
        
    Returns:
        매칭된 키워드 키 (예: "가격") 또는 빈 문자열
    """
    normalized = _normalize(question)
    aliases = _build_keyword_aliases()
    
    # 1. 별칭 사전에서 매칭되는 키워드가 있는지 확인
    for key, tokens in aliases.items():
        for token in tokens:
            if _normalize(token) in normalized:
                # 추출된 키워드 목록에 해당 키가 존재할 경우 반환
                if key in keywords:
                    return key
    return ""


def _answer_query(summary: Dict, question: str) -> str:
    """
    생성된 요약 JSON을 바탕으로 사용자의 질문에 답변합니다.
    제품 타입에 따라 답변 불가능한 질문인지도 판단합니다.
    
    Args:
        summary: LLM이 생성한 요약 정보 JSON
        question: 사용자 질문
        
    Returns:
        답변 문자열
    """
    # 1. 제품 타입 확인
    product_type_str = summary.get("product_type", "OTHER")
    try:
        product_type = ProductType(product_type_str)
    except ValueError:
        product_type = ProductType.OTHER
    
    keywords = summary.get("keywords", {})
    
    # 2. 질문에 해당하는 키 찾기
    key = _find_keyword_key(question, keywords)
    
    # 3. 키워드를 못 찾았을 경우
    if not key:
        available = ", ".join(keywords.keys())
        return f"죄송합니다. 질문과 일치하는 정보를 찾지 못했습니다.\n알려드릴 수 있는 정보: {available}"
    
    # 4. 타입 기반 유효성 검사 (예: 공산품에 '맛'을 물어보면 답변 불가)
    if not is_keyword_valid_for_type(product_type, key):
        type_desc = get_type_description(product_type)
        return f"이 제품은 '{type_desc}'이므로 '{key}'에 대한 정보는 없습니다."
    
    # 5. 결과 반환
    item = keywords.get(key, {})
    status = item.get("status", "not_found")
    answer = item.get("answer", "OCR 텍스트에 없음")
    
    if status != "found":
        return f"죄송합니다. '{key}'에 대한 정보가 포장에 적혀있지 않습니다."
        
    return f"{key}: {answer}"


def main() -> int:
    # 명령줄 인자 파서 설정
    parser = argparse.ArgumentParser(description="OCR 결과를 분석하여 JSON으로 요약합니다.")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="입력 OCR JSON 파일 경로")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="출력 요약 JSON 파일 경로")
    parser.add_argument("--query", default="", help='요약된 JSON에 대해 질문할 때 사용 (예: "가격이 얼마야?")')
    args = parser.parse_args()

    # 모드 1: 질문 답변 모드 (이미 요약된 JSON이 있을 때)
    if args.query:
        if not os.path.exists(args.output):
            print(f"오류: 요약 파일({args.output})을 찾을 수 없습니다. 먼저 분석을 실행해주세요.")
            return 1
        with open(args.output, "r", encoding="utf-8") as f:
            summary = json.load(f)
        print(_answer_query(summary, args.query))
        return 0

    # 모드 2: 분석 및 요약 모드
    print(f"분석 시작: {args.input}")
    
    # 1. OCR 텍스트 로드 및 전처리
    texts, _ = _load_ocr_texts(args.input)
    if not texts:
        print("오류: 유효한 OCR 텍스트가 없습니다.")
        return 1

    # 2. 제품 타입 감지
    product_type = detect_product_type(texts)
    type_desc = get_type_description(product_type)
    print(f"감지된 제품 타입: {product_type.value} ({type_desc})")
    print(f"추출 목표 키워드: {', '.join(get_keywords_for_type(product_type))}")

    # 3. 프롬프트 구성
    prompt = _build_prompt(texts, product_type)
    
    # 4. LLM 호출 (OpenAI API)
    print("LLM 분석 중...", end="", flush=True)
    summary = _call_openai(prompt)
    print(" 완료!")
    
    # 5. 결과 저장
    summary["source_file"] = args.input # 원본 파일 정보 추가
    _write_json(args.output, summary)
    print(f"요약 결과가 저장되었습니다: {args.output}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
