# HEARBE 포팅 매뉴얼

- 프로젝트: HEARBE (시각장애인 음성 쇼핑 지원)
- 작성일: 2026-02-08
- 제출 경로: `exec/PORTING_MANUAL.md`
- 기준 리포지토리: `S14P11D108`

## 1. 프로젝트 구성

- Backend: `Backend` (Spring Boot API, MariaDB/Redis 연동)
- Frontend: `Frontend/hearbe` (React + Vite)
- AI: `AI` (FastAPI + ASR/NLU/LLM/TTS/OCR)

### 1-1. 운영 환경 분리 기준

- 메인 웹서버(Nginx, AWS): Backend API + Frontend 정적 파일 서빙 + PeerJS 프록시
- AI 서버: 별도 서버(Windows 노트북 + WSL2)에서 독립 운영
- Frontend에서 AI 기능(OCR, WebSocket)은 AI 서버 도메인(`jhserver.shop`)으로 직접 호출
- 메인 웹서버 Nginx에는 AI 관련 프록시 설정 없음

## 2. 빌드/런타임 버전

### 2-1. 메인 웹서버 (AWS, 기존 유지)

- OS: Ubuntu 24.04.3 LTS
- Kernel: 6.14.0-1018-aws
- Java: OpenJDK 17.0.18
- Node.js: v24.13.0
- npm: 11.6.2
- Docker: 29.2.0
- Docker Compose: v5.0.2
- Nginx: 1.24.0

### 2-2. AI 서버 (별도 서버, WSL2 기준 확인값)

- OS: Ubuntu 22.04.5 LTS (WSL2)
- Kernel: 6.6.87.2-microsoft-standard-WSL2
- Python: 3.10.12
- Docker: 29.1.3
- Docker Compose: v5.0.1
- GPU: NVIDIA Driver 560.94 / CUDA 12.6 (`/usr/lib/wsl/lib/nvidia-smi` 기준)

### 2-3. Backend 기준 버전 파일

- Java Toolchain: 17 (`Backend/build.gradle`)
- Spring Boot: 3.5.9 (`Backend/build.gradle`)
- Dependency Management Plugin: 1.1.7 (`Backend/build.gradle`)
- Gradle Wrapper: 8.14.3 (`Backend/gradle/wrapper/gradle-wrapper.properties`)
- Docker Build Image: `gradle:8-jdk17` (`Backend/Dockerfile`)
- Docker Runtime Image: `eclipse-temurin:17-jre` (`Backend/Dockerfile`)

### 2-4. Frontend 기준 버전 파일

- React: 19.2.4 (`Frontend/hearbe/package.json`)
- Vite: 7.2.4 (`Frontend/hearbe/package.json`)
- React Router DOM: 6.28.0 (`Frontend/hearbe/package.json`)
- PeerJS: 1.5.5 (`Frontend/hearbe/package.json`)

### 2-5. AI 기준 버전 파일

- Base Image: `nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04` (`AI/Dockerfile`)
- Python: 3.10 (컨테이너 설치) (`AI/Dockerfile`)
- 주요 패키지: FastAPI, Uvicorn, OpenAI SDK, Google TTS, PaddleOCR (`AI/requirements.txt`)
- GPU 예약 설정: `deploy.resources.reservations.devices` (`AI/docker-compose.yml`)

## 3. 배포 포트 및 서비스

### 3-1. Backend Compose (`Backend/docker-compose.yml`)

- Backend API: `${COMPOSE_HOST_PORT}:8080` (기본값: `8080`)
- MariaDB: `3306:3306`
- Redis: `6379:6379`
- phpMyAdmin: `8108:80`
- PeerJS: `9000:9000` (경로: `/hearbe-peer`)

### 3-2. AI Compose (`AI/docker-compose.yml`)

- AI API: `8000:8000`
- 내부 실행 명령: `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

### 3-3. Reverse Proxy (메인 웹서버 Nginx 실제 설정)

설정 파일: `/etc/nginx/sites-available/default`

- HTTPS: `443` (Let's Encrypt, `i14d108.p.ssafy.io`)
- HTTP → HTTPS 리다이렉트 (Certbot 자동 설정)
- Frontend 정적 파일: `location /` → `Frontend/hearbe/dist` (try_files, SPA 폴백)
- Backend API 프록시: `location /api/` → `http://127.0.0.1:8080/` (rate-limit 적용: `limit_req zone=api_rl burst=20 nodelay`)
- PeerJS WebSocket 프록시: `location /hearbe-peer/` → `http://127.0.0.1:9000` (Upgrade/Connection 헤더 포함)
- 보안 헤더: `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`
- 숨김파일 차단: `location ~* /\.(?!well-known)` → deny all

