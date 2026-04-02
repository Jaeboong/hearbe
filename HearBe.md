# HEARBE AI Backend 정리

## 문서 목적

- 이 문서는 `project/S14P11D108`의 AI 백엔드 구현을 자소서, 경험기술서, 면접 답변에 바로 재사용할 수 있도록 정리한 문서다.
- 설명은 문서상의 이상적인 구조보다 **실제 코드와 설정 파일에서 확인한 내용** 위주로 작성했다.
- 현재 대화 기준으로, 이 문서는 사용자가 지정한 `AI`, `LLM`, `flow`, `rules`, `planner`, `sites`, `tests`, `summarizer` 범위를 중심으로 정리한다.

## 프로젝트 개요

- 프로젝트명: HEARBE
- 성격: 시각장애인 음성 쇼핑 지원 서비스
- 구성:
  - `Backend`: Spring Boot API, MariaDB/Redis 연동
  - `Frontend/hearbe`: React + Vite
  - `AI`: FastAPI + ASR/NLU/LLM/TTS/OCR
- 운영 특징:
  - 메인 웹서버와 별도로 **AI 서버를 독립 운영**
  - Frontend는 OCR 및 WebSocket 기반 AI 기능을 AI 서버 도메인으로 직접 호출

## 문서 범위

이 문서는 HEARBE 전체 백엔드가 아니라, 그중에서도 **AI 서버 쪽 백엔드 아키텍처와 로직 설계**를 정리한다.

특히 아래 질문에 답할 수 있도록 구성했다.

- 음성 쇼핑 대화 흐름을 어떤 서버 구조로 처리했는가
- LLM을 어디에 쓰고, 어디는 규칙 기반으로 처리했는가
- 멀티스텝 플로우와 사이트별 자동화는 어떻게 설계했는가
- OCR 요약, 검색 요약, 주문/상품 읽기 흐름은 어떤 방식으로 구현했는가
- 테스트는 어떤 성격의 영역을 검증하고 있는가

## 검증된 AI 백엔드 기술 스택

실제 `AI/requirements.txt`, `AI/main.py`, `exec/PORTING_MANUAL.md` 기준으로 확인되는 스택은 아래와 같다.

- 언어: Python 3.10.12
- 프레임워크: FastAPI, Uvicorn
- 데이터 모델: Pydantic
- 실시간 통신: WebSocket
- 음성 처리:
  - ASR: faster-whisper 계열 구조
  - TTS: Google Cloud Text-to-Speech
- LLM 연동: OpenAI SDK 호환 클라이언트
- OCR:
  - PaddleOCR
  - 이미지 기반 상세설명 추출 및 후처리
- HTML 파싱: BeautifulSoup
- 비동기 통신: aiohttp, httpx
- 테스트: pytest, pytest-asyncio

주의할 점:

- 이 서버는 `LLM만으로 모든 것을 처리하는 구조`가 아니다.
- 실제 구현은 **규칙 기반 + 페이지 컨텍스트 + 세션 상태 + 필요한 경우에만 LLM fallback**을 섞은 하이브리드 구조다.

## AI 백엔드 구조 요약

실제 런타임 기준 전체 흐름은 대략 아래와 같다.

1. WebSocket 연결이 열리면 세션을 만들고 사용자별 상태를 관리한다.
2. 음성 입력이면 ASR을 거쳐 텍스트로 변환하고, 텍스트 입력이면 바로 NLU로 넘긴다.
3. NLU에서 intent, entity, 지시 대상, 순번 표현을 해석한다.
4. `LLMPlanner`가 현재 페이지, 세션 문맥, 규칙 매칭 결과를 바탕으로 명령 생성 경로를 선택한다.
5. 우선 규칙 기반으로 처리하고, 부족한 경우에만 LLM으로 보완한다.
6. 생성된 브라우저 명령은 `goto`, `click`, `fill`, `extract`, `wait` 같은 형태로 내려간다.
7. 검색 결과, 상품 상세, 장바구니, 주문내역 등 추출 데이터는 세션 컨텍스트에 누적된다.
8. 필요한 경우 OCR 및 요약 파이프라인을 거쳐 사용자에게 읽기 쉬운 응답을 만들고, TTS로 음성 응답을 생성한다.

