# C형 회원가입 PRD

## 개요
사용자가 HearBe 서비스의 C형(일반/시각장애인) 회원으로 가입하기 위한 기능 요구사항을 정의합니다.

## 기능 요구사항
- **입력 필드**: 아이디, 비밀번호, 비밀번호 확인, 이름, 이메일, 사용자 유형
- **사용자 유형 선택**: 시각장애인(BLIND), 저시력자(LOW_VISION), 보호자(GUARDIAN) 중 선택 가능

## API 명세
- **Endpoint**: `/auth/regist`
- **Method**: `POST`
- **Request Payload**:
```json
{
  "username": "general_test_001",
  "password": "Password123!",
  "password_check": "Password123!",
  "name": "일반사용자테스트",
  "email": "general@test.com",
  "phone_number": "010-3333-3333",
  "user_type": "GENERAL",
  "simple_password": null,
  "welfare_card": null
}

```
- **Response**:
```json
{
  "code": 201,
  "message": "회원가입 성공",
  "data": {
    "user_id": 101
  }
}
```

## 유효성 검사
- 모든 필드는 필수 입력 항목입니다.
- 비밀번호와 비밀번호 확인은 일치해야 합니다.
- 이메일 형식이 유효해야 합니다.
- 아이디는 영문 및 숫자를 포함해야 합니다.
