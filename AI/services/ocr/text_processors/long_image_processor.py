# -*- coding: utf-8 -*-
import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image

try:
    from . import korean_ocr
except ImportError:
    import korean_ocr

DEFAULT_MAX_HEIGHT = 2500
DEFAULT_OVERLAP = 150
DEFAULT_RESIZE_MAX_HEIGHT = 12000
MIN_CHUNK_HEIGHT = 500
OUTPUT_DIR = "output"


def get_image_info(image_path: str) -> Tuple[int, int]:
    with Image.open(image_path) as img:
        return img.size


def should_split_image(image_path: str, max_height: int = DEFAULT_MAX_HEIGHT) -> bool:
    width, height = get_image_info(image_path)
    return height > max_height


def split_image_to_chunks(
    image_path: str,
    max_height: int = DEFAULT_MAX_HEIGHT,
    overlap: int = DEFAULT_OVERLAP,
    resize_max_height: int = DEFAULT_RESIZE_MAX_HEIGHT,
    save_chunks: bool = False,
    output_dir: str = None
) -> List[Tuple[Image.Image, int]]:
    img = Image.open(image_path)
    width, height = img.size
    
    if resize_max_height and height > resize_max_height:
        scale = resize_max_height / height
        new_size = (max(1, int(width * scale)), resize_max_height)
        img = img.resize(new_size, Image.LANCZOS)
        width, height = img.size
        print(f"큰 이미지 리사이즈: {new_size[0]}x{new_size[1]}px (scale={scale:.3f})")
    
    if save_chunks:
        base_name = Path(image_path).stem
        chunk_dir = output_dir or os.path.join(OUTPUT_DIR, "chunks", base_name)
        os.makedirs(chunk_dir, exist_ok=True)
        print(f"청크 저장 디렉토리: {chunk_dir}")
    
    chunks = []
    y = 0
    chunk_index = 0
    
    while y < height:
        y_end = min(y + max_height, height)
        
        remaining = height - y_end
        if 0 < remaining < MIN_CHUNK_HEIGHT:
            y_end = height
        
        chunk = img.crop((0, y, width, y_end))
        chunks.append((chunk, y))
        
        print(f"  청크 {chunk_index + 1}: y={y} ~ {y_end} (높이: {y_end - y}px)")
        
        if save_chunks:
            chunk_path = os.path.join(chunk_dir, f"chunk_{chunk_index + 1:02d}_y{y}-{y_end}.jpg")
            chunk.save(chunk_path, "JPEG", quality=95)
            print(f"    저장됨: {chunk_path}")
        
        chunk_index += 1
        y = y_end - overlap
        
        if y_end >= height:
            break
    
    return chunks


def process_chunk_ocr(chunk: Image.Image, ocr_instance) -> List[Dict]:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        chunk.save(tmp.name, "PNG")
        tmp_path = tmp.name
    
    try:
        result = ocr_instance.predict(tmp_path)
        return result
    finally:
        os.unlink(tmp_path)


def adjust_coordinates(ocr_result: List[Dict], y_offset: int) -> List[Dict]:
    adjusted = []
    
    for res in ocr_result:
        if hasattr(res, 'get'):
            new_res = res.copy()
            if 'dt_polys' in new_res:
                polys = new_res['dt_polys']
                adjusted_polys = []
                for poly in polys:
                    adjusted_poly = [[p[0], p[1] + y_offset] for p in poly]
                    adjusted_polys.append(adjusted_poly)
                new_res['dt_polys'] = adjusted_polys
            adjusted.append(new_res)
        else:
            adjusted.append(res)
    
    return adjusted


def remove_duplicate_texts(all_results: List[Dict], overlap: int) -> Dict:
    seen_texts = set()
    unique_texts = []
    unique_scores = []
    
    for result in all_results:
        if isinstance(result, list):
            for res in result:
                texts = res.get('rec_texts', [])
                scores = res.get('rec_scores', [])
                
                for text, score in zip(texts, scores):
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
    width, height = get_image_info(image_path)
    print(f"이미지 크기: {width}x{height}px")
    
    if not should_split_image(image_path, max_height):
        print(f"분할 불필요 (높이 {height}px <= {max_height}px)")
        if ocr_instance:
            result = ocr_instance.predict(image_path)
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
    
    if ocr_instance is None:
        ocr_instance = korean_ocr.create_ocr_instance()
    
    print(f"이미지 분할 시작 (max_height={max_height}, overlap={overlap})")
    chunks = split_image_to_chunks(image_path, max_height, overlap, save_chunks=save_chunks)
    print(f"총 {len(chunks)}개 청크로 분할됨")
    
    if save_chunks:
        base_name = Path(image_path).stem
        debug_dir = os.path.join(OUTPUT_DIR, "chunks", base_name)
        os.makedirs(debug_dir, exist_ok=True)
    
    all_results = []
    for idx, (chunk, y_offset) in enumerate(chunks):
        print(f"청크 {idx + 1}/{len(chunks)} OCR 처리 중...")
        
        result = process_chunk_ocr(chunk, ocr_instance)
        
        if save_chunks:
            chunk_texts = []
            for res in result:
                if hasattr(res, 'get'):
                    chunk_texts.extend(res.get('rec_texts', []))
                if hasattr(res, 'save_to_img'):
                    res.save_to_img(debug_dir)
            print(f"  → 청크 {idx + 1} 결과: {len(chunk_texts)}개 텍스트")
            print(f"     샘플: {chunk_texts[:5]}...")
            
            chunk_result_path = os.path.join(debug_dir, f"chunk_{idx + 1:02d}_result.json")
            with open(chunk_result_path, "w", encoding="utf-8") as f:
                json.dump({"chunk_index": idx + 1, "y_offset": y_offset, "texts": chunk_texts}, f, ensure_ascii=False, indent=2)
        
        adjusted = adjust_coordinates(result, y_offset)
        all_results.append(adjusted)
    
    print("결과 병합 및 중복 제거 중...")
    merged = remove_duplicate_texts(all_results, overlap)
    merged["split_count"] = len(chunks)
    merged["image_size"] = {"width": width, "height": height}
    
    print(f"완료! 총 {merged['total_count']}개 텍스트 추출됨")
    
    return merged


def save_result(result: Dict, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"결과 저장: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="긴 이미지 OCR 처리")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default=None)
    parser.add_argument("--max-height", type=int, default=DEFAULT_MAX_HEIGHT)
    parser.add_argument("--overlap", type=int, default=DEFAULT_OVERLAP)
    parser.add_argument("--save-chunks", action="store_true")
    args = parser.parse_args()
    
    ocr = korean_ocr.create_ocr_instance()
    
    result = process_long_image(
        args.input,
        max_height=args.max_height,
        overlap=args.overlap,
        ocr_instance=ocr,
        save_chunks=args.save_chunks
    )
    
    if args.output is None:
        base_name = Path(args.input).stem
        output_path = os.path.join(OUTPUT_DIR, f"{base_name}_long_ocr.json")
    else:
        output_path = args.output
    
    save_result(result, output_path)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
