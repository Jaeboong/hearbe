# Logging Configuration Guide

이 문서는 HEARBE 백엔드 애플리케이션의 로깅 설정 방법을 설명합니다.

## 개요

`application.properties` 파일은 하나만 사용하며, 환경 변수를 통해 개발/운영 환경의 로그 레벨을 제어합니다.

## Docker 구성

### docker-compose.yml 설정

```yaml
services:
  hearbe-backend:
    environment:
      - SPRING_PROFILES_ACTIVE=${APP_PROFILE}  # dev 또는 prod 프로파일 주입
      - LOG_PATH=/logs                          # 컨테이너 내부 로그 경로
    volumes:
      - ${HOST_LOG_PATH}:/logs                  # 호스트와 로그 폴더 연결
    env_file:
      - .env
```

### 환경별 Docker 설정

**.env 파일 (현재 설정)**
```properties
# 애플리케이션 프로파일 및 Docker 설정
APP_PROFILE=prod          # 환경: dev 또는 prod
HOST_PORT=80              # 호스트 포트 (개발: 8080, 운영: 80)
HOST_LOG_PATH=./logs      # 호스트의 로그 파일 저장 경로
```

## 환경별 로그 레벨 설정

### 개발 환경 (.env 파일)

```properties
# 애플리케이션 프로파일 설정
APP_PROFILE=dev
HOST_PORT=8080
HOST_LOG_PATH=./logs

# 개발 환경: DEBUG, TRACE 레벨 사용
LOG_LEVEL=DEBUG
APP_LOG_LEVEL=DEBUG
SPRING_LOG_LEVEL=INFO
SPRING_SECURITY_LOG_LEVEL=INFO
SPRING_DATA_LOG_LEVEL=INFO
HIBERNATE_SQL_LOG_LEVEL=DEBUG
HIBERNATE_BINDER_LOG_LEVEL=TRACE
SPRING_JPA_SHOW_SQL=true
```

### 운영 환경 (.env 파일)

```properties
# 애플리케이션 프로파일 설정
APP_PROFILE=prod
HOST_PORT=80
HOST_LOG_PATH=./logs

# 운영 환경: WARN 레벨 사용 (logback-spring.xml 기준)
# 특정 로거에 대해서만 환경 변수로 오버라이드 가능
LOG_LEVEL=WARN
APP_LOG_LEVEL=WARN
SPRING_LOG_LEVEL=WARN
SPRING_SECURITY_LOG_LEVEL=WARN
SPRING_DATA_LOG_LEVEL=WARN
HIBERNATE_SQL_LOG_LEVEL=WARN
HIBERNATE_BINDER_LOG_LEVEL=WARN
SPRING_JPA_SHOW_SQL=false
```

## 환경별 설정 가이드

### 개발 환경 (Development) 설정

#### 1단계: `.env` 파일 생성

```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env
```

#### 2단계: `.env` 파일 수정

`.env` 파일을 열어서 다음 설정들을 **개발 환경**으로 변경:

```properties
# ===== 개발 환경 필수 설정 =====

# 1. 애플리케이션 프로파일
APP_PROFILE=dev
HOST_PORT=8080
HOST_LOG_PATH=./logs

# 2. 로깅 설정 (상세한 로그 출력)
LOG_LEVEL=DEBUG
APP_LOG_LEVEL=DEBUG
SPRING_LOG_LEVEL=INFO
SPRING_SECURITY_LOG_LEVEL=INFO
SPRING_DATA_LOG_LEVEL=INFO
HIBERNATE_SQL_LOG_LEVEL=DEBUG
HIBERNATE_BINDER_LOG_LEVEL=TRACE
SPRING_JPA_SHOW_SQL=true

# 3. 데이터베이스 설정 (로컬 또는 Docker)
SPRING_DATASOURCE_URL=jdbc:mysql://hearbe-mariadb:3306/hearbe?useSSL=false&allowPublicKeyRetrieval=true&characterEncoding=UTF-8&serverTimezone=UTC
SPRING_DATASOURCE_USERNAME=hearbe
SPRING_DATASOURCE_PASSWORD=1234
SPRING_JPA_HIBERNATE_DDL_AUTO=update  # 개발: update, 운영: validate

# 4. Redis 설정
SPRING_DATA_REDIS_HOST=hearbe-redis
SPRING_DATA_REDIS_PORT=6379
SPRING_DATA_REDIS_PASSWORD=1234

# 5. JWT 및 암호화 (개발용 키 사용)
JWT_SECRET=YOUR_DEV_JWT_SECRET
JWT_EXPIRATION=3600000
ENCRYPTION_SECRET_KEY=thisisaverysecurekeyforaes256bit

# 6. 이메일 설정 (테스트용)
SPRING_MAIL_HOST=smtp.gmail.com
SPRING_MAIL_PORT=587
SPRING_MAIL_USERNAME=test@gmail.com
SPRING_MAIL_PASSWORD=YOUR_APP_PASSWORD

# 7. OpenVidu 설정 (로컬)
OPENVIDU_URL=http://127.0.0.1:4443/
OPENVIDU_SECRET=MY_SECRET
```

