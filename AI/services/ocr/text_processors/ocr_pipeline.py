# -*- coding: utf-8 -*-
"""
OCR 통합 파이프라인 (Unified OCR Pipeline)

이미지 입력 → OCR → 병합 → 전처리 → 텍스트 추출 → 타입 감지 → LLM 요약
전체 과정을 자동화하는 메인 진입점입니다.

=============================================================================
사용 방법
=============================================================================

1. 단일 이미지 처리:
    python ocr_pipeline.py --input image.jpg
    
2. 여러 이미지 병합 처리:
    python ocr_pipeline.py --inputs img1.jpg img2.jpg img3.jpg
    
3. 결과 저장 경로 지정:
    python ocr_pipeline.py --input image.jpg --output result.json

4. 코드에서 import:
    from ocr_pipeline import process_product_image, process_multiple_images
    
    result = process_product_image("샴푸.jpg")
    print(result["summary"])
"""

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

# =============================================================================
# 내부 모듈 import (직접 실행과 패키지 import 모두 지원)
# =============================================================================
try:
    from .korean_ocr import process_image, process_images_parallel
    from .ocr_text_preprocessor import filter_texts, preprocess_ocr_texts
    from .ocr_text_merger import merge_ocr_results
    from .product_type_detector import (
        ProductType,
        detect_product_type,
        get_type_description,
    )
    from .ocr_llm_summarizer import summarize_texts
except ImportError:
    from korean_ocr import process_image, process_images_parallel
    from ocr_text_preprocessor import filter_texts, preprocess_ocr_texts
    from ocr_text_merger import merge_ocr_results
    from product_type_detector import (
        ProductType,
        detect_product_type,
        get_type_description,
    )
    from ocr_llm_summarizer import summarize_texts


# =============================================================================
# 유틸리티 함수
# =============================================================================

def extract_texts_only(
    merged_result: Dict,
    min_score: float = 0.0
) -> List[str]:
    """
    병합 결과에서 텍스트만 추출합니다 (LLM 토큰 절약).
    
    Args:
        merged_result: merge_ocr_results() 또는 process_image()의 반환값
        min_score: 추가 신뢰도 필터 (기본: 0, 이미 필터링됨)
        
    Returns:
        List[str]: 텍스트만 담긴 리스트
    """
    texts = merged_result.get("rec_texts", [])
    scores = merged_result.get("rec_scores", [])
    
    if min_score > 0 and scores:
        return [
            text for text, score in zip(texts, scores)
            if score >= min_score
        ]
    return texts


