# Payment 모듈

결제 비밀번호 입력 화면의 랜덤 키패드를 OCR로 인식하고, DOM 키와 매핑하는 모듈입니다.

## 파일 구조

| 파일 | 역할 |
|------|------|
| `payment_ocr.py` | OCR 인식 (이미지 → JSON) |
| `digit_extractor.py` | 숫자 추출 (JSON → 숫자 리스트) |
| `digit_to_dom_mapper.py` | DOM 키 매핑 (숫자 → DOM 키) |
| `payment_keypad_cli.py` | 통합 실행 (1+2 한번에) |

## 파이프라인

```
[이미지] → payment_ocr.py → 결제_res.json
              ↓
         digit_extractor.py → 결제_res_digits.json
              ↓
         digit_to_dom_mapper.py → 결제_res_mapped.json
```

## 사용법

### 0단계: OCR 인식
```bash
cd AI/services/ocr/payment
python payment_ocr.py
# 또는
python payment_ocr.py "../tests/fixtures/결제.png"
```

### 1단계: 숫자 추출
```bash
python digit_extractor.py "output/결제_res.json"
```

### 2단계: DOM 매핑
```bash
python digit_to_dom_mapper.py "output/결제_res_digits.json"
```

### 통합 실행
```bash
python payment_keypad_cli.py "output/결제_res.json"
```

## 출력 예시

```json
{
  "extracted_digits": ["2", "6", "8", "0", "9", "7", "3", "5", "4", "1"],
  "digit_to_key_mapping": {
    "2": "0", "6": "1", "8": "2", ...
  }
}
```


## 설정

`payment_ocr.py` 상단에서 이미지 경로 수정:
```python
img_path = "../tests/fixtures/결제2.png"
```
