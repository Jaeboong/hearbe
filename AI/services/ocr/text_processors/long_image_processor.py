# -*- coding: utf-8 -*-
"""
긴 이미지 OCR 처리 모듈 (Sliding Window + Overlap)

세로로 긴 이미지(상세페이지 스크린샷 등)를 분할하여 OCR 처리 후
결과를 병합하는 모듈입니다.

주의: 이 모듈은 korean_ocr.py에서 자동으로 호출됩니다.
      직접 실행보다는 korean_ocr.py를 통해 사용하세요.
"""

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image

# 한국어 OCR 모듈 (직접 실행과 패키지 import 모두 지원)
try:
    from . import korean_ocr
except ImportError:
    import korean_ocr

# =============================================================================
# 기본 설정 상수
# =============================================================================
DEFAULT_MAX_HEIGHT = 2000   # 분할 단위 높이 (픽셀)
DEFAULT_OVERLAP = 200       # 오버랩 영역 (픽셀) - 텍스트 잘림 방지
MIN_CHUNK_HEIGHT = 500      # 최소 청크 높이

# 출력 디렉토리
OUTPUT_DIR = "output"


def get_image_info(image_path: str) -> Tuple[int, int]:
    """
    이미지의 너비와 높이를 반환합니다.
    
    Args:
        image_path: 이미지 파일 경로
        
    Returns:
        Tuple[int, int]: (너비, 높이)
    """
    with Image.open(image_path) as img:
        return img.size


def should_split_image(image_path: str, max_height: int = DEFAULT_MAX_HEIGHT) -> bool:
    """
    이미지 분할이 필요한지 판단합니다.
    
    Args:
        image_path: 이미지 파일 경로
        max_height: 분할 기준 높이
        
    Returns:
        bool: 분할 필요 여부
    """
    width, height = get_image_info(image_path)
    return height > max_height


def split_image_to_chunks(
    image_path: str,
    max_height: int = DEFAULT_MAX_HEIGHT,
    overlap: int = DEFAULT_OVERLAP,
    save_chunks: bool = False,
    output_dir: str = None
) -> List[Tuple[Image.Image, int]]:
    """
    이미지를 Sliding Window 방식으로 분할합니다.
    
    Args:
        image_path: 이미지 파일 경로
        max_height: 각 청크의 최대 높이
        overlap: 청크 간 오버랩 영역
        save_chunks: 청크 이미지를 파일로 저장할지 여부
        output_dir: 청크 저장 디렉토리 (None이면 기본 output/chunks 사용)
        
    Returns:
        List[Tuple[Image.Image, int]]: (분할된 이미지, 시작 y좌표) 리스트
    """
    img = Image.open(image_path)
    width, height = img.size
    
    # 청크 저장 디렉토리 설정
    if save_chunks:
        base_name = Path(image_path).stem
        chunk_dir = output_dir or os.path.join(OUTPUT_DIR, "chunks", base_name)
        os.makedirs(chunk_dir, exist_ok=True)
        print(f"청크 저장 디렉토리: {chunk_dir}")
    
    chunks = []
    y = 0
    chunk_index = 0
    
    while y < height:
        # 청크 끝 위치 계산
        y_end = min(y + max_height, height)
        
        # 마지막 청크가 너무 작으면 이전 청크와 합침
        remaining = height - y_end
        if 0 < remaining < MIN_CHUNK_HEIGHT:
            y_end = height
        
        # 청크 추출
        chunk = img.crop((0, y, width, y_end))
        chunks.append((chunk, y))
        
        print(f"  청크 {chunk_index + 1}: y={y} ~ {y_end} (높이: {y_end - y}px)")
        
        # 청크 이미지 저장
        if save_chunks:
            chunk_path = os.path.join(chunk_dir, f"chunk_{chunk_index + 1:02d}_y{y}-{y_end}.jpg")
            chunk.save(chunk_path, "JPEG", quality=95)
            print(f"    저장됨: {chunk_path}")
        
        chunk_index += 1
        
        # 다음 시작 위치 (오버랩 적용)
        y = y_end - overlap
        
        # 끝에 도달하면 종료
        if y_end >= height:
            break
    
    return chunks


