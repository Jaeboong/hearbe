# 포팅 매뉴얼 준비 문서 (정리용 초안)

- 작성일: 2026-02-08
- 제출 마감: 2026-02-09 12:00 (월)
- 대상 저장 위치: `S14P11D108/exec`
- 문서 목적: 포팅 매뉴얼 작성 전에 "필요 파일/기능/외부연동/계정정보"를 한 번에 정리

## 1) 제출 요구사항 체크리스트

- [x] `exec` 폴더 생성 및 문서 업로드
- [x] Git Clone 이후 빌드/배포 절차 문서화
- [x] JVM/웹서버/WAS/IDE 버전 기재
- [x] 빌드/실행 환경변수 상세 기재
- [x] 배포 시 특이사항 기재
- [x] DB 접속 정보 및 주요 계정/프로퍼티 파일 목록 기재
- [ ] 외부 서비스 가입/활용 정보 문서화 (담당자/과금/발급 콘솔 정보 보강 필요)
- [ ] 최신 DB 덤프 파일 첨부

## 2) 프로젝트 구성(포팅 범위)

- Backend: `Backend` (Spring Boot, Java 17, Gradle)
- Frontend: `Frontend/hearbe` (React + Vite)
- AI: `AI` (FastAPI + GPU 기반 OCR/ASR/TTS)
- Infra(Compose): 주로 `Backend/docker-compose.yml`, `AI/docker-compose.yml`

### 2-1) 운영 분리 원칙 (이번 포팅 기준)

- 메인 웹서버(AWS Nginx)는 기존 설정 유지
- AI 서버(Windows + WSL2)는 별도 서버 기준으로 포팅 정보 추가
- 문서에는 웹 메인 설정을 변경하지 않고 AI 서버 항목만 확장

## 3) 기능 목록 (포팅 매뉴얼에 들어갈 요약)

### 3-1. Frontend 주요 기능

- 인증/회원: 로그인, 회원가입, 아이디 찾기, 비밀번호 재설정
- 사용자 타입별 화면 분기: B/C/S/A 모드 라우팅
- 쇼핑 기능: 몰 선택, 스토어 브라우저, 장바구니, 위시리스트, 주문내역
- 사용자 정보: 마이페이지, 복지카드 관리
- 보호자 공유: 공유코드 기반 화면 공유(PeerJS)
- OCR 연동: 복지카드 이미지 업로드 및 자동 입력
- 이메일 인증: EmailJS 기반 인증코드 발송

근거 파일:
- `Frontend/hearbe/src/router/AppRouter.jsx`
- `Frontend/hearbe/src/services/authAPI.js`
- `Frontend/hearbe/src/services/emailService.js`
- `Frontend/hearbe/src/hooks/peerjs/usePeerShare.js`

### 3-2. Backend 주요 기능(API 도메인)

- 인증(Auth): 회원가입, 로그인, 토큰 재발급, 아이디 찾기, 비밀번호 재설정, 회원탈퇴
- 회원(Member): 프로필 조회/수정, 복지카드 CRUD
- 장바구니(Cart): 추가/조회/수정/삭제
- 위시리스트(Wishlist): 추가/조회/삭제
- 주문(Order): 주문 생성, 내 주문 조회
- 공유(Share): 공유코드 발급/조회
- 공통(Global): JWT 보안, 예외 처리, 헬스체크

근거 파일:
- `Backend/src/main/java/com/ssafy/d108/backend/auth/controller/AuthController.java`
- `Backend/src/main/java/com/ssafy/d108/backend/member/controller/ProfileController.java`
- `Backend/src/main/java/com/ssafy/d108/backend/member/controller/WelfareCardController.java`
- `Backend/src/main/java/com/ssafy/d108/backend/cartItem/controller/CartItemController.java`
- `Backend/src/main/java/com/ssafy/d108/backend/wishlist/controller/WishlistController.java`
- `Backend/src/main/java/com/ssafy/d108/backend/order/controller/OrderController.java`
- `Backend/src/main/java/com/ssafy/d108/backend/global/controller/ShareCodeController.java`

### 3-3. AI 주요 기능

- 음성 인식(ASR): Faster-Whisper/Qwen3-ASR
- 자연어 이해 및 명령 계획(LLM Planner)
- 음성 합성(TTS): Google Cloud TTS
- OCR: PaddleOCR 기반 텍스트/복지카드 인식
- WebSocket/HTTP API 제공

근거 파일:
- `AI/README.md`
- `AI/main.py`
- `AI/services/tts/service.py`
- `AI/services/summarizer/ocr_integrator.py`

## 4) 포팅 매뉴얼에 포함할 파일 목록 (필수)

