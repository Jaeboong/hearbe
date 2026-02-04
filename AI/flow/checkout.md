# 결제 (Checkout) Flow

## 개요
사용자가 결제를 요청하면 CheckoutRule이 페이지 타입에 따라 적절한 결제 버튼 클릭 명령을 생성. FlowEngine은 별도의 다단계 워크플로우를 관리하며, 결제 키패드는 OCR 기반으로 처리.

## 핵심 진입 파일

- 결제 명령 규칙: `services/llm/rules/checkout.py`
- 키패드 처리: `api/ws/handlers/payment_keypad.py`

### import 맵 (프로젝트 내부)

`services/llm/rules/checkout.py`
- `services/llm/context/context_rules.py`
- `services/llm/rules/__init__.py`
- `services/llm/sites/site_manager.py`

`api/ws/handlers/payment_keypad.py`
- `core/interfaces.py`
- `services/llm/sites/site_manager.py`
- `services/ocr/payment/keypad_mapper.py`
- `api/ws/presenter/pages/checkout.py`

## 핵심 포인트
- CheckoutRule은 FlowEngine을 직접 호출하지 않음 → click + wait 명령만 생성
- FlowEngine은 LLMPlanner가 `requires_flow=true`를 반환할 때 LLMPipelineHandler에서 시작
- 결제 키패드는 PaymentKeypadManager → OCR 파이프라인으로 별도 처리
- 페이지 타입(product/checkout/cart)에 따라 다른 버튼 셀렉터 사용

---

## Flow A: 결제 버튼 클릭 ("결제해줘", "바로구매")

```
사용자 입력 ("결제해줘")
│
├─ [1] TextRouter → LLMPipelineHandler (SearchQueryHandler 등 미매칭)
│
├─ [2] LLMPlanner.generate_commands()
│   ├─ select_from_results() → 미매칭
│   ├─ handle_product_option_rule() → 미매칭
│   └─ CommandGenerator.generate_rules()
│       └─ services/llm/rules/checkout.py → CheckoutRule.check() 매칭!
│           │
│           ├─ 트리거: 결제/주문/구매하기/바로구매 키워드 확인
│           ├─ get_page_type(current_url) → 페이지 타입 판별
│           │
│           ├─ page_type == "product"
│           │   └─ get_selector(url, "buy_now") → 바로구매 버튼
│           ├─ page_type == "checkout"
│           │   └─ get_selector(url, "pay_button") → 결제하기 버튼
│           ├─ page_type == "cart"
│           │   └─ get_selector(url, "checkout_button") → 구매하기 버튼
│           └─ 폴백: "button:has-text('결제하기'), button:has-text('바로구매'), ..."
│
│           ※ 실제 생성되는 명령:
│           ├─ click(selector="결제 버튼 셀렉터")
│           └─ wait(ms=2000)
│
├─ [3] CommandPipeline.dispatch()
│   ├─ sender.send_tool_calls() → 클라이언트에 클릭 명령
│   └─ sender.send_tts_response() → "결제하기를 진행합니다."
│
└─ [4] 클라이언트: 버튼 클릭 → 결제 페이지 이동 또는 결제 완료
```

## Flow B: 결제 키패드 비밀번호 입력

```
결제 단계에서 키패드 이미지 수신
│
├─ [1] TextRouter.handle_text()
│   └─ PaymentKeypadManager.handle_user_text() ← 최우선 체크!
│       └─ 키패드 활성 상태이면 여기서 처리
│
├─ [2] api/ws/handlers/payment_keypad.py → PaymentKeypadManager
│   └─ 사용자 음성 비밀번호 수신 ("1234")
│
├─ [3] services/ocr/payment/keypad_mapper.py
│   ├─ korean_ocr.process_image() → 숫자 인식
│   ├─ digit_extractor.py → 숫자 추출
│   └─ digit_to_dom_mapper.py → 숫자 → DOM key 매핑
│
└─ [4] 각 숫자별 클릭 명령 생성
    └─ click_element(selector, frame_selector?) × N회 → 클라이언트에서 순차 실행
```

---

## 관련 파일 (실제 호출 관계 기준)

| 단계 | 파일 | 역할 |
|------|------|------|
| **결제 규칙** | `services/llm/rules/checkout.py` | 페이지 타입별 결제 버튼 클릭 명령 생성 |
| 명령 빌더 | `services/llm/context/context_rules.py` | GeneratedCommand 데이터클래스 |
| 사이트 매니저 | `services/llm/sites/site_manager.py` | get_page_type(), get_selector() |
| **결제 키패드** | `api/ws/handlers/payment_keypad.py` | 키패드 OCR 관리 |
| 키패드 OCR | `services/ocr/payment/keypad_mapper.py` | 키패드 이미지 인식 |
| 숫자 추출 | `services/ocr/payment/digit_extractor.py` | 키패드 숫자 위치 추출 |
| DOM 매핑 | `services/ocr/payment/digit_to_dom_mapper.py` | 숫자 → DOM 좌표 |
| 플로우 엔진 | `services/flow/service.py` | 다단계 플로우 관리 |
| 플로우 정의 | `services/flow/service.py` | 하드코딩 플로우 정의 |
