# WebSocket ASR 스트리밍 아키텍처

> Queue 기반 실시간 음성 인식 처리 아키텍처

**버전**: 1.0
**작성일**: 2026-01-21
**관련 문서**: [WEBSOCKET_PROTOCOL.md](./WEBSOCKET_PROTOCOL.md)

---

## 1. 개요

### 1.1 목적

WebSocket을 통한 실시간 음성 스트리밍에서 **수신 루프와 ASR 추론을 분리**하여:
- 네트워크 수신 블로킹 방지
- GPU 리소스 효율적 사용
- 안정적인 백프레셔 처리

### 1.2 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Client (MCP App / Browser Extension)                                    │
│                                                                          │
│  [Microphone] → [20ms chunks] → WebSocket                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  AI Server - WebSocket Handler                                           │
│                                                                          │
│  ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐ │
│  │  Receive Loop    │     │   Audio Queue    │     │   ASR Worker     │ │
│  │                  │     │                  │     │                  │ │
│  │  - Parse JSON    │────▶│  asyncio.Queue   │────▶│  - Buffer mgmt   │ │
│  │  - Decode Base64 │     │  (per session)   │     │  - GPU inference │ │
│  │  - Non-blocking  │     │  max_size=50     │     │  - Result send   │ │
│  └──────────────────┘     └──────────────────┘     └──────────────────┘ │
│           │                                                 │            │
│           │              ┌──────────────────┐               │            │
│           │              │    ASR Lock      │               │            │
│           └─────────────▶│  (GPU serialize) │◀──────────────┘            │
│                          └──────────────────┘                            │
│                                    │                                     │
│                                    ▼                                     │
│                          ┌──────────────────┐                            │
│                          │  Faster-Whisper  │                            │
│                          │  (GPU/CUDA)      │                            │
│                          └──────────────────┘                            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Audio Contract

클라이언트와 서버 간 오디오 포맷 명세입니다.

### 2.1 필수 스펙

| 항목 | 값 | 설명 |
|------|-----|------|
| Sample Rate | 16000 Hz | Whisper 모델 요구사항 |
| Channels | 1 (Mono) | 단일 채널 |
| Bit Depth | 16-bit | Signed Integer |
| Byte Order | Little Endian | PCM 표준 |
| Frame Size | 320 samples | 20ms @ 16kHz |
| Chunk Size | 640 bytes | 320 samples × 2 bytes |

### 2.2 서버 상수

**파일**: [api/websocket.py](../api/websocket.py)

```python
# Audio Contract Constants
AUDIO_SAMPLE_RATE = 16000          # 16kHz (Whisper requirement)
AUDIO_CHANNELS = 1                  # Mono
AUDIO_BIT_DEPTH = 16                # 16-bit signed integer
AUDIO_FRAME_SIZE = 320              # 20ms @ 16kHz (320 samples)
AUDIO_CHUNK_BYTES = 640             # 320 samples * 2 bytes

# Buffer Management
BUFFER_THRESHOLD_BYTES = 32000      # ~1 second of audio (triggers transcription)
BUFFER_OVERLAP_BYTES = 6400         # 200ms overlap for continuity
MAX_BUFFER_SIZE = 320000            # 10 seconds max (memory limit)

# Queue Management
MAX_QUEUE_SIZE = 50                 # Max pending chunks per session
```

### 2.3 클라이언트 구현 예시

```javascript
// JavaScript (Browser)
const audioContext = new AudioContext({ sampleRate: 16000 });
const FRAME_SIZE = 320;  // 20ms

processor.onaudioprocess = (e) => {
  const float32 = e.inputBuffer.getChannelData(0);
  const int16 = new Int16Array(float32.length);

  for (let i = 0; i < float32.length; i++) {
    int16[i] = Math.max(-32768, Math.min(32767, float32[i] * 32768));
  }

  ws.send(JSON.stringify({
    type: "audio_chunk",
    data: {
      audio: btoa(String.fromCharCode(...new Uint8Array(int16.buffer))),
      sample_rate: 16000,
      channels: 1,
      format: "pcm16",
      sequence: sequenceNumber++,
      is_final: false
    }
  }));
};
```

---

## 3. Queue 기반 처리 아키텍처

### 3.1 세션별 리소스

각 WebSocket 연결(세션)마다 독립적인 리소스를 할당합니다.

```python
# Per-session state
self._audio_queues: Dict[str, asyncio.Queue] = {}      # Audio chunk queues
self._audio_buffers: Dict[str, bytes] = {}             # Accumulated audio buffers
self._worker_tasks: Dict[str, asyncio.Task] = {}       # ASR worker tasks
self._chunk_counters: Dict[str, int] = {}              # Received chunk count
self._segment_counters: Dict[str, int] = {}            # Transcription segment count
```

