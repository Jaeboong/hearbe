# 검색 기능 Flow

## 개요
사용자가 음성/텍스트로 상품을 검색하면, goto/fill/press/wait + extract 조합의 브라우저 자동화 명령을 생성하여 검색을 실행하고, extract 결과를 기반으로 음성 안내하는 흐름.

## 핵심 진입 파일

- 검색 명령 규칙: `services/llm/rules/search.py`
- 검색 결과 읽기: `api/ws/handlers/search_query_handler.py`
- 자동 추출: `api/ws/handlers/page_extract_manager.py`

### import 맵 (프로젝트 내부)

`services/llm/rules/search.py`
- `services/llm/context/context_rules.py`
- `services/llm/rules/__init__.py`

`api/ws/handlers/search_query_handler.py`
- `services/llm/generators/tts_pages/search.py`
- `api/ws/search/search_insights.py`

`api/ws/handlers/page_extract_manager.py`
- `core/interfaces.py`
- `services/llm/context/context_rules.py`
- `services/llm/sites/site_manager.py`

## 핵심 포인트
- 검색 명령은 `search`라는 단일 도구가 아닌, `goto` → `fill` → `press`(Enter) → `wait` → `extract` 조합으로 생성됨
- 검색 결과 **읽기만** `SearchQueryHandler`가 LLM 없이 처리
- 최저가/할인율/내일배송/무료배송 필터 요청은 현재 LLM으로 위임됨
- 결과 읽기는 `search_reader.build_search_read_tts()`를 `presenter/pages/search.py`가 래핑하여 사용
- 페이지 변경 시 `PageExtractManager`가 자동으로 extract 명령을 트리거

---

## Flow A: 신규 검색 ("핸드폰 검색해줘")

