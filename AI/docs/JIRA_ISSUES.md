# JIRA 이슈 목록 - AI Server

> AI-01 ~ AI-10 작업에 대한 JIRA 이슈 내용

---

## AI 파트 (AI Server)

### AI-01: 음성 인식 (STT)

**Title (서브태스크):** `Feat: 음성 인식 (STT)`

**설명 (Description):**

사용자는 음성을 텍스트로 변환하기 위해 실시간 스트리밍 음성 인식 기능을 사용하고 싶다.

## ✅ 완료 조건
- MCP 앱에서 오디오 청크 수신 (WebSocket)
- Faster-Whisper(turbo) 모델로 한국어 음성 인식
- STT 결과 텍스트를 MCP 앱으로 전송
- STT 서비스 모듈(`services/stt.py`) 구현

## 💬 기타
- GPU 가속 지원 (CUDA)
- 쇼핑 관련 용어 최적화
- 실시간 스트리밍 처리

**Story Point:** 8

**중요도 (Priority):** High

**담당자:** 김민찬

---

### AI-02: 음성 합성 (TTS)

**Title (서브태스크):** `Feat: 음성 합성 (TTS)`

**설명 (Description):**

사용자는 AI 응답을 음성으로 듣기 위해 텍스트-음성 변환 기능을 사용하고 싶다.

## ✅ 완료 조건
- LLM 응답 텍스트 수신
- Hugging Face TTS 모델로 한국어 음성 합성
- 음성 청크를 실시간 스트리밍으로 MCP 앱에 전송
- TTS 서비스 모듈(`services/tts.py`) 구현
- TTS 모델 선택 (ElevenLabs/MiniMax/CosyVoice)

## 💬 기타
- 개발: MiniMax (저렴, 한국어 품질 우수)
- 프로덕션: ElevenLabs (저지연 ~75ms)
- 스트리밍으로 응답 지연 최소화

**Story Point:** 5

**중요도 (Priority):** High

**담당자:** 김민찬

---

### AI-03: WebSocket 통신

**Title (서브태스크):** `Feat: WebSocket 통신`

**설명 (Description):**

사용자는 실시간 양방향 스트리밍 통신을 위해 WebSocket 서버 기능을 사용하고 싶다.

## ✅ 완료 조건
- MCP 앱과 WebSocket 연결 수립
- 오디오 청크 수신 → STT 처리
- LLM 명령/TTS 음성 → MCP 앱 전송
- 연결 끊김 시 재연결 처리
- WebSocket 게이트웨이 모듈(`websocket/gateway.py`, `websocket/handlers.py`) 구현

## 💬 기타
- 메시지 타입: audio_chunk, stt_result, tool_calls, tts_chunk, flow_step
- 최대 연결 수: 100
- Heartbeat 간격: 30초

**Story Point:** 8

**중요도 (Priority):** High

**담당자:** 김민찬

---

### AI-04: 의도 분석

**Title (서브태스크):** `Feat: 의도 분석`

**설명 (Description):**

사용자는 자연어 명령의 의도를 파악하기 위해 의도 분석 기능을 사용하고 싶다.

## ✅ 완료 조건
- STT 결과 텍스트에서 사용자 의도 추출
- Intent 타입 분류 (검색/비교/장바구니/결제 등)
- NLU(Natural Language Understanding) 모듈 구현
- 의도 분석 결과를 후속 모듈로 전달

## 💬 기타
- GPT-4o-mini 활용
- 다중 의도 처리 가능
- 컨텍스트 기반 의도 파악

**Story Point:** 8

**중요도 (Priority):** High

**담당자:** 김재환

---

### AI-05: MCP 명령 생성 (RAG 기반)

**Title (서브태스크):** `Feat: MCP 명령 생성 (RAG)`

**설명 (Description):**

사용자는 신뢰할 수 있는 명령 생성을 위해 RAG 기반 MCP 명령 생성 기능을 사용하고 싶다.

## ✅ 완료 조건
- MariaDB Vector DB에 MCP 명령 템플릿 저장
- 사용자 발화에 대한 유사 예제 Top-K 검색
- Few-Shot 프롬프트 구성 및 LLM 추론
- 생성된 명령 유효성 검증
- RAG 파이프라인 모듈(`services/rag.py`) 구현

## 💬 기타
- OpenAI Embedding 또는 Sentence-BERT 활용
- 환각 감소를 위한 검증된 예제 기반 생성
- 쇼핑몰별 선택자 매핑 DB화

**Story Point:** 13

**중요도 (Priority):** High

**담당자:** 김재환

---

### AI-06: 플로우 엔진

**Title (서브태스크):** `Feat: 플로우 엔진`

**설명 (Description):**

사용자는 복잡한 작업을 순차적으로 처리하기 위해 플로우 엔진 기능을 사용하고 싶다.