#### 3단계: Docker Compose 실행

```bash
docker-compose up -d
```

---

### 운영 환경 (Production) 설정

#### 1단계: `.env` 파일 준비

운영 서버에 `.env` 파일을 생성하거나 기존 파일 수정:

```bash
# 서버에서 .env 파일 편집
vi .env
```

#### 2단계: `.env` 파일 수정

`.env` 파일을 열어서 다음 설정들을 **운영 환경**으로 변경:

```properties
# ===== 운영 환경 필수 설정 =====

# 1. 애플리케이션 프로파일
APP_PROFILE=prod
HOST_PORT=80
HOST_LOG_PATH=./logs

# 2. 로깅 설정 (경고/에러만 출력)
LOG_LEVEL=WARN
APP_LOG_LEVEL=WARN
SPRING_LOG_LEVEL=WARN
SPRING_SECURITY_LOG_LEVEL=WARN
SPRING_DATA_LOG_LEVEL=WARN
HIBERNATE_SQL_LOG_LEVEL=WARN
HIBERNATE_BINDER_LOG_LEVEL=WARN
SPRING_JPA_SHOW_SQL=false

# 3. 데이터베이스 설정 (운영 DB 정보)
SPRING_DATASOURCE_URL=jdbc:mysql://hearbe-mariadb:3306/hearbe?useSSL=false&allowPublicKeyRetrieval=true&characterEncoding=UTF-8&serverTimezone=UTC
SPRING_DATASOURCE_USERNAME=hearbe
SPRING_DATASOURCE_PASSWORD=STRONG_PRODUCTION_PASSWORD  # 강력한 비밀번호 사용
SPRING_JPA_HIBERNATE_DDL_AUTO=validate  # 운영: validate (스키마 변경 금지)

# 4. Redis 설정
SPRING_DATA_REDIS_HOST=hearbe-redis
SPRING_DATA_REDIS_PORT=6379
SPRING_DATA_REDIS_PASSWORD=STRONG_REDIS_PASSWORD  # 강력한 비밀번호 사용

# 5. JWT 및 암호화 (운영용 보안 키)
JWT_SECRET=PRODUCTION_JWT_SECRET_256BIT_BASE64_ENCODED
JWT_EXPIRATION=3600000
ENCRYPTION_SECRET_KEY=PRODUCTION_ENCRYPTION_KEY_32BYTES

# 6. 이메일 설정 (운영용)
SPRING_MAIL_HOST=smtp.gmail.com
SPRING_MAIL_PORT=587
SPRING_MAIL_USERNAME=production@yourdomain.com
SPRING_MAIL_PASSWORD=PRODUCTION_APP_PASSWORD

# 7. OpenVidu 설정 (운영 서버)
OPENVIDU_URL=https://your-openvidu-domain.com/
OPENVIDU_SECRET=PRODUCTION_OPENVIDU_SECRET
```

#### 3단계: 보안 점검

> [!WARNING]
> 운영 환경 배포 전 반드시 확인:
> - 모든 비밀번호가 강력한 값으로 변경되었는지 확인
> - `APP_PROFILE=prod` 설정 확인
> - `LOG_LEVEL=WARN` 설정 확인
> - `SPRING_JPA_HIBERNATE_DDL_AUTO=validate` 설정 확인

#### 4단계: Docker Compose 실행

```bash
# 운영 환경에서 실행
docker-compose up -d

# 로그 확인
docker logs -f hearbe-backend
```

---

### 환경별 주요 차이점 요약

| 설정 항목 | 개발 환경 (dev) | 운영 환경 (prod) |
|----------|----------------|-----------------|
| **APP_PROFILE** | `dev` | `prod` |
| **HOST_PORT** | `8080` | `80` |
| **LOG_LEVEL** | `DEBUG` | `WARN` |
| **APP_LOG_LEVEL** | `DEBUG` | `WARN` |
| **HIBERNATE_SQL_LOG_LEVEL** | `DEBUG` | `WARN` |
| **HIBERNATE_BINDER_LOG_LEVEL** | `TRACE` | `WARN` |
| **SPRING_JPA_SHOW_SQL** | `true` | `false` |
| **SPRING_JPA_HIBERNATE_DDL_AUTO** | `update` | `validate` |
| **비밀번호** | 간단한 값 가능 | 강력한 보안 값 필수 |
| **로그 출력** | 콘솔 (많은 정보) | 콘솔 + 파일 (경고/에러만) |

