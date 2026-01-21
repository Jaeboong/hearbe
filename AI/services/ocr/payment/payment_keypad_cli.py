"""
결제 키패드 전처리 CLI

OCR 결과 JSON을 입력받아 전처리 후 결과를 JSON 파일로 저장합니다.

사용법:
    python payment_keypad_cli.py <ocr_result.json> [output.json]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Union

from digit_extractor import extract_digits_from_ocr_result
from digit_to_dom_mapper import create_digit_to_key_mapping


def save_processed_result(
    ocr_json_path: Union[str, Path],
    output_path: Union[str, Path] = None,
    dom_keys: List[str] = None
) -> Dict:
    """
    OCR 결과를 전처리하여 JSON 파일로 저장합니다.
    
    Args:
        ocr_json_path: OCR 결과 JSON 파일 경로
        output_path: 출력 파일 경로 (None이면 자동 생성)
        dom_keys: 팀장이 제공하는 DOM 키 리스트
    
    Returns:
        전처리된 결과 딕셔너리
    """
    ocr_json_path = Path(ocr_json_path)
    
    # OCR 결과 로드
    with open(ocr_json_path, 'r', encoding='utf-8') as f:
        ocr_result = json.load(f)
    
    # 숫자 추출
    digits = extract_digits_from_ocr_result(ocr_result)
    
    # 매핑 생성
    mapping = create_digit_to_key_mapping(digits, dom_keys)
    
    # 결과 딕셔너리
    result = {
        "source_file": str(ocr_json_path),
        "extracted_digits": digits,
        "dom_keys": dom_keys if dom_keys else [str(i) for i in range(10)],
        "digit_to_key_mapping": mapping
    }
    
    # 출력 경로 설정
    if output_path is None:
        output_path = ocr_json_path.parent / f"{ocr_json_path.stem}_processed.json"
    
    # JSON 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"전처리 결과 저장 완료: {output_path}")
    return result


def main():
    """CLI 메인 함수"""
    if len(sys.argv) < 2:
        print("Usage: python payment_keypad_cli.py <ocr_result.json> [output.json] [dom_keys.json]")
        sys.exit(1)
    
    json_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].endswith(".json") == False else None
    
    # 세 번째 인자가 있으면 DOM 키 파일로 처리
    dom_keys_path = None
    if len(sys.argv) > 3:
        dom_keys_path = sys.argv[3]
    elif len(sys.argv) > 2 and sys.argv[2].endswith("dom_keys.json"):
        dom_keys_path = sys.argv[2]
        output_path = None

    dom_keys = None
    if dom_keys_path:
        with open(dom_keys_path, 'r', encoding='utf-8') as f:
            dom_keys = json.load(f)
        print(f"DOM 키 로드 완료: {dom_keys_path}")
    
    # 전처리 및 저장
    result = save_processed_result(json_path, output_path, dom_keys)
    
    print(f"\n=== 전처리 결과 ===")
    print(f"추출된 숫자: {result['extracted_digits']}")
    print(f"매핑: {result['digit_to_key_mapping']}")




if __name__ == "__main__":
    main()