참고: AI 서버는 별도 도메인(`jhserver.shop`)으로 운영되며, 메인 웹서버 Nginx에 AI 관련 프록시 설정은 없음. Frontend에서 AI API를 직접 호출하는 구조.

## 4. Git Clone 이후 빌드/배포 절차

### 4-1. Backend

```bash
cd Backend
cp .env.example .env
# .env 값 수정

docker compose build
docker compose up -d

docker compose ps
docker compose logs --tail=200 hearbe-backend
```

검증:

```bash
curl -i http://localhost:${COMPOSE_HOST_PORT}/health
curl -i http://localhost:${COMPOSE_HOST_PORT}/ping
```

### 4-2. Frontend

```bash
cd Frontend/hearbe
cp .env.example .env
# 프로덕션 배포 시 .env.production 이 자동 적용됨 (Vite 빌드 모드 기준)

npm install
npm run build
# 빌드 결과물은 dist/ 에 생성되며, Nginx가 직접 서빙
```

참고:
- 개발용 `.env`와 배포용 `.env.production`이 분리되어 있음
- `.env.production`에 `VITE_API_BASE_URL`, `VITE_PEER_*`, `VITE_OCR_WELFARE_CARD_URL` 설정
- `.env`에 `VITE_EMAILJS_*` 설정 (프로덕션 빌드 시 `.env`도 기본 로딩됨)

### 4-3. AI (별도 서버/별도 환경)

```bash
cd AI
cp .env.example .env
# .env 값 수정

docker compose build
docker compose up -d

docker compose ps
docker compose logs --tail=200 ai-server
```

검증:

```bash
curl -i http://localhost:8000/
curl -i http://localhost:8000/api/v1/health
```

## 5. 기능 목록 (요약)

### 5-1. Frontend

- 인증/회원: 로그인, 회원가입, 아이디 찾기, 비밀번호 재설정
- 모드 분기: A/B/C/S 라우팅 및 사용자 타입별 화면
- 쇼핑 기능: 몰 선택, 스토어 브라우저, 장바구니, 위시리스트, 주문내역
- 보호자 공유: 공유코드 + PeerJS 기반 화면 공유
- 복지카드 OCR 연동(회원가입 자동입력)
- 이메일 인증(EmailJS)

근거 파일:
- `Frontend/hearbe/src/router/AppRouter.jsx`
- `Frontend/hearbe/src/services/authAPI.js`
- `Frontend/hearbe/src/hooks/peerjs/usePeerShare.js`
- `Frontend/hearbe/src/services/emailService.js`

### 5-2. Backend

- 인증: 회원가입/로그인/토큰재발급/회원탈퇴/아이디찾기/비밀번호재설정
- 회원: 프로필 조회/수정, 복지카드 CRUD
- 장바구니: 생성/조회/수정/삭제
- 위시리스트: 생성/조회/삭제
- 주문: 주문 생성/내 주문 조회
- 공유: 공유코드 발급/조회
- 공통: JWT 인증 필터, 헬스체크, 예외 처리

근거 파일:
- `Backend/src/main/java/com/ssafy/d108/backend/auth/controller/AuthController.java`
- `Backend/src/main/java/com/ssafy/d108/backend/member/controller/ProfileController.java`
- `Backend/src/main/java/com/ssafy/d108/backend/member/controller/WelfareCardController.java`
- `Backend/src/main/java/com/ssafy/d108/backend/cartItem/controller/CartItemController.java`
- `Backend/src/main/java/com/ssafy/d108/backend/wishlist/controller/WishlistController.java`
- `Backend/src/main/java/com/ssafy/d108/backend/order/controller/OrderController.java`
- `Backend/src/main/java/com/ssafy/d108/backend/global/controller/ShareCodeController.java`

### 5-3. AI