## 환경 변수 상세 설명

### Docker 및 애플리케이션 설정

| 변수명 | 개발 환경 | 운영 환경 | 용도 |
|--------|----------|----------|------|
| `APP_PROFILE` | dev | prod | Spring 프로파일 (개발/운영 환경 구분) |
| `HOST_PORT` | 8080 | 80 | Docker 호스트 포트 매핑 |
| `HOST_LOG_PATH` | ./logs | ./logs | 호스트의 로그 파일 저장 경로 |

### 로깅 레벨 설정

| 변수명 | 개발 환경 | 운영 환경 | 용도 |
|--------|----------|----------|------|
| `LOG_LEVEL` | DEBUG | WARN | 전체 애플리케이션 기본 로그 레벨 |
| `APP_LOG_LEVEL` | DEBUG | WARN | 애플리케이션 패키지 (com.ssafy.d108) 로그 레벨 |
| `SPRING_LOG_LEVEL` | INFO | WARN | Spring Framework 로그 레벨 |
| `SPRING_SECURITY_LOG_LEVEL` | INFO | WARN | Spring Security 로그 레벨 |
| `SPRING_DATA_LOG_LEVEL` | INFO | WARN | Spring Data 로그 레벨 |
| `HIBERNATE_SQL_LOG_LEVEL` | DEBUG | WARN | Hibernate SQL 쿼리 로그 레벨 |
| `HIBERNATE_BINDER_LOG_LEVEL` | TRACE | WARN | Hibernate 파라미터 바인딩 로그 레벨 |
| `SPRING_JPA_SHOW_SQL` | true | false | JPA SQL 출력 여부 |

## 로그 레벨 설명0                                                                                                                                                                           - **TRACE**: 가장 상세한 로그 (개발 전용, 파라미터 값 등)
- **DEBUG**: 디버깅 정보 (개발 전용, SQL 쿼리 등)
- **INFO**: 일반 정보 (애플리케이션 정상 동작 흐름)
- **WARN**: 경고 메시지 (운영 환경 기본 레벨, 잠재적 문제 상황)
- **ERROR**: 에러 메시지 (반드시 해결해야 할 오류)

### logback-spring.xml 설정

`logback-spring.xml` 파일에서 프로파일별 기본 로그 레벨을 정의합니다:

```xml
<!-- 개발 환경: DEBUG 레벨 -->
<springProfile name="dev">
    <root level="DEBUG"><appender-ref ref="CONSOLE" /></root>
</springProfile>

<!-- 운영 환경: WARN 레벨, 파일로 저장 -->
<springProfile name="prod">
    <root level="WARN">
        <appender-ref ref="CONSOLE" />
        <appender-ref ref="FILE" />
    </root>
</springProfile>
```

> [!NOTE]
> `.env` 파일의 환경 변수(`LOG_LEVEL`, `APP_LOG_LEVEL` 등)는 특정 로거에 대한 세부 설정을 오버라이드할 수 있지만, `logback-spring.xml`의 `<root level>` 설정이 전체 애플리케이션의 기본 로그 레벨을 결정합니다.

## 로그 파일 관리

### 로그 저장 위치

- **컨테이너 내부**: `/logs`
- **호스트**: `${HOST_LOG_PATH}` (기본값: `./logs`)

### 로그 파일 확인

```bash
# 컨테이너 로그 확인 (실시간)
docker logs -f hearbe-backend

# 호스트 로그 파일 확인
ls -lh ./logs
cat ./logs/application.log
```

## 주의사항

> [!WARNING]
> 운영 환경에서는 반드시 `LOG_LEVEL=WARN`으로 설정하세요. DEBUG, TRACE 레벨은 성능 저하 및 민감한 정보 노출 위험이 있습니다. `logback-spring.xml`의 `prod` 프로파일은 기본적으로 `WARN` 레벨을 사용합니다.

> [!IMPORTANT]
> `.env` 파일은 민감한 정보를 포함하므로 Git에 커밋하지 마세요. `.env.example`만 버전 관리에 포함됩니다.

> [!NOTE]
> `.env` 파일은 현재 운영 환경(`APP_PROFILE=prod`, `LOG_LEVEL=WARN`)으로 설정되어 있습니다. 로컬 개발 시에는 위의 **개발 환경 설정 가이드**를 참고하여 `.env` 파일을 수정하세요.
