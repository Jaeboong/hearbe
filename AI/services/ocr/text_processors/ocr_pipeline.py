# -*- coding: utf-8 -*-
import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

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
    from .image_fetcher import (
        filter_product_images,
        download_images,
        detect_site,
        get_selector,
        list_supported_sites,
    )
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
    from image_fetcher import (
        filter_product_images,
        download_images,
        detect_site,
        get_selector,
        list_supported_sites,
    )


def extract_texts_only(
    merged_result: Dict,
    min_score: float = 0.0
) -> List[str]:
    texts = merged_result.get("rec_texts", [])
    scores = merged_result.get("rec_scores", [])
    
    if min_score > 0 and scores:
        return [
            text for text, score in zip(texts, scores)
            if score >= min_score
        ]
    return texts


def _save_json(data: Dict, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def process_product_image(
    image_path: str,
    output_dir: str = "output",
    save_result: bool = True,
    verbose: bool = True
) -> Dict:
    start_time = time.time()
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"🖼️  단일 이미지 처리 시작: {Path(image_path).name}")
        print(f"{'='*60}")
    
    if verbose:
        print("\n📝 [1/5] OCR 처리 중...")
    ocr_result = process_image(image_path, output_dir=output_dir)
    ocr_count = ocr_result.get("total_count", len(ocr_result.get("rec_texts", [])))
    if verbose:
        mode = ocr_result.get("processing_mode", "direct")
        print(f"    → 처리 모드: {'분할 처리' if mode == 'split' else '직접 처리'}")
        print(f"    → OCR 결과: {ocr_count}개 텍스트")
    
    if verbose:
        print("\n🔧 [2/5] 전처리 중...")
    texts = ocr_result.get("rec_texts", [])
    scores = ocr_result.get("rec_scores", [1.0] * len(texts))
    
    filtered = filter_texts(texts, scores, min_score=0.7, min_length=2)
    filtered_texts = [text for text, score in filtered]
    
    if verbose:
        print(f"    → 전처리 후: {len(filtered_texts)}개 텍스트 (원본: {len(texts)}개)")
    
    if verbose:
        print("\n✂️  [3/5] 텍스트 추출 완료 (LLM 토큰 절약)")
    
    if verbose:
        print("\n🏷️  [4/5] 제품 타입 감지 중...")
    product_type = detect_product_type(filtered_texts)
    type_desc = get_type_description(product_type)
    if verbose:
        print(f"    → 감지된 타입: {type_desc} ({product_type.value})")
    
    if verbose:
        print("\n🤖 [5/5] LLM 요약 중...")
    summary = summarize_texts(filtered_texts, product_type, verbose=verbose)
    
    elapsed_time = time.time() - start_time
    summary["source_image"] = str(image_path)
    summary["ocr_count"] = ocr_count
    summary["filtered_count"] = len(filtered_texts)
    summary["processing_time"] = round(elapsed_time, 2)
    
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


def process_multiple_images(
    image_paths: List[str],
    output_dir: str = "output",
    max_workers: int = 4,
    save_result: bool = True,
    verbose: bool = True
) -> Dict:
    start_time = time.time()
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"🖼️  다중 이미지 처리 시작: {len(image_paths)}개 이미지")
        print(f"{'='*60}")
    
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
    
    if verbose:
        print("\n🔗 [2/6] 텍스트 병합 중...")
    merged = merge_ocr_results(ocr_results)
    if verbose:
        print(f"    → 병합 후: {merged['count']}개 텍스트 (중복 제거됨)")
    
    if verbose:
        print("\n🔧 [3/6] 전처리 중...")
    texts = merged.get("rec_texts", [])
    scores = merged.get("rec_scores", [1.0] * len(texts))
    
    filtered = filter_texts(texts, scores, min_score=0.7, min_length=2)
    filtered_texts = [text for text, score in filtered]
    
    if verbose:
        print(f"    → 전처리 후: {len(filtered_texts)}개 텍스트")
    
    if verbose:
        print("\n✂️  [4/6] 텍스트 추출 완료 (LLM 토큰 절약)")
    
    if verbose:
        print("\n🏷️  [5/6] 제품 타입 감지 중...")
    product_type = detect_product_type(filtered_texts)
    type_desc = get_type_description(product_type)
    if verbose:
        print(f"    → 감지된 타입: {type_desc} ({product_type.value})")
    
    if verbose:
        print("\n🤖 [6/6] LLM 요약 중...")
    summary = summarize_texts(filtered_texts, product_type, verbose=verbose)
    
    elapsed_time = time.time() - start_time
    summary["source_images"] = [str(p) for p in image_paths]
    summary["image_count"] = len(image_paths)
    summary["ocr_count"] = total_ocr
    summary["merged_count"] = merged["count"]
    summary["filtered_count"] = len(filtered_texts)
    summary["processing_time"] = round(elapsed_time, 2)
    
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


