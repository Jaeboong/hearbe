# MemberInfo_A PRD

## 1. 개요

A형 회원정보 페이지. 사용자의 기본 정보를 표시한다.

## 2. 현재 상태

### 2.1 파일 구조
```
MemberInfo_A/
  - MemberInfoA.jsx    # 메인 컴포넌트
  - MemberInfoA.css    # 스타일
```

### 2.2 현재 구현 상태
- API 연동 필요 (엔드포인트 변경)
- 로딩/에러 상태 처리 완료
- 표시 정보: 이름, 휴대폰번호, 비밀번호(마스킹)

## 3. API 명세

### 3.1 회원정보 조회
```
GET /members/profile
Authorization: Bearer {accessToken}
```

### 3.2 Response
```json
{
  "user": {
    "user_id": "string",
    "username": "string",
    "phone_number": "string",
    "user_type": "USER",
    "last_login_at": "timestamp",
    "created_at": "timestamp"
  },
  "profile": {
    "gender": "M",
    "height": 170.5,
    "weight": 60.2,
    "birth_date": "1999-01-01",
    "updated_at": "timestamp"
  }
}
```

### 3.3 Response 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| user.user_id | string | 사용자 ID |
| user.username | string | 로그인 아이디 |
| user.phone_number | string | 휴대폰번호 |
| user.user_type | string | 사용자 타입 (USER 등) |
| user.last_login_at | timestamp | 마지막 로그인 시간 |
| user.created_at | timestamp | 계정 생성 시간 |
| profile.gender | string | 성별 (M/F) |
| profile.height | number | 키 (cm) |
| profile.weight | number | 몸무게 (kg) |
| profile.birth_date | string | 생년월일 (YYYY-MM-DD) |
| profile.updated_at | timestamp | 프로필 수정 시간 |

## 4. 구현 요구사항

### 4.1 API 서비스
- 위치: services/memberAPI.js (신규)
- A형, C형에서 공통으로 사용

```javascript
// 사용법
import { memberAPI } from '../../services/memberAPI';

const response = await memberAPI.getProfile();
// response.data 로 접근
```

### 4.2 에러 처리
| HTTP 상태 | 에러 메시지 |
|-----------|------------|
| 401 | 로그인이 필요합니다. |
| 403 | 접근 권한이 없습니다. |
| 404 | 회원정보를 찾을 수 없습니다. |
| 500+ | 서버 오류가 발생했습니다. |
| 네트워크 | 네트워크 연결을 확인해주세요. |

### 4.3 MemberInfoA.jsx 수정 사항
- memberAPI.getProfile() 사용
- response.data에서 데이터 추출

### 4.4 데이터 표시 항목

| 라벨 | 필드 | 비고 |
|------|------|------|
| 이름 | data.name | - |
| 휴대폰번호 | data.phoneNumber | - |
| 비밀번호 | - | ****** 마스킹 |

## 5. UI 상태

### 5.1 로딩 상태
- 스피너 + "사용자 정보를 불러오는 중..." 메시지

### 5.2 에러 상태
- 에러 메시지 표시
- 재시도 버튼

### 5.3 데이터 표시
- 정보 테이블 형태
- 로그아웃 링크

## 6. 작업 체크리스트

- [x] services/memberAPI.js 생성
- [x] MemberInfoA.jsx API 변경 (memberAPI.getProfile)
- [x] 로딩 상태 UI
- [x] 에러 상태 UI
