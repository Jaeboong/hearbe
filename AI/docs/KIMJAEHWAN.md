# 김재환 담당 파트 명세서

> AI 서버 - LLM & Flow Engine & OCR 담당

---

## 담당 기능 목록

| 번호 | 기능명 | 설명 | 상태 |
|------|--------|------|------|
| AI-05 | LLM 명령 생성 | GPT 기반 자연어 → MCP 명령 변환 | 미구현 |
| AI-06 | 플로우 엔진 | 사이트별 쇼핑 플로우 단계 처리 | 미구현 |
| AI-07 | OCR 인식 | 결제 키패드/인증 이미지 인식 | 미구현 |

---

## 담당 모듈 구조

```
AI/
├── services/
│   ├── llm.py              # OpenAI API, 명령 생성
│   ├── flow_engine.py      # 플로우 상태 머신
│   └── ocr.py              # HF OCR 모델, 키패드 인식
├── flows/
│   ├── coupang/
│   │   ├── search.json     # 쿠팡 검색 플로우
│   │   ├── checkout.json   # 쿠팡 결제 플로우
│   │   └── signup.json     # 쿠팡 회원가입 플로우
│   ├── naver/
│   │   ├── search.json     # 네이버 검색 플로우
│   │   └── checkout.json   # 네이버 결제 플로우
│   └── elevenst/
│       ├── search.json     # 11번가 검색 플로우
│       └── checkout.json   # 11번가 결제 플로우
├── models/
│   └── flow.py             # 플로우 데이터 모델 (Pydantic)
└── tests/
    ├── test_llm.py
    ├── test_flow_engine.py
    └── test_ocr.py
```

---

## AI-05: LLM 명령 생성

### 기능 설명
사용자의 자연어 발화를 MCP 브라우저 자동화 명령으로 변환합니다.

### 상세 동작
1. WebSocket에서 STT 결과 텍스트 수신
2. GPT-5-mini로 의도 분석 (NLU)
   - 상품 검색, 장바구니 추가, 결제 진행 등 의도 파악
   - 상품명, 브랜드, 가격 범위 등 개체명 추출 (NER)
3. MCP tool_call 형식으로 명령 생성
4. 일반 명령 vs 플로우 필요 여부 판단
   - 일반 명령 → 즉시 MCP 실행
   - 회원가입/결제 → Flow Engine으로 위임

### 구현 파일
- `services/llm.py`

### 예시: 자연어 → MCP 명령 변환

**입력**:
```
"쿠팡에서 물티슈 검색해줘"
```

**출력** (순차 실행):
```json
[
    {
        "tool_name": "navigate_to_url",
        "arguments": {"url": "https://www.coupang.com"}
    },
    {
        "tool_name": "fill_input",
        "arguments": {"selector": "#headerSearchKeyword", "value": "물티슈"}
    },
    {
        "tool_name": "click_element",
        "arguments": {"selector": ".search-btn"}
    }
]
```

### LLM 프롬프트 구조

```python
SYSTEM_PROMPT = """
당신은 시각장애인을 위한 쇼핑 도우미입니다.
사용자의 자연어 요청을 브라우저 자동화 명령으로 변환합니다.

사용 가능한 도구:
- navigate_to_url(url): URL로 이동
- click_element(selector): 요소 클릭
- fill_input(selector, value): 입력 필드 채우기
- get_text(selector): 텍스트 추출
- take_screenshot(): 스크린샷 캡처
- scroll(direction, amount): 페이지 스크롤

출력 형식: JSON 배열로 tool_call 목록 반환
"""
```

### 환경 변수
```env
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-5-mini
LLM_MAX_TOKENS=1024
LLM_TEMPERATURE=0.7
```

### 인터페이스
```python
class ILLMService:
    async def generate_commands(self, user_input: str, context: dict) -> List[ToolCall]: ...
    async def analyze_intent(self, user_input: str) -> Intent: ...
    def should_use_flow(self, intent: Intent) -> bool: ...
```

---

## AI-06: 플로우 엔진

