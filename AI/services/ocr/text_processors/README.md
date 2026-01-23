# OCR Text Processors

OCR 결과를 추출/정제하고, 제품 타입을 감지한 뒤 LLM 요약을 생성하는 통합 파이프라인입니다.

---

## 🚀 빠른 시작 (통합 파이프라인)

```bash
# 단일 이미지 처리 (자동으로 전체 파이프라인 실행)
python ocr_pipeline.py --input 샴푸.jpg

# 여러 이미지 병합 처리 (상품 상세페이지 등)
python ocr_pipeline.py --inputs img1.jpg img2.jpg img3.jpg
```

---

## 📊 파이프라인 다이어그램

### 전체 구조

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           ocr_pipeline.py                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [단일 이미지]                           [다중 이미지]                          │
│  process_product_image()                process_multiple_images()            │
│         │                                        │                           │
│         ▼                                        ▼                           │
│  ┌─────────────────────┐                ┌─────────────────────┐              │
│  │  korean_ocr.py      │                │  korean_ocr.py      │              │
│  │  process_image()    │                │  process_images_    │              │
│  └──────────┬──────────┘                │  parallel()         │              │
│             │                           └──────────┬──────────┘              │
│             ▼                                      │                         │
│  ┌─────────────────────────────┐       ┌──────────┴──────────┐               │
│  │     이미지 높이 체크          │       │  각 이미지마다 아래   │                │
│  └──────────┬──────────────────┘       │  과정 병렬 수행      │                │
│             │                           └──────────┬──────────┘              │
│     ┌───────┴───────┐                             │                          │
│     ▼               ▼                             ▼                          │
│  ≤2000px        >2000px                    ┌─────────────┐                   │
│  (일반)          (긴 이미지)                 │ 높이 체크    │                   │
│     │               │                      └──────┬──────┘                   │
│     │               ▼                      ┌──────┴──────┐                   │
│     │      ┌─────────────────────┐         ▼             ▼                   │
│     │      │ long_image_         │     ≤2000px       >2000px                 │
│     │      │ processor.py        │         │             │                   │
│     │      │                     │         │             ▼                   │
│     │      │ 1. 이미지 분할       │         │    ┌────────────────┐            │
│     │      │    (2000px 단위)    │         │    │ 분할 → OCR →   │             │
│     │      │                     │         │    │ 청크별 병합     │            │
│     │      │ 2. 청크별 OCR       │         │    └────────┬───────┘            │
│     │      │                     │         │             │                   │
│     │      │ 3. 결과 병합        │         └──────┬──────┘                    │
│     │      │    (중복 제거)      │                │                           │
│     │      └──────────┬──────────┘                ▼                          │
│     │                 │                   ┌─────────────────┐                │
│     ▼                 ▼                   │ 2. 병합         │                 │
│  ┌─────────────────────┐                  │ merge_ocr_      │                │
│  │   OCR 결과           │                  │ results() ⭐    │                │
│  │   {rec_texts,       │                  └────────┬────────┘                 │
│  │    rec_scores}      │                           │                          │
│  └──────────┬──────────┘                           │                          │
│             │                                      │                          │
│             ▼                                      ▼                          │
│  ┌─────────────────────────────────────────────────────────────────┐         │
│  │                    3. 전처리 (ocr_text_preprocessor)             │         │
│  │                    filter_texts() - 노이즈/저신뢰도 제거          │          │
│  └─────────────────────────────┬───────────────────────────────────┘         │
│                                │                                              │
│                                ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────┐          │
│  │                    4. 텍스트 추출 (extract_texts_only)           │          │
│  │                    ["텍스트1", "텍스트2", ...] (LLM 토큰 절약)     │          │
│  └─────────────────────────────┬───────────────────────────────────┘         │
│                                │                                              │
│                                ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────┐         │
│  │                    5. 타입 감지 (product_type_detector)          │         │
│  │                    detect_product_type() → ProductType          │         │
│  └─────────────────────────────┬───────────────────────────────────┘         │
│                                │                                              │
│                                ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────┐         │
│  │                    6. LLM 요약 (ocr_llm_summarizer)              │         │
│  │                    summarize_texts() → 최종 요약                 │         │
│  └─────────────────────────────┬───────────────────────────────────┘         │
│                                │                                              │
│                                ▼                                              │
│                          최종 결과 출력                                        │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 케이스별 처리 단계

