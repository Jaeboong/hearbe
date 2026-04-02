# AI_next 아키텍처

## 목적

기존 `AI/` 에서 **ASR, TTS, OCR, MCP WebSocket 연결** 기능만 추출한 경량 서버.
브라우저 커맨드 생성 규칙(Rules)과 LLM Fallback은 완전히 새로 설계할 예정.

---

## 기존 AI → AI_next 마이그레이션 요약

### 가져온 것 (그대로 복사)
| 모듈 | 경로 | 설명 |
|------|------|------|
| ASR | `services/asr/` | Whisper + Qwen3 provider (전체) |
| TTS | `services/tts/service.py` | Google Cloud TTS API 호출 |
| OCR | `services/ocr/` | PaddleOCR + payment keypad + text_processors (전체) |
| Session | `services/session/service.py` | 세션 상태 관리 |
| Event Bus | `core/event_bus.py` | 이벤트 pub/sub |
| Interfaces | `core/interfaces.py` | 공통 데이터클래스 |
| WS Models | `api/ws/models.py` | 메시지 타입 정의 |
| TTS Normalizer | `api/ws/tts/` | 한국어 TTS 텍스트 정규화 |

### 새로 작성한 것 (경량화)
| 파일 | 설명 |
|------|------|
| `core/config.py` | LLM/NLU/Flow 설정 제거, ASR/TTS/OCR/Server만 |
| `api/websocket.py` | ConnectionManager 동일, WebSocketHandler에서 LLM/NLU/Flow 의존성 제거 |
| `api/ws/router.py` | 동일 구조, LLM 라우팅 없음 |
| `api/ws/sender.py` | TTS 스트리밍 + 기본 응답 전송 (LLM 관련 제거) |
| `api/ws/handlers/handler_manager.py` | AudioHandler만 연결, text/mcp는 stub |
| `api/ws/handlers/audio_handler.py` | ASR 파이프라인 (원본 기반, 콜백 방식으로 변경) |
| `main.py` | FastAPI 진입점 (ASR+TTS+OCR only) |

### 제거한 것 (새로 구현 예정)
- `services/llm/` — 규칙 엔진, LLM generator, context builder, planner 전체
- `services/nlu/` — 의도 분석
- `services/flow/` — 플로우 엔진 (회원가입/결제 등)
- `services/summarizer/` — HTML 파서 + OCR 통합 (필요시 별도 추가)
- `api/ws/handlers/` 하위 비즈니스 핸들러 전부 (coupang, hearbe, text_handler 등)
- `api/ws/feedback/` — 실행 후 피드백
- `api/ws/presenter/` — 페이지별 TTS 생성기

---

## 디렉토리 구조

```
AI_next/
├── main.py                          # FastAPI 진입점
├── Dockerfile                       # nvidia/cuda 기반
├── docker-compose.yml               # hearbe-next 컨테이너 (포트 8001)
├── .env                             # 환경변수
├── requirements.txt                 # 의존성
├── docs/
│   └── ARCHITECTURE.md              # 이 파일
├── core/
│   ├── config.py                    # 설정 (ASR/TTS/OCR/Server)
│   ├── interfaces.py                # 데이터클래스
│   └── event_bus.py                 # 이벤트 시스템
├── services/
│   ├── asr/                         # ASR 서비스
│   │   ├── service.py               # ASRService (facade)
│   │   ├── factory.py               # provider factory
│   │   └── providers/
│   │       ├── base.py              # BaseASRProvider
│   │       ├── whisper.py           # Faster-Whisper
│   │       └── qwen3.py            # Qwen3-ASR
│   ├── tts/
│   │   └── service.py               # Google Cloud TTS
│   ├── ocr/                         # OCR 서비스
│   │   ├── service.py / ocr.py
│   │   ├── payment/                 # 결제 키패드 OCR
│   │   └── text_processors/         # 텍스트 처리 파이프라인
│   └── session/
│       └── service.py               # 세션 관리
└── api/
    ├── websocket.py                 # ConnectionManager + WebSocketHandler
    └── ws/
        ├── models.py                # 메시지 타입
        ├── router.py                # 메시지 라우팅
        ├── sender.py                # 응답 전송 + TTS 스트리밍
        ├── tts/                     # TTS 텍스트 정규화
        └── handlers/
            ├── audio_handler.py     # ASR 파이프라인
            └── handler_manager.py   # 핸들러 오케스트레이터
```

---

## 새 로직 연결 지점 (TODO)

### 1. 텍스트 입력 → 커맨드 생성
**파일:** `api/ws/handlers/handler_manager.py`

```python
async def handle_user_input(self, session_id: str, data: dict):
    # TODO: 새 커맨드 생성 로직
```

### 2. ASR 결과 → 텍스트 처리
**파일:** `api/ws/handlers/handler_manager.py`

```python
async def _on_asr_text(self, session_id: str, text: str):
    # ASR 완료 후 콜백 — 새 로직 연결
```

### 3. MCP 실행 결과 처리
**파일:** `api/ws/handlers/handler_manager.py`

```python
async def handle_mcp_result(self, session_id: str, data: dict):
    # TODO: OCR 연동, 결과 기반 다음 동작 결정
```

---

## WebSocket 프로토콜 (MCP Desktop ↔ AI Server)

### Client → Server
| type | 설명 |
|------|------|
| `audio_chunk` | 오디오 청크 (base64 또는 binary) |
| `user_input` | 텍스트 입력 `{text: "..."}` |
| `mcp_result` | MCP 명령 실행 결과 `{tool_name, result, ...}` |
| `page_update` | 현재 페이지 URL 변경 `{url: "..."}` |
| `interrupt` | TTS/처리 중단 |
| `cancel` | 세션 취소 |

### Server → Client
| type | 설명 |
|------|------|
| `asr_result` | ASR 인식 결과 `{text, confidence, ...}` |
| `tool_calls` | MCP 명령 `{commands: [{tool_name, arguments}, ...]}` |
| `tts_chunk` | TTS 오디오 청크 (hex) |
| `ocr_progress` | OCR 처리 진행률 |
| `status` | 상태 메시지 |
| `error` | 에러 |

---

## Docker 설정

| 항목 | 값 |
|------|-----|
| 컨테이너명 | `hearbe-next` |
| 포트 | `8001` |
| 이미지 | `ai-next-server` |
| GPU | nvidia 1개 |
| 기반 | `nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04` |

기존 `hearbe` (포트 8000) 과 동시 실행 가능.
