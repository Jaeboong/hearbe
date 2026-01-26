import argparse
import json
import os
from pathlib import Path

DEFAULT_INPUT = os.path.join("output", "초코파이_detail_res.json")
DEFAULT_OUTPUT = os.path.join("output", "초코파이_detail_res_texts.json")


def extract_rec_texts(input_path: str, output_path: str = None) -> list:
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    rec_texts = data.get("rec_texts", [])
    rec_texts = [text for text in rec_texts if text.strip()]
    
    if output_path is None:
        input_file = Path(input_path)
        output_path = str(input_file.parent / f"{input_file.stem}_texts.json")
    
    result = {
        "rec_texts": rec_texts,
        "count": len(rec_texts)
    }
    
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"추출 완료: {len(rec_texts)}개 텍스트")
    print(f"저장 위치: {output_path}")
    
    return rec_texts


def main():
    parser = argparse.ArgumentParser(description="OCR JSON에서 텍스트 추출")
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    
    extract_rec_texts(args.input, args.output)


if __name__ == "__main__":
    main()