| 케이스 | 이미지 높이 | 처리 단계 |
|-------|-----------|---------|
| 단일 일반 이미지 | ≤2000px | OCR → 전처리 → 추출 → 타입 → LLM (5단계) |
| 단일 긴 이미지 | >2000px | 분할 → 청크 OCR → 병합 → 전처리 → 추출 → 타입 → LLM |
| 다중 일반 이미지 | 각각 ≤2000px | 병렬 OCR → 병합 → 전처리 → 추출 → 타입 → LLM (6단계) |
| 다중 혼합 이미지 | 일부 >2000px | 병렬(각각 분할 처리) → 병합 → 전처리 → 추출 → 타입 → LLM |

---

## 📁 파일 구조

| 파일 | 역할 | 비고 |
|-----|-----|-----|
| `ocr_pipeline.py` | **통합 파이프라인 (메인 진입점)** ⭐ | 권장 사용 |
| `korean_ocr.py` | PaddleOCR 기반 OCR 실행 + 긴 이미지 자동 분할 | |
| `long_image_processor.py` | 긴 이미지 슬라이딩 윈도우 분할 OCR | korean_ocr에서 자동 호출 |
| `ocr_text_preprocessor.py` | OCR 텍스트 정제/필터링 (중앙 모듈) | |
| `ocr_text_merger.py` | 여러 OCR 결과 병합 + 중복 제거 | |
| `product_type_detector.py` | 제품 타입 분류 + 타입별 키워드 매핑 | |
| `ocr_llm_summarizer.py` | 타입별 프롬프트 구성 후 LLM 요약 생성 | |
| `extract_rec_texts.py` | OCR JSON에서 `rec_texts`만 추출 (유틸리티) | 독립 사용 가능 |

---

## 사용 예시

### 1) 통합 파이프라인 (권장) ⭐

```bash
# 단일 이미지 - 자동으로 전체 과정 수행
python ocr_pipeline.py --input ../tests/fixtures/샴푸.jpg

# 여러 이미지 병합 (상품 상세페이지 등)
python ocr_pipeline.py --inputs detail1.jpg detail2.jpg detail3.jpg

# 조용히 실행 (진행 상황 출력 없이)
python ocr_pipeline.py --input 샴푸.jpg --quiet
```

### 2) 코드에서 import

```python
from ocr_pipeline import process_product_image, process_multiple_images

# 단일 이미지
result = process_product_image("샴푸.jpg")
print(result["summary"])

# 여러 이미지 병합
result = process_multiple_images(["img1.jpg", "img2.jpg"])
print(result["summary"])
```

### 3) 개별 모듈 사용 (기존 방식)

```bash
# OCR 실행
python korean_ocr.py --input ../tests/fixtures/sample.jpg

# 텍스트 추출
python extract_rec_texts.py --input output/sample_ocr_result.json

# LLM 요약
python ocr_llm_summarizer.py --input output/sample_ocr_result_texts.json
```

---

## 환경 변수 (.env)

`AI/services/ocr/text_processors/.env`에 API 키를 설정합니다.

```env
GMS_KEY=your_gms_api_key_here
OPENAI_MODEL=gpt-5-mini
```

---

## 설치 의존성

```bash
# PaddlePaddle (CUDA 11.8)
python -m pip install paddlepaddle-gpu==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/

# PaddlePaddle (CPU)
python -m pip install paddlepaddle==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/

# PaddleOCR + 기타
python -m pip install paddleocr pillow requests python-dotenv
```

---

## 출력 예시

```json
{
  "product_type": "BEAUTY_HAIRCARE",
  "product_name": "케라시스 데미지 클리닉 샴푸",
  "confidence": 0.85,
  "summary": [
    "이 제품은 케라시스 데미지 클리닉 샴푸입니다.",
    "손상된 모발을 위한 집중 케어 샴푸입니다.",
    "용량은 600ml이며, 케라틴 성분이 함유되어 있습니다."
  ],
  "keywords": {
    "용량": {"answer": "600ml", "status": "found"},
    "성분": {"answer": "케라틴, 아르간오일", "status": "found"}
  },
  "source_image": "샴푸.jpg",
  "processing_time": 3.2
}
```