- ASR: Whisper / Qwen3-ASR
- NLU: 의도/컨텍스트 처리
- LLM Planner: 자연어 명령 계획
- TTS: Google Cloud TTS
- OCR: PaddleOCR 기반 복지카드 인식
- 통신: FastAPI HTTP + WebSocket `/ws`

근거 파일:
- `AI/main.py`
- `AI/api/http.py`
- `AI/core/config.py`
- `AI/services/tts/service.py`
- `AI/services/summarizer/ocr_integrator.py`

## 6. 환경 변수 정리 (코드/설정 파일 기준)

주의:
- 민감정보(API Key/비밀번호/시크릿)는 Git에 직접 커밋하지 않음
- 실제 값은 배포 서버 시크릿 또는 `.env`에만 주입

### 6-1. Backend 필수/주요 변수

- App/DB/Redis/JPA
  - `SPRING_APPLICATION_NAME`
  - `SPRING_DATASOURCE_URL`
  - `SPRING_DATASOURCE_USERNAME`
  - `SPRING_DATASOURCE_PASSWORD`
  - `SPRING_DATA_REDIS_HOST`
  - `SPRING_DATA_REDIS_PORT`
  - `SPRING_DATA_REDIS_PASSWORD`
  - `SPRING_JPA_HIBERNATE_DDL_AUTO`

- Auth/암호화
  - `JWT_SECRET`
  - `JWT_EXPIRATION`
  - `ENCRYPTION_SECRET_KEY`

- 메일
  - `SPRING_MAIL_HOST`
  - `SPRING_MAIL_PORT`
  - `SPRING_MAIL_USERNAME`
  - `SPRING_MAIL_PASSWORD`
  - `SPRING_MAIL_PROPERTIES_MAIL_SMTP_AUTH`
  - `SPRING_MAIL_PROPERTIES_MAIL_SMTP_STARTTLS_ENABLE`
  - `SPRING_MAIL_PROPERTIES_MAIL_SMTP_CONNECTIONTIMEOUT`
  - `SPRING_MAIL_PROPERTIES_MAIL_SMTP_TIMEOUT`
  - `SPRING_MAIL_PROPERTIES_MAIL_SMTP_WRITETIMEOUT`

- 화상/외부
  - `OPENVIDU_URL`
  - `OPENVIDU_SECRET`

- Compose 실행 제어
  - `COMPOSE_HOST_PORT`
  - `COMPOSE_HOST_LOG_PATH`
  - `COMPOSE_APP_PROFILE`

- 인프라 컨테이너
  - `MYSQL_ROOT_PASSWORD`
  - `MYSQL_DATABASE`
  - `MYSQL_USER`
  - `MYSQL_PASSWORD`
  - `PMA_HOST`
  - `PMA_USER`
  - `PMA_PASSWORD`
  - `REDIS_PASSWORD`

- 로깅
  - `LOG_LEVEL`
  - `APP_LOG_LEVEL`
  - `SPRING_LOG_LEVEL`
  - `SPRING_SECURITY_LOG_LEVEL`
  - `SPRING_DATA_LOG_LEVEL`
  - `HIBERNATE_SQL_LOG_LEVEL`
  - `HIBERNATE_BINDER_LOG_LEVEL`
  - `SPRING_JPA_SHOW_SQL`

### 6-2. Frontend 변수

- `VITE_API_BASE_URL`
- `VITE_API_URL`
- `VITE_OCR_WELFARE_CARD_URL`
- `VITE_EMAILJS_SERVICE_ID`
- `VITE_EMAILJS_TEMPLATE_ID`
- `VITE_EMAILJS_PUBLIC_KEY`
- `VITE_PEER_HOST`
- `VITE_PEER_PORT`
- `VITE_PEER_SECURE`
- `VITE_SOCKET_SERVER_URL` (코드 참조 존재 시)

### 6-3. AI 변수 (코드 + compose 기준 최대 목록)

- 서버/접속
  - `APP_ENV`
  - `SERVER_HOST`
  - `SERVER_PORT`
  - `WS_PATH`
  - `CORS_ORIGINS`
  - `PUBLIC_BASE_URL`
  - `PUBLIC_WS_URL`
  - `DEBUG`
  - `MAIN_PAGE_URL`
  - `BACKEND_BASE_URL`
  - `BACKEND_URL`
  - `GENERAL_URL`
  - `BLIND_URL`
  - `LOW_VISION_URL`