즉, 이 프로젝트의 핵심은 단순 챗봇이 아니라 **쇼핑 자동화와 접근성을 위한 상태 기반 AI 오케스트레이션 서버**라는 점이다.

## 핵심 기술 요소

### 1. FastAPI + WebSocket 기반 AI 오케스트레이션

`AI/main.py`는 이 서버가 단순 API 서버가 아니라, 여러 AI 컴포넌트를 엮는 진입점이라는 점을 잘 보여준다.

- 초기화 컴포넌트:
  - `SessionManager`
  - `ASRService`
  - `NLUService`
  - `LLMPlanner`
  - `TTSService`
  - `OCRService`
  - `FlowEngine`
- `WebSocketHandler`에 위 컴포넌트를 모두 주입해 세션 단위로 처리
- `/ws`, `/ws/{session_id}` 엔드포인트 제공
- OCR integrator warmup을 백그라운드에서 수행

`api/websocket.py`에서는 아래가 확인된다.

- 사용자별 WebSocket 연결 관리
- 세션별 메시지 송수신 래핑
- 세션이 없으면 자동 생성
- 연결 종료 시 세션/연결 정리
- `HandlerManager`, `WebSocketRouter`, `WSSender`를 통한 계층 분리

왜 좋은가:

- 음성, 텍스트, OCR, TTS, 브라우저 제어를 하나의 세션 상태 안에서 묶는 **실시간 AI 서버 구조**를 설명할 수 있다.
- 단순 LLM 호출이 아니라, 실제 사용자 상호작용을 감당하는 **상태 관리형 WebSocket 백엔드** 경험으로 말할 수 있다.

관련 파일:

- `AI/main.py`
- `AI/api/websocket.py`

### 2. NLU: 패턴 기반 의도 분류와 참조 해석

이 프로젝트의 NLU는 전형적인 대형 모델 기반 NLU가 아니라, **패턴/규칙 기반 경량 NLU**에 가깝다.

확인되는 역할:

- 기본 intent 분석
- 수량, 가격 같은 entity 추출
- `첫 번째`, `두 번째`, `그거`, `이 상품` 같은 참조 표현 해석
- `search_results`, `last_mentioned_product` 같은 세션 문맥을 이용한 대상 복원

`llm_pipeline_handler.py`에서는 NLU 결과를 바탕으로 아래 같은 흐름을 분기한다.

- 페이지 정보 읽기
- 상품 정보 읽기
- 장바구니 요약 읽기
- 주문 목록 요약 읽기
- 검색 결과 요약 읽기
- 읽은 뒤 이어서 행동하는 `read_then_act`

왜 좋은가:

- LLM에만 의존하지 않고, 자주 나오는 쇼핑 명령은 **가볍고 빠른 규칙 기반 NLU로 선처리**했다는 점을 설명할 수 있다.
- 특히 순번 지시어와 직전 문맥을 결합한 참조 해석은 **음성 UI에서 중요한 사용성 문제를 서버 로직으로 해결한 사례**다.

주의할 점:

- `자체 학습 NLU 모델을 구축했다`고 쓰면 과장이다.
- 실제 코드는 **패턴 기반 해석 + 세션 문맥 보강** 구조로 보는 것이 정확하다.

관련 파일:

- `AI/services/nlu/service.py`
- `AI/api/ws/handlers/text_processing/llm_pipeline_handler.py`

### 3. Planner: Rule-First + LLM Fallback 하이브리드 설계

이 프로젝트에서 가장 강하게 어필할 수 있는 부분은 `LLMPlanner`다.