### 4-1. 환경변수/설정 파일

- Backend
  - `Backend/.env.example`
  - `Backend/src/main/resources/application.properties`
  - `Backend/docker-compose.yml`
- Frontend
  - `Frontend/hearbe/.env.example`
  - `Frontend/hearbe/.env.production`
- AI
  - `AI/.env.example`
  - `AI/docker-compose.yml`

### 4-2. 빌드/런타임 버전 근거 파일

- Backend
  - `Backend/build.gradle` (Spring Boot 3.5.9, Java 17)
  - `Backend/gradle/wrapper/gradle-wrapper.properties` (Gradle 8.14.3)
  - `Backend/Dockerfile` (gradle:8-jdk17, eclipse-temurin:17-jre)
- Frontend
  - `Frontend/hearbe/package.json` (Vite 7, React 19)
- AI
  - `AI/Dockerfile` (CUDA 12.3.2, Python 3.10)
  - `AI/requirements.txt`

### 4-3. DB/ERD/시드 데이터

- `Backend/docs/erd/erd.md`
- `Backend/src/main/resources/data.sql`
- [ ] 최신 DB dump 파일 추가 필요 (예: `exec/db_dump_YYYYMMDD.sql`)

## 5) 외부 서비스 목록 (가입/설정 정보 정리 대상)

- OpenAI API (LLM): `AI/.env.example`의 `OPENAI_API_KEY`, `OPENAI_BASE_URL`
- Google Cloud TTS: `GOOGLE_APPLICATION_CREDENTIALS`, `TTS_GOOGLE_VOICE`
- EmailJS: `VITE_EMAILJS_SERVICE_ID`, `VITE_EMAILJS_TEMPLATE_ID`, `VITE_EMAILJS_PUBLIC_KEY`
- SMTP(메일): `SPRING_MAIL_*`
- PeerJS/STUN: `VITE_PEER_HOST`, `VITE_PEER_PORT`, `VITE_PEER_SECURE`, `stun.l.google.com`
- OpenVidu(사용 시): `OPENVIDU_URL`, `OPENVIDU_SECRET`

주의:
- 실 비밀번호/API 키는 문서에 직접 기재하지 않고 "발급 위치/주입 위치/관리 주체"만 기록

## 6) 배포/실행 포트 정리

- Backend API: container `8080`, host `${COMPOSE_HOST_PORT}` (`Backend/docker-compose.yml`)
- MariaDB: `3306`
- Redis: `6379`
- phpMyAdmin: host `8108`
- PeerJS: `9000`
- AI API: `8000`
- Frontend(API 연결): `VITE_API_BASE_URL`, `VITE_API_URL` 기준

추가 정리:
- 메인 웹서버 라우팅 경로는 유지: `/api/`, `/ws`, `/asr-demo/`
- AI 서버가 웹서버와 분리된 경우 `proxy_pass` 대상 주소만 AI 서버 접근 주소로 조정

## 7) 현재 서버에서 확인된 버전(초안)

웹서버(AWS, 기존 유지):
- OS: Ubuntu 24.04.3 LTS
- Kernel: 6.14.0-1018-aws
- Java: OpenJDK 17.0.18
- Node.js: v24.13.0
- npm: 11.6.2
- Docker: 29.2.0
- Docker Compose: v5.0.2
- Nginx: 1.24.0

AI 서버(WSL2):
- OS: Ubuntu 22.04.5 LTS
- Kernel: 6.6.87.2-microsoft-standard-WSL2
- Python: 3.10.12
- Docker: 29.1.3
- Docker Compose: v5.0.1
- GPU 확인: `/usr/lib/wsl/lib/nvidia-smi`

## 8) 포팅 매뉴얼 본문 작성 시 TODO

- [ ] IDE 버전(Backend/Frontend/AI 개발 IDE) 명시
- [x] 실제 운영 도메인 및 Reverse Proxy(Nginx) 설정 파일 경로 명시
- [x] 웹서버 메인 설정 유지 + AI 서버 항목 분리 기재
- [ ] DB dump 최신본 생성/첨부
- [ ] 서비스별 계정 담당자(누가 키 관리하는지) 기재
- [ ] 배포 특이사항(예: GPU 필수, 외부 API 장애 시 fallback) 정리

## 9) 추천 산출물 파일 세트 (`exec`)

- `exec/PORTING_MANUAL.md` (최종 제출본)
- `exec/PORTING_MANUAL_CHECKLIST.md` (본 문서)
- `exec/EXTERNAL_SERVICES.md`
- `exec/ENV_VARIABLES_REFERENCE.md`
- `exec/db_dump_YYYYMMDD.sql`
