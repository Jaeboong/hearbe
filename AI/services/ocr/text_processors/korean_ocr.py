# -*- coding: utf-8 -*-
"""
한국어 OCR 모듈

PaddleOCR을 사용한 한국어 텍스트 인식 기능을 제공합니다.
다른 모듈에서 import하여 재사용할 수 있습니다.

=============================================================================
사용 방법
=============================================================================

1. 단독 실행 (CLI) - 자동으로 이미지 높이에 따라 분할 처리:
    # 긴 이미지 (분할 + 시각화)
    python korean_ocr.py --input ../tests/fixtures/coupang_ohyes.jpg --save-chunks
    
    # 일반 이미지 (직접 + 시각화)
    python korean_ocr.py --input ../tests/fixtures/샴푸.jpg

2. 모듈 import:
    from korean_ocr import process_image, run_ocr
    
    # 방법 1: 통합 처리 (권장) - 자동으로 분할 여부 결정
    result = process_image("image.jpg")
    
    # 방법 2: 직접 OCR (분할 없음)
    ocr_result = run_ocr("image.jpg")
    
    # 방법 3: 텍스트만 추출
    from korean_ocr import extract_texts
    texts = extract_texts(ocr_result)
"""

from paddleocr import PaddleOCR
from typing import List, Dict, Any, Optional


# =============================================================================
# 기본 설정
# =============================================================================
DEFAULT_MODEL_NAME = "korean_PP-OCRv5_mobile_rec"
DEFAULT_DEVICE = "gpu:0"


def create_ocr_instance(
    model_name: str = DEFAULT_MODEL_NAME,
    device: str = DEFAULT_DEVICE,
    use_textline_orientation: bool = True
) -> PaddleOCR:
    """
    한국어 OCR 인스턴스를 생성합니다.
    
    Args:
        model_name: 텍스트 인식 모델명 (기본: korean_PP-OCRv5_mobile_rec)
        device: 실행 장치 (기본: gpu:0, CPU는 'cpu')
        use_textline_orientation: 텍스트 라인 방향 감지 사용 여부
        
    Returns:
        PaddleOCR: 설정된 OCR 인스턴스
    """
    return PaddleOCR(
        # 한국어 텍스트 인식 모델
        text_recognition_model_name=model_name,
        
        # 문서 방향 분류 비활성화 (정방향 이미지 가정)
        use_doc_orientation_classify=False,
        
        # 문서 왜곡 보정 비활성화 (평면 이미지 가정)
        use_doc_unwarping=False,
        
        # 텍스트 라인 방향 감지 (세로쓰기 지원)
        use_textline_orientation=use_textline_orientation,
        
        # 실행 장치
        device=device,
    )


def run_ocr(
    image_path: str,
    ocr_instance: Optional[PaddleOCR] = None
) -> List[Any]:
    """
    이미지에서 텍스트를 추출합니다.
    
    Args:
        image_path: 이미지 파일 경로
        ocr_instance: 기존 OCR 인스턴스 (없으면 새로 생성)
        
    Returns:
        List: OCR 결과 리스트
    """
    if ocr_instance is None:
        ocr_instance = create_ocr_instance()
    
    return ocr_instance.predict(image_path)


def extract_texts(ocr_result: List[Any]) -> List[str]:
    """
    OCR 결과에서 텍스트만 추출합니다.
    
    Args:
        ocr_result: run_ocr() 또는 ocr.predict()의 결과
        
    Returns:
        List[str]: 추출된 텍스트 리스트
    """
    texts = []
    for res in ocr_result:
        if hasattr(res, 'get'):
            texts.extend(res.get('rec_texts', []))
        elif hasattr(res, 'rec_texts'):
            texts.extend(res.rec_texts)
    return texts


def extract_texts_with_scores(ocr_result: List[Any]) -> List[Dict[str, Any]]:
    """
    OCR 결과에서 텍스트와 신뢰도를 함께 추출합니다.
    
    Args:
        ocr_result: run_ocr() 또는 ocr.predict()의 결과
        
    Returns:
        List[Dict]: [{"text": str, "score": float}, ...]
    """
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


# =============================================================================
# 통합 이미지 처리 (자동 라우팅)
# =============================================================================
DEFAULT_MAX_HEIGHT = 2000  # 이 높이 초과 시 분할 처리


def get_image_size(image_path: str) -> tuple:
    """이미지의 너비와 높이를 반환합니다."""
    from PIL import Image
    with Image.open(image_path) as img:
        return img.size  # (width, height)


def process_image(
    image_path: str,
    max_height: int = DEFAULT_MAX_HEIGHT,
    save_chunks: bool = False,
    output_dir: str = "output"
) -> Dict[str, Any]:
    """
    이미지를 자동으로 분석하여 적절한 OCR 처리를 수행합니다.
    
    - 짧은 이미지 (높이 <= max_height): 직접 OCR
    - 긴 이미지 (높이 > max_height): 분할 OCR (long_image_processor 사용)
    
    Args:
        image_path: 이미지 파일 경로
        max_height: 분할 기준 높이 (기본: 2000px)
        save_chunks: 분할 시 청크 이미지 저장 여부
        output_dir: 출력 디렉토리
        
    Returns:
        Dict: 통합된 OCR 결과
            - rec_texts: 추출된 텍스트 리스트
            - rec_scores: 신뢰도 리스트
            - total_count: 총 텍스트 수
            - processing_mode: "direct" 또는 "split"
    """
    import os
    import json
    from pathlib import Path
    
    width, height = get_image_size(image_path)
    print(f"이미지 크기: {width}x{height}px")
    
    # OCR 인스턴스 생성 (한 번만)
    ocr_instance = create_ocr_instance()
    
    if height > max_height:
        # 긴 이미지 → 분할 OCR
        print(f"긴 이미지 감지 (높이 {height}px > {max_height}px) → 분할 처리")
        
        try:
            from . import long_image_processor
        except ImportError:
            import long_image_processor
        
        result = long_image_processor.process_long_image(
            image_path,
            max_height=max_height,
            save_chunks=save_chunks,
            ocr_instance=ocr_instance  # OCR 인스턴스 전달
        )
        result["processing_mode"] = "split"
    else:
        # 일반 이미지 → 직접 OCR
        print(f"일반 이미지 (높이 {height}px <= {max_height}px) → 직접 처리")
        
        ocr_raw_result = ocr_instance.predict(image_path)
        
        # 시각화 이미지 저장
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
    
    # 결과 저장
    os.makedirs(output_dir, exist_ok=True)
    base_name = Path(image_path).stem
    output_path = os.path.join(output_dir, f"{base_name}_ocr_result.json")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"완료! 총 {result['total_count']}개 텍스트 추출됨")
    print(f"결과 저장: {output_path}")
    
    return result


# =============================================================================
# CLI (직접 실행 시)
# =============================================================================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="한국어 OCR (자동 분할 지원)")
    parser.add_argument("--input", default="../tests/fixtures/coupang_ohyes.jpg", help="입력 이미지 경로")
    parser.add_argument("--output", default="output", help="출력 디렉토리")
    parser.add_argument("--max-height", type=int, default=DEFAULT_MAX_HEIGHT, help="분할 기준 높이 (기본: 2000)")
    parser.add_argument("--save-chunks", action="store_true", help="분할 시 청크 이미지 저장")
    args = parser.parse_args()
    
    print(f"이미지 인식 시작: {args.input}")
    
    result = process_image(
        args.input,
        max_height=args.max_height,
        save_chunks=args.save_chunks,
        output_dir=args.output
    )
