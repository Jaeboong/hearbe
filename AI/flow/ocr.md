# OCR 기능 Flow

## 개요
상품 상세 이미지나 결제 키패드 이미지를 OCR로 텍스트 추출하고, LLM으로 요약하여 음성 안내하는 흐름.

## Flow 다이어그램 - 상품 이미지 OCR

```
MCP 결과에 detail_images 포함
│
├─ [1] api/ws/handlers/mcp_handler.py → MCPHandler.handle_mcp_result()
│   └─ detail_images 존재 확인 → OCR 파이프라인 호출
│
├─ [2] services/ocr/text_processors/ocr_pipeline.py → OCRPipeline
│   │
│   ├─ [2-1] image_fetcher.py → ImageFetcher
│   │   └─ URL에서 이미지 다운로드 (base64 또는 URL)
│   │
│   ├─ [2-2] long_image_processor.py → LongImageProcessor
│   │   └─ 긴 이미지를 여러 세그먼트로 분할
│   │
│   ├─ [2-3] extract_rec_texts.py → PaddleOCR 텍스트 추출
│   │   └─ 각 세그먼트에서 텍스트 영역 감지 + 인식
│   │
│   ├─ [2-4] korean_ocr.py → 한국어 특화 처리
│   │   └─ 한글 인코딩, 특수문자 정리
│   │
│   ├─ [2-5] table_reconstructor.py → TableReconstructor
│   │   └─ 표 형태 데이터 구조 복원
│   │
│   ├─ [2-6] ocr_text_merger.py → OCRTextMerger
│   │   └─ 여러 세그먼트 텍스트를 하나로 병합
│   │
│   ├─ [2-7] ocr_text_preprocessor.py → 텍스트 전처리
│   │   └─ 불필요한 문자, 중복 제거
│   │
│   ├─ [2-8] product_type_detector.py → 상품 타입 감지
│   │   └─ 전자기기, 식품, 의류 등 카테고리 판별
│   │
│   └─ [2-9] ocr_llm_summarizer.py → OCRLLMSummarizer
│       └─ OpenAI API로 OCR 텍스트 요약
│           └─ 핵심 상품 정보만 추출
│
├─ [3] services/ocr/service.py → OCRService
│   └─ 프로바이더별 분기
│       ├─ OpenAI Vision API
│       ├─ Tesseract OCR
│       └─ PaddleOCR
│
└─ [4] api/ws/presenter/pages/product.py → build_ocr_summary_tts()
    └─ 요약된 텍스트를 TTS 포맷으로 변환
```

## Flow 다이어그램 - 결제 키패드 OCR

```
결제 단계에서 키패드 이미지 수신
│
├─ [1] api/ws/handlers/payment_keypad.py → PaymentKeypadManager
│   └─ 키패드 이미지 캡처 요청
│
├─ [2] services/ocr/payment/payment_ocr.py → PaymentOCR
│   │
│   ├─ [2-1] payment_ocr_pipeline.py → 키패드 전용 파이프라인
│   │
│   ├─ [2-2] digit_extractor.py → DigitExtractor
│   │   └─ 키패드에서 숫자(0~9) 위치 추출
│   │
│   ├─ [2-3] digit_to_dom_mapper.py → DigitToDomMapper
│   │   └─ 추출된 숫자 위치 → DOM 요소 좌표 매핑
│   │
│   └─ [2-4] keypad_mapper.py → KeypadMapper
│       └─ 사용자 입력 숫자 → 클릭할 DOM 좌표 반환
│
└─ [3] 사용자 음성 비밀번호 → 순서대로 키패드 클릭 명령 생성
    └─ MCPCommand(tool="click", args={x, y}) × N회
```

## 관련 파일

| 단계 | 파일 | 역할 |
|------|------|------|
| OCR 서비스 | `services/ocr/service.py` | OCR 프로바이더 래핑 |
| OCR 코어 | `services/ocr/ocr.py` | 핵심 OCR 로직 |
| OCR 파이프라인 | `services/ocr/text_processors/ocr_pipeline.py` | 이미지 → 텍스트 파이프라인 |
| 이미지 다운로드 | `services/ocr/text_processors/image_fetcher.py` | 이미지 가져오기 |
| 텍스트 추출 | `services/ocr/text_processors/extract_rec_texts.py` | PaddleOCR 텍스트 인식 |
| 한국어 처리 | `services/ocr/text_processors/korean_ocr.py` | 한국어 특화 |
| 긴 이미지 | `services/ocr/text_processors/long_image_processor.py` | 이미지 분할 |
| 표 복원 | `services/ocr/text_processors/table_reconstructor.py` | 표 구조 복원 |
| 텍스트 병합 | `services/ocr/text_processors/ocr_text_merger.py` | 세그먼트 병합 |
| LLM 요약 | `services/ocr/text_processors/ocr_llm_summarizer.py` | OCR 결과 요약 |
| 상품 타입 | `services/ocr/text_processors/product_type_detector.py` | 상품 카테고리 감지 |
| 키패드 OCR | `services/ocr/payment/payment_ocr.py` | 결제 키패드 인식 |
| 숫자 추출 | `services/ocr/payment/digit_extractor.py` | 키패드 숫자 추출 |
| DOM 매핑 | `services/ocr/payment/digit_to_dom_mapper.py` | 숫자 → DOM 좌표 |
| 키패드 매퍼 | `services/ocr/payment/keypad_mapper.py` | 키패드 매핑 |
| 유틸리티 | `services/ocr/text_processors/utils.py` | 공통 유틸 |
