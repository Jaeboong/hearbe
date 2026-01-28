# 팀 역할 분담 및 개발 일정

> MCP 데스크탑 앱 2인 개발 계획 (3주)

## 👥 팀 구성

**총 인원**: 2명
**개발 기간**: 3주 (15 영업일)
**협업 방식**: 모듈별 폴더 완전 분리 + 이벤트 기반 통신

---

## 📋 역할 분담

### 👤 담당자 김민찬: UI & Audio & Session (사용자 인터페이스)

**핵심 역할**: 사용자와 직접 상호작용하는 모든 기능

**담당 모듈**:
- ✅ `ui/` - 사용자 인터페이스 (완료)
- 🔴 `audio/` - 음성 녹음/재생
- 🔴 `network/ws_client.py` - WebSocket 통신
- 🔴 `session/` - 세션 관리

**구현 파일**:
```
✅ ui/mini_window.py           (완료)
✅ ui/ui_manager.py            (완료)
□  ui/tray_icon.py             (선택 사항)
□  audio/hotkey.py             (V키 핫키 감지)
□  audio/recorder.py           (마이크 녹음)
□  audio/player.py             (TTS 재생)
□  network/ws_client.py        (WebSocket 클라이언트)
□  session/state_manager.py   (세션 상태 관리)
```

**필요 기술 스택**:
- Python GUI: `tkinter`, `pystray`
- 오디오: `pyaudio`
- 핫키: `pynput` 또는 `keyboard`
- 비동기 통신: `asyncio`, `websockets`

**예상 작업량**: 약 35시간

---

### 👤 담당자 김재환: Browser & MCP & Auth (브라우저 자동화)

**핵심 역할**: 브라우저 제어 및 MCP 서버 관리

**담당 모듈**:
- 🔴 `browser/` - Chrome 실행 및 제어
- 🔴 `mcp/` - MCP 서버 및 Playwright 도구
- 🔴 `network/auth.py` - OAuth 인증

**구현 파일**:
```
□  browser/launcher.py              (Chrome 실행)
□  browser/cdp_client.py            (CDP 연결)
□  mcp/server_manager.py            (MCP 서버 프로세스 관리)
□  mcp/playwright_mcp_server.py    (Playwright 도구 구현)
□  mcp/client.py                    (MCP 클라이언트)
□  network/auth.py                  (OAuth 인증 처리)
```

**필요 기술 스택**:
- 브라우저 자동화: `playwright`
- 프로토콜: Chrome DevTools Protocol (CDP)
- 프로세스 관리: `subprocess`, `psutil`
- MCP: Model Context Protocol SDK
- 인증: OAuth 2.0

**예상 작업량**: 약 56시간

---

## 📅 3주 개발 일정

### Week 1: 핵심 모듈 구현 (5일)

#### 담당자 A 작업 (Week 1)

| 일차 | 작업 | 파일 | 예상 시간 | 상태 |
|------|------|------|-----------|------|
| 1일 | 환경 설정 & 핫키 구현 | audio/hotkey.py | 4h | □ |
| 2일 | 오디오 녹음 구현 (1/2) | audio/recorder.py | 4h | □ |
| 3일 | 오디오 녹음 구현 (2/2) | audio/recorder.py | 4h | □ |
| 4일 | TTS 재생 구현 | audio/player.py | 4h | □ |
| 5일 | Audio 모듈 테스트 | audio/tests/ | 4h | □ |

**Week 1 목표**: Audio 모듈 완성 (V키 → 녹음 → 재생)

---

#### 담당자 B 작업 (Week 1)

| 일차 | 작업 | 파일 | 예상 시간 | 상태 |
|------|------|------|-----------|------|
| 1일 | 환경 설정 & Chrome 실행 | browser/launcher.py | 4h | □ |
| 2일 | CDP 연결 구현 (1/2) | browser/cdp_client.py | 6h | □ |
| 3일 | CDP 연결 구현 (2/2) | browser/cdp_client.py | 6h | □ |
| 4일 | MCP 서버 관리 구현 | mcp/server_manager.py | 4h | □ |
| 5일 | Browser 모듈 테스트 | browser/tests/ | 4h | □ |

**Week 1 목표**: Browser 모듈 완성 (Chrome 실행 → CDP 연결)

---

### Week 2: 고급 기능 구현 (5일)

#### 담당자 A 작업 (Week 2)

| 일차 | 작업 | 파일 | 예상 시간 | 상태 |
|------|------|------|-----------|------|
| 1일 | WebSocket 클라이언트 (1/3) | network/ws_client.py | 4h | □ |
| 2일 | WebSocket 클라이언트 (2/3) | network/ws_client.py | 4h | □ |
| 3일 | WebSocket 클라이언트 (3/3) | network/ws_client.py | 4h | □ |
| 4일 | 세션 관리 구현 | session/state_manager.py | 4h | □ |
| 5일 | Network & Session 테스트 | tests/ | 4h | □ |

**Week 2 목표**: 서버 통신 완성 (WebSocket + 세션 관리)