핵심 아이디어는 단순하다.

- 먼저 규칙으로 풀 수 있는 것은 규칙으로 처리한다.
- 현재 페이지와 세션 상태로 처리 가능한 것은 전용 핸들러로 처리한다.
- 그래도 애매하면 LLM으로 보완한다.

`planner/service.py` 기준 실제 순서는 아래에 가깝다.

1. `CommandGenerator`를 통한 규칙 기반 해석
2. 페이지/상황 특화 핸들러 처리
   - selection
   - product option
   - cheapest search
   - cart action
   - order list action
   - hearbe order history action
   - product info action
3. `LLMRoutingPolicy`로 rule 결과와 confidence를 평가
4. 필요한 경우에만 `LLMGenerator`로 fallback

이 구조가 좋은 이유:

- 단순 명령은 빠르게 처리하고
- 페이지 맥락이 중요한 경우는 세션 기반 핸들러가 맡고
- 자연어 해석이 어려운 경우만 LLM에 위임해
- **비용, 응답속도, 예측 가능성**을 함께 잡는다

`LLMRoutingPolicy`에서 확인되는 판단 기준:

- intent confidence
- matched rule 존재 여부
- navigation only 명령인지 여부
- LLM 강제 대상 intent인지 여부
- 신뢰도가 낮은 rule category인지 여부

왜 좋은가:

- `LLM을 붙였다` 수준이 아니라 **언제 rule로 처리하고, 언제 LLM으로 넘길지 정책화한 AI 백엔드 설계**로 설명할 수 있다.
- 특히 접근성 서비스에서는 잘못된 자동화가 치명적일 수 있기 때문에, 이 구조는 안정성 측면에서도 설득력이 있다.

관련 파일:

- `AI/services/llm/planner/service.py`
- `AI/services/llm/planner/routing.py`
- `AI/services/llm/generators/llm_generator.py`
- `AI/services/llm/generators/response_generator.py`

### 4. Rules: 쇼핑 명령을 빠르고 안정적으로 처리하는 규칙 엔진

`CommandGenerator`는 여러 규칙 클래스를 순서대로 적용하는 방식으로 동작한다.

확인되는 규칙 예시:

- `SiteAccessRule`
- `HearbeNavRule`
- `HearbeMallSelectRule`
- `HearbeMainModeRule`
- `HearbeSignupRule`
- `SearchSelectRule`
- `SearchRule`
- `SearchSortRule`
- `OrderDetailRule`
- `CartRule`
- `OrderListRule`
- `LogoutRule`
- `LoginRule`
- `CheckoutRule`
- `GenericClickRule`

규칙 구조의 특징:

- `BaseRule`, `RuleResult` 기반 공통 인터페이스
- 규칙 결과를 `CommandResult`로 묶어 planner에 전달
- rule path가 애매하거나 실패하면 LLM fallback 가능

구체적으로 눈에 띄는 구현:

- `SiteAccessRule`은 `쿠팡 열어`, `네이버 접속` 같은 진입 명령 처리
- `SearchRule`은 명시적 플랫폼, 현재 사이트, 기본 fallback를 조합해 검색 명령 구성
- `GenericClickRule`은 짧고 단순한 클릭 명령만 처리하고, 복잡한 케이스는 무리하게 규칙으로 밀어붙이지 않음

왜 좋은가:

- 음성 쇼핑에서 자주 나오는 핵심 명령을 **예측 가능한 규칙 엔진으로 먼저 처리**해 안정성을 높였다.
- 규칙이 전부를 해결하려고 하지 않고, 애매한 경우를 LLM으로 넘기도록 설계해 **보수적 자동화 정책**을 구현했다는 점이 좋다.

관련 파일:

- `AI/services/llm/generators/command_generator.py`
- `AI/services/llm/rules/__init__.py`
- `AI/services/llm/rules/site_access.py`
- `AI/services/llm/rules/search.py`
- `AI/services/llm/rules/generic.py`