- ASR
  - `ASR_PROVIDER`
  - `ASR_DEVICE`
  - `ASR_LANGUAGE`
  - `ASR_MODEL_NAME`
  - `ASR_COMPUTE_TYPE`
  - `ASR_BEAM_SIZE`
  - `ASR_QWEN3_MODEL_NAME`
  - `ASR_QWEN3_MAX_BATCH_SIZE`
  - `ASR_QWEN3_MAX_NEW_TOKENS`

- NLU
  - `NLU_INTENT_MODEL`
  - `NLU_NER_ENABLED`
  - `NLU_CONTEXT_WINDOW`

- LLM
  - `LLM_API_KEY_NAME`
  - `LLM_MODEL_NAME`
  - `LLM_MAX_TOKENS`
  - `LLM_COMMAND_MAX_TOKENS`
  - `LLM_TTS_MAX_TOKENS`
  - `LLM_TEMPERATURE`
  - `LLM_TIMEOUT`
  - `LLM_DEBUG_LOG`
  - `OPENAI_API_KEY`
  - `OPENAI_BASE_URL`
  - `GMS_API_KEY`

- TTS
  - `TTS_SAMPLE_RATE`
  - `TTS_STREAMING`
  - `TTS_SPEAKING_RATE`
  - `GOOGLE_APPLICATION_CREDENTIALS`
  - `TTS_GOOGLE_VOICE`

- OCR
  - `OCR_PROVIDER`
  - `OCR_API_KEY`
  - `OCR_LANGUAGE`
  - `OCR_DEVICE`
  - `OCR_HTTP_MAX_UPLOAD_MB`
  - `OCR_HTTP_TIMEOUT_SECONDS`

- Flow/로그
  - `FLOWS_DIR`
  - `DEFAULT_SITE`
  - `FLOW_CONFIRMATION_REQUIRED`
  - `SEARCH_MATCH_THRESHOLD`
  - `SEARCH_MATCH_USE_LLM`
  - `SEARCH_MATCH_LLM_MODEL`
  - `LOG_LEVEL`
  - `LOG_CONSOLE_LEVEL`
  - `LOG_FILE_LEVEL`
  - `LOG_DIR`
  - `LOG_FILE`
  - `LOG_ROTATE_WHEN`
  - `LOG_ROTATE_INTERVAL`
  - `LOG_BACKUP_COUNT`
  - `LOG_ROTATE_UTC`

- 프로파일 오버라이드
  - `DEV_DEBUG`, `DEV_LOG_LEVEL`, `DEV_LOG_CONSOLE_LEVEL`, `DEV_LOG_FILE_LEVEL`, `DEV_LOG_DIR`, `DEV_LOG_FILE`, `DEV_LOG_ROTATE_WHEN`, `DEV_LOG_ROTATE_INTERVAL`, `DEV_LOG_BACKUP_COUNT`, `DEV_LOG_ROTATE_UTC`
  - `PROD_DEBUG`, `PROD_LOG_LEVEL`, `PROD_LOG_CONSOLE_LEVEL`, `PROD_LOG_FILE_LEVEL`, `PROD_LOG_DIR`, `PROD_LOG_FILE`, `PROD_LOG_ROTATE_WHEN`, `PROD_LOG_ROTATE_INTERVAL`, `PROD_LOG_BACKUP_COUNT`, `PROD_LOG_ROTATE_UTC`

- AI compose에서 추가 참조되는 값
  - `TAG`
  - `ELEVENLABS_API_KEY`
  - `HF_HUB_DISABLE_XET` (compose 고정값 1)

### 6-4. 현재 `.env` 파일 존재 여부

- 웹서버 기준:
  - 존재: `Backend/.env` (키 확인 완료)
  - 존재: `Frontend/hearbe/.env` (개발용, EmailJS 키 포함)
  - 존재: `Frontend/hearbe/.env.production` (배포용, API/PeerJS/OCR URL)
- AI 별도 서버 기준:
  - `AI/.env`는 AI 별도 서버에만 존재 (웹서버에는 없음)

## 7. DB 접속 정보 및 ERD/프로퍼티 파일 목록

