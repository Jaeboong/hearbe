"""
OCR 결과 추출 유틸리티 (OCR Result Text Extractor)

이 스크립트는 OCR 결과가 담긴 JSON 파일에서
'rec_texts' (인식된 텍스트 목록) 부분만 따로 추출하여 새로운 JSON 파일로 저장합니다.
전체 결과를 볼 필요 없이 텍스트만 빠르게 확인하고 싶을 때 유용합니다.
"""

import argparse
import json
import os
from pathlib import Path

# ============================================
# 기본 입출력 경로 설정 (직접 수정 가능)
# ============================================
DEFAULT_INPUT = os.path.join("output", "샴푸_res.json")
DEFAULT_OUTPUT = os.path.join("output", "샴푸_res_texts.json")


def extract_rec_texts(input_path: str, output_path: str = None) -> list:
    """
    OCR JSON 결과에서 텍스트(rec_texts)만 추출하여 따로 저장합니다.
    
    Args:
        input_path: 원본 OCR 결과 JSON 파일 경로
        output_path: 저장할 파일 경로 (None이면 원본 파일명 뒤에 _texts.json을 붙여서 자동 생성)
    
    Returns:
        List[str]: 추출된 텍스트 리스트
    """
    # 1. 원본 JSON 파일 읽기
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 2. 'rec_texts' 키에서 데이터 추출 (없으면 빈 리스트 반환)
    rec_texts = data.get("rec_texts", [])
    
    # 3. 빈 문자열("")이나 공백만 있는 항목 제거 (선택적)
    # 텍스트가 실제로 존재하는 경우만 남겨서 데이터 품질을 높입니다.
    rec_texts = [text for text in rec_texts if text.strip()]
    
    # 4. 저장할 파일 경로가 지정되지 않았을 경우 자동 생성
    # 예: "output/오겹살.json" -> "output/오겹살_texts.json"
    if output_path is None:
        input_file = Path(input_path)
        output_path = str(input_file.parent / f"{input_file.stem}_texts.json")
    
    # 5. 저장할 결과 딕셔너리 구성
    result = {
        "rec_texts": rec_texts,  # 텍스트 목록
        "count": len(rec_texts)  # 총 개수 (편의를 위해 추가)
    }
    
    # 6. 파일로 저장
    # 저장할 폴더가 없으면 생성합니다.
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 결과 출력
    print(f"추출 완료: {len(rec_texts)}개 텍스트")
    print(f"저장 위치: {output_path}")
    
    return rec_texts


def main():
    # 명령줄 인자를 처리하기 위한 설정
    parser = argparse.ArgumentParser(description="OCR JSON 파일에서 텍스트 부분만 추출합니다.")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="입력 OCR 결과 파일 (.json)")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="저장할 파일 경로 (.json)")
    args = parser.parse_args()
    
    # 추출 함수 실행
    extract_rec_texts(args.input, args.output)


if __name__ == "__main__":
    main()
