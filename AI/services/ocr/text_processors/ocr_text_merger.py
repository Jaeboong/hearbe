# 여러 OCR 결과 병합/중복 제거
import argparse
import json
import os
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Any

try:
    from .ocr_text_preprocessor import normalize_text, filter_texts
    from .utils import save_json
except ImportError:
    from ocr_text_preprocessor import normalize_text, filter_texts
    from utils import save_json


def _merge_entries(
    entries: Iterable[Dict],
    similarity_threshold: float,
) -> List[Dict]:
    merged: List[Dict] = []
    for entry in entries:
        text = entry.get("text", "")
        score = float(entry.get("score", 1.0))
        source = entry.get("source")
        box = entry.get("box", [])
        norm = normalize_text(text)
        if not norm:
            continue

        match_idx = None
        for idx, existing in enumerate(merged):
            if norm == existing["norm"]:
                match_idx = idx
                break
            if similarity_threshold > 0:
                ratio = SequenceMatcher(None, norm, existing["norm"]).ratio()
                if ratio >= similarity_threshold:
                    match_idx = idx
                    break

        if match_idx is None:
            merged.append(
                {
                    "text": text,
                    "score": score,
                    "box": box,
                    "sources": [source] if source else [],
                    "norm": norm,
                }
            )
        else:
            existing = merged[match_idx]
            if score > existing["score"]:
                existing["text"] = text
                existing["score"] = score
                existing["box"] = box  # 더 높은 스코어의 box로 업데이트
            if source and source not in existing["sources"]:
                existing["sources"].append(source)

    for item in merged:
        item.pop("norm", None)
    return merged


def merge_ocr_results(
    ocr_results: List[Dict[str, Any]],
    min_score: float = 0.7,
    min_length: int = 2,
    similarity_threshold: float = 0.9,
) -> Dict:
    entries: List[Dict] = []

    for result in ocr_results:
        texts = result.get("rec_texts", []) or []
        scores = result.get("rec_scores", []) or [1.0] * len(texts)
        boxes = result.get("boxes", []) or []
        source = result.get("source", None)

        # boxes가 texts보다 짧으면 빈 리스트로 채움
        if len(boxes) < len(texts):
            boxes = boxes + [[]] * (len(texts) - len(boxes))

        filtered = filter_texts(texts, scores, min_score, min_length)

        # 필터링된 인덱스를 추적하여 해당하는 box도 함께 가져옴
        text_to_box = {}
        for i, (text, score) in enumerate(zip(texts, scores)):
            if i < len(boxes):
                text_to_box[text] = boxes[i]

        for text, score in filtered:
            box = text_to_box.get(text, [])
            entries.append({"text": text, "score": score, "box": box, "source": source})

    merged = _merge_entries(entries, similarity_threshold)

    return {
        "rec_texts": [item["text"] for item in merged],
        "rec_scores": [item["score"] for item in merged],
        "boxes": [item.get("box", []) for item in merged],
        "items": merged,
        "count": len(merged),
    }


def _load_json_texts(path: str) -> Tuple[List[str], List[float]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    texts = data.get("rec_texts", []) or []
    scores = data.get("rec_scores", []) or []
    if not scores:
        scores = [1.0] * len(texts)
    return texts, scores


def merge_ocr_texts(
    inputs: List[str],
    min_score: float = 0.7,
    min_length: int = 2,
    similarity_threshold: float = 0.9,
) -> Dict:
    ocr_results = []
    for json_path in inputs:
        texts, scores = _load_json_texts(json_path)
        ocr_results.append({
            "rec_texts": texts,
            "rec_scores": scores,
            "source": Path(json_path).name
        })
    
    return merge_ocr_results(
        ocr_results,
        min_score=min_score,
        min_length=min_length,
        similarity_threshold=similarity_threshold
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="OCR 텍스트 병합")
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--output", default=os.path.join("output", "merged_ocr_texts.json"))
    parser.add_argument("--min-score", type=float, default=0.7)
    parser.add_argument("--min-length", type=int, default=2)
    parser.add_argument("--similarity-threshold", type=float, default=0.9)
    args = parser.parse_args()

    result = merge_ocr_texts(
        inputs=args.inputs,
        min_score=args.min_score,
        min_length=args.min_length,
        similarity_threshold=args.similarity_threshold,
    )
    save_json(result, args.output)
    print(f"병합 완료: {result['count']}개 텍스트 -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