```
사용자 입력 ("쿠팡에서 핸드폰 검색해줘")
│
├─ [1] api/websocket.py → WebSocketHandler
│   └─ WebSocket user_input 메시지 수신
│
├─ [2] api/ws/router.py → WebSocketRouter.handle_text()
│   └─ HandlerManager.handle_user_input() → TextHandler 위임
│
├─ [3] api/ws/handlers/text_handler.py → TextHandler.enqueue_text()
│   └─ 텍스트 큐에 추가, 워커가 비동기 처리
│
├─ [4] api/ws/handlers/text_routing/text_router.py → TextRouter.handle_text()
│   │
│   │  ※ 라우팅 우선순위 (실제 코드 순서):
│   │  1. PaymentKeypadManager → 결제 키패드 입력 확인
│   │  2. FlowHandler → 플로우 활성 중인지 확인
│   │  3. SearchQueryHandler → 결과 읽기/필터 요청인지 확인 (★ LLM 전에 먼저!)
│   │  4. ProductOptionRule → 상품 옵션 선택인지 확인
│   │  5. AiNextRouter → AI_next 규칙 라우터 (외부 모듈)
│   │  6. LLMPipelineHandler → 최종 폴백
│   │
│   ├─ SearchQueryHandler.handle_query() → "검색" 포함이므로 읽기 요청 아님 → False
│   └─ LLMPipelineHandler.handle() 로 진입
│
├─ [5] api/ws/handlers/text_processing/llm_pipeline_handler.py
│   │
│   ├─ [5-1] NLU 분석
│   │   └─ services/nlu/service.py → analyze_intent() + resolve_reference()
│   │       └─ IntentResult(intent=SEARCH)
│   │
│   └─ [5-2] services/llm/planner/service.py → LLMPlanner.generate_commands()
│       │
│       │  ※ LLMPlanner 내부 처리 순서 (실제 코드):
│       │  1. select_from_results() → 검색 결과 선택인지 확인
│       │  2. handle_product_option_rule() → 옵션 선택인지 확인
│       │  3. CommandGenerator.generate_rules() → 규칙 기반 매칭 ★
│       │  4. handle_cart_action() → 장바구니 액션 확인 (규칙 실패 시)
│       │  5. LLMRoutingPolicy.decide() → LLM 폴백 여부 결정
│       │  6. LLMGenerator.generate() → LLM 폴백 (정책 허용 시)
│       │
│       ├─ CommandGenerator.generate_rules() 진입
│       │   └─ 규칙 순서: SiteAccessRule → SearchSelectRule → SearchRule → ...
│       │
│       └─ services/llm/rules/search.py → SearchRule.check() 매칭됨!
│           │
│           ├─ context_rules.extract_search_query("쿠팡에서 핸드폰 검색해줘")
│           │   └─ 정규식으로 "검색" 앞 텍스트 추출 → query = "핸드폰"
│           │
│           ├─ context_rules.detect_target_site() → "쿠팡" 키워드 감지
│           │   └─ site_manager.get_site("coupang") → SiteConfig 반환
│           │
│           ├─ context_rules.build_search_with_navigation_commands()
│           │   │  ※ 실제 생성되는 명령들:
│           │   ├─ goto(url="https://www.coupang.com")  ← 사이트 이동 필요 시
│           │   ├─ wait(ms=1000)                        ← 페이지 로딩 대기
│           │   ├─ fill(selector="#headerSearchKeyword", text="핸드폰")
│           │   ├─ press(selector="#headerSearchKeyword", key="Enter")
│           │   └─ wait(ms=1500)                        ← 검색 결과 로딩 대기
│           │
│           └─ context_rules.build_extract_products_command()
│               └─ extract(selector="상품리스트 셀렉터",
│                          fields=["name","price","rating","discount","delivery",...],
│                          field_selectors={...},
│                          fallback_dynamic=True)
│
├─ [6] api/ws/handlers/command_pipeline.py → CommandPipeline
│   ├─ prepare_commands() → 로그인 페이지면 captcha 핸들러 추가, 명령 정규화
│   └─ dispatch()
│       ├─ LoginGuard.prepare_guard() → 로그인 가드 체크
│       ├─ sender.send_tool_calls() → 클라이언트에 명령 전송 ★
│       ├─ ActionFeedback.register_commands() → 액션 피드백 등록
│       └─ sender.send_tts_response() → "'핸드폰'을 쿠팡에서 검색합니다." TTS 전송
│
├─ [7] 클라이언트: 브라우저에서 명령 순차 실행
│   └─ goto → wait → fill → press → wait → extract 실행
│       └─ extract 결과: { products: [{name, price, rating, ...}, ...] }
│
├─ [8] 클라이언트 → mcp_result 전송 (tool_name="extract", result={products: [...]})
│
├─ [9] api/ws/handlers/mcp_handler.py → MCPHandler.handle_mcp_result()
│   │
│   ├─ products 데이터 추출 (page_data.products 또는 result.products)
│   ├─ 세션에 저장:
│   │   ├─ session.context["search_results"] = products
│   │   ├─ session.context["search_active_results"] = products
│   │   └─ session.context["search_read_index"] = 0
│   ├─ JSON 파일로 저장 (TempFileManager)
│   │
│   └─ presenter/pages/search.py → build_search_list_tts()
│       └─ search/search_reader.py → build_search_read_tts()
│           └─ 상위 4개 상품: "총 N개 상품입니다. 1번, {이름}. 가격 {가격}. ..."
│
└─ [10] api/ws/sender.py → send_tts_response()
    └─ TTS: "총 20개 상품입니다. 1번 삼성 갤럭시 S25. 가격 120만원. 2번 ..."
    └─ "더 읽어드릴까요? '몇 개 더 읽어줘' 또는 '전체 읽어줘'라고 말해 주세요."
```

---

## Flow B: 검색 결과 읽기/필터 ("전체 읽어줘", "더 읽어줘", "내일 도착하는 상품")

```
사용자 입력 ("3개 더 읽어줘")
│
├─ [1~3] WebSocket → TextHandler → TextRouter
│
├─ [4] TextRouter.handle_text()
│   └─ SearchQueryHandler.handle_query() ← LLM 가기 전에 여기서 처리됨!
│       │
│       ├─ _is_attribute_query() → 가격/할인/배송/평점 질문? → LLM에 위임 (False 반환)
│       ├─ _is_read_request() → "읽어" 키워드 + "더" + "3개" 패턴 매칭 → True
│       │
│       └─ _handle_read_query()
│           ├─ session.context["search_active_results"] 에서 결과 가져옴
│           ├─ session.context["search_read_index"] 에서 현재 위치 가져옴
│           ├─ _parse_read_request() → mode="more", count=3
│           ├─ build_search_list_tts(results, start_index, count=3)
│           │   └─ search_reader.build_search_read_tts()
│           └─ sender.send_tts_response() → "5번 ... 6번 ... 7번 ..."
│
└─ LLM Pipeline 까지 도달하지 않음 (SearchQueryHandler가 True 반환)
```