def _save_json(data: Dict, output_path: str) -> None:
    """결과를 JSON 파일로 저장합니다."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =============================================================================
# 단일 이미지 처리 (병합 불필요)
# =============================================================================

def process_product_image(
    image_path: str,
    output_dir: str = "output",
    save_result: bool = True,
    verbose: bool = True
) -> Dict:
    """
    단일 이미지에 대한 전체 OCR 파이프라인 실행.
    
    Pipeline (5단계):
        1. OCR (korean_ocr) - 긴 이미지는 자동 분할 처리
        2. 전처리 (ocr_text_preprocessor)
        3. 텍스트 추출 (extract_texts_only)
        4. 타입 감지 (product_type_detector)
        5. LLM 요약 (ocr_llm_summarizer)
    
    Args:
        image_path: 입력 이미지 경로
        output_dir: 출력 디렉토리 (기본: output)
        save_result: 결과 JSON 저장 여부 (기본: True)
        verbose: 진행 상황 출력 여부 (기본: True)
        
    Returns:
        Dict: LLM 요약 결과
    """
    start_time = time.time()
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"🖼️  단일 이미지 처리 시작: {Path(image_path).name}")
        print(f"{'='*60}")
    
    # 1. OCR 처리 (긴 이미지는 자동 분할)
    if verbose:
        print("\n📝 [1/5] OCR 처리 중...")
    ocr_result = process_image(image_path, output_dir=output_dir)
    ocr_count = ocr_result.get("total_count", len(ocr_result.get("rec_texts", [])))
    if verbose:
        mode = ocr_result.get("processing_mode", "direct")
        print(f"    → 처리 모드: {'분할 처리' if mode == 'split' else '직접 처리'}")
        print(f"    → OCR 결과: {ocr_count}개 텍스트")
    
    # 2. 전처리 (노이즈/저신뢰도 제거)
    if verbose:
        print("\n🔧 [2/5] 전처리 중...")
    texts = ocr_result.get("rec_texts", [])
    scores = ocr_result.get("rec_scores", [1.0] * len(texts))
    
    # filter_texts 사용하여 필터링
    filtered = filter_texts(texts, scores, min_score=0.7, min_length=2)
    filtered_texts = [text for text, score in filtered]
    
    if verbose:
        print(f"    → 전처리 후: {len(filtered_texts)}개 텍스트 (원본: {len(texts)}개)")
    
    # 3. 텍스트 추출 (이미 완료)
    if verbose:
        print("\n✂️  [3/5] 텍스트 추출 완료 (LLM 토큰 절약)")
    
    # 4. 타입 감지
    if verbose:
        print("\n🏷️  [4/5] 제품 타입 감지 중...")
    product_type = detect_product_type(filtered_texts)
    type_desc = get_type_description(product_type)
    if verbose:
        print(f"    → 감지된 타입: {type_desc} ({product_type.value})")
    
    # 5. LLM 요약
    if verbose:
        print("\n🤖 [5/5] LLM 요약 중...")
    summary = summarize_texts(filtered_texts, product_type, verbose=verbose)
    
    # 메타 정보 추가
    elapsed_time = time.time() - start_time
    summary["source_image"] = str(image_path)
    summary["ocr_count"] = ocr_count
    summary["filtered_count"] = len(filtered_texts)
    summary["processing_time"] = round(elapsed_time, 2)
    
    # 결과 저장
    if save_result:
        base_name = Path(image_path).stem
        output_path = os.path.join(output_dir, f"{base_name}_summary.json")
        _save_json(summary, output_path)
        if verbose:
            print(f"\n💾 결과 저장: {output_path}")
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"✅ 완료! (소요 시간: {elapsed_time:.1f}초)")
        print(f"{'='*60}\n")
    
    return summary


# =============================================================================
# 다중 이미지 처리 (병합 필요)
# =============================================================================

def process_multiple_images(
    image_paths: List[str],
    output_dir: str = "output",
    max_workers: int = 4,
    save_result: bool = True,
    verbose: bool = True
) -> Dict:
    """
    여러 이미지를 병합하여 하나의 요약 생성.
    
    Pipeline (6단계):
        1. 병렬 OCR (korean_ocr.process_images_parallel)
        2. 병합 (ocr_text_merger.merge_ocr_results)
        3. 전처리 (ocr_text_preprocessor)
        4. 텍스트 추출 (extract_texts_only)
        5. 타입 감지 (product_type_detector)
        6. LLM 요약 (ocr_llm_summarizer)
    
    Args:
        image_paths: 입력 이미지 경로 리스트
        output_dir: 출력 디렉토리 (기본: output)
        max_workers: 병렬 처리 워커 수 (기본: 4)
        save_result: 결과 JSON 저장 여부 (기본: True)
        verbose: 진행 상황 출력 여부 (기본: True)
        
    Returns:
        Dict: 병합된 LLM 요약 결과
    """
    start_time = time.time()
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"🖼️  다중 이미지 처리 시작: {len(image_paths)}개 이미지")
        print(f"{'='*60}")
    
    # 1. 병렬 OCR 처리
    if verbose:
        print("\n📝 [1/6] 병렬 OCR 처리 중...")
    ocr_results = process_images_parallel(
        image_paths,
        max_workers=max_workers,
        output_dir=output_dir
    )
    total_ocr = sum(r.get("total_count", 0) for r in ocr_results)
    if verbose:
        print(f"    → 총 OCR 결과: {total_ocr}개 텍스트")
    
    # 2. 결과 병합
    if verbose:
        print("\n🔗 [2/6] 텍스트 병합 중...")
    merged = merge_ocr_results(ocr_results)
    if verbose:
        print(f"    → 병합 후: {merged['count']}개 텍스트 (중복 제거됨)")
    
    # 3. 전처리 (추가 필터링)
    if verbose:
        print("\n🔧 [3/6] 전처리 중...")
    texts = merged.get("rec_texts", [])
    scores = merged.get("rec_scores", [1.0] * len(texts))
    
    filtered = filter_texts(texts, scores, min_score=0.7, min_length=2)
    filtered_texts = [text for text, score in filtered]
    
    if verbose:
        print(f"    → 전처리 후: {len(filtered_texts)}개 텍스트")
    
    # 4. 텍스트 추출
    if verbose:
        print("\n✂️  [4/6] 텍스트 추출 완료 (LLM 토큰 절약)")
    
    # 5. 타입 감지
    if verbose:
        print("\n🏷️  [5/6] 제품 타입 감지 중...")
    product_type = detect_product_type(filtered_texts)
    type_desc = get_type_description(product_type)
    if verbose:
        print(f"    → 감지된 타입: {type_desc} ({product_type.value})")
    
    # 6. LLM 요약
    if verbose:
        print("\n🤖 [6/6] LLM 요약 중...")
    summary = summarize_texts(filtered_texts, product_type, verbose=verbose)
    
    # 메타 정보 추가
    elapsed_time = time.time() - start_time
    summary["source_images"] = [str(p) for p in image_paths]
    summary["image_count"] = len(image_paths)
    summary["ocr_count"] = total_ocr
    summary["merged_count"] = merged["count"]
    summary["filtered_count"] = len(filtered_texts)
    summary["processing_time"] = round(elapsed_time, 2)
    
    # 결과 저장
    if save_result:
        first_name = Path(image_paths[0]).stem
        output_path = os.path.join(output_dir, f"{first_name}_merged_summary.json")
        _save_json(summary, output_path)
        if verbose:
            print(f"\n💾 결과 저장: {output_path}")
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"✅ 완료! (소요 시간: {elapsed_time:.1f}초)")
        print(f"{'='*60}\n")
    
    return summary


# =============================================================================
# CLI 인터페이스
# =============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="OCR 통합 파이프라인: 이미지 → OCR → 전처리 → LLM 요약"
    )
    
    # 입력 옵션 (둘 중 하나 필수)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--input", "-i",
        help="단일 이미지 경로"
    )
    input_group.add_argument(
        "--inputs", "-I",
        nargs="+",
        help="여러 이미지 경로 (병합 처리)"
    )
    
    # 출력 옵션
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="출력 JSON 파일 경로"
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="출력 디렉토리 (기본: output)"
    )
    
    # 처리 옵션
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=4,
        help="병렬 처리 워커 수 (기본: 4)"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="결과 파일 저장하지 않음"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="진행 상황 출력하지 않음"
    )
    
    args = parser.parse_args()
    
    try:
        if args.input:
            # 단일 이미지 처리
            result = process_product_image(
                image_path=args.input,
                output_dir=args.output_dir,
                save_result=not args.no_save,
                verbose=not args.quiet
            )
        else:
            # 다중 이미지 처리
            result = process_multiple_images(
                image_paths=args.inputs,
                output_dir=args.output_dir,
                max_workers=args.workers,
                save_result=not args.no_save,
                verbose=not args.quiet
            )
        
        # 지정된 출력 경로가 있으면 추가 저장
        if args.output:
            _save_json(result, args.output)
            if not args.quiet:
                print(f"📄 추가 저장: {args.output}")
        
        # 요약 출력
        if not args.quiet:
            print("\n📋 요약 결과:")
            print(f"  제품명: {result.get('product_name', '알 수 없음')}")
            print(f"  타입: {result.get('product_type', 'OTHER')}")
            if "summary" in result:
                print("  요약:")
                for line in result["summary"]:
                    print(f"    - {line}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
