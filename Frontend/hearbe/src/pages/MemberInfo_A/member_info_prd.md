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
  "code": 200,
  "message": "Success",
  "data": {
    "id": 1,
    "username": "testuser123",
    "name": "홍길동",
    "userType": "BLIND",
    "phoneNumber": "010-1234-5678",
    "gender": "M",
    "birthDate": "1990-01-01",
    "height": 175.5,
    "weight": 70.0,
    "topSize": "L",
    "bottomSize": "32",
    "shoeSize": "270",
    "allergies": ["NUTS", "DAIRY"],
    "etcAllergy": "복숭아"
  }
}
```

### 3.3 Response 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| id | number | 사용자 ID |
| username | string | 로그인 아이디 |
| name | string | 사용자 이름 |
| userType | string | 사용자 타입 (BLIND 등) |
| phoneNumber | string | 휴대폰번호 |
| gender | string | 성별 (M/F) |
| birthDate | string | 생년월일 (YYYY-MM-DD) |
| height | number | 키 (cm) |
| weight | number | 몸무게 (kg) |
| topSize | string | 상의 사이즈 (S/M/L/XL) |
| bottomSize | string | 하의 사이즈 (26/27/28...) |
| shoeSize | string | 신발 사이즈 (mm) |
| allergies | array | 알레르기 목록 |
| etcAllergy | string | 기타 알레르기 |

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