### 필터 요청 ("내일 도착하는 상품만 보여줘")

```
※ 현재 코드에서 필터 요청은 handle_query()에서 False를 반환하고 LLM에 위임됨
※ _handle_insight_query()는 존재하지만 handle_query()에서 직접 호출되지 않음
※ 할인율/최저가/내일배송/무료배송 필터는 _is_*_request()에서 True이면 LLM으로 위임
```

---

## Flow C: 페이지 변경 시 자동 검색 결과 추출

```
클라이언트가 검색 결과 페이지로 이동 (page_update 이벤트)
│
├─ api/ws/handlers/page_extract_manager.py → PageExtractManager.handle_page_update()
│   ├─ get_page_type(url) → "search" 판별
│   ├─ 동일 URL이면 스킵, 최소 간격 1초 체크
│   ├─ _build_extract_commands("search", url)
│   │   ├─ wait(ms=1200)
│   │   └─ extract(selector=상품리스트, fields=[...], fallback_dynamic=True)
│   └─ sender.send_tool_calls() → 자동 extract 명령 전송
│
└─ 클라이언트 → extract 실행 → mcp_result → MCPHandler → 결과 저장 + TTS
```

---

## 관련 파일 (실제 호출 관계 기준)

| 단계 | 파일 | 역할 |
|------|------|------|
| WS 라우팅 | `api/ws/router.py` | 메시지 타입별 분기 |
| 텍스트 큐 | `api/ws/handlers/text_handler.py` | 큐 기반 비동기 텍스트 처리 |
| **텍스트 라우팅** | `api/ws/handlers/text_routing/text_router.py` | SearchQueryHandler → LLM Pipeline 순서 분기 |
| **검색 결과 읽기** | `api/ws/handlers/search_query_handler.py` | 읽기/필터 요청 LLM 없이 직접 처리 |
| NLU | `services/nlu/service.py` | 의도 분석 (SEARCH 의도 감지) |
| **LLM 플래너** | `services/llm/planner/service.py` | select → option → rules → cart → LLM 폴백 |
| **규칙 생성기** | `services/llm/generators/command_generator.py` | 규칙 체인: SiteAccess → Select → Search → Cart → Checkout → Generic |
| **검색 규칙** | `services/llm/rules/search.py` | "검색" 키워드 매칭 → build_search_with_navigation_commands 호출 |
| **명령 빌더** | `services/llm/context/context_rules.py` | goto/fill/press/wait/extract 명령 실제 생성 |
| 명령 파이프라인 | `api/ws/handlers/command_pipeline.py` | 명령 정규화, 로그인 가드, 전송 |
| **MCP 결과 처리** | `api/ws/handlers/mcp_handler.py` | extract 결과 → 세션 저장 → TTS |
| **TTS 포매팅** | `api/ws/presenter/pages/search.py` | build_search_list_tts() → search_reader 래핑 |
| **결과 읽기** | `api/ws/search/search_reader.py` | build_search_read_tts() → 이름+가격 포맷 |
| 결과 분석 | `api/ws/search/search_insights.py` | 최저가/할인율/배송 필터 유틸 |
| **자동 추출** | `api/ws/handlers/page_extract_manager.py` | 페이지 변경 시 auto-extract 트리거 |
| LLM 폴백 | `services/llm/generators/llm_generator.py` | 규칙 실패 시 OpenAI API 호출 |
| LLM 라우팅 | `services/llm/planner/routing.py` | LLM 폴백 사용 여부 정책 결정 |

## 실제 MCP 도구 목록 (검색 관련)

| 도구명 | 설명 | 생성 위치 |
|--------|------|-----------|
| `goto` | URL 이동 | `context_rules.build_goto_command()` |
| `fill` | 검색창에 텍스트 입력 | `context_rules.build_fill_command()` |
| `press` | Enter 키 입력 | `context_rules.build_press_command()` |
| `click` | 검색 버튼 클릭 | `context_rules.build_click_command()` |
| `wait` | 페이지 로딩 대기 | `context_rules.build_wait_command()` |
| `extract` | 검색 결과 상품 목록 추출 | `context_rules.build_extract_products_command()` |
