## Logging Configuration Guide

`application.properties` 파일은 하나만 사용하며, 환경 변수를 통해 개발/운영 환경의 로그 레벨을 제어합니다.

### 환경별 로그 레벨 설정 방법

#### 개발 환경 (.env 파일)
```properties
# 개발 환경에서는 DEBUG, TRACE 레벨 사용
LOG_LEVEL=DEBUG
APP_LOG_LEVEL=DEBUG
HIBERNATE_SQL_LOG_LEVEL=DEBUG
HIBERNATE_BINDER_LOG_LEVEL=TRACE
SPRING_JPA_SHOW_SQL=true
```

#### 운영 환경 (서버 환경 변수 또는 .env 파일)
```properties
# 운영 환경에서는 INFO 레벨만 사용 (DEBUG, TRACE 비활성화)
LOG_LEVEL=INFO
APP_LOG_LEVEL=INFO
HIBERNATE_SQL_LOG_LEVEL=INFO
HIBERNATE_BINDER_LOG_LEVEL=INFO
SPRING_JPA_SHOW_SQL=false
```

### 사용 방법

1. **로컬 개발**: `.env.example`을 복사하여 `.env` 파일 생성
   ```bash
   cp .env.example .env
   ```
   - `.env` 파일에서 `LOG_LEVEL=DEBUG` 유지

2. **운영 서버 배포**: 
   - 서버 환경 변수로 `LOG_LEVEL=INFO` 설정
   - 또는 운영용 `.env` 파일에서 `LOG_LEVEL=INFO`로 변경

### 환경 변수 목록

| 변수명 | 개발 환경 | 운영 환경 | 용도 |
|--------|----------|----------|------|
| `LOG_LEVEL` | DEBUG | INFO | 전체 애플리케이션 기본 로그 레벨 |
| `APP_LOG_LEVEL` | DEBUG | INFO | 애플리케이션 패키지 (com.ssafy.d108) 로그 레벨 |
| `SPRING_LOG_LEVEL` | INFO | INFO | Spring Web 로그 레벨 |
| `SPRING_SECURITY_LOG_LEVEL` | INFO | INFO | Spring Security 로그 레벨 |
| `SPRING_DATA_LOG_LEVEL` | INFO | INFO | Spring Data 로그 레벨 |
| `HIBERNATE_SQL_LOG_LEVEL` | DEBUG | INFO | Hibernate SQL 쿼리 로그 레벨 |
| `HIBERNATE_BINDER_LOG_LEVEL` | TRACE | INFO | Hibernate 파라미터 바인딩 로그 레벨 |
| `SPRING_JPA_SHOW_SQL` | true | false | JPA SQL 출력 여부 |

### 로그 레벨 설명

- **TRACE**: 가장 상세한 로그 (개발 전용, 파라미터 값 등)
- **DEBUG**: 디버깅 정보 (개발 전용, SQL 쿼리 등)
- **INFO**: 일반 정보 (개발/운영 공통)
- **WARN**: 경고 메시지
- **ERROR**: 에러 메시지

### Docker 배포 시

`docker-compose.yml` 또는 Dockerfile에서 환경 변수 설정:

```yaml
environment:
  - LOG_LEVEL=INFO
  - APP_LOG_LEVEL=INFO
  - HIBERNATE_SQL_LOG_LEVEL=INFO
  - HIBERNATE_BINDER_LOG_LEVEL=INFO
  - SPRING_JPA_SHOW_SQL=false
```
