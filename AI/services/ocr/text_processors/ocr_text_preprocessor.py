# OCR 텍스트 정제·필터링
import re
from typing import Callable, Dict, List, Optional, Tuple


def normalize_text(text: str) -> str:
    return re.sub(r"[^0-9a-zA-Z가-힣]", "", text).lower()


def is_meaningful_text(text: str) -> bool:
    has_korean = bool(re.search(r'[가-힣]', text))
    has_english_word = bool(re.search(r'[a-zA-Z]{2,}', text))
    alphanumeric_count = len(re.findall(r'[가-힣a-zA-Z0-9]', text))
    alphanumeric_ratio = alphanumeric_count / max(len(text), 1)
    return (has_korean or has_english_word) and alphanumeric_ratio > 0.5


def filter_texts(
    texts: List[str],
    scores: List[float],
    min_score: float = 0.7,
    min_length: int = 2,
    important_text_predicate: Optional[Callable[[str], bool]] = None,
) -> List[Tuple[str, float]]:
    filtered: List[Tuple[str, float]] = []
    
    for text, score in zip(texts, scores):
        if not isinstance(text, str):
            continue
        text = text.strip()
        if not text:
            continue
        if score < min_score:
            if not (important_text_predicate and important_text_predicate(text)):
                continue
        if len(text) < min_length:
            continue
        if not is_meaningful_text(text):
            continue
        filtered.append((text, score))
    
    return filtered


def preprocess_ocr_texts(
    texts: List[str],
    scores: List[float],
    min_score: float = 0.7,
    min_length: int = 2,
    verbose: bool = True
) -> Tuple[List[str], Dict]:
    if len(texts) != len(scores):
        raise ValueError(f"texts와 scores의 길이가 같아야 합니다: {len(texts)} vs {len(scores)}")
    
    cleaned = []
    filtered_examples = {
        "by_score": [],
        "by_length": [],
        "by_pattern": []
    }
    
    stats = {
        "original_count": len(texts),
        "filtered_by_score": 0,
        "filtered_by_length": 0,
        "filtered_by_pattern": 0,
        "duplicates_removed": 0,
        "final_count": 0
    }
    
    for text, score in zip(texts, scores):
        text = text.strip()
        
        if score < min_score:
            stats["filtered_by_score"] += 1
            if len(filtered_examples["by_score"]) < 3:
                filtered_examples["by_score"].append(f'"{text}" (점수: {score:.2f})')
            continue
            
        if len(text) < min_length:
            stats["filtered_by_length"] += 1
            if len(filtered_examples["by_length"]) < 3:
                filtered_examples["by_length"].append(f'"{text}" (길이: {len(text)})')
            continue
            
        if not is_meaningful_text(text):
            stats["filtered_by_pattern"] += 1
            if len(filtered_examples["by_pattern"]) < 3:
                filtered_examples["by_pattern"].append(f'"{text}"')
            continue
            
        cleaned.append(text)
    
    original_cleaned_count = len(cleaned)
    cleaned = list(dict.fromkeys(cleaned))
    stats["duplicates_removed"] = original_cleaned_count - len(cleaned)
    stats["final_count"] = len(cleaned)
    
    if verbose:
        print("\n=== OCR 텍스트 전처리 통계 ===")
        print(f"원본 텍스트 개수: {stats['original_count']}")
        print(f"점수 미달로 제외됨 (< {min_score}): {stats['filtered_by_score']}")
        if filtered_examples["by_score"]:
            print(f"  예시: {', '.join(filtered_examples['by_score'])}")
        print(f"길이 미달로 제외됨 (< {min_length}): {stats['filtered_by_length']}")
        if filtered_examples["by_length"]:
            print(f"  예시: {', '.join(filtered_examples['by_length'])}")
        print(f"패턴 필터링으로 제외됨: {stats['filtered_by_pattern']}")
        if filtered_examples["by_pattern"]:
            print(f"  예시: {', '.join(filtered_examples['by_pattern'])}")
        print(f"중복 제거됨: {stats['duplicates_removed']}")
        print(f"최종 정제된 텍스트 개수: {stats['final_count']}")
        
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
    texts = json_data.get("rec_texts", [])
    scores = json_data.get("rec_scores", [])
    
    if not texts:
        raise ValueError("JSON 데이터에 'rec_texts'가 없습니다.")
    
    if not scores:
        if verbose:
            print("참고: 'rec_scores'가 없어 모든 텍스트의 점수를 1.0으로 가정합니다.")
        scores = [1.0] * len(texts)
    
    return preprocess_ocr_texts(texts, scores, min_score, min_length, verbose)


def extract_rec_texts_from_data(data: Dict) -> List[str]:
    """OCR 결과 딕셔너리에서 유효한 텍스트만 추출"""
    rec_texts = data.get("rec_texts", [])
    cleaned = []
    for text in rec_texts:
        if not isinstance(text, str):
            continue
        text = text.strip()
        if not text:
            continue
        if not normalize_text(text):
            continue
        cleaned.append(text)
    return cleaned


if __name__ == "__main__":
    import json
    import sys
    
    if len(sys.argv) < 2:
        print("사용법: python ocr_text_preprocessor.py <ocr_json_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    cleaned_texts, stats = load_and_preprocess_ocr_json(data, verbose=True)
    
    print("\n정제된 텍스트 목록:")
    for i, text in enumerate(cleaned_texts, 1):
        print(f"{i}. {text}")
