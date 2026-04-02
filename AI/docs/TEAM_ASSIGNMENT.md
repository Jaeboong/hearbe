# AI 서버 팀 역할 분담 및 개발 일정

> FastAPI 기반 음성 쇼핑 AI 서버 3인 개발 계획 (3주 5일, 20일)

## 👥 팀 구성

**총 인원**: 3명
**개발 기간**: 3주 5일 (20 영업일)
**기술 스택**: FastAPI, WebSocket, Whisper, Hugging Face, OpenAI GPT-5-mini
**배포 환경**: Ubuntu + Docker + Nginx

---

## 📋 역할 분담

### 👤 담당자 김민찬: STT & TTS & WebSocket Core

**핵심 역할**: 음성 입출력 및 실시간 통신 담당

**담당 모듈**:
- 🔴 `services/stt.py` - Whisper STT (음성→텍스트)
- 🔴 `services/tts.py` - Hugging Face TTS (텍스트→음성)
- 🔴 `websocket/gateway.py` - WebSocket 연결 관리
- 🔴 `websocket/session.py` - 세션 관리 (메모리/Redis)

**구현 파일**:
```
□  services/stt.py              (Whisper 모델 로딩, 스트리밍 STT)
□  services/tts.py              (HF TTS 모델, 음성 합성)
□  websocket/gateway.py         (WS 연결, 메시지 라우팅)
□  websocket/session.py         (세션 생성/관리/삭제)
□  tests/test_stt.py
□  tests/test_tts.py
□  tests/test_websocket.py
```

**필요 기술**:
- Whisper (openai-whisper 또는 faster-whisper)
- Hugging Face Transformers (TTS 모델)
- FastAPI WebSocket
- asyncio (비동기 처리)
- Redis (선택, 세션 관리)

**예상 작업량**: 35시간

---

### 👤 담당자 김재환: LLM & Flow Engine

**핵심 역할**: AI 명령 생성 및 플로우 관리

**담당 모듈**:
- 🔴 `services/llm.py` - OpenAI GPT-5-mini
- 🔴 `services/rag.py` - RAG 파이프라인 (Vector 검색, Few-Shot)
- 🔴 `services/embedding.py` - 임베딩 생성
- 🔴 `services/flow_engine.py` - 플로우 엔진 (사이트별 단계 처리)
- 🔴 `flows/` - 사이트별 플로우 JSON 정의

**구현 파일**:
```
□  services/llm.py              (OpenAI API, 명령 생성)
□  services/rag.py              (RAG 파이프라인)
□  services/embedding.py        (임베딩 생성)
□  services/flow_engine.py      (플로우 상태 머신)
□  flows/coupang/search.json    (쿠팡 검색 플로우)
□  flows/coupang/checkout.json  (쿠팡 결제 플로우)
□  flows/naver/search.json      (네이버 검색 플로우)
□  flows/elevenst/search.json   (11번가 검색 플로우)
□  models/flow.py               (플로우 데이터 모델)
□  tests/test_llm.py
□  tests/test_rag.py
□  tests/test_flow_engine.py
```

**필요 기술**:
- OpenAI API (GPT-5-mini)
- MariaDB Vector (RAG용 Vector DB)
- JSON 플로우 설계
- 상태 머신 패턴

**예상 작업량**: 35시간

---

### 👤 담당자 하주형: OCR

**핵심 역할**: 결제 키패드/CAPTCHA/상품 이미지 인식

**담당 모듈**:
- 🔴 `services/ocr.py` - 결제 키패드 OCR
- 🔴 `services/image_recognition.py` - 상품 이미지 인식

**구현 파일**:
```
□  services/ocr.py              (HF OCR 모델, 키패드 인식)
□  services/image_recognition.py (상품 이미지 텍스트/특징 추출)
□  tests/test_ocr.py
```

**필요 기술**:
- Hugging Face OCR (TrOCR, PaddleOCR)
- 이미지 전처리
- 바운딩 박스 검출

**예상 작업량**: 20시간

---

### 👤 담당자 김민찬: WebRTC & HTTP API & 통합

**핵심 역할**: 보호자 원격 제어 및 시스템 통합

**담당 모듈**:
- 🔴 `webrtc/` - WebRTC 시그널링 (보호자 원격 제어)
- 🔴 `api/` - HTTP API (인증, 헬스체크, 백엔드 통신)
- 🔴 `websocket/handlers.py` - WebSocket 메시지 핸들러
- 🔴 `main.py` - FastAPI 앱 통합

