# OCR 전체 처리 파이프라인
import argparse
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from .korean_ocr import process_image, process_images_parallel
    from .ocr_text_preprocessor import filter_texts, preprocess_ocr_texts, extract_rec_texts_from_data
    from .ocr_text_merger import merge_ocr_results
    from .product_type_detector import (
        ProductType,
        detect_product_type,
        get_type_description,
        override_product_type,
    )
    from .ocr_llm_summarizer import summarize_texts
    from .image_fetcher import (
        filter_product_images,
        download_images,
        detect_site,
        get_selector,
        list_supported_sites,
    )
    from .utils import (
        save_json,
        compute_image_hash,
        load_cache,
        save_cache,
        update_cache_metadata,
        get_cache_stats,
        compute_imageset_hash,
        compute_urllist_hash,
        load_pipeline_cache,
        save_pipeline_cache,
    )
except ImportError:
    from korean_ocr import process_image, process_images_parallel
    from ocr_text_preprocessor import filter_texts, preprocess_ocr_texts, extract_rec_texts_from_data
    from ocr_text_merger import merge_ocr_results
    from product_type_detector import (
        ProductType,
        detect_product_type,
        get_type_description,
        override_product_type,
    )
    from ocr_llm_summarizer import summarize_texts
    from image_fetcher import (
        filter_product_images,
        download_images,
        detect_site,
        get_selector,
        list_supported_sites,
    )
    from utils import (
        save_json,
        compute_image_hash,
        load_cache,
        save_cache,
        update_cache_metadata,
        get_cache_stats,
        compute_imageset_hash,
        compute_urllist_hash,
        load_pipeline_cache,
        save_pipeline_cache,
    )


def _summary_only(summary: Dict) -> Dict:
    return {"summary": summary.get("summary", [])}


_IMPORTANT_TOKENS = (
    "특가", "할인", "세일", "반값", "쿠폰", "무료배송",
    "원산지", "제조", "브랜드", "유통기한", "보관",
    "용량", "중량", "구성", "증정", "1+1", "2+1",
    "원", "%", "kg", "g", "ml", "l", "개", "입", "팩", "박스"
)


def _is_important_text(text: str) -> bool:
    for token in _IMPORTANT_TOKENS:
        if token in text:
            return True
    # 숫자 + 단위/통화 패턴
    return bool(re.search(r"\d+\s*(원|%|kg|g|ml|l|개|입|팩|박스)", text.lower()))


def _select_texts_by_importance(
    filtered: List[Tuple[str, float]],
    max_items: int = 100
) -> List[str]:
    """중요도 기반 텍스트 선별: 중요 키워드 포함 텍스트 우선 + 높은 스코어 순"""
    if len(filtered) <= max_items:
        return [text for text, score in filtered]

    important = []
    normal = []

    for text, score in filtered:
        if _is_important_text(text):
            important.append((text, score))
        else:
            normal.append((text, score))

    # 각 그룹 내에서 스코어 높은 순 정렬
    important.sort(key=lambda x: x[1], reverse=True)
    normal.sort(key=lambda x: x[1], reverse=True)

    # 중요 텍스트 우선 선택
    selected = important + normal
    return [text for text, score in selected[:max_items]]