### 기능 설명
회원가입, 결제 등 복잡한 작업을 사이트별 정의된 단계에 따라 처리합니다.

### 상세 동작
1. LLM이 플로우 필요 여부 판단 (회원가입/결제 요청 시)
2. 사이트별 플로우 JSON 파일 로딩
3. 각 단계 실행:
   - TTS로 안내 메시지 출력
   - 사용자 입력 대기 (음성/텍스트)
   - MCP 명령 실행
   - 성공/실패 검증
4. 결제 전 최종 확인 삽입 (Policy/Guard)
   - 상품명, 가격, 수량, 배송지 음성 확인
   - 민감 정보는 로컬에서만 입력

### 구현 파일
- `services/flow_engine.py` - 플로우 상태 머신
- `flows/**/*.json` - 사이트별 플로우 정의
- `models/flow.py` - Pydantic 데이터 모델

### 플로우 JSON 스키마

```json
{
    "flow_id": "coupang_checkout",
    "flow_type": "checkout",
    "site": "coupang",
    "total_steps": 5,
    "steps": [
        {
            "step_id": 1,
            "name": "cart_confirm",
            "prompt": "장바구니에 {product_name}이 담겨있습니다. 결제를 진행할까요?",
            "required_fields": [],
            "action": {
                "tool_name": "click_element",
                "arguments": {"selector": ".checkout-btn"}
            },
            "validation": {
                "type": "selector_exists",
                "selector": ".order-sheet"
            },
            "fallback": "결제 페이지로 이동하지 못했습니다. 다시 시도할까요?",
            "next_step": 2
        },
        {
            "step_id": 2,
            "name": "address_confirm",
            "prompt": "배송지를 확인해주세요. {address}로 배송됩니다. 맞으시면 '네'라고 말씀해주세요.",
            "required_fields": ["address"],
            "user_confirmation": true,
            "action": null,
            "next_step": 3
        }
    ]
}
```

### 지원 플로우 목록

| 사이트 | 플로우 타입 | 파일 | 상태 |
|--------|-------------|------|------|
| 쿠팡 | 검색 | `flows/coupang/search.json` | 미구현 |
| 쿠팡 | 결제 | `flows/coupang/checkout.json` | 미구현 |
| 쿠팡 | 회원가입 | `flows/coupang/signup.json` | 미구현 |
| 네이버 | 검색 | `flows/naver/search.json` | 미구현 |
| 네이버 | 결제 | `flows/naver/checkout.json` | 미구현 |
| 11번가 | 검색 | `flows/elevenst/search.json` | 미구현 |
| 11번가 | 결제 | `flows/elevenst/checkout.json` | 미구현 |

### 상태 머신 구조

```
[IDLE] → [FLOW_STARTED] → [STEP_EXECUTING] → [WAITING_USER] → [STEP_COMPLETED]
                                    ↓                                ↓
                              [STEP_FAILED]                   [FLOW_COMPLETED]
                                    ↓
                              [RETRY/ABORT]
```

### 인터페이스
```python
class IFlowEngine:
    async def start_flow(self, flow_id: str, context: dict) -> FlowState: ...
    async def execute_step(self, flow_state: FlowState) -> StepResult: ...
    async def handle_user_input(self, flow_state: FlowState, user_input: str) -> FlowState: ...
    def get_current_prompt(self, flow_state: FlowState) -> str: ...
```

---

## AI-07: OCR 인식

### 기능 설명
결제 키패드, CAPTCHA, 보안문자 등 인증 이미지를 인식합니다.

### 상세 동작
1. MCP 앱에서 스크린샷 (base64) 수신
2. 이미지 전처리 (크기 조정, 노이즈 제거)
3. TrOCR 또는 PaddleOCR로 텍스트 추출
4. 키패드인 경우:
   - 키패드 영역 검출 (바운딩 박스)
   - 숫자 위치 매핑
   - 좌표 → 숫자 변환 결과 반환
5. 인식 결과를 LLM에 전달하여 다음 액션 결정

### 구현 파일
- `services/ocr.py`

### 키패드 인식 예시