**구현 파일**:
```
□  webrtc/signaling.py          (WebRTC 오퍼/앤서)
□  webrtc/guardian.py           (보호자 세션 관리)
□  api/health.py                (/health, /status)
□  api/auth.py                  (/auth/token, 임시 토큰)
□  api/backend.py               (/backend/cart, /backend/order)
□  websocket/handlers.py        (메시지 타입별 처리)
□  main.py                      (앱 초기화, 라우터 등록)
□  core/config.py               (환경 변수 관리)
□  core/logging.py              (로깅 설정)
□  tests/test_api.py
□  tests/test_webrtc.py
```

**필요 기술**:
- WebRTC (aiortc)
- FastAPI HTTP Routing
- Pydantic (데이터 검증)
- 시스템 통합 경험

**예상 작업량**: 35시간

---

## 📅 개발 일정 (4주, 20일)

### Week 1: 기반 구축 (Day 1-5)

#### Day 1 (공동 작업)
**환경 설정 및 프로젝트 초기화**

| 작업 | 담당 | 시간 | 상태 |
|------|------|------|------|
| 프로젝트 폴더 구조 생성 | 전체 | 1h | □ |
| Docker 환경 설정 | C | 2h | □ |
| requirements.txt 작성 | 전체 | 1h | □ |
| .env.example 작성 | 전체 | 1h | □ |
| AI 모델 다운로드 스크립트 | A, B | 3h | □ |

---

#### Day 2-5 (병렬 작업)

**담당자 A: STT & TTS 기반 구현**

| 일차 | 작업 | 파일 | 시간 | 상태 |
|------|------|------|------|------|
| 2일 | Whisper 모델 로딩 | services/stt.py | 4h | □ |
| 2일 | STT 기본 구현 | services/stt.py | 4h | □ |
| 3일 | 오디오 스트리밍 처리 | services/stt.py | 4h | □ |
| 3일 | STT 단위 테스트 | tests/test_stt.py | 4h | □ |
| 4일 | HF TTS 모델 로딩 | services/tts.py | 4h | □ |
| 4일 | TTS 음성 합성 구현 | services/tts.py | 4h | □ |
| 5일 | TTS 단위 테스트 | tests/test_tts.py | 4h | □ |
| 5일 | 성능 최적화 | services/stt.py, tts.py | 4h | □ |

**Week 1 목표**: STT/TTS 모델 로딩 및 기본 변환 기능 완성

---

**담당자 B: LLM & Flow Engine 기반**

| 일차 | 작업 | 파일 | 시간 | 상태 |
|------|------|------|------|------|
| 2일 | OpenAI API 연동 | services/llm.py | 4h | □ |
| 2일 | 명령 생성 로직 | services/llm.py | 4h | □ |
| 3일 | 플로우 엔진 구조 설계 | services/flow_engine.py | 4h | □ |
| 3일 | 플로우 JSON 스키마 정의 | models/flow.py | 4h | □ |
| 4일 | 쿠팡 검색 플로우 JSON | flows/coupang/search.json | 4h | □ |
| 4일 | 플로우 실행 엔진 구현 | services/flow_engine.py | 4h | □ |
| 5일 | LLM 단위 테스트 | tests/test_llm.py | 4h | □ |
| 5일 | Flow 단위 테스트 | tests/test_flow_engine.py | 4h | □ |

**Week 1 목표**: LLM 명령 생성 + 기본 플로우 엔진

---

**담당자 C: WebSocket & HTTP API**

| 일차 | 작업 | 파일 | 시간 | 상태 |
|------|------|------|------|------|
| 2일 | FastAPI 앱 구조 | main.py | 4h | □ |
| 2일 | 환경 변수 관리 | core/config.py | 2h | □ |
| 2일 | 로깅 설정 | core/logging.py | 2h | □ |
| 3일 | WebSocket Gateway | websocket/gateway.py | 4h | □ |
| 3일 | 세션 관리 (메모리) | websocket/session.py | 4h | □ |
| 4일 | HTTP Health API | api/health.py | 4h | □ |
| 4일 | HTTP Auth API | api/auth.py | 4h | □ |
| 5일 | WS 메시지 핸들러 구조 | websocket/handlers.py | 4h | □ |
| 5일 | API 단위 테스트 | tests/test_api.py | 4h | □ |

**Week 1 목표**: FastAPI 앱 기본 구조 + WebSocket 연결

---

### Week 2: 핵심 기능 구현 (Day 6-10)

#### 담당자 김민찬: WebSocket 통신 완성