def process_chunk_ocr(chunk: Image.Image, ocr_instance) -> List[Dict]:
    """
    단일 청크에 대해 OCR을 수행합니다.
    
    Args:
        chunk: 분할된 이미지 청크
        ocr_instance: PaddleOCR 인스턴스
        
    Returns:
        List[Dict]: OCR 결과 리스트
    """
    # 임시 파일로 저장 (PNG 무손실 포맷 사용 - JPEG 압축으로 인한 텍스트 손실 방지)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        chunk.save(tmp.name, "PNG")
        tmp_path = tmp.name
    
    try:
        # OCR 수행
        result = ocr_instance.predict(tmp_path)
        return result
    finally:
        # 임시 파일 삭제
        os.unlink(tmp_path)


def adjust_coordinates(ocr_result: List[Dict], y_offset: int) -> List[Dict]:
    """
    OCR 결과의 좌표를 원본 이미지 기준으로 보정합니다.
    
    Args:
        ocr_result: OCR 결과 리스트
        y_offset: 청크의 시작 y좌표
        
    Returns:
        List[Dict]: 좌표가 보정된 OCR 결과
    """
    adjusted = []
    
    for res in ocr_result:
        # PaddleOCR 결과 구조에 따라 처리
        if hasattr(res, 'get'):
            # dict 형태인 경우
            new_res = res.copy()
            if 'dt_polys' in new_res:
                # 다각형 좌표 보정
                polys = new_res['dt_polys']
                adjusted_polys = []
                for poly in polys:
                    adjusted_poly = [[p[0], p[1] + y_offset] for p in poly]
                    adjusted_polys.append(adjusted_poly)
                new_res['dt_polys'] = adjusted_polys
            adjusted.append(new_res)
        else:
            # 다른 형태의 결과는 그대로 추가
            adjusted.append(res)
    
    return adjusted


def remove_duplicate_texts(all_results: List[Dict], overlap: int) -> Dict:
    """
    오버랩 영역에서 발생한 중복 텍스트를 제거합니다.
    
    Args:
        all_results: 모든 청크의 OCR 결과
        overlap: 오버랩 영역 크기
        
    Returns:
        Dict: 중복 제거된 최종 결과
    """
    seen_texts = set()
    unique_texts = []
    unique_scores = []
    
    for result in all_results:
        if isinstance(result, list):
            for res in result:
                texts = res.get('rec_texts', [])
                scores = res.get('rec_scores', [])
                
                for text, score in zip(texts, scores):
                    # 정규화된 텍스트로 중복 체크
                    normalized = text.strip().lower()
                    if normalized and normalized not in seen_texts:
                        seen_texts.add(normalized)
                        unique_texts.append(text)
                        unique_scores.append(score)
    
    return {
        "rec_texts": unique_texts,
        "rec_scores": unique_scores,
        "total_count": len(unique_texts)
    }