### 3.2 Receive Loop (Non-blocking)

WebSocket 메시지 수신은 빠르게 처리하고 Queue에 전달합니다.

```python
async def _handle_audio_chunk(self, session_id: str, data: dict):
    """Handle incoming audio chunk - fast path to queue."""
    queue = self._audio_queues.get(session_id)
    if not queue:
        return

    chunk = AudioChunk(
        data=base64.b64decode(data.get("audio", "")),
        sequence=data.get("sequence", 0),
        is_final=data.get("is_final", False),
        timestamp=datetime.now()
    )

    # Non-blocking queue put with backpressure handling
    try:
        queue.put_nowait(chunk)
    except asyncio.QueueFull:
        logger.warning(f"Queue full, dropping oldest chunk: {session_id}")
        queue.get_nowait()  # Drop oldest
        queue.put_nowait(chunk)
```

### 3.3 ASR Worker (Per-session)

각 세션마다 독립적인 Worker Task가 Queue를 소비합니다.

```python
async def _asr_worker(self, session_id: str):
    """Background worker that processes audio from queue."""
    queue = self._audio_queues.get(session_id)

    while True:
        try:
            chunk: AudioChunk = await asyncio.wait_for(
                queue.get(),
                timeout=30.0
            )

            # Accumulate buffer
            buffer = self._audio_buffers.get(session_id, b"")
            buffer += chunk.data

            # Check transcription trigger
            should_transcribe = (
                len(buffer) >= BUFFER_THRESHOLD_BYTES or
                chunk.is_final
            )

            if should_transcribe and self.asr.is_ready():
                await self._process_audio_buffer(
                    session_id,
                    buffer,
                    is_final=chunk.is_final
                )

                # Keep overlap for continuity (or clear if final)
                if chunk.is_final:
                    self._audio_buffers[session_id] = b""
                else:
                    self._audio_buffers[session_id] = buffer[-BUFFER_OVERLAP_BYTES:]
            else:
                self._audio_buffers[session_id] = buffer

        except asyncio.TimeoutError:
            continue  # Keep waiting
        except asyncio.CancelledError:
            break  # Clean shutdown
```

---

## 4. GPU 동시성 제어

### 4.1 ASR Lock

단일 GPU에서 여러 세션의 동시 추론을 방지합니다.

```python
# Global ASR lock for GPU serialization
_asr_lock = asyncio.Lock()

async def _process_audio_buffer(self, session_id: str, buffer: bytes, is_final: bool):
    """Process accumulated audio buffer with GPU lock."""

    async with _asr_lock:  # Serialize GPU access
        segment_id = f"seg_{self._segment_counters[session_id]}"
        self._segment_counters[session_id] += 1

        result = await self.asr.transcribe(
            buffer,
            is_final=is_final,
            segment_id=segment_id
        )

    # Send result (outside lock)
    await self._send_asr_result(session_id, result)
```

### 4.2 왜 Lock이 필요한가?

| 문제 | Lock 없을 때 | Lock 있을 때 |
|------|-------------|-------------|
| GPU 메모리 | OOM 위험 | 순차 사용으로 안정 |
| 추론 속도 | 경합으로 느려짐 | 예측 가능한 latency |
| 결과 순서 | 뒤섞임 가능 | 세션별 순서 보장 |

---

## 5. 버퍼링 전략

### 5.1 Fixed Buffer + Overlap

```
Time →
┌────────────────────────────────────────────────────────────┐
│  Audio Stream                                               │
├────────┬────────┬────────┬────────┬────────┬────────┬─────┤
│ chunk1 │ chunk2 │ chunk3 │ chunk4 │ chunk5 │ chunk6 │ ... │
└────────┴────────┴────────┴────────┴────────┴────────┴─────┘

Buffer accumulation:
├─────────────── 1 second (32000 bytes) ───────────────┤
                                                        ↓ Transcribe
                               ├── 200ms overlap ──┤
                               └─────────────────────── Next buffer starts
```

### 5.2 버퍼 크기 선택 근거

| 버퍼 크기 | 장점 | 단점 |
|-----------|------|------|
| 500ms | 낮은 latency | 문맥 부족, 정확도 저하 |
| **1초 (선택)** | 균형잡힌 latency/정확도 | - |
| 2초 | 높은 정확도 | 체감 지연 증가 |
| 5초 | 최고 정확도 | 실시간 부적합 |

### 5.3 Overlap 필요성

발화가 버퍼 경계에서 끊길 때 문맥 손실 방지:

```
Without overlap:
"쿠팡에서 우유" | "검색해줘"  → 두 개의 불완전한 문장

With 200ms overlap:
"쿠팡에서 우유 검" | "유 검색해줘"  → 겹침으로 문맥 연결
```

---