def process_product_image(
    image_path: str,
    output_dir: str = "output",
    save_result: bool = True,
    verbose: bool = True,
    use_cache: bool = True
) -> Dict:
    start_time = time.time()
    image_hash = None

    if verbose:
        print(f"\n{'='*60}")
        print(f"🖼️  단일 이미지 처리 시작: {Path(image_path).name}")
        print(f"{'='*60}")

    # 캐시 체크
    if use_cache:
        if verbose:
            print("\n💾 캐시 확인 중...")
        image_hash = compute_image_hash(image_path)
        cached_summary = load_cache(image_hash)

        if cached_summary:
            elapsed_time = time.time() - start_time
            update_cache_metadata(hit=True)
            if verbose:
                print(f"    ✅ 캐시 히트! (소요 시간: {elapsed_time:.3f}초)")
                print(f"\n{'='*60}")
                print(f"✅ 캐시에서 로드 완료! (소요 시간: {elapsed_time:.3f}초)")
                print(f"{'='*60}\n")
            return cached_summary
        else:
            update_cache_metadata(hit=False)
            if verbose:
                print(f"    ⚠️  캐시 미스 - 정상 처리 시작")

    if verbose:
        print("\n📝 [1/5] OCR 처리 중...")
    step_start = time.time()
    ocr_result = process_image(image_path, output_dir=output_dir, save_vis=False)
    step_time = time.time() - step_start
    ocr_count = ocr_result.get("total_count", len(ocr_result.get("rec_texts", [])))
    if verbose:
        mode = ocr_result.get("processing_mode", "direct")
        print(f"    → 처리 모드: {'분할 처리' if mode == 'split' else '직접 처리'}")
        print(f"    → OCR 결과: {ocr_count}개 텍스트 ({step_time:.2f}초)")
    
    if verbose:
        print("\n🔧 [2/5] 전처리 중...")
    step_start = time.time()
    texts = extract_rec_texts_from_data(ocr_result)
    scores = ocr_result.get("rec_scores", [1.0] * len(texts))
    
    filtered = filter_texts(
        texts,
        scores,
        min_score=0.7,
        min_length=2,
        important_text_predicate=_is_important_text,
    )
    filtered_texts = _select_texts_by_importance(filtered, max_items=100)
    step_time = time.time() - step_start

    if verbose:
        print(f"    → 전처리 후: {len(filtered_texts)}개 텍스트 (원본: {len(texts)}개, 중요도 기반 선별, {step_time:.2f}초)")
    
    if verbose:
        print("\n✂️  [3/5] 텍스트 추출 완료 (LLM 토큰 절약)")
    
    if verbose:
        print("\n🏷️  [4/5] 제품 타입 감지 중...")
    step_start = time.time()
    product_type = detect_product_type(filtered_texts)
    product_type = override_product_type(filtered_texts, product_type)
    type_desc = get_type_description(product_type)
    step_time = time.time() - step_start
    if verbose:
        print(f"    → 감지된 타입: {type_desc} ({product_type.value}) ({step_time:.2f}초)")
    
    if verbose:
        print("\n🤖 [5/5] LLM 요약 중...")
    step_start = time.time()
    summary = summarize_texts(filtered_texts, product_type, verbose=verbose, use_cache=use_cache)
    step_time = time.time() - step_start
    if verbose:
        print(f"    → LLM 처리 완료 ({step_time:.2f}초)")
    
    elapsed_time = time.time() - start_time
    summary["source_image"] = str(image_path)
    summary["ocr_count"] = ocr_count
    summary["filtered_count"] = len(filtered_texts)
    summary["processing_time"] = round(elapsed_time, 2)
    
    if save_result:
        base_name = Path(image_path).stem
        output_path = os.path.join(output_dir, f"{base_name}_summary.json")
        save_json(_summary_only(summary), output_path)
        if verbose:
            print(f"\n💾 결과 저장: {output_path}")

    # 캐시 저장
    if use_cache and image_hash:
        save_cache(image_hash, summary)
        if verbose:
            print(f"💾 캐시 저장: {image_hash[:16]}")

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
    verbose: bool = True,
    use_cache: bool = True
) -> Dict:
    start_time = time.time()
    pipeline_hash = None
    pipeline_hash = None

    if use_cache:
        if verbose:
            print("\n[cache] checking multi-image pipeline cache...")
        pipeline_hash = compute_imageset_hash(image_paths)
        cached_result = load_pipeline_cache(pipeline_hash)
        if cached_result:
            if verbose:
                print("    cache hit: returning cached pipeline result")
            return cached_result
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"🖼️  다중 이미지 처리 시작: {len(image_paths)}개 이미지")
        print(f"{'='*60}")
    
    if verbose:
        print("\n📝 [1/6] 병렬 OCR 처리 중...")
    step_start = time.time()
    ocr_results = process_images_parallel(
        image_paths,
        max_workers=max_workers,
        output_dir=output_dir,
        save_vis=False
    )
    step_time = time.time() - step_start
    total_ocr = sum(r.get("total_count", 0) for r in ocr_results)
    if verbose:
        print(f"    → 총 OCR 결과: {total_ocr}개 텍스트 ({step_time:.2f}초)")
    
    if verbose:
        print("\n🔗 [2/6] 텍스트 병합 중...")
    step_start = time.time()
    merged = merge_ocr_results(ocr_results)
    step_time = time.time() - step_start
    if verbose:
        print(f"    → 병합 후: {merged['count']}개 텍스트 (중복 제거됨, {step_time:.2f}초)")
    
    if verbose:
        print("\n🔧 [3/6] 전처리 중...")
    step_start = time.time()
    texts = extract_rec_texts_from_data(merged)
    scores = merged.get("rec_scores", [1.0] * len(texts))
    
    filtered = filter_texts(
        texts,
        scores,
        min_score=0.7,
        min_length=2,
        important_text_predicate=_is_important_text,
    )
    filtered_texts = _select_texts_by_importance(filtered, max_items=100)
    step_time = time.time() - step_start

    if verbose:
        print(f"    → 전처리 후: {len(filtered_texts)}개 텍스트 (중요도 기반 선별, {step_time:.2f}초)")
    
    if verbose:
        print("\n✂️  [4/6] 텍스트 추출 완료 (LLM 토큰 절약)")
    
    if verbose:
        print("\n🏷️  [5/6] 제품 타입 감지 중...")
    step_start = time.time()
    product_type = detect_product_type(filtered_texts)
    product_type = override_product_type(filtered_texts, product_type)
    type_desc = get_type_description(product_type)
    step_time = time.time() - step_start
    if verbose:
        print(f"    → 감지된 타입: {type_desc} ({product_type.value}) ({step_time:.2f}초)")
    
    if verbose:
        print("\n🤖 [6/6] LLM 요약 중...")
    step_start = time.time()
    summary = summarize_texts(filtered_texts, product_type, verbose=verbose, use_cache=use_cache)
    step_time = time.time() - step_start
    if verbose:
        print(f"    → LLM 처리 완료 ({step_time:.2f}초)")
    
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
        save_json(_summary_only(summary), output_path)
        if verbose:
            print(f"\n💾 결과 저장: {output_path}")
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"✅ 완료! (소요 시간: {elapsed_time:.1f}초)")
        print(f"{'='*60}\n")
    
    if use_cache and pipeline_hash:
        save_pipeline_cache(pipeline_hash, summary)
        if verbose:
            print("    cache saved: multi-image pipeline result")

    return summary