### 5. Planner 보조 로직: 세션/페이지 인지형 액션 처리

이 프로젝트는 단순히 규칙 몇 개를 맞추는 수준에서 끝나지 않는다.
현재 페이지와 세션에 쌓인 데이터를 활용해, **상황 인지형 액션 핸들러**를 추가로 둔다.

대표적인 예:

- 검색 결과 목록에서 `첫 번째 상품`, `두 번째 상품`, 상품명 일부를 해석해 대상 선택
- `search_results` 세션 데이터를 기반으로 상품 URL 우선 선택
- 추출된 상품 URL이 있으면 brittle한 nth-selector보다 URL 중심으로 액션 수행
- Hearbe 주문내역 페이지에서 추천/이력 데이터를 읽고 문맥 기반 응답 처리

왜 좋은가:

- 음성 명령에서 자주 발생하는 `모호한 지시어 해석`을 단순 문자열 파싱이 아니라 **세션 상태 기반 액션 계층**으로 해결했다.
- 이 부분 덕분에 사용자는 긴 상품명을 반복하지 않아도 되고, 시스템은 더 안정적으로 대상 상품을 찾을 수 있다.

관련 파일:

- `AI/services/llm/planner/selection/selection.py`
- `AI/services/llm/planner/hearbe_order_history_action.py`

### 6. Flow: 회원가입/결제 같은 멀티스텝 작업의 상태 기반 처리

`flow` 영역은 이 프로젝트에서 중요한데, 현재 구현은 **전환 중인 구조**로 보인다.

확인되는 구현은 두 축이다.

1. `services/flow/service.py`
   - `FLOW_DEFINITIONS`를 코드 안에 두는 정적 방식
   - 쿠팡, 네이버, 11번가의 회원가입/결제 흐름 정의
2. `services/flow/flow_engine.py`
   - `FlowState`, `FlowType`, `FlowStep`, `FlowDefinition`, `FlowContext`, `StepResult`로 구성된 엔진형 구조
   - JSON 기반 플로우 정의를 읽어 상태 머신처럼 실행하는 방향

즉, 의도 자체는 분명하다.

- 회원가입
- 결제
- 본인인증
- 순차 입력

같은 **멀티턴/멀티스텝 작업을 단계별 상태로 관리**하려는 설계다.

왜 좋은가:

- 접근성 서비스에서 가장 어려운 영역 중 하나가 `여러 단계를 끊기지 않고 안내하는 것`인데, 이를 위해 상태 기반 플로우 엔진을 도입한 점은 강점이다.
- 특히 단발성 명령 처리와 달리, 회원가입/결제는 중간 실패와 재시도가 많기 때문에 **대화형 상태 전이 설계 경험**으로 연결하기 좋다.

주의할 점:

- 현재는 정적 flow 정의와 엔진형 flow가 함께 존재해, `완전히 하나로 정리된 구조`라고 쓰면 과장이다.
- 자소서에서는 `멀티스텝 자동화를 위한 상태 기반 flow 구조를 설계/구현했다` 정도가 안전하다.

관련 파일:

- `AI/services/flow/service.py`
- `AI/services/flow/flow_engine.py`
- `AI/api/ws/handlers/text_processing/flow_handler.py`

### 7. Sites: 사이트/페이지/셀렉터를 JSON으로 분리한 자동화 구조

이 프로젝트는 쇼핑 사이트별 제어 로직을 코드에 하드코딩하지 않고, 상당 부분을 **사이트 설정 파일**로 분리했다.

`SiteManager` 기준 확인되는 역할:

- 사이트 정의 로딩
- 도메인 기반 현재 사이트 판별
- URL 기반 페이지 타입 판별
- 페이지별 selector 조회
- site/page 설정을 planner와 extract command에서 재사용

실제 설정 파일 기준 지원 축:

- `hearbe`
- `coupang`
- `naver`
- `11st`

특징:

- `hearbe/index.json`에는 typed route 기반 URL 체계가 정의됨
- `coupang/search.json`에는 검색창, 결과 리스트, 상품명, 가격, 리뷰, 할인, 배송 등 비교적 풍부한 selector가 있음
- `hearbe/order_history.json`처럼 내부 페이지 타입도 별도 파일로 관리
- `11st.json`처럼 단일 파일 기반 사이트 정의도 존재

이 구조가 좋은 이유:

- 사이트별 차이를 코드가 아니라 설정으로 흡수해 **유지보수성과 확장성**을 높인다.
- 같은 planner/rule 로직을 두고도, 사이트 설정만 바꿔서 행동을 달리할 수 있다.
- 추출 명령에서 상품 URL, 텍스트, 속성 값을 selector 기반으로 가져오도록 설계해 자동화 내구성을 높인다.

주의할 점:

- 멀티사이트 지원 자체는 맞지만, **모든 사이트의 완성도가 동일하다고 보기는 어렵다**.
- 현재 파일 구성상 Hearbe와 Coupang이 가장 풍부하고, Naver/11번가는 상대적으로 범위가 얕아 보인다.

관련 파일:

- `AI/services/llm/sites/site_manager.py`
- `AI/config/sites/hearbe/index.json`
- `AI/config/sites/hearbe/order_history.json`
- `AI/config/sites/coupang/index.json`
- `AI/config/sites/coupang/search.json`
- `AI/config/sites/naver/search.json`
- `AI/config/sites/11st.json`

### 8. Context와 Extract 명령: 페이지 상태를 LLM 친화적인 문맥으로 변환

이 프로젝트에서 planner와 summarizer 사이를 이어주는 핵심은 context 계층이다.

`ContextBuilder`와 `context_rules.py`에서 확인되는 역할:

- 현재 URL과 사이트 정보 결합
- 대화 이력, 세션 상태, 페이지 상태를 LLM 메시지로 재구성
- 검색 결과, 상품 상세, 장바구니, 주문 상세, 주문 목록을 상황별로 선택
- `goto`, `wait`, `click`, `fill`, `click_text`, `extract` 명령을 표준화
- 상품 URL 추출까지 포함한 extract command 생성

왜 좋은가:

- 브라우저 자동화와 LLM 응답 사이에 **명시적인 중간 표현층**이 존재해 구조가 깔끔하다.
- 나중에 사이트가 늘어나도, planner 전체를 다시 짜기보다 context/selectors를 보강하는 식으로 확장하기 좋다.

관련 파일:

- `AI/services/llm/context/context_builder.py`
- `AI/services/llm/context/context_rules.py`

### 9. Summarizer: HTML 파싱 + OCR + LLM 후처리를 결합한 상품 정보 요약

이 프로젝트에서 가장 차별화되는 영역 중 하나가 `summarizer`다.

상품 상세설명은 보통 이미지와 긴 HTML로 섞여 있어, 시각장애인 사용자에게 바로 읽어주기 어렵다.
이 프로젝트는 이를 여러 단계로 나눠 처리한다.

1. `html_parser.py`
   - HTML에서 상품명, 가격, 판매자, 옵션, 상세 이미지 URL 등 빠르게 구조화 가능한 정보를 먼저 추출
2. `ocr_integrator.py`
   - 상세 이미지 URL을 chunk 단위로 나눠 OCR 처리
   - 비동기 파이프라인으로 OCR 결과를 순차 수집
   - warmup 및 TTS용 포맷팅 지원
3. `ocr_llm_summarizer.py`
   - OCR 텍스트 전처리
   - LLM 프롬프트를 통해 핵심 정보 요약
   - 날짜, 전압, 사이즈 등은 추측하지 않도록 강하게 제약
   - JSON summary + keyword 형태로 후처리