---

#### 담당자 B 작업 (Week 2)

| 일차 | 작업 | 파일 | 예상 시간 | 상태 |
|------|------|------|-----------|------|
| 1일 | Playwright 도구 (1/4) | mcp/playwright_mcp_server.py | 6h | □ |
| 2일 | Playwright 도구 (2/4) | mcp/playwright_mcp_server.py | 6h | □ |
| 3일 | Playwright 도구 (3/4) | mcp/playwright_mcp_server.py | 6h | □ |
| 4일 | Playwright 도구 (4/4) | mcp/playwright_mcp_server.py | 4h | □ |
| 5일 | MCP 클라이언트 & OAuth | mcp/client.py, network/auth.py | 6h | □ |

**Week 2 목표**: MCP 완성 (Playwright 도구 + 클라이언트)

---

### Week 3: 통합 및 테스트 (5일)

#### 공동 작업 (Week 3)

| 일차 | 작업 | 담당 | 예상 시간 | 상태 |
|------|------|------|-----------|------|
| 1일 | main.py 통합 | A + B | 4h | □ |
| 1일 | 초기화 순서 테스트 | A + B | 4h | □ |
| 2일 | 전체 플로우 테스트 | A + B | 8h | □ |
| 3일 | 버그 수정 (1) | A + B | 8h | □ |
| 4일 | 버그 수정 (2) | A + B | 8h | □ |
| 5일 | 최종 테스트 & 문서화 | A + B | 8h | □ |

**Week 3 목표**: 완전한 앱 통합 및 배포 준비

---

## 📊 작업량 분석

### 담당자 A (총 35시간)

| 모듈 | 예상 시간 | 난이도 | 비중 |
|------|-----------|--------|------|
| UI | 0h (완료) | ⭐⭐ | 0% |
| Audio | 16h | ⭐⭐⭐ | 46% |
| Network | 12h | ⭐⭐⭐ | 34% |
| Session | 6h | ⭐⭐ | 17% |
| 테스트 | 8h | - | - |
| **총계** | **35h + 8h** | - | 100% |

---

### 담당자 B (총 56시간)

| 모듈 | 예상 시간 | 난이도 | 비중 |
|------|-----------|--------|------|
| Browser | 20h | ⭐⭐⭐⭐ | 36% |
| MCP | 30h | ⭐⭐⭐⭐⭐ | 54% |
| Auth | 4h | ⭐⭐ | 7% |
| 테스트 | 8h | - | - |
| **총계** | **56h + 8h** | - | 100% |

**참고**: 담당자 B의 작업량이 더 많지만, 난이도가 높은 만큼 기술적 성장 기회도 큽니다.

---

## 🔄 협업 프로세스

### 매일 (Daily)

#### 아침 스탠드업 (10분)
- **시간**: 오전 10시
- **형식**: Slack/Discord 또는 대면
- **내용**:
  - 어제 한 일
  - 오늘 할 일
  - 블로커/이슈

#### 저녁 동기화 (5분)
- **시간**: 오후 6시
- **형식**: 간단한 메시지
- **내용**: 진행 상황 공유

---

### 주 2회 (화요일, 목요일)

#### 코드 리뷰 세션 (30분)
- **시간**: 오후 4시
- **형식**: 화면 공유 또는 PR 리뷰
- **내용**:
  - 서로의 코드 리뷰
  - 이벤트 연동 확인
  - 아키텍처 논의

---

### 주 1회 (금요일)

#### 주간 회고 (1시간)
- **시간**: 오후 5시
- **형식**: 대면 또는 화상
- **내용**:
  - 이번 주 성과
  - 다음 주 계획
  - 개선 사항

---

## 🚨 중요 규칙

### 1. Git 커밋 전 체크리스트
```
□ 내 담당 폴더 내에서만 수정했는가?
□ core/ 폴더를 수정했다면 상대방에게 알렸는가?
□ 새로운 이벤트를 추가했다면 EVENT_SPECIFICATION.md를 업데이트했는가?
□ 환경 변수를 추가했다면 ENV_SPECIFICATION.md를 업데이트했는가?
□ 테스트 코드를 작성했는가?
```

### 2. 공통 파일 수정 규칙

**core/ 폴더 수정 시**:
1. Slack/Discord에 먼저 공지
2. 상대방의 승인 후 수정
3. 즉시 PR 생성하여 리뷰 요청

**main.py 수정 시**:
- Week 3 통합 단계에서만 수정
- 두 사람이 함께 수정

### 3. 이벤트 추가 규칙

새로운 이벤트 타입 필요 시:
1. `core/event_bus.py`의 `EventType` enum에 추가
2. `docs/EVENT_SPECIFICATION.md`에 명세 추가
3. Slack/Discord에 공지

---

## 📞 의사소통 채널

### 실시간 질문
- **채널**: Slack/Discord
- **응답 시간**: 30분 이내

### 긴급 이슈
- **채널**: 전화 또는 화상 회의
- **대상**: 블로커, 아키텍처 변경

