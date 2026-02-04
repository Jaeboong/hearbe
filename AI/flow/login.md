# 로그인 Flow

## 개요
로그인 관련 규칙은 CommandGenerator에 등록되어 있지 않고, login.py에 4개의 별도 규칙 클래스가 정의됨.
LoginRule은 로그인 페이지 이동만 처리하고, 로그인 페이지 내 동작(전화번호/OTP/탭전환)은 별도 규칙으로 처리.

## 핵심 포인트
- LoginRule, LoginPhoneRule, LoginPhoneTabRule, LoginOtpRule → 4개 클래스 존재
- CommandGenerator의 규칙 체인에는 미등록 → LLM 폴백 또는 별도 경로로 동작
- 로그인 페이지(get_page_type == "login")에서는 LoginRule.check()가 None 반환
- 로그인 가드(LoginGuard)와 로그인 피드백(LoginFeedback)이 CommandPipeline에서 작동
- 캡차 처리: 로그인 URL이면 CommandPipeline이 handle_captcha_modal 명령을 자동 추가

---

## Flow A: 로그인 페이지 이동 ("로그인 해줘")

```
사용자 입력 ("로그인 해줘")
│
├─ [1] TextRouter → LLMPipelineHandler
│
├─ [2] LLMPlanner.generate_commands()
│   └─ CommandGenerator.generate_rules() → 규칙 체인 순회
│       └─ LoginRule은 CommandGenerator에 미등록
│       └─ GenericClickRule: "클릭/눌러/선택" 키워드 없음 → 미매칭
│       └─ matched_rule="none"
│
│   ※ LoginRule은 CommandGenerator 외부에서 사용되거나 LLM 폴백으로 처리
│   └─ LLM 폴백 → build_login_page_commands()와 유사한 명령 생성
│
├─ [3] 실제 생성되는 명령:
│   └─ goto(url="https://login.coupang.com/...")
│   └─ 폴백: click_text("로그인")
│
├─ [4] CommandPipeline.prepare_commands()
│   └─ current_url에 "login" 포함 시:
│       └─ handle_captcha_modal 명령을 명령 리스트 맨 앞에 추가
│
├─ [5] CommandPipeline.dispatch()
│   ├─ LoginGuard.prepare_guard() → 로그인 보호 검증
│   ├─ LoginFeedback.mark_login_submit_pending() → 로그인 제출 추적
│   └─ sender.send_tool_calls() + send_tts_response()
│
└─ [6] 클라이언트: 로그인 페이지 이동
```

## Flow B: 전화번호 로그인 ("010-1234-5678")

```
사용자 입력 ("010-1234-5678" 또는 "01012345678")
│
├─ login.py → LoginPhoneRule.check()
│   ├─ get_page_type(url) == "login" 확인
│   ├─ _extract_phone_digits(text) → "01012345678"
│   ├─ get_selector(url, "phone_input") → 전화번호 입력칸 셀렉터
│   ├─ get_selector(url, "phone_submit_button") → 인증번호 요청 버튼
│   │
│   └─ 실제 생성되는 명령:
│       ├─ wait_for_selector(phone_input, state="visible", timeout=8000)
│       ├─ fill(selector=phone_input, text="01012345678")
│       ├─ wait_for_selector(submit_button, state="visible", timeout=8000)
│       └─ click(selector=submit_button) → "인증번호 요청"
│
└─ TTS: "휴대폰 번호를 입력하고 인증번호를 요청합니다."
```

## Flow C: 휴대폰 로그인 탭 전환 ("휴대폰 로그인")

```
사용자 입력 ("휴대폰으로 로그인")
│
├─ login.py → LoginPhoneTabRule.check()
│   ├─ get_page_type(url) == "login" 확인
│   ├─ "휴대폰" 키워드 확인
│   ├─ get_selector(url, "tab_phone_login") → 탭 셀렉터
│   │
│   └─ 실제 생성되는 명령:
│       ├─ click(selector=tab_phone_login) → "휴대폰 로그인 탭 전환"
│       └─ wait_for_selector(phone_input, state="visible", timeout=8000)
│
└─ TTS: "휴대폰 로그인 탭으로 전환합니다, 휴대폰 번호를 불러주시면 대신 입력해 드릴게요."
```

## Flow D: OTP 인증번호 입력 ("인증번호 123456")

```
사용자 입력 ("인증번호 123456")
│
├─ login.py → LoginOtpRule.check()
│   ├─ get_page_type(url) == "login" 확인
│   ├─ _extract_otp_code(text) → "123456" (4~8자리)
│   ├─ get_selector(url, "otp_input") → OTP 입력칸 셀렉터
│   │
│   └─ 실제 생성되는 명령:
│       ├─ wait_for_selector(otp_input, state="visible", timeout=8000)
│       ├─ fill(selector=otp_input, text="123456")
│       └─ press(selector=otp_input, key="Enter")
│
└─ TTS: "인증번호를 입력합니다."
```

## Flow E: 로그인 완료 감지

```
로그인 후 페이지 이동 시
│
├─ MCPHandler.handle_mcp_result()
│   └─ previous_url != page_url 감지
│       └─ LoginFeedback.maybe_announce_login_success()
│           └─ 로그인 URL → 비로그인 URL 변경 감지
│               └─ TTS: "로그인에 성공했습니다."
```

---

## 관련 파일 (실제 호출 관계 기준)

| 단계 | 파일 | 역할 |
|------|------|------|
| **로그인 규칙들** | `services/llm/rules/login.py` | LoginRule, LoginPhoneRule, LoginPhoneTabRule, LoginOtpRule |
| 명령 빌더 | `services/llm/context/context_rules.py` | goto, fill, click, press, wait_for_selector 생성 |
| 사이트 매니저 | `services/llm/sites/site_manager.py` | get_page_type(), get_selector() |
| **로그인 가드** | `api/ws/feedback/login_guard.py` | 로그인 안전 검증 |
| **로그인 피드백** | `api/ws/feedback/login_feedback.py` | 로그인 성공/실패 감지 및 피드백 |
| 명령 파이프라인 | `api/ws/handlers/command_pipeline.py` | captcha 핸들러 자동 추가, 로그인 가드 |
| 명령 정규화 | `api/ws/handlers/command_normalizers.py` | normalize_login_phone_commands() |
| TTS 포매팅 | `api/ws/presenter/pages/login.py` | 로그인 안내, 캡차 안내 TTS |
| 캡차 처리 | MCPHandler | handle_captcha_modal 결과 → captcha_found 시 TTS 안내 |
