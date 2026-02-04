# WebSocket 연결 생명주기 Flow

## 개요
클라이언트가 WebSocket으로 연결하면 세션을 생성하고, 메시지 타입에 따라 각 핸들러로 라우팅하는 전체 생명주기.

## Flow 다이어그램

```
클라이언트 WebSocket 연결 (/ws 또는 /ws/{session_id})
│
├─ [1] api/websocket.py → WebSocketHandler.handle_connection()
│   ├─ ConnectionManager.connect() → 연결 등록
│   └─ 세션 생성/복원
│
├─ [2] api/ws/handlers/handler_manager.py → HandlerManager.create_session()
│   └─ services/session/service.py → SessionManager.create_session()
│
├─ [3] api/ws/sender.py → send_status("connected")
│   └─ { type: "status", data: { status: "connected", session_id } }
│
├─ [4] 메시지 수신 루프 ──────────────────────────────────
│   │
│   ├─ 텍스트 메시지
│   │   └─ api/ws/router.py → WebSocketRouter.handle_text()
│   │       │
│   │       ├─ type: "user_input"
│   │       │   └─ HandlerManager.handle_user_input()
│   │       │       └─ → text_handler.py (검색/상품/장바구니/결제 등)
│   │       │
│   │       ├─ type: "user_confirm"
│   │       │   └─ HandlerManager.handle_user_confirm()
│   │       │       └─ → flow_handler.py (플로우 단계 진행)
│   │       │
│   │       ├─ type: "cancel"
│   │       │   └─ HandlerManager.handle_cancel()
│   │       │       └─ 현재 작업 취소
│   │       │
│   │       ├─ type: "interrupt"
│   │       │   └─ → interrupt_manager.py (TTS 중단)
│   │       │
│   │       ├─ type: "mcp_result"
│   │       │   └─ HandlerManager.handle_mcp_result()
│   │       │       └─ → mcp_handler.py (도구 결과 처리)
│   │       │
│   │       └─ type: "page_update"
│   │           └─ HandlerManager.handle_page_update()
│   │               └─ 세션 URL 업데이트
│   │
│   └─ 바이너리 메시지 (오디오)
│       └─ api/ws/router.py → WebSocketRouter.handle_binary()
│           └─ HandlerManager.handle_binary_audio()
│               └─ → audio_handler.py (ASR 처리)
│
└─ [5] 연결 종료
    ├─ api/ws/handlers/handler_manager.py → HandlerManager.cleanup_session()
    │   ├─ AudioHandler 정리
    │   ├─ TextHandler 정리
    │   └─ 세션 타이머 시작 (30분 유지)
    └─ ConnectionManager.disconnect()
```

## 메시지 타입 정리

### 클라이언트 → 서버

| 타입 | 설명 | 핸들러 |
|------|------|--------|
| `audio_chunk` | 마이크 오디오 (바이너리) | `audio_handler.py` |
| `user_input` | 텍스트 입력 | `text_handler.py` |
| `user_confirm` | 플로우 확인 | `flow_handler.py` |
| `cancel` | 작업 취소 | `handler_manager.py` |
| `interrupt` | TTS 중단 | `interrupt_manager.py` |
| `mcp_result` | 도구 실행 결과 | `mcp_handler.py` |
| `page_update` | URL 변경 알림 | `handler_manager.py` |

### 서버 → 클라이언트

| 타입 | 설명 | 전송 위치 |
|------|------|-----------|
| `asr_result` | ASR 인식 결과 | `sender.py` |
| `tool_calls` | MCP 명령 리스트 | `sender.py` |
| `flow_step` | 플로우 단계 안내 | `sender.py` |
| `tts_chunk` | 음성 오디오 (바이너리) | `sender.py` |
| `status` | 서버 상태 | `sender.py` |
| `error` | 에러 메시지 | `sender.py` |
| `ocr_progress` | OCR 처리 상태 | `sender.py` |

## 관련 파일

| 파일 | 역할 |
|------|------|
| `api/websocket.py` | WebSocket 연결 관리 |
| `api/ws/router.py` | 메시지 타입별 라우팅 |
| `api/ws/sender.py` | 응답 전송 |
| `api/ws/models.py` | 메시지 타입 정의 |
| `api/ws/handlers/handler_manager.py` | 핸들러 오케스트레이션 |
| `api/ws/handlers/audio_handler.py` | 오디오 처리 |
| `api/ws/handlers/text_handler.py` | 텍스트 처리 |
| `api/ws/handlers/mcp_handler.py` | MCP 결과 처리 |
| `api/ws/handlers/text_session/interrupt_manager.py` | 인터럽트 관리 |
| `services/session/service.py` | 세션 상태 관리 |
