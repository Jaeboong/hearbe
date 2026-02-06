# 음성 인식 (ASR) Flow

## 개요
클라이언트에서 마이크 오디오 청크를 WebSocket으로 전송하면, ASR 모델이 음성을 텍스트로 변환하여 반환하는 흐름.

## 핵심 진입 파일

- `api/ws/handlers/audio_handler.py`

### import 맵 (프로젝트 내부)

- `core/event_bus.py`
- `core/interfaces.py`
- `api/ws/models.py`

## Flow 다이어그램

```
클라이언트 마이크 입력 (audio_chunk)
│
├─ [1] api/websocket.py → WebSocketHandler.handle_connection()
│   ├─ 텍스트 메시지: type="audio_chunk" (base64)
│   └─ 바이너리 프레임: raw bytes
│
├─ [2] api/ws/router.py → WebSocketRouter.handle_text()/handle_binary()
│   ├─ 텍스트: HandlerManager.handle_audio_chunk() (base64 → bytes)
│   └─ 바이너리: HandlerManager.handle_binary_audio() (raw bytes)
│
├─ [3] api/ws/handlers/handler_manager.py → handle_audio_chunk()
│   └─ AudioHandler로 위임
│
├─ [4] api/ws/handlers/audio_handler.py → AudioHandler
│   ├─ handle_audio_chunk() → 세션별 큐에 청크 적재
│   ├─ _asr_worker() → 큐에서 꺼내 버퍼 누적
│   └─ is_final=True일 때만 전사 수행
│
├─ [5] services/asr/service.py → ASRService.transcribe()
│   └─ Factory 패턴으로 선택된 프로바이더 호출
│
├─ [6] services/asr/factory.py → ASRServiceFactory.create()
│   ├─ config.provider == "whisper"
│   │   └─ services/asr/providers/whisper.py → WhisperASRProvider
│   │       └─ faster_whisper.WhisperModel (GPU CUDA)
│   │       └─ 모델: large-v3-turbo, 16kHz mono
│   │
│   └─ config.provider == "qwen3"
│       └─ services/asr/providers/qwen3.py → Qwen3ASRProvider
│           └─ qwen_asr.Qwen3ASRModel (GPU bfloat16)
│
├─ [7] services/asr/providers/base.py → BaseASRProvider._preprocess_audio()
│   └─ 오디오 전처리: 16kHz, mono, float32 변환
│
├─ [8] ASRResult(text="핸드폰 검색해줘", confidence=0.98, is_final=true)
│
├─ [9] api/ws/sender.py → WSSender.send_asr_result()
│   └─ WebSocket: { type: "asr_result", data: { text, confidence, language, duration, segment_id } }
│
└─ [10] 클라이언트: 인식 결과를 user_input으로 자동 전송
```

## 관련 파일

| 단계 | 파일 | 역할 |
|------|------|------|
| 바이너리 수신 | `api/ws/router.py` | 바이너리 메시지 라우팅 |
| 오디오 버퍼링 | `api/ws/handlers/audio_handler.py` | 청크 축적 및 ASR 큐 관리 |
| ASR 래퍼 | `services/asr/service.py` | 프로바이더 래핑 |
| 팩토리 | `services/asr/factory.py` | Whisper/Qwen3 선택 |
| 추상 베이스 | `services/asr/providers/base.py` | 오디오 전처리, 인터페이스 |
| Whisper | `services/asr/providers/whisper.py` | Faster-Whisper 구현 |
| Qwen3 | `services/asr/providers/qwen3.py` | Qwen3-ASR 구현 |
| 결과 전송 | `api/ws/sender.py` | ASR 결과 WebSocket 전송 |

## 오디오 스펙

- **포맷**: 16kHz mono PCM (16-bit) 또는 WAV
- **버퍼 처리**: is_final=true일 때만 전사 (세션별 버퍼 누적)
- **Whisper 모델**: large-v3-turbo (float16, CUDA)
- **Qwen3 모델**: bfloat16, GPU
