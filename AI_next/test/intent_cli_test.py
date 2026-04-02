"""
터미널 입력으로 intent 분류 모델을 직접 테스트하는 스크립트.

사용 예시:
  python test/intent_cli_test.py
  python test/intent_cli_test.py --model kakao1513/koelectra_intent_model --top-k 3
  python test/intent_cli_test.py --text "장바구니 보여줘"
"""

from __future__ import annotations

import argparse
import sys


DEFAULT_MODEL_ID = r"C:\ssafy\공통설계\model_training\outputs\koelectra_coupang_v1_1\best_model_export"

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="KoELECTRA intent model CLI tester",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL_ID,
        help=f"Hugging Face model id (default: {DEFAULT_MODEL_ID})",
    )
    parser.add_argument(
        "--text",
        default=None,
        help="단일 문장 테스트 모드. 지정하면 1회 추론 후 종료",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=1,
        help="출력할 상위 라벨 개수 (default: 1)",
    )
    return parser


def load_classifier(model_id: str):
    try:
        from transformers import pipeline
    except Exception as exc:
        print(
            "[오류] transformers를 불러오지 못했습니다. "
            "pip install transformers torch 후 다시 실행하세요.",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    print(f"[INFO] 모델 로드 중: {model_id}")
    try:
        classifier = pipeline("text-classification", model=model_id)
    except Exception as exc:
        print(f"[오류] 모델 로드 실패: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print("[INFO] 모델 로드 완료")
    return classifier


def run_inference(classifier, text: str, top_k: int) -> None:
    if not text.strip():
        return

    results = classifier(text, top_k=top_k)
    if isinstance(results, dict):
        results = [results]

    print(f"\n입력: {text}")
    for i, item in enumerate(results, start=1):
        label = item.get("label", "UNKNOWN")
        score = item.get("score", 0.0)
        print(f"{i}. {label} (확신도: {score:.4f})")


def interactive_loop(classifier, top_k: int) -> None:
    print("\n[대화형 테스트 시작]")
    print("- 문장을 입력하면 intent 추론 결과를 출력합니다.")
    print("- 종료: exit / quit / q")

    while True:
        try:
            text = input("\n입력 > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n종료합니다.")
            break

        if text.lower() in {"exit", "quit", "q"}:
            print("종료합니다.")
            break

        run_inference(classifier, text, top_k)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    top_k = max(1, args.top_k)
    classifier = load_classifier(args.model)

    if args.text is not None:
        run_inference(classifier, args.text, top_k)
        return

    interactive_loop(classifier, top_k)


if __name__ == "__main__":
    main()
