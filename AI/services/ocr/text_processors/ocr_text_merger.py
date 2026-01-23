# -*- coding: utf-8 -*-
"""
OCR 텍스트 병합 모듈

여러 OCR 결과의 텍스트를 점수 기반으로 병합하고 중복을 제거합니다.
OCR 처리는 korean_ocr.py에서 수행하고, 이 모듈은 텍스트 병합만 담당합니다.
텍스트 전처리는 ocr_text_preprocessor.py에서 import하여 사용합니다.

=============================================================================
사용 방법
=============================================================================

1. 병렬 OCR 결과 병합 (권장):
    from korean_ocr import process_images_parallel
    from ocr_text_merger import merge_ocr_results
    
    # OCR 처리 (korean_ocr에서)
    ocr_results = process_images_parallel(["img1.jpg", "img2.jpg"], max_workers=4)
    
    # 텍스트 병합 (이 모듈)
    merged = merge_ocr_results(ocr_results)
    print(merged["rec_texts"])

2. JSON 파일에서 병합:
    from ocr_text_merger import merge_ocr_texts
    
    merged = merge_ocr_texts(
        inputs=["result1.json", "result2.json"],
        min_score=0.7,
        similarity_threshold=0.9
    )

3. CLI 사용:
    python ocr_text_merger.py --inputs result1.json result2.json --output merged.json
"""

import argparse
import json
import os
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Any

# =============================================================================
# 텍스트 전처리 모듈에서 공용 함수 import
# =============================================================================
try:
    from .ocr_text_preprocessor import normalize_text, filter_texts
except ImportError:
    from ocr_text_preprocessor import normalize_text, filter_texts


# =============================================================================
# 텍스트 병합
# =============================================================================

def _merge_entries(
    entries: Iterable[Dict],
    similarity_threshold: float,
) -> List[Dict]:
    """정규화 및 유사도 기준으로 중복 병합."""
    merged: List[Dict] = []
    for entry in entries:
        text = entry.get("text", "")
        score = float(entry.get("score", 1.0))
        source = entry.get("source")
        norm = normalize_text(text)
        if not norm:
            continue

        match_idx = None
        for idx, existing in enumerate(merged):
            if norm == existing["norm"]:
                match_idx = idx
                break
            if similarity_threshold > 0:
                ratio = SequenceMatcher(None, norm, existing["norm"]).ratio()
                if ratio >= similarity_threshold:
                    match_idx = idx
                    break

        if match_idx is None:
            merged.append(
                {
                    "text": text,
                    "score": score,
                    "sources": [source] if source else [],
                    "norm": norm,
                }
            )
        else:
            existing = merged[match_idx]
            if score > existing["score"]:
                existing["text"] = text
                existing["score"] = score
            if source and source not in existing["sources"]:
                existing["sources"].append(source)

    for item in merged:
        item.pop("norm", None)
    return merged


# =============================================================================
# OCR 결과 병합 (주요 API)
# =============================================================================

def merge_ocr_results(
    ocr_results: List[Dict[str, Any]],
    min_score: float = 0.7,
    min_length: int = 2,
    similarity_threshold: float = 0.9,
) -> Dict:
    """
    OCR 결과 리스트를 받아 텍스트를 병합합니다.
    
    korean_ocr.process_image() 또는 process_images_parallel()의 결과를 받아
    텍스트를 병합하고 중복을 제거합니다.
    
    Args:
        ocr_results: OCR 결과 Dict 리스트. 각 Dict는 다음 형태:
            - rec_texts: 텍스트 리스트
            - rec_scores: 신뢰도 리스트
            - source (optional): 소스 식별자
        min_score: 최소 신뢰도 (기본: 0.7)
        min_length: 최소 텍스트 길이 (기본: 2)
        similarity_threshold: 중복 판정 유사도 임계값 (기본: 0.9)
        
    Returns:
        Dict: 병합된 결과
            - rec_texts: 병합된 텍스트 리스트
            - rec_scores: 해당 신뢰도 리스트
            - items: 상세 정보 (텍스트, 점수, 소스)
            - count: 병합된 텍스트 수
            
    Example:
        >>> from korean_ocr import process_images_parallel
        >>> from ocr_text_merger import merge_ocr_results
        >>> 
        >>> results = process_images_parallel(["img1.jpg", "img2.jpg"])
        >>> merged = merge_ocr_results(results)
        >>> print(merged["rec_texts"])
    """
    entries: List[Dict] = []
    
    for result in ocr_results:
        texts = result.get("rec_texts", []) or []
        scores = result.get("rec_scores", []) or [1.0] * len(texts)
        source = result.get("source", None)
        
        filtered = filter_texts(texts, scores, min_score, min_length)
        for text, score in filtered:
            entries.append({"text": text, "score": score, "source": source})
    
    merged = _merge_entries(entries, similarity_threshold)
    
    return {
        "rec_texts": [item["text"] for item in merged],
        "rec_scores": [item["score"] for item in merged],
        "items": merged,
        "count": len(merged),
    }


# =============================================================================
# JSON 파일 기반 병합
# =============================================================================

def _load_json_texts(path: str) -> Tuple[List[str], List[float]]:
    """OCR JSON 파일에서 텍스트/점수 로드."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    texts = data.get("rec_texts", []) or []
    scores = data.get("rec_scores", []) or []
    if not scores:
        scores = [1.0] * len(texts)
    return texts, scores


def merge_ocr_texts(
    inputs: List[str],
    min_score: float = 0.7,
    min_length: int = 2,
    similarity_threshold: float = 0.9,
) -> Dict:
    """
    여러 JSON 파일의 OCR 텍스트를 병합합니다.
    
    Args:
        inputs: OCR 결과 JSON 파일 경로 리스트
        min_score: 최소 신뢰도 (기본: 0.7)
        min_length: 최소 텍스트 길이 (기본: 2)
        similarity_threshold: 중복 판정 유사도 임계값 (기본: 0.9)
        
    Returns:
        Dict: 병합된 결과
    """
    ocr_results = []
    for json_path in inputs:
        texts, scores = _load_json_texts(json_path)
        ocr_results.append({
            "rec_texts": texts,
            "rec_scores": scores,
            "source": Path(json_path).name
        })
    
    return merge_ocr_results(
        ocr_results,
        min_score=min_score,
        min_length=min_length,
        similarity_threshold=similarity_threshold
    )


# =============================================================================
# 유틸리티
# =============================================================================

def _write_json(path: str, data: Dict) -> None:
    """JSON 결과 저장."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =============================================================================
# CLI
# =============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="여러 OCR JSON 파일의 텍스트를 병합합니다."
    )
    parser.add_argument(
        "--inputs", nargs="+", required=True, 
        help="OCR 결과 JSON 파일 경로들"
    )
    parser.add_argument(
        "--output", 
        default=os.path.join("output", "merged_ocr_texts.json"),
        help="출력 파일 경로"
    )
    parser.add_argument("--min-score", type=float, default=0.7)
    parser.add_argument("--min-length", type=int, default=2)
    parser.add_argument("--similarity-threshold", type=float, default=0.9)
    args = parser.parse_args()

    result = merge_ocr_texts(
        inputs=args.inputs,
        min_score=args.min_score,
        min_length=args.min_length,
        similarity_threshold=args.similarity_threshold,
    )
    _write_json(args.output, result)
    print(f"병합 완료: {result['count']}개 텍스트 -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
