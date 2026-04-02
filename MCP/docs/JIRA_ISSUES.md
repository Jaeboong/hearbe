# JIRA 이슈 목록

> MCP-01 ~ MCP-09, AI-04 ~ AI-08 작업에 대한 JIRA 이슈 내용

---

## MCP 파트 (Desktop App)

### MCP-01: 음성 녹음

**Title (서브태스크):** `Feat: 음성 녹음`

**설명 (Description):**

사용자는 음성 명령을 입력하기 위해 V키 핫키로 음성 녹음 기능을 사용하고 싶다.

## ✅ 완료 조건
- V키 누름 감지 시 녹음 시작
- V키 뗌 감지 시 녹음 종료  
- 마이크로부터 오디오 캡처 (16kHz, 모노, 16-bit PCM)
- 녹음된 오디오 데이터를 AUDIO_READY 이벤트로 발행
- 핫키 감지 모듈(`audio/hotkey.py`) 구현
- 녹음 처리 모듈(`audio/recorder.py`) 구현

## 💬 기타
- pynput 라이브러리 사용 (핫키 처리)
- pyaudio 라이브러리 사용 (오디오 녹음)
- 이벤트 버스 연동: HOTKEY_PRESSED, RECORDING_STARTED, RECORDING_STOPPED, AUDIO_READY 발행

**Story Point:** 5

**중요도 (Priority):** High

---

### MCP-02: 음성 재생

**Title (서브태스크):** `Feat: 음성 재생`

**설명 (Description):**

사용자는 AI 응답을 듣기 위해 TTS 음성 재생 기능을 사용하고 싶다.

## ✅ 완료 조건
- 서버로부터 TTS 오디오 수신(TTS_AUDIO_RECEIVED 이벤트 구독)
- MP3/WAV 오디오 스피커로 재생
- 재생 완료 후 TTS_PLAYBACK_FINISHED 이벤트 발행
- 오디오 재생 모듈(`audio/player.py`) 구현

## 💬 기타
- pyaudio 라이브러리 사용
- 재생 중 중단 기능 지원

**Story Point:** 3

**중요도 (Priority):** High

---

### MCP-03: 브라우저 실행

**Title (서브태스크):** `Feat: 브라우저 실행`

**설명 (Description):**

사용자는 웹 쇼핑을 위해 Chrome 브라우저 자동 실행 기능을 사용하고 싶다.

## ✅ 완료 조건
- 앱 시작 시 Chrome 브라우저 자동 실행
- CDP(Chrome DevTools Protocol) 모드로 실행 (--remote-debugging-port=9222)
- 사용자 프로필 디렉토리 지정으로 로그인 유지
- CDP WebSocket URL 획득
- BROWSER_READY 이벤트 발행 (cdp_url, process_id 포함)
- Chrome 실행 모듈(`browser/launcher.py`) 구현

## 💬 기타
- psutil 라이브러리로 프로세스 관리
- 실행 실패 시 에러 처리 및 재시도 로직
- 추후 자사 웹사이트로 자동 리다이렉트 기능 추가 예정

**Story Point:** 5

**중요도 (Priority):** High

---

### MCP-04: 브라우저 제어

**Title (서브태스크):** `Feat: 브라우저 제어`

**설명 (Description):**

사용자는 음성 명령으로 웹 페이지를 조작하기 위해 브라우저 자동화 기능을 사용하고 싶다.

## ✅ 완료 조건
- Playwright를 통해 CDP 연결된 Chrome 제어
- MCP 도구 6개 구현: navigate_to_url, click_element, fill_input, get_text, take_screenshot, scroll
- MCP_TOOL_CALL 이벤트 구독 및 도구 실행
- 실행 결과를 MCP_RESULT 이벤트로 발행
- 브라우저 도구 모듈(`mcp/tools.py`) 구현
- MCP 핸들러 모듈(`mcp/handler.py`) 구현

## 💬 기타
- Playwright Python 라이브러리 사용
- 각 도구별 에러 처리 및 타임아웃 설정
- CSS 선택자 기반 요소 조작

**Story Point:** 8

**중요도 (Priority):** High

---

### MCP-05: 서버 통신

**Title (서브태스크):** `Feat: 서버 통신`

**설명 (Description):**

사용자는 실시간 음성 쇼핑 서비스를 이용하기 위해 AI 서버와의 WebSocket 통신 기능을 사용하고 싶다.

## ✅ 완료 조건
- 앱 시작 시 WebSocket 연결 수립
- 오디오 데이터 서버로 전송(audio_chunk 메시지)
- 서버 메시지 수신: stt_result, llm_command, tool_call, tts_audio, flow_step
- 각 메시지 타입별 이벤트 발행
- 연결 끊김 시 자동 재연결 로직
- WebSocket 클라이언트 모듈(`network/ws_client.py`) 구현

