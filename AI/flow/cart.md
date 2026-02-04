# 장바구니 기능 Flow

## 개요
장바구니 관련 기능은 두 경로로 처리됨:
1. CartRule (CommandGenerator 내부) — "장바구니에 담아줘", "장바구니 보여줘"
2. cart_action.py (LLMPlanner에서 규칙 실패 후 호출) — 장바구니 페이지 내 조작 (선택/해제/수량변경)

## 핵심 포인트
- 장바구니 담기 명령은 `click(장바구니 버튼 셀렉터) + wait` 조합
- 장바구니 이동은 `goto(장바구니 URL)` 또는 `click_text("장바구니")` 폴백
- 장바구니 페이지 조작(선택/해제/수량)은 CommandGenerator가 아닌 cart_action.py에서 별도 처리
- 장바구니 내용 읽기는 MCPHandler에서 extract_cart 결과를 build_cart_summary_tts()로 포매팅

---

## Flow A: 장바구니 담기 ("장바구니에 담아줘")

```
사용자 입력 ("장바구니에 담아줘")
│
├─ [1] TextRouter → LLMPipelineHandler
│
├─ [2] LLMPlanner.generate_commands()
│   └─ CommandGenerator.generate_rules()
│       └─ services/llm/rules/cart.py → CartRule.check()
│           ├─ "장바구니" 키워드 확인 ✓
│           ├─ CART_ADD_TRIGGERS: "담", "추가", "넣" 매칭 ✓
│           └─ context_rules.build_add_to_cart_commands(current_site, current_url)
│               ├─ get_selector(url, "add_to_cart") → 사이트별 셀렉터
│               ├─ 폴백: site.get_selector("product", "add_to_cart")
│               └─ 최종 폴백: click_text("장바구니")
│
│           ※ 실제 생성되는 명령:
│           ├─ click(selector="장바구니 담기 버튼 셀렉터")
│           └─ wait(ms=1000)
│
├─ [3] CommandPipeline.dispatch()
│   ├─ ActionFeedback.register_commands() → 완료 피드백 등록
│   ├─ sender.send_tool_calls() → 클라이언트에 클릭 명령
│   └─ sender.send_tts_response() → "장바구니에 담고 있습니다."
│
├─ [4] 클라이언트: 버튼 클릭 → mcp_result 전송
│
└─ [5] MCPHandler.handle_mcp_result()
    └─ ActionFeedback.handle_mcp_result() → 완료 TTS
```

## Flow B: 장바구니 이동 ("장바구니 보여줘")

```
사용자 입력 ("장바구니 보여줘")
│
├─ CartRule.check()
│   ├─ "장바구니" ✓ + CART_GO_TRIGGERS: "이동/가/보/열" 매칭 ✓
│   └─ context_rules.build_go_to_cart_commands(current_site)
│       ├─ site.get_url("cart") → 장바구니 URL
│       └─ 폴백: click_text("장바구니")
│
│   ※ 실제 생성되는 명령:
│   └─ goto(url="https://cart.coupang.com/cartView.pang")
│
├─ 클라이언트: 장바구니 페이지 이동 → page_update 이벤트
│
├─ PageExtractManager.handle_page_update()
│   ├─ get_page_type(url) → "cart"
│   └─ _build_extract_commands("cart")
│       ├─ wait(ms=1200)
│       └─ extract_cart() → 장바구니 내용 추출
│
├─ 클라이언트: extract_cart 실행 → mcp_result(cart_items=[...]) 전송
│
└─ MCPHandler.handle_mcp_result()
    ├─ session.context["cart_items"] = cart_items
    ├─ session.context["cart_summary"] = cart_summary
    ├─ JSON 파일로 저장 (TempFileManager)
    └─ presenter/pages/cart.py → build_cart_summary_tts(cart_items, cart_summary)
        └─ TTS: "장바구니에 N개 상품이 있습니다. 1번 ..."
```

## Flow C: 장바구니 페이지 조작 ("2번 상품 선택해줘", "수량 3개로")

```
사용자 입력 ("2번 상품 수량 3개로 변경해줘")
│
├─ [1] TextRouter → LLMPipelineHandler
│
├─ [2] LLMPlanner.generate_commands()
│   ├─ CommandGenerator.generate_rules() → 모든 규칙 미매칭 (matched_rule="none")
│   │   └─ CartRule: "장바구니" 키워드 없음 → 미매칭
│   │
│   └─ services/llm/planner/cart_action.py → handle_cart_action() ★
│       ├─ get_page_type(current_url) == "cart" 확인
│       ├─ session.context["cart_items"] 에서 상품 목록 가져옴
│       ├─ _resolve_target_item() → "2번" → cart_items[1] → 상품명 추출
│       ├─ _extract_quantity() → "3개" → 3
│       └─ 수량 변경 명령 생성:
│           ├─ fill(selector="해당 상품 수량 입력칸", text="3")
│           └─ press(selector="해당 상품 수량 입력칸", key="Enter")
│
├─ [3] LLMResponse 반환 → CommandPipeline.dispatch()
│   └─ TTS: "'상품명' 수량을 3개로 변경합니다."
│
└─ 기타 조작:
    ├─ "전체 선택" → click(select_all_checkbox)
    ├─ "1번 상품 선택" → click(해당 상품 체크박스)
    └─ "1번 상품 해제" → click(해당 상품 체크박스)
```

---

## 관련 파일 (실제 호출 관계 기준)

| 단계 | 파일 | 역할 |
|------|------|------|
| **장바구니 규칙** | `services/llm/rules/cart.py` | 담기/이동 명령 생성 |
| **장바구니 액션** | `services/llm/planner/cart_action.py` | 장바구니 페이지 내 조작 (선택/수량) |
| 명령 빌더 | `services/llm/context/context_rules.py` | click/goto/click_text 명령 생성 |
| 사이트 매니저 | `services/llm/sites/site_manager.py` | get_selector(), get_page_type() |
| 자동 추출 | `api/ws/handlers/page_extract_manager.py` | 장바구니 페이지 진입 시 auto-extract |
| MCP 결과 | `api/ws/handlers/mcp_handler.py` | cart_items 세션 저장 + TTS |
| TTS 포매팅 | `api/ws/presenter/pages/cart.py` | build_cart_summary_tts() |
| 액션 피드백 | `api/ws/feedback/action_feedback.py` | 담기 완료 피드백 |