## 6. Backpressure 처리

### 6.1 Queue Full 시나리오

클라이언트가 빠르게 전송하고 서버 처리가 느릴 때:

```python
MAX_QUEUE_SIZE = 50  # ~1초 분량 (20ms × 50)

try:
    queue.put_nowait(chunk)
except asyncio.QueueFull:
    # Strategy: Drop oldest chunk
    logger.warning(f"Queue full, dropping oldest: {session_id}")
    queue.get_nowait()
    queue.put_nowait(chunk)
```

### 6.2 대안 전략

| 전략 | 구현 | 장단점 |
|------|------|--------|
| **Drop Oldest (현재)** | `get_nowait()` 후 `put_nowait()` | 최신 데이터 유지, 일부 손실 |
| Drop Newest | `put_nowait()` 무시 | 구현 간단, 최신 손실 |
| Block | `await queue.put()` | 손실 없음, 지연 누적 |
| Resize | 동적 큐 확장 | 메모리 증가 |

---

## 7. 세션 생명주기

### 7.1 연결 시 초기화

```python
async def _initialize_session(self, session_id: str):
    """Initialize per-session resources."""
    self._audio_queues[session_id] = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)
    self._audio_buffers[session_id] = b""
    self._chunk_counters[session_id] = 0
    self._segment_counters[session_id] = 0

    # Start ASR worker task
    self._worker_tasks[session_id] = asyncio.create_task(
        self._asr_worker(session_id)
    )
```

### 7.2 연결 해제 시 정리

```python
async def _cleanup_session(self, session_id: str):
    """Clean up session resources on disconnect."""
    # Cancel worker task
    if session_id in self._worker_tasks:
        task = self._worker_tasks.pop(session_id)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    # Clear resources
    self._audio_queues.pop(session_id, None)
    self._audio_buffers.pop(session_id, None)
    self._chunk_counters.pop(session_id, None)
    self._segment_counters.pop(session_id, None)
```

---

## 8. 메시지 프로토콜 확장

### 8.1 `audio_chunk` 확장 필드

```json
{
  "type": "audio_chunk",
  "data": {
    "audio": "base64_encoded_pcm16",
    "sample_rate": 16000,
    "channels": 1,
    "format": "pcm16",
    "sequence": 123,
    "is_final": false
  }
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `audio` | string | O | Base64 인코딩된 PCM 데이터 |
| `sample_rate` | int | O | 16000 (고정) |
| `channels` | int | O | 1 (고정) |
| `format` | string | O | "pcm16" |
| `sequence` | int | O | 청크 순서 번호 |
| `is_final` | bool | O | 녹음 종료 시 true |

### 8.2 `asr_result` 확장 필드

```json
{
  "type": "asr_result",
  "data": {
    "text": "쿠팡에서 우유 검색해줘",
    "confidence": 0.95,
    "language": "ko",
    "duration": 2.5,
    "is_final": true,
    "segment_id": "seg_3"
  }
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `text` | string | 인식된 텍스트 |
| `confidence` | float | 언어 감지 신뢰도 (0.0~1.0) |
| `language` | string | 언어 코드 ("ko") |
| `duration` | float | 처리된 오디오 길이 (초) |
| `is_final` | bool | 최종 결과 여부 |
| `segment_id` | string | 세그먼트 식별자 ("seg_N") |

---

## 9. 성능 메트릭

### 9.1 모니터링 지표

| 메트릭 | 측정 방법 | 목표값 |
|--------|----------|--------|
| Queue Depth | `queue.qsize()` | < 30 |
| Buffer Size | `len(buffer)` | < 64KB |
| ASR Latency | 추론 시작~완료 | < 500ms |
| End-to-End | 청크 수신~결과 전송 | < 1.5s |

### 9.2 로깅

```python
logger.debug(f"ASR transcribed: session={session_id}, "
             f"duration={result.duration:.2f}s, "
             f"text={result.text[:50]}...")
```

---

## 10. 향후 개선 계획

| 기능 | 우선순위 | 설명 |
|------|----------|------|
| VAD Integration | High | 발화 경계 자동 감지 |
| Adaptive Buffering | Medium | 네트워크 상태에 따른 버퍼 조절 |
| Multi-GPU | Low | 여러 GPU 간 로드밸런싱 |
| WebRTC | Low | UDP 기반 저지연 전송 |

---

## 11. 참고 자료

- [Faster-Whisper GitHub](https://github.com/SYSTRAN/faster-whisper)
- [asyncio.Queue Documentation](https://docs.python.org/3/library/asyncio-queue.html)
- [WebSocket Backpressure Patterns](https://websockets.readthedocs.io/en/stable/topics/flow-control.html)

---

**문서 버전**: 1.0
**최종 수정일**: 2026-01-21