| 일차 | 작업 | 파일 | 시간 | 상태 |
|------|------|------|------|------|
| 6일 | 오디오 스트림 수신 | websocket/gateway.py | 4h | □ |
| 6일 | STT 결과 전송 | websocket/handlers.py | 4h | □ |
| 7일 | TTS 음성 전송 | websocket/handlers.py | 4h | □ |
| 7일 | 에러 처리 | websocket/gateway.py | 4h | □ |
| 8일 | Redis 세션 관리 (선택) | websocket/session.py | 4h | □ |
| 8일 | 재연결 로직 | websocket/gateway.py | 4h | □ |
| 9일 | WS 통합 테스트 | tests/test_websocket.py | 4h | □ |
| 10일 | 성능 튜닝 | websocket/ | 4h | □ |

**Week 2 목표**: 오디오 스트리밍 → STT → TTS 전체 파이프라인

---

#### 담당자 하주형: Flow Engine & OCR

| 일차 | 작업 | 파일 | 시간 | 상태 |
|------|------|------|------|------|
| 6일 | 쿠팡 결제 플로우 JSON | flows/coupang/checkout.json | 4h | □ |
| 6일 | 플로우 단계별 실행 | services/flow_engine.py | 4h | □ |
| 7일 | OCR 모델 로딩 | services/ocr.py | 4h | □ |
| 7일 | 키패드 인식 로직 | services/ocr.py | 4h | □ |
| 8일 | 네이버 검색 플로우 | flows/naver/search.json | 4h | □ |
| 8일 | 11번가 검색 플로우 | flows/elevenst/search.json | 4h | □ |
| 9일 | OCR 단위 테스트 | tests/test_ocr.py | 4h | □ |
| 10일 | 플로우 통합 테스트 | tests/test_flow_engine.py | 4h | □ |

**Week 2 목표**: 사이트별 플로우 완성 + OCR 결제 인증

---

#### 담당자 김민찬: WebRTC & 통합

| 일차 | 작업 | 파일 | 시간 | 상태 |
|------|------|------|------|------|
| 6일 | WebRTC 시그널링 서버 | webrtc/signaling.py | 4h | □ |
| 6일 | 오퍼/앤서 처리 | webrtc/signaling.py | 4h | □ |
| 7일 | 보호자 세션 관리 | webrtc/guardian.py | 4h | □ |
| 7일 | ICE 후보 교환 | webrtc/signaling.py | 4h | □ |
| 8일 | Backend API 연동 | api/backend.py | 4h | □ |
| 8일 | 장바구니/주문 전송 | api/backend.py | 4h | □ |
| 9일 | WS 핸들러 통합 | websocket/handlers.py | 4h | □ |
| 10일 | WebRTC 테스트 | tests/test_webrtc.py | 4h | □ |

**Week 2 목표**: WebRTC 보호자 원격 제어 + 백엔드 연동

---

### Week 3: 통합 및 테스트 (Day 11-15)

#### Day 11-13 (공동 작업): 전체 통합

| 일차 | 작업 | 담당 | 시간 | 상태 |
|------|------|------|------|------|
| 11일 | main.py 모듈 통합 | C | 4h | □ |
| 11일 | 전체 플로우 테스트 (쿠팡 검색) | A+B+C | 4h | □ |
| 12일 | MCP 앱과 WebSocket 연동 | A+C | 4h | □ |
| 12일 | 플로우 엔진 통합 테스트 | B+C | 4h | □ |
| 13일 | 버그 수정 (1차) | 전체 | 8h | □ |

---

#### Day 14-15 (배포 준비)

| 일차 | 작업 | 담당 | 시간 | 상태 |
|------|------|------|------|------|
| 14일 | Docker 이미지 빌드 | C | 4h | □ |
| 14일 | Nginx 리버스 프록시 설정 | C | 2h | □ |
| 14일 | 환경 변수 정리 | 전체 | 2h | □ |
| 15일 | Ubuntu 배포 테스트 | C | 4h | □ |
| 15일 | 로컬→서버 연동 테스트 | 전체 | 4h | □ |

**Week 3 목표**: 전체 시스템 통합 + 배포 완료

---

### Week 4: 고급 기능 & 최적화 (Day 16-20)

#### Day 16-18 (병렬 작업)

**담당자 A: 성능 최적화**

