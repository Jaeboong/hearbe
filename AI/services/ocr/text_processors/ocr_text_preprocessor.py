"""
OCR 텍스트 전처리 모듈 (OCR Text Preprocessing Module)

이 모듈은 OCR(광학 문자 인식) 결과의 텍스트를 정제하고 필터링하는 **중앙 모듈**입니다.
다른 모듈(ocr_text_merger.py, ocr_llm_summarizer.py 등)에서 import하여 사용합니다.

주요 기능:
- 텍스트 정규화 (normalize_text)
- 의미 있는 텍스트 판별 (is_meaningful_text)
- 점수/길이/패턴 기반 필터링 (filter_texts)
- 전처리 통계 포함 처리 (preprocess_ocr_texts)

사용 예시:
    from ocr_text_preprocessor import normalize_text, is_meaningful_text, filter_texts
"""

import re
from typing import Dict, List, Tuple


# =============================================================================
# 공개 API (Public API) - 다른 모듈에서 import하여 사용
# =============================================================================

def normalize_text(text: str) -> str:
    """
    중복 비교를 위한 텍스트 정규화.
    
    특수문자, 공백을 제거하고 소문자로 변환합니다.
    유사도 비교나 중복 검사에 사용됩니다.
    
    Args:
        text: 정규화할 텍스트
        
    Returns:
        str: 정규화된 텍스트 (한글/영문/숫자만 포함, 소문자)
        
    Example:
        >>> normalize_text("Hello, 안녕! 123")
        'hello안녕123'
    """
    return re.sub(r"[^0-9a-zA-Z가-힣]", "", text).lower()


def is_meaningful_text(text: str) -> bool:
    """
    텍스트에 의미 있는 한글이나 영어가 포함되어 있는지 확인합니다.
    
    Args:
        text: 검사할 텍스트 문자열
        
    Returns:
        bool: 의미 있는 텍스트이면 True, 아니면 False
    """
    # 1. 최소한 하나의 한글 음절이나 영어 단어가 포함되어야 합니다.
    # [가-힣]: 모든 완성형 한글 문자를 찾는 정규식 패턴입니다.
    has_korean = bool(re.search(r'[가-힣]', text))
    
    # [a-zA-Z]{2,}: 알파벳이 2글자 이상 연속으로 나오는 패턴을 찾습니다 (단어로 인식).
    has_english_word = bool(re.search(r'[a-zA-Z]{2,}', text))
    
    # 2. 특수문자나 숫자만 있는 경우를 걸러내기 위해 비율을 계산합니다.
    # 한글, 영문, 숫자 개수를 셉니다.
    alphanumeric_count = len(re.findall(r'[가-힣a-zA-Z0-9]', text))
    
    # 전체 텍스트 길이 대비 유효 문자의 비율을 계산합니다. (0으로 나누기 방지 위해 max 사용)
    alphanumeric_ratio = alphanumeric_count / max(len(text), 1)
    
    # 한글/영어가 포함되어 있고, 유효 문자 비율이 50%를 넘어야 의미 있는 텍스트로 판단합니다.
    return (has_korean or has_english_word) and alphanumeric_ratio > 0.5


def filter_texts(
    texts: List[str],
    scores: List[float],
    min_score: float = 0.7,
    min_length: int = 2,
) -> List[Tuple[str, float]]:
    """
    점수/길이/패턴 기준으로 텍스트를 필터링합니다.
    
    ocr_text_merger.py 등 다른 모듈에서 import하여 사용하는 공용 API입니다.
    preprocess_ocr_texts()보다 간단한 버전으로, 통계 없이 필터링만 수행합니다.
    
    Args:
        texts: OCR로 인식된 텍스트 리스트
        scores: 각 텍스트에 대한 신뢰도 점수 리스트
        min_score: 최소 신뢰도 임계값 (기본: 0.7)
        min_length: 최소 텍스트 길이 (기본: 2)
        
    Returns:
        List[Tuple[str, float]]: [(텍스트, 점수), ...] 형태의 필터링된 리스트
        
    Example:
        >>> from ocr_text_preprocessor import filter_texts
        >>> filtered = filter_texts(["안녕하세요", "a", "!!!"], [0.9, 0.8, 0.5], min_score=0.7)
        >>> # [("안녕하세요", 0.9)]
    """
    filtered: List[Tuple[str, float]] = []
    
    for text, score in zip(texts, scores):
        if not isinstance(text, str):
            continue
        text = text.strip()
        if not text:
            continue
        if score < min_score:
            continue
        if len(text) < min_length:
            continue
        if not is_meaningful_text(text):
            continue
        filtered.append((text, score))
    
    return filtered


