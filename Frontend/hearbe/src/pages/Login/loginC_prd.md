# C형 로그인 PRD

## 개요
사용자가 HearBe 서비스의 C형으로 로그인하기 위한 기능 요구사항을 정의합니다.

## 기능 요구사항
- **입력 필드**: 아이디, 비밀번호
- **로그인 상태 유지**: 체크박스를 통한 토큰 저장 기능

## API 명세
- **Endpoint**: `api/auth/login`
- **Method**: `POST`
- **Request Payload**:
```json
{
  "username": "아이디",
  "password": "비밀번호"
}
```
*주의: A형의 경우 password 대신 simple_password 필드를 사용할 수 있음.*

- **Response**:
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "id": 1,
    "name": "성명",
    "userType": "guardian",
    "accessToken": "JWT_TOKEN",
    "message": "로그인 성공"
  }
}
```

## 예외 처리
- 아이디/비밀번호 불일치 시 에러 메시지 표시
- 서버 연결 실패 시 안내 메시지 표시
