# 음성 인식 (ASR) Flow

## 개요
클라이언트에서 마이크 오디오 청크를 WebSocket으로 전송하면, ASR 모델이 음성을 텍스트로 변환하여 반환하는 흐름.

## Flow 다이어그램

```
클라이언트 마이크 입력 (audio_chunk)
│
├─ [1] api/websocket.py → WebSocketHandler.handle_connection()
│   └─ 바이너리 프레임 수신
│
├─ [2] api/ws/router.py → WebSocketRouter.handle_binary()
│   └─ HandlerManager.handle_binary_audio()로 위임
│
├─ [3] api/ws/handlers/handler_manager.py → handle_audio_chunk()
│   └─ AudioHandler로 위임
│
├─ [4] api/ws/handlers/audio_handler.py → AudioHandler
│   ├─ handle_audio_chunk() → 오디오 버퍼에 축적
│   ├─ 32KB 임계값 도달 시 ASR 워커 큐에 전달
│   └─ _asr_worker() → 비동기 루프에서 처리
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
│   └─ WebSocket: { type: "asr_result", data: { text, confidence } }
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
- **버퍼 임계값**: 32KB
- **Whisper 모델**: large-v3-turbo (float16, CUDA)
- **Qwen3 모델**: bfloat16, GPU
