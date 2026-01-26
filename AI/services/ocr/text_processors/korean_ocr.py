# -*- coding: utf-8 -*-
from paddleocr import PaddleOCR
from typing import List, Dict, Any, Optional

DEFAULT_MODEL_NAME = "korean_PP-OCRv5_mobile_rec"
DEFAULT_DEVICE = "gpu:0"


def create_ocr_instance(
    model_name: str = DEFAULT_MODEL_NAME,
    device: str = DEFAULT_DEVICE,
    use_textline_orientation: bool = True
) -> PaddleOCR:
    return PaddleOCR(
        text_recognition_model_name=model_name,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=use_textline_orientation,
        device=device,
    )


def run_ocr(
    image_path: str,
    ocr_instance: Optional[PaddleOCR] = None
) -> List[Any]:
    if ocr_instance is None:
        ocr_instance = create_ocr_instance()
    return ocr_instance.predict(image_path)


def extract_texts(ocr_result: List[Any]) -> List[str]:
    texts = []
    for res in ocr_result:
        if hasattr(res, 'get'):
            texts.extend(res.get('rec_texts', []))
        elif hasattr(res, 'rec_texts'):
            texts.extend(res.rec_texts)
    return texts


def extract_texts_with_scores(ocr_result: List[Any]) -> List[Dict[str, Any]]:
    results = []
    for res in ocr_result:
        if hasattr(res, 'get'):
            texts = res.get('rec_texts', [])
            scores = res.get('rec_scores', [])
        elif hasattr(res, 'rec_texts'):
            texts = res.rec_texts
            scores = res.rec_scores if hasattr(res, 'rec_scores') else [1.0] * len(texts)
        else:
            continue
        for text, score in zip(texts, scores):
            results.append({"text": text, "score": score})
    return results


DEFAULT_MAX_HEIGHT = 2000


def get_image_size(image_path: str) -> tuple:
    from PIL import Image
    with Image.open(image_path) as img:
        return img.size


def process_image(
    image_path: str,
    max_height: int = DEFAULT_MAX_HEIGHT,
    save_chunks: bool = False,
    output_dir: str = "output"
) -> Dict[str, Any]:
    import os
    import json
    from pathlib import Path
    
    width, height = get_image_size(image_path)
    print(f"이미지 크기: {width}x{height}px")
    
    ocr_instance = create_ocr_instance()
    
    if height > max_height:
        print(f"긴 이미지 감지 (높이 {height}px > {max_height}px) → 분할 처리")
        
        try:
            from . import long_image_processor
        except ImportError:
            import long_image_processor
        
        result = long_image_processor.process_long_image(
            image_path,
            max_height=max_height,
            save_chunks=save_chunks,
            ocr_instance=ocr_instance
        )
        result["processing_mode"] = "split"
    else:
        print(f"일반 이미지 (높이 {height}px <= {max_height}px) → 직접 처리")
        
        ocr_raw_result = ocr_instance.predict(image_path)
        
        os.makedirs(output_dir, exist_ok=True)
        for res in ocr_raw_result:
            res.save_to_img(output_dir)
        print(f"시각화 이미지 저장: {output_dir}/")
        
        texts_with_scores = extract_texts_with_scores(ocr_raw_result)
        
        result = {
            "rec_texts": [item["text"] for item in texts_with_scores],
            "rec_scores": [item["score"] for item in texts_with_scores],
            "total_count": len(texts_with_scores),
            "processing_mode": "direct",
            "image_size": {"width": width, "height": height}
        }
    
    os.makedirs(output_dir, exist_ok=True)
    base_name = Path(image_path).stem
    output_path = os.path.join(output_dir, f"{base_name}_ocr_result.json")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"완료! 총 {result['total_count']}개 텍스트 추출됨")
    print(f"결과 저장: {output_path}")
    
    return result


def process_images_parallel(
    image_paths: List[str],
    max_workers: int = 4,
    max_height: int = DEFAULT_MAX_HEIGHT,
    save_results: bool = False,
    output_dir: str = "output"
) -> List[Dict[str, Any]]:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from pathlib import Path
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    
    def process_single(image_path: str) -> Dict[str, Any]:
        try:
            result = process_image(
                image_path,
                max_height=max_height,
                save_chunks=save_results,
                output_dir=output_dir
            )
            result["source"] = Path(image_path).name
            return result
        except Exception as e:
            return {
                "rec_texts": [],
                "rec_scores": [],
                "total_count": 0,
                "processing_mode": "error",
                "source": Path(image_path).name,
                "error": str(e)
            }
    
    results = []
    print(f"병렬 OCR 처리 시작: {len(image_paths)}개 이미지, {max_workers} 워커")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_path = {
            executor.submit(process_single, path): path 
            for path in image_paths
        }
        
        for future in as_completed(future_to_path):
            path = future_to_path[future]
            try:
                result = future.result()
                results.append(result)
                status = "✓" if result["processing_mode"] != "error" else "✗"
                print(f"  {status} {result['source']}: {result['total_count']}개 텍스트")
            except Exception as e:
                print(f"  ✗ {Path(path).name}: 처리 실패 - {e}")
                results.append({
                    "rec_texts": [],
                    "rec_scores": [],
                    "total_count": 0,
                    "processing_mode": "error",
                    "source": Path(path).name,
                    "error": str(e)
                })
    
    path_order = {Path(p).name: i for i, p in enumerate(image_paths)}
    results.sort(key=lambda x: path_order.get(x["source"], 999))
    
    total_texts = sum(r["total_count"] for r in results)
    print(f"병렬 OCR 완료: 총 {total_texts}개 텍스트 추출")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="한국어 OCR")
    parser.add_argument("--input", default="../tests/fixtures/coupang_ohyes.jpg")
    parser.add_argument("--output", default="output")
    parser.add_argument("--max-height", type=int, default=DEFAULT_MAX_HEIGHT)
    parser.add_argument("--save-chunks", action="store_true")
    args = parser.parse_args()
    
    print(f"이미지 인식 시작: {args.input}")
    
    result = process_image(
        args.input,
        max_height=args.max_height,
        save_chunks=args.save_chunks,
        output_dir=args.output
    )
