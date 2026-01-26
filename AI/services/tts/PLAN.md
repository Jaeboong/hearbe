# Google Cloud TTS Chirp 구현 계획

## 개요
Google Cloud Text-to-Speech API의 Chirp 모델을 사용한 TTS 서비스 구현

---

## 1. Google Cloud TTS Chirp 모델 정보

### Chirp 모델 종류
| 모델 | 설명 | 특징 |
|------|------|------|
| `chirp_2` | Chirp 2 (최신) | 가장 자연스러운 음성, 32개 언어 지원 |
| `chirp` | Chirp 1 | 기본 Chirp 모델 |

### 한국어 음성 코드
- `ko-KR-Chirp-HD-D` (여성)
- `ko-KR-Chirp-HD-F` (여성)
- `ko-KR-Chirp-HD-O` (남성)

### 지원 오디오 형식
- `LINEAR16` (PCM 16-bit) - 실시간 스트리밍에 적합
- `MP3` - 파일 저장에 적합
- `OGG_OPUS` - 웹 스트리밍에 적합

---

## 2. 구현 작업 목록

### 2.1 의존성 추가
- [ ] `requirements.txt`에 `google-cloud-texttospeech>=2.16.0` 추가

### 2.2 설정 수정
- [ ] `core/config.py` - TTSConfig에 Google Cloud 관련 설정 추가
  - `provider: "google"` 옵션 추가
  - `google_project_id` 필드
  - `google_credentials_path` 필드 (서비스 계정 JSON)

- [ ] `.env.example` 업데이트
  ```env
  TTS_PROVIDER=google
  GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
  GOOGLE_PROJECT_ID=your-project-id
  TTS_GOOGLE_VOICE=ko-KR-Chirp-HD-D
  TTS_GOOGLE_MODEL=chirp_2
  ```

### 2.3 TTS 서비스 구현 (`services/tts/service.py`)

```
수정할 메서드:
├── __init__()        # Google Cloud 클라이언트 설정 추가
├── initialize()      # _init_google() 호출 분기 추가
├── _init_google()    # [신규] Google Cloud TTS 클라이언트 초기화
├── synthesize()      # _synthesize_google() 호출 분기 추가
├── _synthesize_google()     # [신규] 텍스트 → 음성 변환
├── synthesize_stream()      # _stream_google() 호출 분기 추가
├── _stream_google()         # [신규] 스트리밍 TTS
└── get_voice_list()         # Google 음성 목록 추가
```

### 2.4 상세 구현 사항

#### A. 클라이언트 초기화 (`_init_google`)
```python
from google.cloud import texttospeech_v1 as texttospeech

async def _init_google(self):
    # 인증: GOOGLE_APPLICATION_CREDENTIALS 환경변수 또는 명시적 경로
    self._client = texttospeech.TextToSpeechAsyncClient()
```

#### B. 일반 합성 (`_synthesize_google`)
```python
async def _synthesize_google(self, text: str) -> bytes:
    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="ko-KR",
        name=self._config.voice_id,  # ko-KR-Chirp-HD-D
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        sample_rate_hertz=self._config.sample_rate,
    )

    response = await self._client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config,
    )

    return response.audio_content
```

#### C. 스트리밍 합성 (`_stream_google`)
```python
async def _stream_google(self, text: str) -> AsyncGenerator[TTSChunk, None]:
    # Google Cloud TTS는 Streaming Synthesis API 지원
    streaming_config = texttospeech.StreamingSynthesizeConfig(
        voice=texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name=self._config.voice_id,
        ),
    )

    # StreamingSynthesizeRequest 스트림 생성
    async for audio_chunk in self._client.streaming_synthesize(...):
        yield TTSChunk(
            audio_data=audio_chunk.audio_content,
            is_final=False,
            sample_rate=self._config.sample_rate,
            format="pcm"
        )
```

---

## 3. 테스트 계획

### 3.1 단위 테스트 (`tests/test_tts_google.py`)
```python
# 테스트 케이스
- test_google_tts_init()           # 초기화 테스트
- test_google_synthesize()         # 기본 합성 테스트
- test_google_synthesize_stream()  # 스트리밍 테스트
- test_google_korean_voice()       # 한국어 음성 테스트
- test_google_error_handling()     # 에러 처리 테스트
```

### 3.2 수동 테스트 스크립트 (`services/tts/test_google_tts.py`)
```python
# 간단한 테스트 스크립트
async def main():
    tts = TTSService()
    await tts.initialize()

    # 테스트 문장
    audio = await tts.synthesize("안녕하세요, 상품을 검색해드리겠습니다.")

    # WAV 파일로 저장
    with open("test_output.wav", "wb") as f:
        f.write(audio)
```

---

## 4. 파일 변경 목록

| 파일 | 변경 유형 | 설명 |
|------|----------|------|
| `requirements.txt` | 수정 | google-cloud-texttospeech 추가 |
| `core/config.py` | 수정 | TTSConfig에 Google 관련 필드 추가 |
| `.env.example` | 수정 | Google Cloud 환경변수 추가 |
| `services/tts/service.py` | 수정 | Google TTS 구현 추가 |
| `services/tts/test_google_tts.py` | 신규 | 테스트 스크립트 |
| `tests/test_tts_google.py` | 신규 | 단위 테스트 |

---

## 5. Google Cloud 설정 가이드

### 5.1 사전 준비
1. Google Cloud Console에서 프로젝트 생성
2. Text-to-Speech API 활성화
3. 서비스 계정 생성 및 JSON 키 다운로드

### 5.2 인증 설정
```bash
# 방법 1: 환경변수 설정
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"

# 방법 2: .env 파일에 설정
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### 5.3 비용
- Chirp 모델: $16 / 1백만 문자 (표준 음성 대비 약간 높음)
- 월 무료 할당량: 1백만 문자

---

## 6. 구현 순서

```
1단계: 의존성 및 설정 추가
       ├── requirements.txt 수정
       ├── core/config.py TTSConfig 수정
       └── .env.example 업데이트

2단계: 기본 TTS 구현
       ├── _init_google() 구현
       └── _synthesize_google() 구현

3단계: 스트리밍 TTS 구현
       └── _stream_google() 구현

4단계: 테스트
       ├── 단위 테스트 작성
       └── 수동 테스트 실행

5단계: WebSocket 연동 테스트
       └── 전체 파이프라인 테스트 (LLM → TTS → 클라이언트)
```

---

## 7. 참고 자료

- [Google Cloud TTS 문서](https://cloud.google.com/text-to-speech/docs)
- [Chirp 2 소개](https://cloud.google.com/text-to-speech/docs/chirp)
- [Python 클라이언트 라이브러리](https://cloud.google.com/python/docs/reference/texttospeech/latest)
- [스트리밍 합성 가이드](https://cloud.google.com/text-to-speech/docs/streaming-synthesis)