# =============================================================================
# 상세 전처리 (통계 포함)
# =============================================================================

def preprocess_ocr_texts(
    texts: List[str],
    scores: List[float],
    min_score: float = 0.7,
    min_length: int = 2,
    verbose: bool = True
) -> Tuple[List[str], Dict]:
    """
    OCR 텍스트를 전처리하여 노이즈와 신뢰도가 낮은 결과를 필터링합니다.
    
    이 함수는 다음과 같은 기준으로 텍스트를 걸러냅니다:
    1. 신뢰도(Confidence Score)가 기준치(min_score) 미만인 경우
    2. 텍스트 길이(Length)가 기준치(min_length) 미만인 경우
    3. 의미 있는 패턴(한글/영어 포함 여부 등)이 없는 경우
    4. 중복된 텍스트
    
    Args:
        texts: OCR로 인식된 텍스트 리스트
        scores: 각 텍스트에 대한 신뢰도 점수 리스트 (0~1 사이)
        min_score: 최소 신뢰도 임계값 (기본값: 0.7) - 이보다 낮으면 버려집니다.
        min_length: 최소 텍스트 길이 (기본값: 2) - 이보다 짧으면 버려집니다.
        verbose: 처리 통계 출력 여부 (기본값: True)
        
    Returns:
        Tuple[List[str], Dict]: (정제된 텍스트 리스트, 처리 통계 딕셔너리)
    """
    # 입력 데이터 유효성 검사: 텍스트와 점수의 개수가 일치해야 합니다.
    if len(texts) != len(scores):
        raise ValueError(f"texts와 scores의 길이가 같아야 합니다: {len(texts)} vs {len(scores)}")
    
    cleaned = []  # 정제된 텍스트를 담을 리스트
    filtered_examples = {  # 필터링된 예시를 저장할 딕셔너리 (디버깅용)
        "by_score": [],    # 점수 미달로 걸러진 예시
        "by_length": [],   # 길이 미달로 걸러진 예시
        "by_pattern": []   # 패턴 불일치로 걸러진 예시
    }
    
    # 전처리 통계를 집계할 딕셔너리 
    stats = {
        "original_count": len(texts),  # 원본 개수
        "filtered_by_score": 0,        # 점수 미달 개수
        "filtered_by_length": 0,       # 길이 미달 개수
        "filtered_by_pattern": 0,      # 패턴 필터링 개수
        "duplicates_removed": 0,       # 중복 제거 개수
        "final_count": 0               # 최종 개수
    }
    
    # 모든 텍스트와 점수를 순회하며 필터링을 수행합니다.
    for text, score in zip(texts, scores):
        original_text = text
        text = text.strip()  # 앞뒤 공백 제거
        
        # 1. 신뢰도 점수(Confidence Score) 검사
        if score < min_score:
            stats["filtered_by_score"] += 1
            # 예시는 최대 3개까지만 저장합니다.
            if len(filtered_examples["by_score"]) < 3:
                filtered_examples["by_score"].append(f'"{text}" (점수: {score:.2f})')
            continue  # 다음 텍스트로 넘어갑니다.
            
        # 2. 텍스트 길이 검사
        if len(text) < min_length:
            stats["filtered_by_length"] += 1
            if len(filtered_examples["by_length"]) < 3:
                filtered_examples["by_length"].append(f'"{text}" (길이: {len(text)})')
            continue
            
        # 3. 패턴 검사 (의미 있는 텍스트인지 확인)
        # is_meaningful_text 함수를 호출하여 내용을 검사합니다.
        if not is_meaningful_text(text):
            stats["filtered_by_pattern"] += 1
            if len(filtered_examples["by_pattern"]) < 3:
                filtered_examples["by_pattern"].append(f'"{text}"')
            continue
            
        # 모든 검사를 통과하면 결과 리스트에 추가합니다.
        cleaned.append(text)
    
    # 4. 중복 제거
    # 순서를 유지하면서 중복을 제거하기 위해 dict.fromkeys()를 사용합니다.
    original_cleaned_count = len(cleaned)
    cleaned = list(dict.fromkeys(cleaned))
    stats["duplicates_removed"] = original_cleaned_count - len(cleaned)
    stats["final_count"] = len(cleaned)
    
    # 통계 출력 (verbose가 True일 경우)
    if verbose:
        print("\n=== OCR 텍스트 전처리 통계 (OCR Text Preprocessing Statistics) ===")
        print(f"원본 텍스트 개수: {stats['original_count']}")
        print(f"점수 미달로 제외됨 (< {min_score}): {stats['filtered_by_score']}")
        if filtered_examples["by_score"]:
            print(f"  예시: {', '.join(filtered_examples['by_score'])}")
        print(f"길이 미달로 제외됨 (< {min_length}): {stats['filtered_by_length']}")
        if filtered_examples["by_length"]:
            print(f"  예시: {', '.join(filtered_examples['by_length'])}")
        print(f"패턴 필터링으로 제외됨 (의미 없음): {stats['filtered_by_pattern']}")
        if filtered_examples["by_pattern"]:
            print(f"  예시: {', '.join(filtered_examples['by_pattern'])}")
        print(f"중복 제거됨: {stats['duplicates_removed']}")
        print(f"최종 정제된 텍스트 개수: {stats['final_count']}")
        
        # 얼마나 줄어들었는지 감소율 계산
        reduction_count = stats['original_count'] - stats['final_count']
        reduction_rate = (1 - stats['final_count'] / max(stats['original_count'], 1)) * 100
        print(f"감소량: {reduction_count}개 텍스트 ({reduction_rate:.1f}% 감소)")
        print("=" * 60 + "\n")
    
    return cleaned, stats