## 💬 기타
- websockets 라이브러리 사용
- JSON 메시지 포맷
- 재연결 최대 시도 횟수 설정 (환경변수)

**Story Point:** 8

**중요도 (Priority):** High

---

### MCP-06: 세션 관리

**Title (서브태스크):** `Feat: 세션 관리`

**설명 (Description):**

사용자는 쇼핑 맥락을 유지하기 위해 세션 상태 추적 기능을 사용하고 싶다.

## ✅ 완료 조건
- 현재 쇼핑 세션 상태 추적 (사이트, 작업, 쿼리, 플로우)
- 주요 이벤트 구독하여 상태 자동 업데이트
- 상태 변경 시 SESSION_UPDATED 이벤트 발행
- 선택적 파일 저장 기능 (session.json)
- 세션 관리 모듈(`session/state_manager.py`) 구현

## 💬 기타
- 세션 데이터: session_id, current_site, current_task, last_query, flow
- 구독 이벤트: RECORDING_STARTED, STT_RESULT_RECEIVED, LLM_COMMAND_RECEIVED, TTS_PLAYBACK_FINISHED

**Story Point:** 5

**중요도 (Priority):** Medium

---

### MCP-07: 상태 표시

**Title (서브태스크):** `Feat: 상태 표시`

**설명 (Description):**

사용자는 앱 동작 상태를 확인하기 위해 최소 UI 표시 기능을 사용하고 싶다.

## ✅ 완료 조건
- tkinter 기반 최소 창 표시 (300x150 px)
- 우측 하단 위치, 항상 최상위 표시
- 상태별 텍스트 업데이트: 대기중, 녹음중, 처리중, 재생중, 오류
- 이벤트에 따른 실시간 상태 변경
- UI 관리자 모듈(`ui/ui_manager.py`) 개선
- 미니 창 모듈(`ui/mini_window.py`) 개선

## 💬 기타
- 이미 구현되어 있지만 상태 표시 기능 보완 필요
- 구독 이벤트: RECORDING_STARTED, RECORDING_STOPPED, TTS_AUDIO_RECEIVED, TTS_PLAYBACK_FINISHED, ERROR_OCCURRED

**Story Point:** 3

**중요도 (Priority):** Low

---

### MCP-08: 텍스트 입력 (테스트용)

**Title (서브태스크):** `Feat: 텍스트 입력 테스트 기능`

**설명 (Description):**

개발자는 음성 녹음 없이 빠른 테스트를 위해 콘솔 텍스트 입력 기능을 사용하고 싶다.

## ✅ 완료 조건
- 콘솔에서 텍스트 입력 받기
- 입력된 텍스트를 TEXT_INPUT_READY 이벤트로 발행
- 네트워크 모듈에서 text_input 메시지로 서버 전송
- --console 플래그로 활성화
- 콘솔 입력 모듈(`debug/console_input.py`) 구현 (이미 완료)

## 💬 기타
- 개발/디버깅 목적 기능
- STT 과정 생략하여 빠른 테스트 가능

**Story Point:** 1

**중요도 (Priority):** Low

---

### MCP-09: WS 게이트웨이

**Title (서브태스크):** `Feat: WS 게이트웨이`

**설명 (Description):**

사용자는 안정적인 실시간 통신을 위해 WebSocket 세션 관리 및 재연결 정책을 사용하고 싶다.

## ✅ 완료 조건
- WebSocket 연결 시 세션 생성 (session_id 발급)
- 세션 별 상태 관리 (연결/해제, 마지막 활동 시간)
- 주기적인 상태(status) 메시지 송수신 (heartbeat)
- 연결 끊김 감지 및 자동 재연결 정책
- 재연결 시 세션 복구 로직
- 타임아웃 및 재시도 횟수 제한
- WebSocket 게이트웨이 모듈(`network/ws_gateway.py`) 구현

## 💬 기타
- 세션 타임아웃: 30분 비활성 시 종료
- Heartbeat 주기: 30초마다 ping/pong
- 재연결 최대 시도: 10회 (지수 백오프)
- 세션 상태: connected, disconnected, reconnecting

**Story Point:** 5

**중요도 (Priority):** High

---

## AI 파트 (AI Server)

### AI-04: STT 서비스 구현

**Title (서브태스크):** `Feat: STT 서비스`

**설명 (Description):**

사용자는 음성 명령을 텍스트로 변환하기 위해 실시간 음성 인식 기능을 사용하고 싶다.