특히 `ocr_llm_summarizer.py`는 아래 점에서 강점이 있다.

- 쇼핑 상품 특화 요약 프롬프트를 설계
- 의류/신발 사이즈 같은 도메인별 해석 규칙 반영
- 읽기 쉬운 요약과 검색 키워드를 동시에 생성
- 잘못 추론하면 안 되는 값에 대해 no-guessing 원칙을 둠

왜 좋은가:

- 이 부분은 단순 OCR 연동이 아니라, **접근성을 위한 정보 재구성 파이프라인**으로 설명할 수 있다.
- 이미지 기반 상품 상세를 그대로 읽는 대신, 사용자에게 필요한 정보만 선별해 전달하는 구조라서 서비스 가치와도 직접 연결된다.

관련 파일:

- `AI/services/summarizer/html_parser.py`
- `AI/services/summarizer/ocr_integrator.py`
- `AI/services/ocr/text_processors/ocr_llm_summarizer.py`

### 10. Read/Summary Pipeline: 검색결과, 상품, 주문내역을 읽기 좋은 형태로 재구성

이 프로젝트는 명령 실행뿐 아니라, **읽기 전용 파이프라인**도 꽤 잘 분리되어 있다.

확인되는 파이프라인 예:

- `search_summary.py`
  - 검색 결과를 배치 단위로 읽어주는 요약
- `order_list_summary.py`
  - 주문 목록을 세션 문맥과 함께 정리
- `product_info.py`
  - 상품 상세와 OCR 결과를 합쳐 설명

왜 좋은가:

- 접근성 서비스에서는 `무언가를 클릭하는 것`만큼 `현재 페이지를 이해시키는 것`이 중요하다.
- 이 프로젝트는 행동 자동화와 정보 요약을 분리해, **읽기와 행동을 모두 지원하는 음성 쇼핑 서버**로 설계되었다.

관련 파일:

- `AI/services/llm/pipelines/read/search_summary.py`
- `AI/services/llm/pipelines/read/order_list_summary.py`
- `AI/services/llm/pipelines/read/product_info.py`

### 11. Tests: 규칙, 핸들러, 결제 보조 로직, WebSocket 흐름 검증

`AI/tests`와 일부 테스트성 스크립트 기준으로, 현재 테스트는 다음 영역에 집중되어 있다.

- 주문 상세 규칙 검증
- 주문 상세 핸들러 검증
- 상품 상세 유틸 검증
- 결제 키패드 처리 검증
- 결제 후처리 핸들러 검증
- 복지카드 관련 HTTP 흐름 검증
- 한국어 날짜/상품명 포맷팅 검증
- WebSocket 마이크/PTT/시나리오 테스트

`pytest.ini`에서는 아래가 확인된다.

- `pytest-asyncio` 기반 비동기 테스트 설정
- `integration`, `slow` 마커 정의
- 테스트 루트는 `tests`

왜 좋은가:

- 테스트가 단순 계산 함수만이 아니라, 실제로 오류가 나기 쉬운 **주문/결제/핸들러/WebSocket 경로**를 겨냥하고 있다.
- 음성 쇼핑 서비스 특성상 복잡한 end-to-end 흐름이 많은데, 그중 취약 지점을 우선 검증하는 접근으로 볼 수 있다.

주의할 점:

- `전 영역이 자동화 테스트로 완전히 커버되어 있다`고 쓰면 과장이다.
- 일부는 수동 실행을 염두에 둔 보조 테스트 스크립트 성격도 섞여 있다.

관련 파일:

- `AI/pytest.ini`
- `AI/tests/test_orderdetail_rule.py`
- `AI/tests/test_order_detail_handler.py`
- `AI/tests/test_product_detail_utils.py`
- `AI/tests/test_payment_keypad.py`
- `AI/tests/test_payment_post_handler.py`
- `AI/tests/test_http_welfare_card.py`
- `AI/tests/test_ws_mic.py`
- `AI/tests/test_ws_ptt.py`
- `AI/tests/test_ws_scripted.py`
- `AI/services/llm/tests/test_command_cli.py`

