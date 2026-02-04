# TTS (음성 합성) Flow

## 개요
서버에서 생성된 텍스트 응답을 Google Cloud TTS로 음성으로 변환하여 클라이언트에 스트리밍 전송하는 흐름.

## Flow 다이어그램

```
텍스트 응답 생성 (LLM/규칙/플로우)
│
├─ [1] api/ws/sender.py → WSSender.send_tts_response()
│   └─ 텍스트 정규화
│
├─ [2] api/ws/tts/tts_normalizer.py → TTSNormalizer
│   └─ TTS 전 텍스트 정리
│       ├─ 숫자 → 한국어 읽기 ("10만원" → "십만 원")
│       ├─ 특수문자 제거/변환
│       ├─ 약어 풀어쓰기
│       └─ 긴 텍스트 문장 단위 분할
│
├─ [3] services/tts/service.py → TTSService.synthesize_stream()
│   ├─ Google Cloud Text-to-Speech API 호출
│   ├─ 음성: ko-KR-Chirp3-HD-Leda (한국어, 여성, HD)
│   ├─ 샘플레이트: 24kHz
│   └─ 청크 단위 스트리밍 반환
│
├─ [4] api/ws/sender.py → 청크별 WebSocket 전송
│   ├─ tts_chunk (바이너리 오디오)
│   ├─ tts_chunk (바이너리 오디오)
│   ├─ ...
│   └─ tts_chunk (is_final: true)
│
└─ [5] 클라이언트: 오디오 청크 수신 → 즉시 재생
```

## 인터럽트 처리

```
사용자가 TTS 재생 중 새 입력
│
├─ api/ws/handlers/text_session/interrupt_manager.py → InterruptManager
│   ├─ 현재 TTS 스트리밍 중단
│   ├─ 오디오 큐 비우기
│   └─ 새 입력 처리 시작
│
└─ 클라이언트: 재생 중인 오디오 즉시 중지
```

## 관련 파일

| 단계 | 파일 | 역할 |
|------|------|------|
| TTS 서비스 | `services/tts/service.py` | Google Cloud TTS 래핑 |
| TTS 정규화 | `api/ws/tts/tts_normalizer.py` | TTS 전 텍스트 정리 |
| 응답 전송 | `api/ws/sender.py` | TTS 청크 WebSocket 전송 |
| 인터럽트 | `api/ws/handlers/text_session/interrupt_manager.py` | TTS 중단 관리 |
| 페이지별 포매팅 | `api/ws/presenter/pages/*.py` | 페이지별 TTS 텍스트 생성 |

## TTS 스펙

- **프로바이더**: Google Cloud Text-to-Speech
- **음성**: ko-KR-Chirp3-HD-Leda
- **샘플레이트**: 24kHz
- **스트리밍**: 청크 단위 전송