### 7-1. DB/계정 관련 핵심 파일

- `Backend/src/main/resources/application.properties`
- `Backend/.env.example`
- `Backend/.env` (실서버 값, 민감정보)
- `Backend/docker-compose.yml`

### 7-2. ERD/초기 데이터

- ERD 문서: `Backend/docs/erd/erd.md`
- 시드 데이터: `Backend/src/main/resources/data.sql`

### 7-3. DB 덤프 제출

- 제출 파일 예시: `exec/db_dump_20260209.sql`
- 최신본 생성 예시:

```bash
mysqldump -h <DB_HOST> -u <DB_USER> -p <DB_NAME> > exec/db_dump_YYYYMMDD.sql
```

## 8. 외부 서비스 목록

### 8-1. 유료 API (AI 서버에서 사용)

| 서비스 | 용도 | 모델 | 과금 | 환경변수 |
|---|---|---|---|---|
| OpenAI API | LLM Planner / NLU 의도 분류 | GPT-5 mini | Input $0.25/1M tokens, Cached $0.025/1M, Output $2.00/1M tokens | `OPENAI_API_KEY`, `LLM_MODEL_NAME` |
| Google Cloud TTS | 음성 합성 | Chirp 3: HD | 무료 ~100만자, 이후 $30/100만자 (US$0.00003/자) | `GOOGLE_APPLICATION_CREDENTIALS`, `TTS_GOOGLE_VOICE` |

- OpenAI: https://platform.openai.com
- Google Cloud: https://console.cloud.google.com (서비스계정 JSON 발급 필요, `config/google-service-account.json`에 배치)

### 8-2. 무료 서비스

| 서비스 | 용도 | 적용 위치 | 비고 |
|---|---|---|---|
| EmailJS | Frontend 이메일 인증코드 발송 | `VITE_EMAILJS_SERVICE_ID`, `VITE_EMAILJS_TEMPLATE_ID`, `VITE_EMAILJS_PUBLIC_KEY` | https://www.emailjs.com (무료 플랜) |
| PeerJS + STUN | 보호자 화면 공유 (WebRTC) | `VITE_PEER_HOST`, `VITE_PEER_PORT`, `VITE_PEER_SECURE` | STUN: `stun:stun.l.google.com:19302` (무료) |

### 8-3. 자체 호스팅 (외부 API 호출 없음)

| 서비스 | 용도 | 모델 | 실행 위치 |
|---|---|---|---|
| ASR (음성 인식) | 음성→텍스트 변환 | Faster-Whisper large-v3-turbo / Qwen3-ASR-0.6B | AI 서버 GPU 로컬 |
| OCR (문자 인식) | 복지카드 텍스트 추출 | PaddleOCR | AI 서버 GPU 로컬 |

## 9. AI 서버가 별도 환경일 때 필수 확인 항목

### 9-1. 인프라/런타임 확인

```bash
uname -a
cat /etc/os-release
python3 --version
docker --version
docker compose version
nvidia-smi
/usr/lib/wsl/lib/nvidia-smi
```

### 9-2. GPU/컨테이너 확인

```bash
cd AI
docker compose config
docker compose up -d
docker compose ps
docker compose logs --tail=200 ai-server
```

### 9-3. 헬스체크/기능 확인

```bash
curl -i http://localhost:8000/
curl -i http://localhost:8000/api/v1/health
curl -i http://localhost:8000/api/v1/health/asr
curl -i http://localhost:8000/api/v1/health/tts
```

### 9-4. 운영 필수 확인

- `AI/.env` 생성 및 키 주입 완료 여부
- `config/google-service-account.json` 배치 여부
- GPU 메모리 여유(ASR/OCR 모델 로딩 가능)
- 외부 API 키(OpenAI/GMS/Google TTS) 유효성
- Reverse Proxy 경로(`/api/v1`, `/ws`) 연결 여부
- 로그 저장 경로(`AI/logs`) 및 로테이션 정책 확인

## 10. 배포 시 특이사항

### 10-1. 웹서버 (AWS)

