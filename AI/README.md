1. 데스크탑 앱 실행 → 로컬 콜백 서버(예: http://127.0.0.1:port/callback) 열기
2. 앱이 자사 로그인 URL을 브라우저로 오픈
3. 사용자 로그인 완료 → 서버가 **리다이렉트**로 앱 로컬 콜백에 auth_code 전달
4. 앱이 auth_code를 서버로 전송(HTTP) → access/refresh 토큰 발급
5. 앱이 WebSocket 연결 → 세션 생성
6. V 키 → 오디오 스트림 전송(WS) → STT → 텍스트 반환
7. 서버 LLM(GPT‑5‑mini)로 명령 생성
8. “일반 명령”이면 바로 MCP 실행 결과 수신
9. “회원가입/결제 플로우”면 **사이트별 플로우 엔진**이 단계별로 진행
10. 각 단계마다 TTS 안내(빈 칸/필수정보/확인)
11. 결제 인증: 사용자 유형별 분기
    - 시각장애인 카드: 음성 기반/대체 인증
    - 일반 사용자: 직접 2차 비밀번호 입력(로컬)
12. 완료/실패 결과를 TTS로 안내

---

**서버 시스템 아키텍처(모듈 구조)**

- **API Service (HTTP)**
    - /auth/login (로그인 시작)
    - /auth/callback (로컬 콜백용)
    - /auth/token (code → access/refresh)
    - /auth/refresh
- **WebSocket Gateway**
    - 오디오 스트림 수신
    - STT 결과/LLM 명령/TTS 음성 전송
- **Session Manager**
    - 사용자 세션 상태, 현재 사이트, 진행 중 플로우 저장
- **ASR Service (HF 모델)**
    - 스트리밍/버퍼링 처리
- **LLM Planner (GPT‑5‑mini)**
    - 일반 명령 생성
    - 플로우 엔진으로 위임 판단(회원가입/결제)
- **Flow Engine**
    - 사이트별 플로우 정의(쿠팡/네이버/11번가 등)
    - 단계별 질문/확인/폼 채우기 로직
- **TTS Service (HF 모델)**
    - 음성 합성
- **Policy/Guard**
    - 결제/회원가입은 “확인 단계” 삽입
    - 민감 입력은 로컬에서만 처리하도록 강제

---

**플로우 엔진 설계 개념**

- flow_type: signup | checkout
- site: coupang | naver | …
- steps: 순서형 상태 머신
- 각 step은:
    - prompt(TTS 안내 문구)
    - required_fields
    - action(MCP 호출)
    - validation(성공/실패 판단)
    - fallback(다음 안내)

---

**통신 구조(HTTP + WS)**

- HTTP: 인증/토큰 갱신/헬스체크
- WS: 오디오 업로드, STT 결과, LLM 명령, TTS 음성
- 메시지 타입 예시:
    - audio_chunk
    - stt_result
    - tool_calls
    - flow_step
    - tts_audio
    - status

---

**보안/프라이버시**

- 음성 데이터 저장 없음
- 결제/2차 비밀번호는 로컬 입력만 허용
- 토큰은 단기 access + refresh 로테이션