def process_product_from_urls(
    image_urls: List[str],
    site: str = "auto",
    output_dir: str = "output",
    max_workers: int = 4,
    save_result: bool = True,
    verbose: bool = True
) -> Dict:
    start_time = time.time()
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"🌐 URL 기반 이미지 처리 시작: {len(image_urls)}개 URL")
        print(f"{'='*60}")
    
    if verbose:
        print(f"\n🔍 [1/4] 이미지 URL 필터링 (사이트: {site})...")
    
    filtered_urls = filter_product_images(image_urls, site=site)
    
    if verbose:
        print(f"    → {len(image_urls)}개 → {len(filtered_urls)}개 (광고/배너 제외)")
    
    if not filtered_urls:
        print("⚠️  필터링 후 이미지가 없습니다.")
        return {
            "summary": ["상품 상세 이미지를 찾을 수 없습니다."],
            "product_name": "알 수 없음",
            "product_type": "기타",
            "source_urls": image_urls,
            "error": "no_images_after_filter"
        }
    
    if verbose:
        print(f"\n📥 [2/4] 이미지 다운로드 중...")
    
    download_dir = os.path.join(output_dir, "downloaded")
    local_paths = download_images(
        filtered_urls,
        save_dir=download_dir,
        max_workers=max_workers
    )
    
    if verbose:
        print(f"    → {len(local_paths)}개 다운로드 완료")
    
    if not local_paths:
        print("⚠️  다운로드된 이미지가 없습니다.")
        return {
            "summary": ["이미지 다운로드에 실패했습니다."],
            "product_name": "알 수 없음",
            "product_type": "기타",
            "source_urls": filtered_urls,
            "error": "download_failed"
        }
    
    if verbose:
        print(f"\n🔄 [3/4] OCR 파이프라인 실행 중...")
    
    result = process_multiple_images(
        image_paths=local_paths,
        output_dir=output_dir,
        max_workers=max_workers,
        save_result=save_result,
        verbose=verbose
    )
    
    elapsed_time = time.time() - start_time
    result["source_urls"] = filtered_urls
    result["site"] = site if site != "auto" else detect_site(filtered_urls[0]) if filtered_urls else "unknown"
    result["total_processing_time"] = round(elapsed_time, 2)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"✅ URL 기반 처리 완료! (소요 시간: {elapsed_time:.1f}초)")
        print(f"{'='*60}\n")
    
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="OCR 통합 파이프라인"
    )
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--input", "-i")
    input_group.add_argument("--inputs", "-I", nargs="+")
    input_group.add_argument("--urls", "-U", nargs="+")
    
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--workers", "-w", type=int, default=4)
    parser.add_argument("--site", "-s", default="auto", choices=["auto", "coupang", "naver"])
    parser.add_argument("--no-save", action="store_true")
    parser.add_argument("--quiet", "-q", action="store_true")
    
    args = parser.parse_args()
    
    try:
        if args.input:
            result = process_product_image(
                image_path=args.input,
                output_dir=args.output_dir,
                save_result=not args.no_save,
                verbose=not args.quiet
            )
        elif args.inputs:
            result = process_multiple_images(
                image_paths=args.inputs,
                output_dir=args.output_dir,
                max_workers=args.workers,
                save_result=not args.no_save,
                verbose=not args.quiet
            )
        else:
            result = process_product_from_urls(
                image_urls=args.urls,
                site=args.site,
                output_dir=args.output_dir,
                max_workers=args.workers,
                save_result=not args.no_save,
                verbose=not args.quiet
            )
        
        if args.output:
            _save_json(result, args.output)
            if not args.quiet:
                print(f"📄 추가 저장: {args.output}")
        
        if not args.quiet:
            print("\n📋 요약 결과:")
            print(f"  제품명: {result.get('product_name', '알 수 없음')}")
            print(f"  타입: {result.get('product_type', '기타')}")
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
