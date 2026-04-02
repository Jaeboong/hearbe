# koElectra Shopping Intent Model Guide

## Model
- Model ID: `kakao1513/koElectra_shopping_intent_v2`
- Type: Text Classification (Intent Classification)
- Base: koELECTRA
- Purpose: ASR로 들어온 쇼핑 명령 문장을 intent 라벨로 분류

## Install
```bash
pip install torch transformers
```

## Input / Output
- Input: 사용자 문장 1개 (`str`)
  - 예: `장바구니 보여줘`, `옵션 빨간색으로 바꿔줘`
- Output: 라벨 + 신뢰도(score)
  - 예: `{"label": "click_cart", "score": 0.97}`

## Quick Test
테스트 스크립트: `AI_next/test/intent_cli_test.py`

```bash
python AI_next/test/intent_cli_test.py
python AI_next/test/intent_cli_test.py --text "장바구니 보여줘" --top-k 3
python AI_next/test/intent_cli_test.py --model kakao1513/koElectra_shopping_intent_v2
```

## Training Data Paths (Current Project)
- Hearbe: `C:\ssafy\공통설계\hearbe\func_data`
- Coupang: `C:\ssafy\공통설계\coupang\func_data`

주요 파일:
- `train.csv`
- `test.csv`
- `label_map.csv`
- `summary.csv`

## ASR-Oriented Notes
이 서비스 입력은 ASR 텍스트 기준이다.
- 영문/특수문자 입력 빈도 낮음
- 숫자는 한글 형태로 변환되어 들어오는 경우가 많음
  - 예: `+1` -> `플러스 일`
- 전처리 시 숫자 한글화, 특수문자 제거, 띄어쓰기 흔들림 대응을 권장

## Minimal Inference Example
```python
from transformers import pipeline

model_id = "kakao1513/koElectra_shopping_intent_v2"
classifier = pipeline("text-classification", model=model_id)

text = "장바구니 보여줘"
result = classifier(text)

print(result[0]["label"], result[0]["score"])
```