### 코드 리뷰
- **채널**: GitHub PR 코멘트
- **응답 시간**: 24시간 이내

---

## 🎯 마일스톤

### Week 1 마일스톤 (Day 5)
- [ ] 담당자 A: Audio 모듈 단위 테스트 통과
- [ ] 담당자 B: Browser 모듈 단위 테스트 통과
- [ ] V키 눌렀을 때 녹음 가능 (A)
- [ ] Chrome 실행 및 CDP 연결 확인 (B)

**확인 방법**:
```bash
# 담당자 A
pytest audio/tests/

# 담당자 B
pytest browser/tests/
```

---

### Week 2 마일스톤 (Day 10)
- [ ] 담당자 A: WebSocket 서버 연결 성공
- [ ] 담당자 B: MCP 서버 실행 및 도구 호출 성공
- [ ] 오디오 데이터를 서버로 전송 가능 (A)
- [ ] Playwright로 브라우저 자동화 가능 (B)

**확인 방법**:
```bash
# 담당자 A
python -m network.ws_client  # 연결 테스트

# 담당자 B
python -m mcp.playwright_mcp_server  # 서버 실행
```

---

### Week 3 마일스톤 (Day 15)
- [ ] main.py 통합 완료
- [ ] 전체 플로우 테스트 통과:
  - V키 → 녹음 → 서버 전송 → MCP 실행 → TTS 재생
- [ ] 버그 수정 완료
- [ ] 문서 업데이트 완료

**최종 확인**:
```bash
python main.py
# 1. UI 창 표시
# 2. V키 눌러 음성 명령
# 3. 브라우저 자동 실행 및 동작
# 4. TTS 음성 재생
# 5. 정상 종료
```

---

## 📈 진행 상황 추적

### GitHub Projects 또는 Notion 보드 사용

#### 컬럼 구성:
```
📋 To Do  →  🏗 In Progress  →  👀 Review  →  ✅ Done
```

#### 각 작업을 Issue로 생성:
```markdown
# 예시 Issue
Title: [A] Audio 핫키 구현
Assignee: 담당자 A
Labels: audio, week1
Description:
- [ ] pynput 라이브러리 조사
- [ ] V키 감지 코드 작성
- [ ] HOTKEY_PRESSED 이벤트 발행
- [ ] 단위 테스트 작성
```

---

## 🔍 주간 점검 체크리스트

### Week 1 종료 시
```
담당자 A:
□ audio/hotkey.py 완성
□ audio/recorder.py 완성
□ audio/player.py 완성
□ 단위 테스트 통과
□ EVENT_SPECIFICATION.md 확인

담당자 B:
□ browser/launcher.py 완성
□ browser/cdp_client.py 완성
□ mcp/server_manager.py 완성
□ 단위 테스트 통과
□ Chrome 실행 확인
```

### Week 2 종료 시
```
담당자 A:
□ network/ws_client.py 완성
□ session/state_manager.py 완성
□ WebSocket 연결 테스트 통과
□ 서버와 통신 확인

담당자 B:
□ mcp/playwright_mcp_server.py 완성
□ mcp/client.py 완성
□ network/auth.py 완성
□ MCP 도구 실행 확인
```

### Week 3 종료 시
```
공동:
□ main.py 통합 완료
□ 전체 플로우 테스트 통과
□ 버그 수정 완료
□ 문서 업데이트 완료
□ .exe 빌드 성공 (선택)
```

---

## 🎓 학습 리소스

### 담당자 A 추천 자료
- PyAudio 튜토리얼: https://people.csail.mit.edu/hubert/pyaudio/
- WebSocket 가이드: https://websockets.readthedocs.io/
- pynput 문서: https://pynput.readthedocs.io/

### 담당자 B 추천 자료
- Playwright Python: https://playwright.dev/python/
- Chrome DevTools Protocol: https://chromedevtools.github.io/devtools-protocol/
- MCP 공식 문서: https://modelcontextprotocol.io/

---

## 📝 참고 문서

- [이벤트 명세서](EVENT_SPECIFICATION.md)
- [모듈 통합 가이드](INTEGRATION_GUIDE.md)
- [환경 변수 명세서](ENV_SPECIFICATION.md)
- [클라이언트 설정 가이드](MCP_CLIENT_SETUP_GUIDE.md)
- [프로젝트 README](../README.md)

---

## 🚀 시작하기

### 1. 환경 설정 (첫 날)
```bash
# 저장소 클론
git clone <repository-url>
cd MCP

# 가상 환경 생성
python -m venv venv
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# Playwright 설치 (담당자 B만)
playwright install chromium

# .env 파일 생성
cp .env.example .env
```

### 2. 브랜치 생성
```bash
# 담당자 A
git checkout -b feature/audio-module

# 담당자 B
git checkout -b feature/browser-module
```

### 3. 개발 시작
각자 담당 모듈 폴더에서 작업 시작!

---

**문서 버전**: 1.0
**작성일**: 2026-01-14
**다음 업데이트**: Week 1 종료 후
