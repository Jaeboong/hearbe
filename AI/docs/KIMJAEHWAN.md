# 김재환 담당 파트 명세서

> AI 서버 - LLM & Flow Engine 담당

---

## 담당 기능 목록

| 번호 | 기능명 | 설명 | 상태 |
|------|--------|------|------|
| AI-05 | LLM 명령 생성 | GPT 기반 자연어 → MCP 명령 변환 | 미구현 |
| AI-06 | 플로우 엔진 | 사이트별 쇼핑 플로우 단계 처리 | 미구현 |

---

## 담당 모듈 구조

```
AI/
├── services/
│   └── llm/                     # LLM 관련 모듈 (담당 핵심)
│       ├── service.py           # LLMPlanner (의도 기반 명령 생성)
│       ├── command_generator.py # 규칙 기반 명령 생성 ✅ 구현
│       ├── site_manager.py      # 사이트 설정 관리 ✅ 구현
│       └── context_rules.py     # 컨텍스트 인식 규칙 ✅ 구현
├── sites/                       # 사이트별 JSON 설정 ✅ 구현
│   ├── coupang.json             # 쿠팡 URL/셀렉터
│   ├── naver.json               # 네이버쇼핑 URL/셀렉터
│   └── 11st.json                # 11번가 URL/셀렉터
├── flows/                       # 플로우 정의 (미구현)
│   ├── coupang/
│   │   ├── search.json
│   │   ├── checkout.json
│   │   └── signup.json
│   ├── naver/
│   └── elevenst/
├── models/
│   └── flow.py                  # 플로우 데이터 모델 (Pydantic)
├── scripts/
│   └── test_command_cli.py      # 명령 생성 테스트 CLI ✅ 구현
└── tests/
    ├── test_llm.py
    └── test_flow_engine.py
```


---

## AI-05: LLM 명령 생성 (RAG 기반)

### 기능 설명
사용자의 자연어 발화를 MCP 브라우저 자동화 명령으로 변환합니다.
**RAG(Retrieval-Augmented Generation)** 기반으로 MariaDB Vector DB에서 유사 예제를 검색하여 신뢰도를 높입니다.

### 아키텍처

