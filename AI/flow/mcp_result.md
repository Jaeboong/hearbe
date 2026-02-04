# MCP 결과 처리 Flow

## 개요
클라이언트가 브라우저에서 MCP 도구를 실행한 결과를 서버가 수신하여, 페이지 데이터를 파싱하고 사용자에게 음성으로 안내하는 흐름.

## Flow 다이어그램

```
클라이언트 → mcp_result 전송
│ { tool_name, arguments, success, result, page_data, html, detail_images }
│
├─ [1] api/ws/router.py → WebSocketRouter.handle_text()
│   └─ 메시지 타입: mcp_result → HandlerManager로 위임
│
├─ [2] api/ws/handlers/handler_manager.py → handle_mcp_result()
│   └─ MCPHandler로 위임
│
├─ [3] api/ws/handlers/mcp_handler.py → MCPHandler.handle_mcp_result()
│   │
│   ├─ [3-1] 실패 처리 (success=false)
│   │   └─ api/ws/feedback/tool_failure_notifier.py → 실패 TTS 안내
│   │
│   ├─ [3-2] 페이지 데이터 추출
│   │   ├─ URL 파싱 → 사이트 판별
│   │   │   └─ services/llm/sites/site_manager.py → SiteManager.detect_site()
│   │   └─ 현재 페이지 타입 판별 (검색, 상품, 장바구니, 결제)
│   │
│   ├─ [3-3] 페이지 타입별 처리 분기
│   │   │
│   │   ├─ 검색 결과 페이지
│   │   │   ├─ api/ws/search/search_reader.py → 검색 결과 파싱
│   │   │   ├─ api/ws/search/search_matcher.py → 결과 매칭
│   │   │   ├─ api/ws/search/search_insights.py → 결과 분석
│   │   │   └─ api/ws/presenter/pages/search.py → TTS 포매팅
│   │   │
│   │   ├─ 상품 상세 페이지
│   │   │   ├─ services/summarizer/html_parser.py → HTML 파싱
│   │   │   ├─ services/ocr/text_processors/ocr_pipeline.py → 이미지 OCR
│   │   │   ├─ services/summarizer/ocr_integrator.py → HTML + OCR 통합
│   │   │   └─ api/ws/presenter/pages/product.py → TTS 포매팅
│   │   │
│   │   ├─ 장바구니 페이지
│   │   │   ├─ api/ws/cart/cart_reader.py → 장바구니 파싱
│   │   │   └─ api/ws/presenter/pages/cart.py → TTS 포매팅
│   │   │
│   │   └─ 결제 페이지
│   │       └─ api/ws/presenter/pages/checkout.py → TTS 포매팅
│   │
│   ├─ [3-4] 세션 상태 업데이트
│   │   └─ services/session/service.py → 현재 URL, 페이지 정보 저장
│   │
│   └─ [3-5] 페이지 추출 관리
│       └─ api/ws/handlers/page_extract_manager.py → 페이지 데이터 추출 관리
│
├─ [4] api/ws/sender.py → send_tts_response()
│   └─ 페이지별 요약 텍스트를 TTS로 변환 후 스트리밍 전송
│
└─ [5] api/ws/feedback/action_feedback.py → ActionFeedback
    └─ 액션 완료 피드백 ("장바구니에 담았습니다" 등)
```

## 관련 파일

| 단계 | 파일 | 역할 |
|------|------|------|
| MCP 핸들러 | `api/ws/handlers/mcp_handler.py` | MCP 결과 처리 오케스트레이션 |
| 사이트 매니저 | `services/llm/sites/site_manager.py` | 사이트/페이지 타입 감지 |
| 검색 리더 | `api/ws/search/search_reader.py` | 검색 결과 HTML 파싱 |
| 검색 매처 | `api/ws/search/search_matcher.py` | 검색 결과 매칭 |
| 검색 인사이트 | `api/ws/search/search_insights.py` | 검색 결과 분석 |
| HTML 파서 | `services/summarizer/html_parser.py` | 상품 HTML 파싱 |
| OCR 통합 | `services/summarizer/ocr_integrator.py` | HTML + OCR 결합 |
| 장바구니 리더 | `api/ws/cart/cart_reader.py` | 장바구니 HTML 파싱 |
| 페이지 추출 | `api/ws/handlers/page_extract_manager.py` | 페이지 데이터 추출 관리 |
| 실패 알림 | `api/ws/feedback/tool_failure_notifier.py` | 도구 실패 TTS 안내 |
| 액션 피드백 | `api/ws/feedback/action_feedback.py` | 완료 피드백 |
| 검색 TTS | `api/ws/presenter/pages/search.py` | 검색 결과 음성 포맷 |
| 상품 TTS | `api/ws/presenter/pages/product.py` | 상품 정보 음성 포맷 |
| 장바구니 TTS | `api/ws/presenter/pages/cart.py` | 장바구니 음성 포맷 |
| 결제 TTS | `api/ws/presenter/pages/checkout.py` | 결제 정보 음성 포맷 |