def load_and_preprocess_ocr_json(
    json_data: Dict,
    min_score: float = 0.7,
    min_length: int = 2,
    verbose: bool = True
) -> Tuple[List[str], Dict]:
    """
    OCR 결과 JSON 데이터를 로드하고 전처리합니다.
    외부에서 호출하기 편하도록 만든 래퍼(Wrapper) 함수입니다.
    
    Args:
        json_data: OCR 결과가 담긴 JSON 딕셔너리
        min_score: 최소 신뢰도 임계값
        min_length: 최소 텍스트 길이
        verbose: 통계 출력 여부
        
    Returns:
        Tuple[List[str], Dict]: (정제된 텍스트 리스트, 처리 통계)
    """
    # JSON에서 텍스트 목록과 점수 목록을 추출합니다.
    texts = json_data.get("rec_texts", [])
    scores = json_data.get("rec_scores", [])
    
    # 텍스트 데이터가 없으면 에러를 발생시킵니다.
    if not texts:
        raise ValueError("JSON 데이터에 'rec_texts'가 없습니다.")
    
    # 점수 데이터가 없는 경우 (예: 일부 OCR 엔진), 모든 점수를 1.0(최고점)으로 가정합니다.
    if not scores:
        if verbose:
            print("참고: 'rec_scores'가 없어 모든 텍스트의 점수를 1.0으로 가정합니다.")
        scores = [1.0] * len(texts)
    
    # 실제 전처리 로직을 수행하는 함수를 호출합니다.
    return preprocess_ocr_texts(texts, scores, min_score, min_length, verbose)


if __name__ == "__main__":
    # 이 파일을 직접 실행했을 때의 동작 (테스트 용도)
    import json
    import sys
    
    # 명령줄 인자로 파일 경로를 받지 않았을 경우 사용법 출력
    if len(sys.argv) < 2:
        print("사용법: python ocr_text_preprocessor.py <ocr_json_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # 지정된 JSON 파일을 엽니다.
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 전처리 함수 실행
    cleaned_texts, stats = load_and_preprocess_ocr_json(data, verbose=True)
    
    # 결과 출력
    print("\n정제된 텍스트 목록:")
    for i, text in enumerate(cleaned_texts, 1):
        print(f"{i}. {text}")