| 일차 | 작업 | 파일 | 시간 | 상태 |
|------|------|------|------|------|
| 16일 | STT 스트리밍 최적화 | services/stt.py | 4h | □ |
| 16일 | TTS 캐싱 구현 | services/tts.py | 4h | □ |
| 17일 | WebSocket 동시 연결 테스트 | websocket/gateway.py | 4h | □ |
| 18일 | 메모리 사용량 최적화 | services/ | 4h | □ |

---

**담당자 B: 플로우 확장**

| 일차 | 작업 | 파일 | 시간 | 상태 |
|------|------|------|------|------|
| 16일 | 쿠팡 회원가입 플로우 | flows/coupang/signup.json | 4h | □ |
| 16일 | 네이버 결제 플로우 | flows/naver/checkout.json | 4h | □ |
| 17일 | 11번가 결제 플로우 | flows/elevenst/checkout.json | 4h | □ |
| 18일 | 플로우 에러 처리 개선 | services/flow_engine.py | 4h | □ |

---

**담당자 C: 모니터링 & 문서**

| 일차 | 작업 | 파일 | 시간 | 상태 |
|------|------|------|------|------|
| 16일 | 로깅 개선 | core/logging.py | 4h | □ |
| 16일 | 에러 추적 (Sentry 등) | core/ | 4h | □ |
| 17일 | API 문서 작성 | docs/API_SPECIFICATION.md | 4h | □ |
| 18일 | WebSocket 프로토콜 문서 | docs/WEBSOCKET_PROTOCOL.md | 4h | □ |

---

#### Day 19-20 (최종 테스트 & 문서화)

| 일차 | 작업 | 담당 | 시간 | 상태 |
|------|------|------|------|------|
| 19일 | 전체 통합 테스트 | 전체 | 8h | □ |
| 20일 | 버그 수정 (최종) | 전체 | 4h | □ |
| 20일 | README 및 문서 정리 | 전체 | 4h | □ |

**Week 4 목표**: 프로덕션 준비 완료

---

## 🔄 협업 프로세스

### 매일 (Daily)

#### 아침 스탠드업 (10분)
- **시간**: 오전 10시
- **형식**: Slack/Discord
- **내용**:
  - 어제 한 일
  - 오늘 할 일
  - 블로커/이슈

#### 저녁 동기화 (5분)
- **시간**: 오후 6시
- **형식**: 간단한 메시지
- **내용**: 진행 상황 공유

---

### 주 2회 (화요일, 목요일)

#### 코드 리뷰 세션 (30분)
- **시간**: 오후 4시
- **형식**: GitHub PR 리뷰
- **내용**:
  - 서로의 코드 리뷰
  - 모듈 간 연동 확인
  - API 설계 논의

---

### 주 1회 (금요일)

#### 주간 회고 (1시간)
- **시간**: 오후 5시
- **형식**: 대면 또는 화상
- **내용**:
  - 이번 주 성과
  - 다음 주 계획
  - 개선 사항

---

## 🚨 중요 규칙

### 1. Git 커밋 전 체크리스트
```
□ 내 담당 모듈만 수정했는가?
□ core/ 폴더를 수정했다면 팀원에게 알렸는가?
□ API 스키마를 변경했다면 문서를 업데이트했는가?
□ WebSocket 메시지 타입을 추가했다면 WEBSOCKET_PROTOCOL.md를 업데이트했는가?
□ 환경 변수를 추가했다면 .env.example을 업데이트했는가?
□ 테스트 코드를 작성했는가?
```

### 2. 공통 파일 수정 규칙

**core/ 폴더 수정 시**:
1. Slack/Discord에 먼저 공지
2. 팀원 승인 후 수정
3. 즉시 PR 생성하여 리뷰 요청

**models/ 폴더 수정 시**:
- 데이터 모델 변경 시 팀 전체에 영향
- 먼저 논의 후 수정

### 3. WebSocket 메시지 타입 추가 규칙

새로운 메시지 타입 필요 시:
1. `models/websocket.py`에 Pydantic 모델 추가
2. `docs/WEBSOCKET_PROTOCOL.md`에 명세 추가
3. Slack/Discord에 공지

---

## 📞 의사소통 채널

### 실시간 질문
- **채널**: Slack/Discord
- **응답 시간**: 30분 이내

### 긴급 이슈
- **채널**: 전화 또는 화상 회의
- **대상**: 블로커, 아키텍처 변경, 모델 크래시

### 코드 리뷰
- **채널**: GitHub PR 코멘트
- **응답 시간**: 24시간 이내

---

## 🎯 주간 마일스톤