## ✅ 완료 조건
- Faster-Whisper(turbo) 모델 통합
- WebSocket으로 오디오 청크 실시간 수신
- 한국어 음성 → 텍스트 변환
- 변환 결과를 stt_result 메시지로 전송
- ASR 서비스 모듈 구현

## 💬 기타
- GPU 가속 지원
- 쇼핑 관련 용어 최적화
- 신뢰도(confidence) 값 포함

**Story Point:** 8

**중요도 (Priority):** High

---

### AI-05: LLM 명령 생성 서비스

**Title (서브태스크):** `Feat: LLM 명령 생성`

**설명 (Description):**

사용자는 자연어 명령을 브라우저 조작 명령으로 변환하기 위해 LLM Planner 기능을 사용하고 싶다.

## ✅ 완료 조건
- GPT-4o-mini 모델 통합
- 사용자 발화 의도 분석 (NLU)
- 개체명 인식 (상품명, 브랜드, 가격 등)
- 자연어 → MCP 도구 호출 변환
- tool_call 메시지 생성 및 전송
- 일반 명령 vs 플로우 엔진 위임 판단
- LLM Planner 모듈 구현

## 💬 기타
- 대화 맥락 유지
- 대명사 참조 해석 ("아까 그거", "방금 본 거")
- 플로우 필요 시 Flow Engine으로 위임

**Story Point:** 13

**중요도 (Priority):** High

---

### AI-06: TTS 서비스 구현

**Title (서브태스크):** `Feat: TTS 서비스`

**설명 (Description):**

사용자는 AI 응답을 음성으로 듣기 위해 실시간 음성 합성 기능을 사용하고 싶다.

## ✅ 완료 조건
- TTS 모델 통합 (ElevenLabs Flash v2.5 또는 MiniMax Speech-02)
- 텍스트 → 음성 변환
- 음성 청크 실시간 스트리밍
- tts_chunk/tts_audio 메시지로 전송
- 카테고리별 상품 정보 요약 안내
- TTS 서비스 모듈 구현

## 💬 기타
- 개발: MiniMax (저렴, 한국어 품질 우수)
- 프로덕션: ElevenLabs (저지연 ~75ms)
- 스트리밍으로 응답 지연 최소화

**Story Point:** 5

**중요도 (Priority):** High

---

### AI-07: Flow Engine 구현

**Title (서브태스크):** `Feat: 쇼핑 플로우 엔진`

**설명 (Description):**

사용자는 복잡한 작업(회원가입, 결제)을 단계별로 진행하기 위해 플로우 엔진 기능을 사용하고 싶다.

## ✅ 완료 조건
- 사이트별 플로우 시나리오 정의 (쿠팡, 네이버, 11번가)
- 플로우 타입: signup, checkout
- 각 단계별 prompt, required_fields, action, validation 정의
- flow_step 메시지 전송
- 결제 안전 확인 로직 (Policy/Guard)
- 최종 확인 단계 필수 삽입
- Flow Engine 모듈 구현

## 💬 기타
- 단계별 TTS 안내
- 민감정보는 로컬 입력만 허용
- Backend 서버와 연동하여 플로우 DB 조회

**Story Point:** 13

**중요도 (Priority):** Medium

---

### AI-08: WebSocket Gateway 구현

**Title (서브태스크):** `Feat: WebSocket Gateway`

**설명 (Description):**

사용자는 실시간 양방향 통신을 위해 WebSocket 서버 기능을 사용하고 싶다.

## ✅ 완료 조건
- FastAPI WebSocket 엔드포인트 구현
- 메시지 타입별 라우팅 (audio_chunk, text_input, mcp_result)
- 세션 관리 (연결/해제, 세션 ID)
- ASR, LLM, TTS 서비스 연동
- 에러 처리 및 재연결 지원
- WebSocket Gateway 모듈 구현

## 💬 기타
- 메시지 포맷: JSON
- 연결 상태 모니터링
- 로깅 및 디버깅

**Story Point:** 8

**중요도 (Priority):** High

---

## 요약

### MCP 파트 Story Points 합계
- MCP-01: 5
- MCP-02: 3
- MCP-03: 5
- MCP-04: 8
- MCP-05: 8
- MCP-06: 5
- MCP-07: 3
- MCP-08: 1
- MCP-09: 5
**Total: 43 포인트**

### AI 파트 Story Points 합계
- AI-04: 8
- AI-05: 13
- AI-06: 5
- AI-07: 13
- AI-08: 8
**Total: 47 포인트**

### 중요도 분류
**High Priority:**
- MCP-01, MCP-02, MCP-03, MCP-04, MCP-05, MCP-09
- AI-04, AI-05, AI-06, AI-08

**Medium Priority:**
- MCP-06
- AI-07

**Low Priority:**
- MCP-07, MCP-08