```
┌─────────────────────────────────────────────────────────────────────┐
│                     RAG 기반 명령 생성 파이프라인                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   [사용자 발화] → [임베딩 생성] → [Vector 검색] → [Few-Shot 구성]     │
│                         ↓                                           │
│                   MariaDB Vector DB                                 │
│                   ┌─────────────────┐                               │
│                   │ - Intent 예제   │                               │
│                   │ - MCP 명령 템플릿│                               │
│                   │ - Flow 패턴     │                               │
│                   │ - 에러 복구 예제│                               │
│                   └─────────────────┘                               │
│                         ↓                                           │
│   [유사 예제 Top-K] → [Few-Shot 프롬프트] → [GPT-5-mini] → [tool_calls]│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 상세 동작
1. **임베딩 생성**: 사용자 발화를 OpenAI Embedding 또는 Sentence-BERT로 벡터화
2. **Vector 검색**: MariaDB Vector DB에서 유사한 예제 Top-K 검색
3. **Few-Shot 프롬프트 구성**: 검색된 예제를 프롬프트에 포함
4. **LLM 추론**: GPT-5-mini로 명령 생성 (Few-Shot 컨텍스트 활용)
5. **검증**: 생성된 명령이 DB 템플릿과 일치하는지 확인

### MariaDB Vector DB 스키마

```sql
-- Intent 예제 테이블
CREATE TABLE intent_examples (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_input TEXT NOT NULL,
    intent_type VARCHAR(50) NOT NULL,  -- search, compare, cart, checkout
    embedding BLOB NOT NULL,            -- 768차원 벡터
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- MCP 명령 템플릿 테이블
CREATE TABLE mcp_command_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    intent_type VARCHAR(50) NOT NULL,
    site VARCHAR(30) NOT NULL,          -- coupang, naver, 11st
    input_pattern TEXT NOT NULL,        -- 입력 패턴 예제
    tool_calls JSON NOT NULL,           -- MCP 명령 시퀀스
    embedding BLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 플로우 패턴 테이블
CREATE TABLE flow_patterns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flow_type VARCHAR(30) NOT NULL,     -- signup, checkout
    site VARCHAR(30) NOT NULL,
    trigger_keywords JSON NOT NULL,     -- 플로우 트리거 키워드
    embedding BLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 구현 파일
- `services/llm.py` - LLM 추론 및 명령 생성
- `services/rag.py` - RAG 파이프라인 (Vector 검색, 프롬프트 구성)
- `services/embedding.py` - 임베딩 생성
- `db/vector_store.py` - MariaDB Vector DB 연동

### 예시: RAG 기반 명령 생성

**입력**:
```
"쿠팡에서 물티슈 검색해줘"
```

**1. Vector 검색 결과 (Top-3):**
```json
[
    {"input": "쿠팡에서 우유 찾아줘", "intent": "search", "similarity": 0.95},
    {"input": "쿠팡에서 라면 검색", "intent": "search", "similarity": 0.92},
    {"input": "네이버에서 세제 검색해줘", "intent": "search", "similarity": 0.88}
]
```

**2. Few-Shot 프롬프트 구성 → LLM 추론**

**3. 출력** (순차 실행):
```json
[
    {"tool_name": "navigate_to_url", "arguments": {"url": "https://www.coupang.com"}},
    {"tool_name": "fill_input", "arguments": {"selector": "#headerSearchKeyword", "value": "물티슈"}},
    {"tool_name": "click_element", "arguments": {"selector": ".search-btn"}}
]
```

### RAG 장점
1. **신뢰도 향상**: 검증된 예제 기반으로 환각(hallucination) 감소
2. **일관성**: 동일 상황에서 일관된 명령 생성
3. **확장 용이**: 새 쇼핑몰 추가 시 DB에 예제만 삽입
4. **디버깅 용이**: 어떤 예제가 사용되었는지 추적 가능

### 환경 변수
```env
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-5-mini
LLM_MAX_TOKENS=1024
LLM_TEMPERATURE=0.3          # RAG 사용 시 낮은 temperature
EMBEDDING_MODEL=text-embedding-3-small
MARIADB_HOST=localhost
MARIADB_PORT=3306
MARIADB_DATABASE=ai_rag
RAG_TOP_K=5
```

### 인터페이스
```python
class ILLMService:
    async def generate_commands(self, user_input: str, context: dict) -> List[ToolCall]: ...
    async def analyze_intent(self, user_input: str) -> Intent: ...
    def should_use_flow(self, intent: Intent) -> bool: ...

class IRAGService:
    async def search_similar_examples(self, query: str, top_k: int = 5) -> List[Example]: ...
    async def build_few_shot_prompt(self, examples: List[Example], user_input: str) -> str: ...
    async def index_new_example(self, example: Example) -> None: ...
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

- **OpenAI API** - GPT-5-mini 호출, Embedding 생성
- **MariaDB Vector** - Vector DB (예제 저장/검색)
- **Sentence-BERT** - 대안 임베딩 모델 (로컬)
- **Pydantic** - 데이터 모델 정의/검증
- **JSON Schema** - 플로우 정의 파일
- **상태 머신 패턴** - 플로우 엔진 구현
- **Hugging Face Transformers** - TrOCR 모델
- **PaddleOCR** - 대안 OCR 엔진

---

## 학습 리소스

- OpenAI API: https://platform.openai.com/docs/api-reference
- OpenAI Embeddings: https://platform.openai.com/docs/guides/embeddings
- MariaDB Vector: https://mariadb.com/kb/en/vector-overview/
- RAG Pattern: https://www.pinecone.io/learn/retrieval-augmented-generation/
- Flow State Machine: https://en.wikipedia.org/wiki/Finite-state_machine
- TrOCR: https://huggingface.co/microsoft/trocr-base-printed
- PaddleOCR: https://github.com/PaddlePaddle/PaddleOCR
- JSON Schema: https://json-schema.org/

---

**문서 버전**: 1.0
**작성일**: 2026-01-16
**담당자**: 김재환
