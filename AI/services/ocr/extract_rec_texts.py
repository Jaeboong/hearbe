"""
OCR 결과에서 rec_texts만 추출하는 유틸리티 스크립트
"""
import argparse
import json
import os
from pathlib import Path

# ============================================
# 기본 입출력 경로 설정 (직접 수정 가능)
# ============================================
DEFAULT_INPUT = os.path.join("output", "오겹살_res.json")
DEFAULT_OUTPUT = os.path.join("output", "오겹살_res_texts.json")


def extract_rec_texts(input_path: str, output_path: str = None) -> list:
    """
    OCR JSON 결과에서 rec_texts만 추출하여 저장
    
    Args:
        input_path: 원본 OCR JSON 파일 경로
        output_path: 출력 파일 경로 (None이면 _texts.json 접미사로 자동 생성)
    
    Returns:
        추출된 rec_texts 리스트
    """
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    rec_texts = data.get("rec_texts", [])
    
    # 빈 문자열 제거 (선택적)
    rec_texts = [text for text in rec_texts if text.strip()]
    
    # 출력 경로 자동 생성
    if output_path is None:
        input_file = Path(input_path)
        output_path = str(input_file.parent / f"{input_file.stem}_texts.json")
    
    # 결과 저장
    result = {"rec_texts": rec_texts, "count": len(rec_texts)}
    
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"추출 완료: {len(rec_texts)}개 텍스트")
    print(f"저장 위치: {output_path}")
    
    return rec_texts


def main():
    parser = argparse.ArgumentParser(description="OCR JSON에서 rec_texts만 추출")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="입력 파일 경로")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="출력 파일 경로")
    args = parser.parse_args()
    
    extract_rec_texts(args.input, args.output)


if __name__ == "__main__":
    main()