### Week 1 마일스톤 (Day 5)
- [ ] 담당자 A: STT/TTS 모델 로딩 및 변환 성공
- [ ] 담당자 B: LLM 명령 생성 성공
- [ ] 담당자 C: WebSocket 연결 성공
- [ ] 통합: FastAPI 서버 로컬 실행 가능

**확인 방법**:
```bash
# 담당자 A
pytest tests/test_stt.py
pytest tests/test_tts.py

# 담당자 B
pytest tests/test_llm.py

# 담당자 C
curl http://localhost:8000/health
```

---

### Week 2 마일스톤 (Day 10)
- [ ] 담당자 A: 오디오 스트리밍 → STT → TTS 파이프라인 완성
- [ ] 담당자 B: 쿠팡 검색/결제 플로우 완성
- [ ] 담당자 C: WebRTC 시그널링 성공
- [ ] 통합: MCP 앱과 WebSocket 연동 테스트

**확인 방법**:
```bash
# WebSocket 테스트
pytest tests/test_websocket.py

# Flow 테스트
pytest tests/test_flow_engine.py
```

---

### Week 3 마일스톤 (Day 15)
- [ ] 전체 플로우 통합 완료
- [ ] Docker 이미지 빌드 성공
- [ ] Ubuntu 서버 배포 성공
- [ ] MCP 앱 → AI 서버 → Backend 전체 연동

**최종 확인**:
```bash
# Docker 실행
docker-compose up -d

# 헬스 체크
curl http://서버주소/health

# WebSocket 연결
wscat -c ws://서버주소/ws
```

---

### Week 4 마일스톤 (Day 20)
- [ ] 모든 사이트 플로우 완성 (쿠팡, 네이버, 11번가)
- [ ] 성능 최적화 완료
- [ ] 문서 정리 완료
- [ ] 프로덕션 배포 준비 완료

---

## 📈 진행 상황 추적

### GitHub Projects 사용

#### 컬럼 구성:
```
📋 To Do  →  🏗 In Progress  →  👀 Review  →  ✅ Done
```

#### Issue 템플릿:
```markdown
# [A] Whisper STT 구현
Assignee: 담당자 A
Labels: stt, week1
Milestone: Week 1

## 작업 내용
- [ ] Whisper 모델 다운로드
- [ ] 모델 로딩 코드 작성
- [ ] 오디오 스트림 처리
- [ ] 단위 테스트 작성

## 완료 조건
- pytest 통과
- 한국어 음성 인식률 90% 이상
```

---

## 🎓 학습 리소스

### 담당자 A 추천 자료
- Whisper: https://github.com/openai/whisper
- faster-whisper: https://github.com/guillaumekln/faster-whisper
- FastAPI WebSocket: https://fastapi.tiangolo.com/advanced/websockets/
- Hugging Face TTS: https://huggingface.co/models?pipeline_tag=text-to-speech

### 담당자 B 추천 자료
- OpenAI API: https://platform.openai.com/docs/api-reference
- Flow State Machine: https://en.wikipedia.org/wiki/Finite-state_machine
- TrOCR: https://huggingface.co/microsoft/trocr-base-printed
- JSON Schema: https://json-schema.org/

### 담당자 C 추천 자료
- WebRTC: https://webrtc.org/
- aiortc: https://github.com/aiortc/aiortc
- FastAPI Routing: https://fastapi.tiangolo.com/tutorial/bigger-applications/
- Docker: https://docs.docker.com/

---

## 📝 참고 문서

- [API 명세서](API_SPECIFICATION.md)
- [WebSocket 프로토콜](WEBSOCKET_PROTOCOL.md)
- [플로우 엔진 가이드](FLOW_ENGINE_GUIDE.md)
- [환경 설정 가이드](SETUP_GUIDE.md)
- [프로젝트 README](../README.md)

---

## 🚀 시작하기

### 1. 환경 설정 (Day 1)
```bash
# 저장소 클론
git clone <repository-url>
cd AI

# 가상 환경 생성
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt

# AI 모델 다운로드
python scripts/download_models.py

# .env 파일 생성
cp .env.example .env
```

### 2. 브랜치 생성
```bash
# 담당자 A
git checkout -b feature/stt-tts-websocket

# 담당자 B
git checkout -b feature/llm-flow-ocr

# 담당자 C
git checkout -b feature/webrtc-api-integration
```

### 3. 개발 시작
각자 담당 모듈 폴더에서 작업 시작!

---

**문서 버전**: 1.0
**작성일**: 2026-01-14
**다음 업데이트**: Week 1 종료 후 (Day 5)
