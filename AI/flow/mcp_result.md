# MCP 결과 처리 Flow

## 개요
클라이언트가 브라우저에서 MCP 도구를 실행한 결과를 서버가 수신하여, 페이지 데이터를 파싱하고 사용자에게 음성으로 안내하는 흐름.

## 핵심 진입 파일

- `api/ws/handlers/mcp_handler.py`

### import 맵 (프로젝트 내부)

- `core/event_bus.py`
- `services/llm/generators/tts_generator.py`
- `services/llm/planner/selection/option_select.py`
- `services/llm/sites/site_manager.py`
- `services/summarizer/__init__.py`
- `api/ws/utils/temp_file_manager.py`

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
│   │   ├─ URL 파싱 → 페이지 타입 판별
│   │   │   └─ services/llm/sites/site_manager.py → get_page_type()
│   │   └─ HTML/이미지/결과 데이터 추출
│   │
│   ├─ [3-3] 페이지 타입별 처리 분기
│   │   │
│   │   ├─ 검색 결과 페이지
│   │   │   ├─ session.context["search_results"] 갱신
│   │   │   └─ services/llm/generators/tts_generator.py → build_search_list()
│   │   │
│   │   ├─ 상품 상세 페이지
│   │   │   ├─ services/summarizer/html_parser.py → HTML 파싱
│   │   │   ├─ services/summarizer/ocr_integrator.py → 이미지 OCR (비동기)
│   │   │   └─ api/ws/presenter/pages/product.py → TTS 포매팅
│   │   │
│   │   ├─ 장바구니 페이지
│   │   │   ├─ api/ws/cart/cart_reader.py → 장바구니 파싱
│   │   │   └─ api/ws/presenter/pages/cart.py → TTS 포매팅
│   │
│   ├─ [3-4] 세션 상태 업데이트
│   │   └─ services/session/service.py → 현재 URL, 페이지 정보 저장
│   │
│   └─ [3-5] 옵션 선택 대기 처리 (옵션 정보 도착 시)
│       └─ services/llm/planner/selection/option_select.py
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
| HTML 파서 | `services/summarizer/html_parser.py` | 상품 HTML 파싱 |
| 장바구니 리더 | `api/ws/cart/cart_reader.py` | 장바구니 HTML 파싱 |
| OCR 통합 | `services/summarizer/ocr_integrator.py` | 이미지 OCR 실행 |
| 실패 알림 | `api/ws/feedback/tool_failure_notifier.py` | 도구 실패 TTS 안내 |
| 액션 피드백 | `api/ws/feedback/action_feedback.py` | 완료 피드백 |
| 검색 TTS | `api/ws/presenter/pages/search.py` | 검색 결과 음성 포맷 |
| 상품 TTS | `api/ws/presenter/pages/product.py` | 상품 정보 음성 포맷 |
| 장바구니 TTS | `api/ws/presenter/pages/cart.py` | 장바구니 음성 포맷 |
