# PaddleOCR 기반 한글 OCR 실행
from paddleocr import PaddleOCR
from typing import List, Dict, Any, Optional

try:
    from .utils import get_image_size
except ImportError:
    from utils import get_image_size

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
            boxes = res.get('dt_polys', [])
        elif hasattr(res, 'rec_texts'):
            texts = res.rec_texts
            scores = res.rec_scores if hasattr(res, 'rec_scores') else [1.0] * len(texts)
            boxes = res.dt_polys if hasattr(res, 'dt_polys') else []
        else:
            continue

        # boxes가 없으면 빈 리스트로 채움
        if len(boxes) < len(texts):
            boxes = boxes + [[]] * (len(texts) - len(boxes))

        for text, score, box in zip(texts, scores, boxes):
            # NumPy 배열을 Python list로 변환
            if hasattr(box, 'tolist'):
                box = box.tolist()
            elif box and hasattr(box[0], 'tolist'):
                box = [pt.tolist() if hasattr(pt, 'tolist') else pt for pt in box]

            results.append({"text": text, "score": float(score), "box": box})
    return results


DEFAULT_MAX_HEIGHT = 2500


def process_image(
    image_path: str,
    max_height: int = DEFAULT_MAX_HEIGHT,
    save_chunks: bool = False,
    save_vis: bool = True,
    output_dir: str = "output",
    ocr_instance: Optional[PaddleOCR] = None
) -> Dict[str, Any]:
    import os
    import json
    from pathlib import Path
    
    width, height = get_image_size(image_path)
    print(f"이미지 크기: {width}x{height}px")
    
    if ocr_instance is None:
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

        if save_vis:
            os.makedirs(output_dir, exist_ok=True)
            for res in ocr_raw_result:
                res.save_to_img(output_dir)
            print(f"Saved visualization images: {output_dir}/")

        texts_with_scores = extract_texts_with_scores(ocr_raw_result)


        result = {
            "rec_texts": [item["text"] for item in texts_with_scores],
            "rec_scores": [item["score"] for item in texts_with_scores],
            "boxes": [item["box"] for item in texts_with_scores],
            "total_count": len(texts_with_scores),
            "processing_mode": "direct",
            "image_size": {"width": int(width), "height": int(height)}
        }
    
    os.makedirs(output_dir, exist_ok=True)
    base_name = Path(image_path).stem
    output_path = os.path.join(output_dir, f"{base_name}_ocr_result.json")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"완료! 총 {result['total_count']}개 텍스트 추출됨")
        print(f"결과 저장: {output_path}")
    except Exception as e:
        print(f"❌ JSON 저장 실패: {type(e).__name__}: {e}")
        print(f"  result 타입: {type(result)}")
        print(f"  result keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
        if isinstance(result, dict):
            for key, value in result.items():
                print(f"    {key}: {type(value).__name__}")
                if isinstance(value, list) and value:
                    print(f"      첫 번째 요소 타입: {type(value[0]).__name__}")
        raise
    
    return result


def process_images_parallel(
    image_paths: List[str],
    max_workers: int = 4,
    max_height: int = DEFAULT_MAX_HEIGHT,
    save_results: bool = False,
    save_vis: bool = True,
    output_dir: str = "output"
) -> List[Dict[str, Any]]:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from pathlib import Path
    import threading
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    thread_local = threading.local()
    
    def process_single(image_path: str) -> Dict[str, Any]:
        try:
            if not hasattr(thread_local, "ocr_instance"):
                thread_local.ocr_instance = create_ocr_instance()
            result = process_image(
                image_path,
                max_height=max_height,
                save_chunks=save_results,
                save_vis=save_vis,
                output_dir=output_dir,
                ocr_instance=thread_local.ocr_instance
            )
            result["source"] = Path(image_path).name
            return result
        except Exception as e:
            return {
                "rec_texts": [],
                "rec_scores": [],
                "boxes": [],
                "total_count": 0,
                "processing_mode": "error",
                "source": Path(image_path).name,
                "error": str(e)
            }
    
    results = []
    if isinstance(DEFAULT_DEVICE, str) and DEFAULT_DEVICE.startswith("gpu"):
        max_workers = min(max_workers, 2)
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
                    "boxes": [],
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