- Nginx에서 Backend API(`/api/`)에 rate-limit(`limit_req zone=api_rl burst=20 nodelay`) 적용 중
- Frontend는 `npm run build` 후 `dist/` 디렉토리를 Nginx가 직접 서빙 (별도 WAS 없음)
- PeerJS는 Nginx WebSocket 프록시(`/hearbe-peer/`)를 통해 외부 접근
- Backend Security 설정상 일부 엔드포인트가 `permitAll`로 열려 있으므로 운영 정책 검토 필요
- 민감정보는 반드시 `.env` 또는 시크릿 매니저로 분리

### 10-2. AI 서버 (별도)

- AI는 GPU 가속 의존도가 높아 CPU-only 서버에서 성능/지연 저하 가능
- AI compose에 `--reload`가 포함되어 있어 운영 시 비활성 고려
- AI 서버는 메인 웹서버와 독립 운영, Frontend에서 AI 도메인으로 직접 호출

## 11. 발표 기준 이슈 분류 (코드 변경 없이 운영)

### 11-1. 논블로킹 이슈 (발표 핵심 기능 영향 없음)

- `AI/api/http.py`의 일부 상태 조회 엔드포인트(`/api/v1/health/tts`, `/api/v1/config`)는 설정 필드 참조 불일치로 오류 가능성이 있음
- 영향 범위: 상태 조회성 API에 한정
- 비영향 범위: 핵심 데모 플로우(프론트 회원가입 OCR, AI `/api/v1/ocr/welfare-card`, WebSocket `/ws`)는 별도 경로로 동작
- 발표 대응: 상태 조회 API 호출은 생략하고 핵심 플로우 위주로 시연

### 11-2. 블로킹 이슈 (발표 전 반드시 확인)

웹서버 측:
- Frontend `.env.production`의 `VITE_OCR_WELFARE_CARD_URL`이 실제 AI 도메인(`jhserver.shop`)과 불일치하면 OCR 기능 즉시 실패
- Frontend 빌드 시 `.env.production`에 EmailJS 키가 없으면 이메일 인증 실패 가능 (`.env`에만 존재하므로 Vite 빌드 시 자동 머지 여부 확인 필요)
- Nginx PeerJS 프록시(`/hearbe-peer/`) WebSocket 업그레이드 설정 정상 동작 확인

AI 서버 측 (별도 서버에서 확인):
- AI 서버의 Google 서비스계정 JSON 미배치 시 TTS 기능 실패
- AI 서버에서 GPU 미인식 시 ASR/OCR 초기화 지연 또는 실패 가능
- AI 서버 WebSocket(`/ws`) 경로 접근 가능 여부 확인

## 12. 포트/경로 최종 체크표 (발표 전 확인용)

### 12-1. 웹서버 (AWS) 라우팅

| 경로 | 대상 | 비고 |
|---|---|---|
| `https://i14d108.p.ssafy.io` | Frontend 정적 파일 (`dist/`) | Nginx 직접 서빙, SPA 폴백 |
| `https://i14d108.p.ssafy.io/api/*` | Backend `127.0.0.1:8080` | rate-limit 적용 |
| `https://i14d108.p.ssafy.io/hearbe-peer/` | PeerJS `127.0.0.1:9000` | WebSocket 프록시 |

### 12-2. 웹서버 컨테이너 포트

| 서비스 | 호스트:컨테이너 | 비고 |
|---|---|---|
| Backend API | `8080:8080` | `COMPOSE_HOST_PORT` 기본값 |
| MariaDB | `3306:3306` | |
| Redis | `6379:6379` | |
| phpMyAdmin | `8108:80` | |
| PeerJS | `9000:9000` | 경로: `/hearbe-peer` |

### 12-3. AI 서버 (별도)

| 경로 | 대상 | 비고 |
|---|---|---|
| `https://jhserver.shop/api/v1/ocr/welfare-card` | AI OCR API | Frontend에서 직접 호출 |
| `wss://jhserver.shop/ws` | AI WebSocket | Frontend에서 직접 호출 |
| AI 내부 컨테이너 | `8000` | |

## 13. 제출 전 최종 체크리스트

- [ ] `exec/PORTING_MANUAL.md` 최신화
- [ ] `exec/PORTING_MANUAL_CHECKLIST.md` 완료 체크
- [ ] `exec/db_dump_YYYYMMDD.sql` 첨부
- [ ] AI 별도환경 실제 값/버전 반영
- [ ] 외부 서비스 담당자/계정 정보 반영
