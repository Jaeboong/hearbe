# 상품 상세 조회 Flow

## 개요
사용자가 검색 결과에서 상품을 선택하면, 해당 상품 페이지로 이동 후 HTML 파싱 + OCR로 상품 정보를 추출하여 음성으로 안내하는 흐름.

## Flow 다이어그램

```
사용자 입력 ("첫 번째 거 보여줘" / "두 번째 상품")
│
├─ [1] api/ws/handlers/text_handler.py → TextHandler.enqueue_text()
│
├─ [2] api/ws/handlers/text_processing/llm_pipeline_handler.py
│   │
│   ├─ [2-1] services/nlu/service.py → analyze_intent()
│   │   └─ IntentResult(intent=SELECT_ITEM, entities={index: 1})
│   │   └─ resolve_reference() → "첫 번째" → 인덱스 1로 변환
│   │
│   ├─ [2-2] services/llm/planner/service.py → generate_commands()
│   │   └─ services/llm/generators/command_generator.py
│   │       └─ services/llm/rules/select.py → SearchSelectRule 매칭
│   │           └─ services/llm/planner/selection/selection.py
│   │               ├─ selection_intent.py → 선택 의도 확인
│   │               ├─ selection_extract.py → 인덱스 추출
│   │               └─ site_extractors/coupang.py → 사이트별 선택기
│   │
│   └─ [2-3] MCPCommand(tool="click", args={selector: "상품 링크"})
│
├─ [3] api/ws/sender.py → send_tool_calls() → 클라이언트에 클릭 명령
│
├─ [4] 클라이언트: 상품 클릭 → 상품 페이지 이동 → mcp_result 전송
│   └─ { success: true, page_data: { html, url }, detail_images: [...] }
│
├─ [5] api/ws/handlers/mcp_handler.py → MCPHandler.handle_mcp_result()
│   │
│   ├─ [5-1] HTML 파싱
│   │   └─ services/summarizer/html_parser.py → parse_product_html()
│   │       ├─ detect_site() → "coupang"
│   │       └─ 추출: 상품명, 가격, 평점, 배송정보, 옵션
│   │
│   ├─ [5-2] OCR 처리 (상세 이미지가 있는 경우)
│   │   └─ services/ocr/text_processors/ocr_pipeline.py
│   │       ├─ image_fetcher.py → 이미지 다운로드
│   │       ├─ extract_rec_texts.py → PaddleOCR 텍스트 추출
│   │       ├─ korean_ocr.py → 한국어 특화 처리
│   │       ├─ long_image_processor.py → 긴 이미지 분할 처리
│   │       ├─ table_reconstructor.py → 표 구조 복원
│   │       ├─ ocr_text_merger.py → 세그먼트 병합
│   │       └─ ocr_llm_summarizer.py → LLM으로 요약
│   │
│   ├─ [5-3] TTS 포매팅
│   │   └─ api/ws/presenter/pages/product.py
│   │       ├─ build_product_summary_tts() → HTML 기반 요약
│   │       └─ build_ocr_summary_tts() → OCR 기반 요약
│   │
│   └─ [5-4] 세션 업데이트
│       └─ services/session/service.py → 현재 상품 정보 저장
│
└─ [6] api/ws/sender.py → send_tts_response()
    └─ "삼성 갤럭시 S25, 가격 120만원, 평점 4.8점..."
```

## 관련 파일

| 단계 | 파일 | 역할 |
|------|------|------|
| 선택 규칙 | `services/llm/rules/select.py` | 상품 선택 명령 생성 |
| 선택 처리 | `services/llm/planner/selection/selection.py` | 선택 로직 오케스트레이션 |
| 인덱스 추출 | `services/llm/planner/selection/selection_extract.py` | "첫 번째" → 1 변환 |
| 사이트 추출기 | `services/llm/planner/selection/site_extractors/coupang.py` | 쿠팡 상품 선택기 |
| HTML 파싱 | `services/summarizer/html_parser.py` | 상품 HTML → 구조화 |
| OCR 파이프라인 | `services/ocr/text_processors/ocr_pipeline.py` | 이미지 → 텍스트 |
| OCR 요약 | `services/ocr/text_processors/ocr_llm_summarizer.py` | LLM 기반 OCR 요약 |
| TTS 포매팅 | `api/ws/presenter/pages/product.py` | 상품 정보 음성 포맷 |
| OCR 통합 | `services/summarizer/ocr_integrator.py` | HTML + OCR 결합 |
