# SignUp API Integration - Product Requirements Document

## Overview
회원가입 기능을 백엔드 API와 연동하여 실제 사용자 등록이 가능하도록 구현

## API Specification

### Endpoint
- **URL**: `/auth/regist`
- **Method**: POST
- **Content-Type**: application/json

### Request Body
```json
{
  "user_id": "user123",
  "password": "Password123!",
  "password_check": "Password123!",
  "username": "홍길동",
  "email": "user123@ssafy.com",
  "phone_number": "010-1234-5678",
  "user_type": "BLIND | GENERAL",
  "simple_password": "123456"
}
```

### Response
```json
{
  "code": 201,
  "message": "회원가입 성공",
  "data": {
    "user_id": 101
  }
}
```

## Current Implementation Analysis

### Existing Form Fields (SignUpA.jsx)
- `id` (아이디) → API: `user_id`
- `password` (비밀번호) → API: `password`
- `name` (이름) → API: `username`
- `phone` (전화번호) → API: `phone_number`

### Missing Required Fields
- `password_check` (비밀번호 확인) - 추가 필요
- `email` (이메일) - 추가 필요
- `user_type` (BLIND | GENERAL) - 추가 필요
- `simple_password` (간편 비밀번호) - 추가 필요

### Hardcoded Logic to Remove
1. **ID 중복 확인**: 현재 `alert("사용 가능한 아이디입니다.")` - API 연동 필요
2. **회원가입 처리**: `saveUser()` localStorage 저장 → API 호출로 변경
3. **카드 등록**: 현재 하드코딩된 카드 데이터 - 별도 처리 또는 제거

## Implementation Requirements

### 1. Form Fields Update
- 비밀번호 확인 필드 추가
- 이메일 입력 필드 추가
- 사용자 유형 선택 (시각장애인/일반사용자)
- 간편 비밀번호 입력 (6자리 숫자)

### 2. Validation Rules
**password**
- 영문, 숫자, 특수문자 조합
- 최소 8자 이상

**password_check**
- password와 일치 확인

**email**
- 이메일 형식 검증 (정규식)

**phone_number**
- 형식: 010-XXXX-XXXX
- 숫자만 입력 가능

**simple_password**
- 6자리 숫자
- 비밀번호와 중복 불가

### 3. API Integration Points

**ID 중복 확인** (선택사항)
- 별도 중복 확인 API가 있다면 연동
- 없다면 회원가입 시 에러 처리

**회원가입 제출**
- POST /auth/regist 호출
- 성공 시 (code: 201) → 로그인 페이지로 이동
- 실패 시 → 오류 메시지 표시

### 4. Error Handling
- 네트워크 오류 처리
- API 오류 코드별 사용자 친화적 메시지
- 입력 검증 실패 시 필드별 오류 표시

### 5. UX Flow
1. 사용자가 모든 필드 입력
2. 필수 약관 동의 체크
3. "회원가입" 버튼 클릭
4. 클라이언트 측 유효성 검증
5. API 호출
6. 성공 시 로그인 페이지로 리다이렉트
7. 실패 시 오류 메시지 표시

## Technical Notes

### API Base URL 설정
환경 변수 또는 설정 파일에서 API base URL 관리 필요

### 보안 고려사항
- 비밀번호 평문 전송 (HTTPS 필수)
- 민감 정보 로깅 방지

### 카드 등록 기능
현재 구현된 카드 등록 기능은 회원가입과 별도로 처리하거나 제거 검토 필요