def process_long_image(
    image_path: str,
    max_height: int = DEFAULT_MAX_HEIGHT,
    overlap: int = DEFAULT_OVERLAP,
    ocr_instance = None,
    save_chunks: bool = False
) -> Dict:
    """
    긴 이미지를 분할 처리하여 OCR을 수행합니다.
    
    Args:
        image_path: 이미지 파일 경로
        max_height: 분할 단위 높이 (픽셀)
        overlap: 오버랩 영역 (픽셀)
        ocr_instance: PaddleOCR 인스턴스 (None이면 새로 생성)
        
    Returns:
        Dict: 통합된 OCR 결과
    """
    # 이미지 정보 확인
    width, height = get_image_info(image_path)
    print(f"이미지 크기: {width}x{height}px")
    
    # 분할 필요 여부 체크
    if not should_split_image(image_path, max_height):
        print(f"분할 불필요 (높이 {height}px <= {max_height}px)")
        if ocr_instance:
            result = ocr_instance.predict(image_path)
            # 결과 추출
            all_texts = []
            all_scores = []
            for res in result:
                all_texts.extend(res.get('rec_texts', []))
                all_scores.extend(res.get('rec_scores', []))
            return {
                "rec_texts": all_texts,
                "rec_scores": all_scores,
                "total_count": len(all_texts),
                "split_count": 1
            }
        return {"error": "OCR 인스턴스가 필요합니다."}
    
    # OCR 인스턴스 생성 (없는 경우)
    if ocr_instance is None:
        ocr_instance = korean_ocr.create_ocr_instance()
    
    # 이미지 분할
    print(f"이미지 분할 시작 (max_height={max_height}, overlap={overlap})")
    chunks = split_image_to_chunks(image_path, max_height, overlap, save_chunks=save_chunks)
    print(f"총 {len(chunks)}개 청크로 분할됨")
    
    # 디버그 모드용 청크별 결과 저장 디렉토리
    if save_chunks:
        base_name = Path(image_path).stem
        debug_dir = os.path.join(OUTPUT_DIR, "chunks", base_name)
        os.makedirs(debug_dir, exist_ok=True)
    
    # 각 청크 OCR 처리
    all_results = []
    for idx, (chunk, y_offset) in enumerate(chunks):
        print(f"청크 {idx + 1}/{len(chunks)} OCR 처리 중...")
        
        # OCR 수행
        result = process_chunk_ocr(chunk, ocr_instance)
        
        # 디버그: 청크별 결과 출력 및 저장
        if save_chunks:
            chunk_texts = []
            for res in result:
                if hasattr(res, 'get'):
                    chunk_texts.extend(res.get('rec_texts', []))
                # 청크별 시각화 이미지 저장
                if hasattr(res, 'save_to_img'):
                    res.save_to_img(debug_dir)
            print(f"  → 청크 {idx + 1} 결과: {len(chunk_texts)}개 텍스트")
            print(f"     샘플: {chunk_texts[:5]}...")
            
            # 청크별 결과 JSON 저장
            chunk_result_path = os.path.join(debug_dir, f"chunk_{idx + 1:02d}_result.json")
            with open(chunk_result_path, "w", encoding="utf-8") as f:
                # 청크 텍스트만 저장 (간단한 형식)
                json.dump({"chunk_index": idx + 1, "y_offset": y_offset, "texts": chunk_texts}, f, ensure_ascii=False, indent=2)
        
        # 좌표 보정
        adjusted = adjust_coordinates(result, y_offset)
        all_results.append(adjusted)
    
    # 중복 제거 및 결과 병합
    print("결과 병합 및 중복 제거 중...")
    merged = remove_duplicate_texts(all_results, overlap)
    merged["split_count"] = len(chunks)
    merged["image_size"] = {"width": width, "height": height}
    
    print(f"완료! 총 {merged['total_count']}개 텍스트 추출됨")
    
    return merged


def save_result(result: Dict, output_path: str) -> None:
    """
    결과를 JSON 파일로 저장합니다.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"결과 저장: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="긴 이미지 OCR 처리 (Sliding Window + Overlap)")
    parser.add_argument("--input", required=True, help="입력 이미지 경로")
    parser.add_argument("--output", default=None, help="출력 JSON 경로")
    parser.add_argument("--max-height", type=int, default=DEFAULT_MAX_HEIGHT, help="분할 단위 높이")
    parser.add_argument("--overlap", type=int, default=DEFAULT_OVERLAP, help="오버랩 영역")
    parser.add_argument("--save-chunks", action="store_true", help="분할된 청크 이미지를 저장")
    args = parser.parse_args()
    
    # OCR 인스턴스 생성 (한국어 모델 사용)
    ocr = korean_ocr.create_ocr_instance()
    
    # 처리 실행
    result = process_long_image(
        args.input,
        max_height=args.max_height,
        overlap=args.overlap,
        ocr_instance=ocr,
        save_chunks=args.save_chunks
    )
    
    # 출력 경로 설정
    if args.output is None:
        base_name = Path(args.input).stem
        output_path = os.path.join(OUTPUT_DIR, f"{base_name}_long_ocr.json")
    else:
        output_path = args.output
    
    # 결과 저장
    save_result(result, output_path)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
