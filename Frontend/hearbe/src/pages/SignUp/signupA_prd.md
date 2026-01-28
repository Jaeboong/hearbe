# SignUp API Integration - Product Requirements Document

## Overview
회원가입 기능을 백엔드 API와 연동하여 실제 사용자 등록이 가능하도록 구현

## API Specification

### Endpoint
- **URL**: `/api/auth/regist`
- **Method**: POST
- **Content-Type**: application/json

### Request Body
```json
{
  "user_id": "user123",
  "password": "123456",
  "password_check": "123456",
  "username": "홍길동",
  "email": null,
  "phone_number": "010-1234-5678",
  "user_type": "BLIND",
  "simple_password": null
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
- password_check 필드 추가 (비밀번호 확인)
- user_type 고정값: **BLIND** (장애인 복지카드 등록 필수)
- 장애인 복지카드 등록은 **필수** 항목

### 2. Validation Rules

**user_id**
- 영문자와 숫자 포함 필수
- 최소 3글자 이상
- 검증 실패 시: "아이디는 영문자와 숫자를 포함하여 3글자 이상이어야 합니다."

**password**
- 숫자 6자리만 허용
- 검증 실패 시: "비밀번호는 숫자 6자리여야 합니다."

**phone_number**
- 총 11자리 숫자 (하이픈 제외)
- 입력 시 자동 포맷팅: 01012345678 → 010-1234-5678
- 010으로 시작하는 휴대전화번호만 허용
- 검증 실패 시: "휴대전화번호는 11자리 숫자여야 합니다."

### 3. API Integration Points

**ID 중복 확인** (선택사항)
- 별도 중복 확인 API가 있다면 연동
- 없다면 회원가입 시 에러 처리

**회원가입 제출**
- POST /auth/regist 호출
- 성공 시 (code: 201) → 로그인 페이지로 이동
- 실패 시 → 오류 메시지 표시

### 4. Error Handling

**클라이언트 검증 오류 메시지**
- 아이디 미입력: "아이디를 입력해주세요."
- 아이디 형식 오류: "아이디는 영문자와 숫자를 포함하여 3글자 이상이어야 합니다."
- 아이디 중복 미확인: "아이디 중복확인을 해주세요."
- 비밀번호 미입력: "비밀번호를 입력해주세요."
- 비밀번호 형식 오류: "비밀번호는 숫자 6자리여야 합니다."
- 비밀번호 불일치: "비밀번호가 일치하지 않습니다."
- 이름 미입력: "이름을 입력해주세요."
- 휴대전화번호 형식 오류: "휴대전화번호는 11자리 숫자여야 합니다."
- 복지카드 미등록: "장애인 복지카드를 등록해주세요."
- 약관 미동의: "필수 약관에 동의해주세요."

**서버 오류 처리**
- 네트워크 오류: "서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요."
- API 오류 코드별 사용자 친화적 메시지
- 중복 아이디: "이미 존재하는 아이디입니다."

### 5. UX Flow
1. 사용자가 아이디 입력 후 중복확인 버튼 클릭
2. 비밀번호, 이름, 휴대전화번호 입력
   - 휴대전화번호는 숫자만 입력 시 자동으로 하이픈 삽입
3. **[필수]** 장애인 복지카드 촬영 및 등록
   - 등록 완료 시 user_type = BLIND로 설정
   - **미등록 시 회원가입 불가(C 형으로 가입해주세요)** (오류 메시지 표시)
4. 필수 약관 "전체 동의하기" 체크
5. "회원가입" 버튼 클릭
6. 클라이언트 측 유효성 검증
   - 아이디: 영문+숫자 포함, 3글자 이상
   - 비밀번호: 숫자 6자리
   - 휴대전화번호: 11자리
   - **복지카드 등록 여부 확인 (필수)**
   - 약관 동의: 필수 약관 모두 체크
7. API 호출 (POST /auth/regist)
8. 성공 (code: 201) → 로그인 페이지로 리다이렉트
9. 실패 → 오류 메시지 모달 표시

## Technical Notes

### API Base URL 설정
환경 변수 또는 설정 파일에서 API base URL 관리 필요

### 보안 고려사항
- 비밀번호 암호화 전송 (HTTPS 필수)
- 민감 정보 로깅 방지

### 카드 등록 기능
현재 구현된 카드 등록 기능은 회원가입과 별도로 처리하거나 제거 검토 필요
- 추후 OCR 연동 예정