## 자소서에서 특히 강하게 쓸 수 있는 역량

### 핵심 역량 1

**규칙 기반 자동화와 LLM을 혼합해 안정성과 유연성을 함께 확보하는 AI 백엔드 설계 역량**

이렇게 풀기 좋다:

- 단순 명령은 rule-first로 빠르게 처리
- 페이지와 세션 상태가 중요한 경우는 전용 planner handler로 처리
- 애매한 자연어만 LLM fallback으로 넘겨 비용과 안정성을 함께 고려

### 핵심 역량 2

**세션 상태와 페이지 문맥을 이해하는 대화형 쇼핑 AI 서버 구현 역량**

이렇게 풀기 좋다:

- WebSocket 세션 안에서 음성/텍스트 입력을 처리
- 검색 결과, 주문내역, 상품 상세를 세션 컨텍스트에 유지
- `첫 번째 상품`, `이거`, `그 주문` 같은 참조 표현을 문맥 기반으로 해석

### 핵심 역량 3

**접근성을 위한 OCR + 요약 파이프라인 설계 역량**

이렇게 풀기 좋다:

- HTML 구조화, 이미지 OCR, LLM 요약을 결합
- 시각장애인 사용자가 이해하기 어려운 상품 상세를 읽기 쉬운 정보로 재구성
- 추측하면 안 되는 값을 제한하는 프롬프트 정책까지 포함

### 핵심 역량 4

**멀티사이트 자동화 구조를 설정 기반으로 설계한 역량**

이렇게 풀기 좋다:

- 사이트/페이지/셀렉터를 JSON으로 분리
- Hearbe, Coupang, Naver, 11번가 등 사이트별 차이를 설정으로 흡수
- planner/rule/context 로직을 공통화하면서도 사이트별 세부 동작을 분리

## HEARBE 프로젝트 기준 추천 포지셔닝

이 프로젝트는 다음 방향으로 포지셔닝하는 것이 가장 좋다.

- `LLM을 붙여본 경험`보다 `안정성을 고려해 rule-first + LLM fallback 구조를 설계한 경험`
- `단순 챗봇`보다 `세션 상태와 페이지 문맥을 이해하는 음성 쇼핑 AI 서버`
- `OCR 사용 경험`보다 `접근성을 위해 상품 상세를 구조화·요약한 정보 재구성 파이프라인`
- `멀티사이트 지원`보다 `사이트 설정과 selector를 분리한 자동화 아키텍처`

특히 강조할 키워드:

- FastAPI
- WebSocket
- Session State
- NLU
- Rule Engine
- LLM Planner
- Flow Engine
- Site Configuration
- OCR
- Accessibility

## 자소서에서 약하게 쓰거나 빼야 하는 항목

### 1. 전부 LLM이 판단하는 완전 자율형 에이전트

실제 구현은 그보다 훨씬 보수적이고 안정성 중심이다.

- 규칙 기반 처리 비중이 크고
- 페이지 특화 핸들러가 많이 들어가며
- LLM은 fallback 또는 보조 역할로 들어간다

따라서 아래 표현은 과장이다.

- `모든 쇼핑 플로우를 자율적으로 수행하는 에이전트를 구현했다`

### 2. 학습형 NLU 모델 구축

현재 NLU는 pattern/rule 기반 해석이 중심이다.

- entity 추출과 순번 해석은 구현되어 있지만
- 학습 데이터 기반 intent classifier를 직접 훈련한 구조는 아니다

따라서 아래 표현은 피하는 것이 좋다.

- `맞춤형 자연어 이해 모델을 학습시켜 적용했다`

### 3. 모든 쇼핑몰에 동일 수준으로 적용된 자동화

