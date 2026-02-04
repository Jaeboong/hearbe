# LLM 명령 생성 Flow

## 개요
사용자 텍스트를 받아 TextRouter에서 먼저 분기 처리 후, LLMPipelineHandler에서 NLU 분석 → LLMPlanner(규칙 기반 + LLM 폴백)로 MCP 명령을 생성하는 파이프라인.

## 핵심 포인트
- TextRouter가 LLM 전에 SearchQueryHandler, ProductOptionRule, AiNextRouter를 먼저 체크
- LLMPlanner 내부에서도 규칙 전에 select_from_results(), handle_product_option_rule() 먼저 체크
- CommandGenerator의 규칙은 6개만 등록: SiteAccess → SearchSelect → Search → Cart → Checkout → Generic
- LoginRule, ProductOptionRule은 CommandGenerator에 없음 (별도 경로로 처리)
- 장바구니 페이지 액션(선택/해제/수량변경)은 cart_action.py에서 별도 처리

---

## Flow 다이어그램 (전체 텍스트 처리 경로)

```
사용자 텍스트 입력
│
├─ [0] api/ws/handlers/text_routing/text_router.py → TextRouter.handle_text()
│   │
│   │  ※ LLM 도달 전 선처리 순서 (실제 코드):
│   │
│   ├─ 1. PaymentKeypadManager.handle_user_text() → 결제 키패드 입력 처리
│   ├─ 2. FlowHandler.is_flow_active() → 플로우 진행 중이면 플로우 핸들러로
│   ├─ 3. SearchQueryHandler.handle_query() → 검색 결과 읽기 요청이면 직접 처리 ★
│   ├─ 4. handle_product_option_rule() → 상품 옵션 선택이면 직접 처리 ★
│   ├─ 5. AiNextRouter.route() → AI_next 외부 규칙 매칭
│   └─ 6. LLMPipelineHandler.handle() → 위 모두 불일치 시 ★
│
├─ [1] api/ws/handlers/text_processing/llm_pipeline_handler.py → LLMPipelineHandler.handle()
│   │
│   ├─ [1-1] NLU 분석
│   │   └─ services/nlu/service.py
│   │       ├─ analyze_intent(text, context) → IntentResult(intent, confidence, entities)
│   │       └─ resolve_reference(text, context) → "그거" → 실제 상품명 치환
│   │
│   └─ [1-2] services/llm/planner/service.py → LLMPlanner.generate_commands()
│
├─ [2] LLMPlanner.generate_commands() 내부 처리 순서 (실제 코드 line 84~131)
│   │
│   ├─ Step 1: select_from_results(user_text, session)
│   │   └─ 검색 결과에서 "첫 번째", "그거" 등으로 상품 선택
│   │   └─ 매칭 시 → LLMResponse 즉시 반환 (규칙/LLM 스킵)
│   │
│   ├─ Step 2: handle_product_option_rule(user_text, session)
│   │   └─ 상품 상세 페이지에서 옵션 선택 ("빨간색", "XL")
│   │   └─ 매칭 시 → LLMResponse 즉시 반환
│   │
│   ├─ Step 3: CommandGenerator.generate_rules(user_text, current_url)
│   │   │
│   │   │  ※ CommandGenerator에 등록된 규칙 6개 (실제 코드):
│   │   ├─ 1. SiteAccessRule  → "쿠팡 열어", "네이버 접속"
│   │   │   └─ 키워드: 쿠팡/네이버/11번가 + 접속/열어/가
│   │   │   └─ 명령: goto(사이트 홈 URL) + wait(1000)
│   │   │
│   │   ├─ 2. SearchSelectRule → "선택해줘", "열어줘" (검색 페이지에서)
│   │   │   └─ 트리거: 선택/골라/열어/눌러/클릭 + 검색 페이지인지 확인
│   │   │   └─ 명령: click_text(대상) + wait_for_new_page + wait + extract_detail
│   │   │
│   │   ├─ 3. SearchRule → "핸드폰 검색해줘"
│   │   │   └─ 트리거: "검색" 키워드 포함
│   │   │   └─ 명령: goto + wait + fill + press(Enter) + wait + extract
│   │   │
│   │   ├─ 4. CartRule → "장바구니에 담아줘", "장바구니 보여줘"
│   │   │   └─ 트리거: "장바구니" + 담/추가/넣 또는 이동/가/보/열
│   │   │   └─ 명령: click(장바구니 버튼) + wait 또는 goto(장바구니 URL)
│   │   │
│   │   ├─ 5. CheckoutRule → "결제해줘", "바로구매"
│   │   │   └─ 트리거: 결제/주문/구매하기/바로구매
│   │   │   └─ 페이지별 분기: product→buy_now, checkout→pay_button, cart→checkout_button
│   │   │   └─ 명령: click(셀렉터) + wait(2000)
│   │   │
│   │   └─ 6. GenericClickRule → 그 외 클릭 시도
│   │       └─ 트리거: 클릭/눌러/선택
│   │       └─ 명령: click_text(대상 텍스트)
│   │
│   ├─ Step 4: handle_cart_action(user_text, session) — 규칙 실패(matched_rule="none") 시
│   │   └─ 장바구니 페이지에서만 동작
│   │   └─ 전체선택/해제, 개별 상품 선택/해제, 수량 변경
│   │   └─ 명령: click(체크박스 셀렉터) 또는 fill + press(수량 입력)
│   │
│   ├─ Step 5: LLMRoutingPolicy.decide(user_text, intent, rule_result)
│   │   └─ 규칙 결과와 의도를 고려하여 LLM 폴백 사용 여부 결정
│   │
│   └─ Step 6: LLMGenerator.generate() — 정책이 LLM 사용 결정 시
│       ├─ resolve_llm_api_key() → API 키 확인
│       ├─ OpenAI API 호출 (conversation_history, session_context 포함)
│       ├─ tool_calls 응답 파싱 → GeneratedCommand 리스트
│       └─ LLMResult → LLMResponse 변환
│
└─ [3] LLMPipelineHandler로 돌아옴
    │
    ├─ coerce_option_clicks() → 옵션 명령 보정
    ├─ FlowEngine.start_flow() → requires_flow=true이면 플로우 시작
    │
    └─ CommandPipeline
        ├─ prepare_commands() → 로그인 가드, captcha 핸들러, 정규화
        └─ dispatch()
            ├─ sender.send_tool_calls() → 클라이언트에 명령 전송
            └─ sender.send_tts_response() → TTS 응답 전송
```