def process_product_from_urls(
    image_urls: List[str],
    site: str = "auto",
    output_dir: str = "output",
    max_workers: int = 4,
    save_result: bool = True,
    verbose: bool = True,
    use_cache: bool = True
) -> Dict:
    start_time = time.time()
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"🌐 URL 기반 이미지 처리 시작: {len(image_urls)}개 URL")
        print(f"{'='*60}")
    
    if verbose:
        print(f"\n🔍 [1/4] 이미지 URL 필터링 (사이트: {site})...")
    step_start = time.time()
    
    filtered_urls = filter_product_images(image_urls, site=site)
    step_time = time.time() - step_start
    
    if verbose:
        print(f"    → {len(image_urls)}개 → {len(filtered_urls)}개 (광고/배너 제외, {step_time:.2f}초)")
    
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
    step_start = time.time()
    
    if use_cache:
        if verbose:
            print("\n[cache] checking URL pipeline cache...")
        pipeline_hash = compute_urllist_hash(filtered_urls, site)
        cached_result = load_pipeline_cache(pipeline_hash)
        if cached_result:
            if verbose:
                print("    cache hit: returning cached pipeline result")
            return cached_result

    download_dir = os.path.join(output_dir, "downloaded")
    local_paths = download_images(
        filtered_urls,
        save_dir=download_dir,
        max_workers=max_workers
    )
    step_time = time.time() - step_start
    
    if verbose:
        print(f"    → {len(local_paths)}개 다운로드 완료 ({step_time:.2f}초)")
    
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
        verbose=verbose,
        use_cache=use_cache
    )
    
    elapsed_time = time.time() - start_time
    result["source_urls"] = filtered_urls
    result["site"] = site if site != "auto" else detect_site(filtered_urls[0]) if filtered_urls else "unknown"
    result["total_processing_time"] = round(elapsed_time, 2)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"✅ URL 기반 처리 완료! (소요 시간: {elapsed_time:.1f}초)")
        print(f"{'='*60}\n")
    
    if use_cache and pipeline_hash:
        save_pipeline_cache(pipeline_hash, result)
        if verbose:
            print("    cache saved: URL pipeline result")

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
    parser.add_argument("--no-cache", action="store_true", help="캐시 사용 안 함")
    parser.add_argument("--cache-stats", action="store_true", help="캐시 통계 출력")
    parser.add_argument("--quiet", "-q", action="store_true")

    args = parser.parse_args()

    # 캐시 통계만 출력하고 종료
    if args.cache_stats:
        stats = get_cache_stats()
        print("\n📊 캐시 통계")
        print(f"{'='*60}")
        print(f"총 요청 수: {stats['total_requests']}")
        print(f"캐시 히트: {stats['cache_hits']}")
        print(f"캐시 미스: {stats['cache_misses']}")
        print(f"히트율: {stats['hit_rate']:.1%}")
        print(f"{'='*60}\n")
        return 0
    
    try:
        if args.input:
            result = process_product_image(
                image_path=args.input,
                output_dir=args.output_dir,
                save_result=not args.no_save,
                verbose=not args.quiet,
                use_cache=not args.no_cache
            )
        elif args.inputs:
            result = process_multiple_images(
                image_paths=args.inputs,
                output_dir=args.output_dir,
                max_workers=args.workers,
                save_result=not args.no_save,
                verbose=not args.quiet,
                use_cache=not args.no_cache
            )
        else:
            result = process_product_from_urls(
                image_urls=args.urls,
                site=args.site,
                output_dir=args.output_dir,
                max_workers=args.workers,
                save_result=not args.no_save,
                verbose=not args.quiet,
                use_cache=not args.no_cache
            )
        
        if args.output:
            save_json(_summary_only(result), args.output)
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

            # 캐시 통계 간단 출력
            if not args.no_cache:
                stats = get_cache_stats()
                if stats['total_requests'] > 0:
                    print(f"\n💾 캐시 통계: {stats['cache_hits']}/{stats['total_requests']} 히트 ({stats['hit_rate']:.1%})")

        return 0
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
