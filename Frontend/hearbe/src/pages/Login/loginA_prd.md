# LoginA 기능 구현 PRD

## 개요
LoginA.jsx의 하드코딩된 로컬 스토리지 인증 방식을 백엔드 API 연동으로 교체

## 현재 상태 분석

### Login 디렉토리 파일 구성
- `LoginA.jsx`: 로컬 스토리지 기반 인증을 사용하는 메인 로그인 컴포넌트
- `LoginA.css`: 스타일 파일
- `LoginC.jsx`: 빈 파일 (미사용)

### 현재 구현의 문제점
1. LoginA.jsx가 `userStorage.js`의 `findUser()` 함수를 사용하여 로컬 스토리지 확인
2. 회원가입은 백엔드 API로 데이터 전송하지만 로컬 스토리지와 동기화되지 않음
3. API로 가입한 사용자는 데이터가 백엔드에만 존재하여 로그인 불가

## API 명세

### 엔드포인트
- 경로: `/auth/login`
- 메서드: POST
- Base URL: 환경변수 `VITE_API_BASE_URL` 사용

### 요청 형식
```json
{
  "username": "testuser123",
  "password": "Password123!"
}
```

### 응답 형식
성공 (200):
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "id": 1,
    "name": "홍길동",
    "userType": "BLIND",
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "message": "로그인 성공"
  }
}
```

실패 (401):
```json
{
  "code": 401,
  "message": "아이디 또는 비밀번호가 일치하지 않습니다."
}
```

## 구현 변경사항

### 1. authAPI.js에 login 메서드 추가
- 위치: `src/services/authAPI.js`
- `authAPI` 객체에 `login` 메서드 추가
- localStorage에 토큰 저장 처리
- 성공 시 사용자 데이터 반환

### 2. LoginA.jsx 업데이트
- 위치: `src/pages/Login/LoginA.jsx`
- `userStorage.js` import 제거
- `findUser()` 호출을 `authAPI.login()` API 호출로 교체
- API 호출 중 로딩 상태 처리
- 성공 시 localStorage에 토큰 저장
- 로그인 성공 시 `/mall` 페이지로 이동
- 적절한 에러 메시지 표시

### 3. 하드코딩 제거
- LoginA.jsx에서 `userStorage.js` 의존성 제거
- `userStorage.js` 파일은 향후 사용을 위해 유지하되 Login에서는 import하지 않음

## 검증 계획

### 수동 테스트
1. 개발 서버 실행: `Frontend/hearbe` 디렉토리에서 `npm run dev`
2. 로그인 페이지 접속: `http://localhost:5173/login`
3. 가입된 사용자 계정으로 테스트:
   - 이전에 가입한 user_id와 password 입력
   - 로그인 버튼 클릭
   - `/mall` 페이지로 정상 이동 확인
   - 브라우저 localStorage에 `accessToken`, `refreshToken` 저장 확인
4. 잘못된 인증 정보로 테스트:
   - 틀린 비밀번호 입력
   - 에러 메시지 표시 확인
   - 페이지 이동이 발생하지 않는지 확인
5. 빈 필드 테스트:
   - 필드를 비워둔 채로 로그인 시도
   - 유효성 검사 메시지 표시 확인

### 브라우저 콘솔 검증
- Network 탭에서 `/auth/login`으로 POST 요청 확인
- 요청 payload가 명세와 일치하는지 확인
- 응답에 토큰이 포함되어 있는지 확인
- 콘솔에 에러가 없는지 확인

## 토큰 갱신 API 명세

### 엔드포인트
- 경로: `/auth/refresh`
- 메서드: POST

### 요청 형식
```json
{
  "refreshToken": "<저장된 refreshToken>"
}
```

### 응답 형식
성공 (200):
```json
{
  "code": 200,
  "message": "성공적으로 처리되었습니다.",
  "data": {
    "accessToken": "새로운 accessToken",
    "refreshToken": "새로운 refreshToken",
    "message": "토큰 재발급 성공"
  }
}
```