---

## CommandGenerator 규칙 (실제 등록 순서)

```
CommandGenerator.rules = [
    1. SiteAccessRule    → 사이트 접속
    2. SearchSelectRule  → 검색 결과에서 상품 선택 (검색 페이지 한정)
    3. SearchRule        → 상품 검색
    4. CartRule          → 장바구니 담기/이동
    5. CheckoutRule      → 결제/구매
    6. GenericClickRule  → 일반 클릭 (최후 폴백)
]

※ 다음 규칙은 CommandGenerator에 없음:
- ProductOptionRule → TextRouter와 LLMPlanner에서 별도 호출
- LoginRule → CommandGenerator에 미등록 (LLM 폴백 또는 별도 처리)
- CartAction → LLMPlanner에서 규칙 실패 후 별도 호출
```

---

## 관련 파일 (실제 호출 관계 기준)

| 단계 | 파일 | 역할 |
|------|------|------|
| **텍스트 라우팅** | `api/ws/handlers/text_routing/text_router.py` | LLM 전 선처리 분기 |
| NLU 파이프라인 | `api/ws/handlers/text_processing/llm_pipeline_handler.py` | NLU → LLMPlanner 호출 |
| NLU | `services/nlu/service.py` | 의도 분석 + 참조 해소 |
| **LLM 플래너** | `services/llm/planner/service.py` | select → option → rules → cart_action → LLM |
| **규칙 생성기** | `services/llm/generators/command_generator.py` | 6개 규칙 순차 매칭 |
| 규칙 베이스 | `services/llm/rules/__init__.py` | BaseRule, RuleResult 정의 |
| 사이트 접속 규칙 | `services/llm/rules/site_access.py` | 사이트 이동 명령 |
| 검색 선택 규칙 | `services/llm/rules/select.py` | 검색 결과 클릭 |
| 검색 규칙 | `services/llm/rules/search.py` | 검색 명령 생성 |
| 장바구니 규칙 | `services/llm/rules/cart.py` | 장바구니 담기/이동 |
| 결제 규칙 | `services/llm/rules/checkout.py` | 결제 버튼 클릭 |
| 일반 클릭 규칙 | `services/llm/rules/generic.py` | 텍스트 기반 클릭 |
| **상품 옵션** | `services/llm/rules/product_option.py` | 옵션 선택 (별도 호출) |
| **장바구니 액션** | `services/llm/planner/cart_action.py` | 장바구니 페이지 조작 |
| 검색 결과 선택 | `services/llm/planner/selection/` | 검색 결과에서 상품 선택 |
| LLM 라우팅 정책 | `services/llm/planner/routing.py` | LLM 폴백 사용 여부 결정 |
| LLM 폴백 빌더 | `services/llm/planner/fallback.py` | LLM 결과 없을 때 폴백 |
| **명령 빌더** | `services/llm/context/context_rules.py` | goto/fill/press/wait/extract 등 실제 명령 생성 |
| LLM 생성기 | `services/llm/generators/llm_generator.py` | OpenAI API 호출 |
| 명령 파이프라인 | `api/ws/handlers/command_pipeline.py` | 명령 정규화, 전송 |

## 실제 MCP 도구 (규칙에서 생성하는 명령들)

| 도구명 | 설명 | 사용하는 규칙 |
|--------|------|---------------|
| `goto` | URL 이동 | SiteAccess, Search, Cart, Login |
| `fill` | 텍스트 입력 | Search, Login, CartAction |
| `press` | 키 입력 (Enter 등) | Search, Login, CartAction |
| `click` | CSS 셀렉터 클릭 | Cart, Checkout, SearchSelect, CartAction |
| `click_text` | 텍스트로 요소 찾아 클릭 | SearchSelect, Generic, Cart(폴백) |
| `wait` | 대기 (ms) | 대부분의 규칙 |
| `wait_for_selector` | 셀렉터 대기 | Login |
| `wait_for_new_page` | 새 탭/페이지 감지 | SearchSelect |
| `extract` | 검색 결과 추출 | Search |
| `extract_detail` | 상품 상세 추출 | SearchSelect, PageExtractManager |
| `extract_cart` | 장바구니 추출 | PageExtractManager |
| `handle_captcha_modal` | 캡차 처리 | CommandPipeline(로그인 페이지) |