멀티사이트 구조는 맞지만, 완성도는 동일하지 않다.

- Hearbe와 Coupang 관련 설정/로직이 비교적 풍부
- Naver, 11번가는 범위가 더 얕아 보임

따라서 아래 표현은 조심해야 한다.

- `국내 주요 쇼핑몰 전반에 동일한 수준의 자동화를 구현했다`

### 4. 완전히 통합된 Flow Engine

flow 영역은 방향성은 좋지만, 구현이 아직 이행기 성격을 보인다.

- 정적 정의 방식과 엔진형 방식이 공존

따라서 아래처럼 정리하는 편이 안전하다.

- `회원가입과 결제 같은 멀티스텝 작업을 상태 기반 flow 구조로 관리하도록 설계했다`

### 5. 전면적인 자동화 테스트 체계

중요 경로 테스트는 존재하지만, 전 범위 완전 커버리지라고 보긴 어렵다.

- 규칙, 핸들러, WebSocket, 결제 보조 로직 중심
- 일부는 수동 실행 보조 스크립트 성격 포함

## 문항용 핵심 문장 예시

### 짧은 버전

`저는 규칙 기반 자동화와 LLM fallback을 결합해, 안정성과 유연성을 함께 확보하는 AI 백엔드 시스템을 설계하고 구현해왔습니다.`

### HEARBE 연결 버전

`HEARBE 프로젝트에서 FastAPI 기반 AI 서버를 중심으로 WebSocket 세션 관리, 경량 NLU, rule-first LLM planner, 상태 기반 flow, 사이트 설정 기반 자동화, OCR+요약 파이프라인을 연결해 시각장애인을 위한 음성 쇼핑 지원 기능을 구현했습니다.`

### 접근성 강조 버전

`저의 핵심 역량은 복잡한 웹 정보를 접근 가능한 형태로 재구성하는 AI 백엔드 설계 능력입니다. HEARBE에서 상품 HTML 파싱, 이미지 OCR, LLM 요약, 음성 응답 생성을 하나의 파이프라인으로 연결하며 사용자가 쇼핑 페이지를 더 쉽게 이해하고 조작할 수 있도록 지원했습니다.`

## 참고용 근거 파일

- `exec/PORTING_MANUAL.md`
- `AI/requirements.txt`
- `AI/main.py`
- `AI/api/websocket.py`
- `AI/api/ws/handlers/text_processing/llm_pipeline_handler.py`
- `AI/api/ws/handlers/text_processing/flow_handler.py`
- `AI/services/nlu/service.py`
- `AI/services/llm/planner/service.py`
- `AI/services/llm/planner/routing.py`
- `AI/services/llm/planner/selection/selection.py`
- `AI/services/llm/planner/hearbe_order_history_action.py`
- `AI/services/llm/generators/command_generator.py`
- `AI/services/llm/generators/llm_generator.py`
- `AI/services/llm/rules/__init__.py`
- `AI/services/llm/rules/site_access.py`
- `AI/services/llm/rules/search.py`
- `AI/services/llm/rules/generic.py`
- `AI/services/llm/sites/site_manager.py`
- `AI/services/llm/context/context_builder.py`
- `AI/services/llm/context/context_rules.py`
- `AI/services/flow/service.py`
- `AI/services/flow/flow_engine.py`
- `AI/services/summarizer/html_parser.py`
- `AI/services/summarizer/ocr_integrator.py`
- `AI/services/ocr/text_processors/ocr_llm_summarizer.py`
- `AI/services/llm/pipelines/read/search_summary.py`
- `AI/services/llm/pipelines/read/order_list_summary.py`
- `AI/services/llm/pipelines/read/product_info.py`
- `AI/pytest.ini`
- `AI/tests/test_orderdetail_rule.py`
- `AI/tests/test_order_detail_handler.py`
- `AI/tests/test_product_detail_utils.py`
- `AI/tests/test_payment_keypad.py`