## ✅ 완료 조건
- 쇼핑몰별 회원가입/결제 플로우 정의 (쿠팡, 네이버, 11번가)
- 플로우 단계(step) 생성 및 순환 로직 구현
- 각 단계별 검증 및 다음 단계 전환
- 플로우 엔진 모듈(`services/flow_engine.py`) 구현

## 💬 기타
- JSON 기반 플로우 정의
- 조건부 분기 지원
- 에러 핸들링 및 재시도

**Story Point:** 13

**중요도 (Priority):** High

**담당자:** 김재환

---

### AI-07: 대화형 응답 생성

**Title (서브태스크):** `Feat: 대화형 응답 생성`

**설명 (Description):**

사용자는 자연스러운 대화를 위해 대화형 응답 생성 기능을 사용하고 싶다.

## ✅ 완료 조건
- 실행 결과 기반 다음 절차/작업 멘트 생성
- 대화 맥락 유지 및 자연스러운 응답
- 단계별 안내 및 확인 멘트 생성
- 대화 생성 모듈 구현

## 💬 기타
- GPT 기반 응답 생성
- 페르소나 설정 (친절한 쇼핑 도우미)
- TTS 출력용 텍스트 최적화

**Story Point:** 5

**중요도 (Priority):** Medium

**담당자:** 김재환

---

### AI-08: 플로우 위임 판단

**Title (서브태스크):** `Feat: 플로우 위임 판단`

**설명 (Description):**

사용자는 작업 유형에 따른 적절한 처리 방식을 선택하기 위해 플로우 위임 판단 기능을 사용하고 싶다.

## ✅ 완료 조건
- 일반 명령 vs 플로우 필요 작업 판단
- 회원가입/결제 등 복잡한 작업 감지
- 플로우 엔진으로 위임 결정
- 판단 로직 모듈 구현

## 💬 기타
- 규칙 기반 + LLM 기반 하이브리드 판단
- 플로우 필요 키워드 목록 관리
- 위임 결정 로깅

**Story Point:** 3

**중요도 (Priority):** Medium

**담당자:** 김재환

---

### AI-09: HTTP API

**Title (서브태스크):** `Feat: HTTP API`

**설명 (Description):**

사용자는 인증, 헬스체크, 백엔드 통신을 위해 REST API 기능을 사용하고 싶다.

## ✅ 완료 조건
- /health, /status 헬스체크 엔드포인트 구현
- /auth/token, /auth/refresh 인증 API 구현
- /backend/cart, /backend/order 백엔드 통신 API 구현
- HTTP API 모듈(`api/health.py`, `api/auth.py`, `api/backend.py`) 구현

## 💬 기타
- FastAPI 라우터 사용
- JWT 토큰 기반 인증
- 백엔드 서버 연동

**Story Point:** 5

**중요도 (Priority):** Medium

**담당자:** 하주형

---

### AI-10: 시스템 통합

**Title (서브태스크):** `Feat: 시스템 통합`

**설명 (Description):**

개발자는 모든 모듈을 통합하고 배포하기 위해 FastAPI 앱 통합 기능을 사용하고 싶다.

## ✅ 완료 조건
- FastAPI 앱 초기화 및 라우터 등록
- 환경 변수 관리 (`core/config.py`)
- 로깅 설정 (`core/logging.py`)
- 메인 앱 파일 (`main.py`) 구현
- Docker/배포 환경 설정

## 💬 기타
- 모든 서비스 모듈 통합
- 환경별 설정 (dev, prod)
- 에러 핸들링 및 모니터링

**Story Point:** 8

**중요도 (Priority):** High

**담당자:** 하주형

---

## 요약

### AI 파트 Story Points 합계
- AI-01: 8 (김민찬)
- AI-02: 5 (김민찬)
- AI-03: 8 (김민찬)
- AI-04: 5 (김민찬)
- AI-05: 13 (김재환)
- AI-06: 13 (김재환)
- AI-07: 8 (김재환)
- AI-08: 13 (하주형)
- AI-09: 5 (하주형)
- AI-10: 8 (하주형)
**Total: 86 포인트**

### 중요도 분류
**High Priority:**
- AI-01, AI-02, AI-03, AI-05, AI-10

**Medium Priority:**
- AI-04, AI-06, AI-07, AI-09

**Low Priority:**
- AI-08

### 담당자별 작업 분배

**김민찬:**
- AI-01: STT (8pt)
- AI-02: TTS (5pt)
- AI-03: WebSocket 통신 (8pt)
- AI-04: 세션 관리 (5pt)
- **총: 26 포인트**

**김재환:**
- AI-05: LLM 명령 생성 (13pt)
- AI-06: 플로우 엔진 (13pt)
- AI-07: OCR 인식 (8pt)
- **총: 34 포인트**

**하주형:**
- AI-08: WebRTC 시그널링 (13pt)
- AI-09: HTTP API (5pt)
- AI-10: 시스템 통합 (8pt)
- **총: 26 포인트**