**입력**: 결제 키패드 스크린샷

**출력**:
```json
{
    "type": "keypad",
    "layout": [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"],
        ["", "0", ""]
    ],
    "positions": {
        "0": {"x": 150, "y": 300},
        "1": {"x": 50, "y": 100},
        "2": {"x": 150, "y": 100},
        ...
    }
}
```

### CAPTCHA 인식 예시

**입력**: 보안문자 이미지

**출력**:
```json
{
    "type": "captcha",
    "text": "X7K9M2",
    "confidence": 0.92
}
```

### 환경 변수
```env
OCR_MODEL=trocr-base-printed
OCR_DEVICE=cuda
OCR_CONFIDENCE_THRESHOLD=0.8
```

### 인터페이스
```python
class IOCRService:
    async def recognize_image(self, image_base64: str) -> OCRResult: ...
    async def detect_keypad(self, image_base64: str) -> KeypadLayout: ...
    async def recognize_captcha(self, image_base64: str) -> str: ...
```

---

## 개발 일정 (TEAM_ASSIGNMENT 기준)

### Week 1 (Day 2-5)
| 일차 | 작업 | 파일 | 시간 |
|------|------|------|------|
| 2일 | OpenAI API 연동 | services/llm.py | 4h |
| 2일 | 명령 생성 로직 | services/llm.py | 4h |
| 3일 | 플로우 엔진 구조 설계 | services/flow_engine.py | 4h |
| 3일 | 플로우 JSON 스키마 정의 | models/flow.py | 4h |
| 4일 | 쿠팡 검색 플로우 JSON | flows/coupang/search.json | 4h |
| 4일 | 플로우 실행 엔진 구현 | services/flow_engine.py | 4h |
| 5일 | LLM 단위 테스트 | tests/test_llm.py | 4h |
| 5일 | Flow 단위 테스트 | tests/test_flow_engine.py | 4h |

### Week 2 (Day 6-10)
| 일차 | 작업 | 파일 | 시간 |
|------|------|------|------|
| 6일 | 쿠팡 결제 플로우 JSON | flows/coupang/checkout.json | 4h |
| 6일 | 플로우 단계별 실행 | services/flow_engine.py | 4h |
| 7일 | OCR 모델 로딩 | services/ocr.py | 4h |
| 7일 | 키패드 인식 로직 | services/ocr.py | 4h |
| 8일 | 네이버 검색 플로우 | flows/naver/search.json | 4h |
| 8일 | 11번가 검색 플로우 | flows/elevenst/search.json | 4h |
| 9일 | OCR 단위 테스트 | tests/test_ocr.py | 4h |
| 10일 | 플로우 통합 테스트 | tests/test_flow_engine.py | 4h |

### Week 4 (Day 16-18)
| 일차 | 작업 | 파일 | 시간 |
|------|------|------|------|
| 16일 | 쿠팡 회원가입 플로우 | flows/coupang/signup.json | 4h |
| 16일 | 네이버 결제 플로우 | flows/naver/checkout.json | 4h |
| 17일 | 11번가 결제 플로우 | flows/elevenst/checkout.json | 4h |
| 18일 | 플로우 에러 처리 개선 | services/flow_engine.py | 4h |

---

## 필요 기술 스택

- **OpenAI API** - GPT-5-mini 호출
- **Pydantic** - 데이터 모델 정의/검증
- **JSON Schema** - 플로우 정의 파일
- **상태 머신 패턴** - 플로우 엔진 구현
- **Hugging Face Transformers** - TrOCR 모델
- **PaddleOCR** - 대안 OCR 엔진

---

## 학습 리소스

- OpenAI API: https://platform.openai.com/docs/api-reference
- Flow State Machine: https://en.wikipedia.org/wiki/Finite-state_machine
- TrOCR: https://huggingface.co/microsoft/trocr-base-printed
- PaddleOCR: https://github.com/PaddlePaddle/PaddleOCR
- JSON Schema: https://json-schema.org/

---

**문서 버전**: 1.0
**작성일**: 2026-01-16
**담당자**: 김재환
