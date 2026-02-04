# AI Server 전체 아키텍처 개요

## 엔트리포인트

`main.py` → FastAPI 앱 생성 → 7개 핵심 서비스 초기화

```
main.py (AIServer)
├── FastAPI lifespan 관리
├── 서비스 초기화 (ASR, NLU, LLM, TTS, OCR, Flow, Session)
├── WebSocket 엔드포인트 (/ws)
├── HTTP API 엔드포인트 (/api/v1)
└── Health check (/)
```

## 핵심 서비스 7개

| 서비스 | 파일 | 역할 |
|--------|------|------|
| ASR | `services/asr/service.py` | 음성 → 텍스트 변환 |
| NLU | `services/nlu/service.py` | 텍스트 → 의도 분석 |
| LLM Planner | `services/llm/planner/service.py` | 의도 → MCP 명령 생성 |
| TTS | `services/tts/service.py` | 텍스트 → 음성 합성 |
| OCR | `services/ocr/service.py` | 이미지 → 텍스트 추출 |
| Flow Engine | `services/flow/service.py` | 다단계 워크플로우 관리 |
| Session | `services/session/service.py` | 세션 상태 관리 |

## 디렉토리 구조

```
AI/
├── main.py                     # 앱 엔트리포인트
├── core/                       # 핵심 인프라
│   ├── config.py               # 설정 관리
│   ├── event_bus.py            # 이벤트 발행/구독
│   ├── interfaces.py           # 추상 인터페이스
│   └── korean_numbers.py       # 한국어 숫자 파싱
├── api/                        # API 레이어
│   ├── http.py                 # REST 엔드포인트
│   ├── websocket.py            # WebSocket 연결 관리
│   └── ws/                     # WebSocket 프로토콜
│       ├── router.py           # 메시지 라우팅
│       ├── sender.py           # 응답 전송
│       ├── models.py           # 메시지 타입 정의
│       ├── handlers/           # 메시지 핸들러
│       ├── presenter/          # TTS 응답 포매팅
│       ├── feedback/           # 액션 피드백
│       ├── search/             # 검색 결과 캐싱
│       └── tts/                # TTS 텍스트 정규화
├── services/                   # 비즈니스 로직
│   ├── asr/                    # 음성 인식
│   ├── nlu/                    # 자연어 이해
│   ├── llm/                    # LLM 명령 생성
│   ├── tts/                    # 음성 합성
│   ├── ocr/                    # 문자 인식
│   ├── flow/                   # 플로우 엔진
│   ├── session/                # 세션 관리
│   └── summarizer/             # HTML/OCR 요약
└── config/                     # 설정 파일
    ├── flows/                  # 플로우 정의 (사이트별)
    └── sites/                  # 사이트 감지 규칙
```

## 핵심 설계 패턴

- **Factory Pattern**: ASR 프로바이더 선택 (Whisper vs Qwen3)
- **Provider Pattern**: ASR/OCR/TTS 구현체 교체 가능
- **Event Bus**: 비동기 이벤트 발행/구독 (core/event_bus.py)
- **Pipeline Pattern**: 텍스트 입력 → 큐 → 라우팅 → 처리
- **Rule + LLM Fallback**: 규칙 기반 우선, 실패 시 LLM 호출
