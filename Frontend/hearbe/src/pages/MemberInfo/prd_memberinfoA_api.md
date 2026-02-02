# MemberInfo API 연동 - 기능 요구사항 명세서

## 개요
`/auth/mypage` API 엔드포인트를 연동하여 MemberInfo 페이지에서 사용자 정보를 동적으로 가져와 표시하고, 현재 하드코딩된 데이터를 제거합니다.

## API 명세

### 엔드포인트
- **경로**: `/auth/mypage`
- **메서드**: `GET`
- **Base URL**: `http://localhost:8080` (설정 필요)

### 요청
```
Headers:
  Authorization: Bearer {access_token}
```

### 응답
```json
{
  "user": {
    "user_id": "string",
    "username": "string",
    "phone_number": "string",
    "user_type": "USER",
    "last_login_at": "timestamp",
    "created_at": "timestamp"
  }
}
```

## 현재 상태 분석

### MemberInfoA.jsx - 하드코딩된 데이터
```javascript
const userData = {
    name: '김싸피',
    phone: '010-1234-5678',
    password: '******'
};
```

**문제점**:
- 정적 사용자 데이터로 인해 실제 사용자 정보를 표시할 수 없음
- 사용자 프로필 가져오기 위한 API 연동 없음
- 인증 토큰 처리 없음
- 로딩 및 에러 상태 없음

## 필요한 변경사항

### 1. 인증 설정
- localStorage 또는 context에서 액세스 토큰 가져오기
- Authorization 헤더에 토큰 전달
- 토큰 만료 및 갱신 로직 처리

### 2. API 연동
- `authAPI.js` 서비스 파일 생성/업데이트
- `getUserProfile()` 메서드 추가
- 적절한 에러 처리 구현
- API 호출 중 로딩 상태 추가

### 3. 컴포넌트 업데이트 (MemberInfoA.jsx)
- 하드코딩된 `userData` 객체 제거
- API 데이터 및 로딩 상태를 위한 state 관리 추가
- 마운트 시 데이터를 가져오기 위한 `useEffect` 훅 구현
- API 에러를 우아하게 처리
- 데이터 가져오는 동안 로딩 인디케이터 표시
- 표시를 위한 전화번호 포맷팅 (필요시 하이픈 추가)

### 4. 데이터 매핑
| API 필드 | 표시 필드 | 비고 |
|-----------|---------------|-------|
| `username` | 이름 | 직접 매핑 |
| `phone_number` | 휴대폰번호 | 하이픈 포맷 적용 |
| N/A | 비밀번호 | 마스킹 유지 (******) |

**참고**: 보안상 비밀번호는 API에서 반환되지 않음. 표시는 마스킹 상태 유지.

### 5. 에러 처리
- 네트워크 에러: 에러 메시지 표시, 재시도 옵션
- 401 Unauthorized: 로그인 페이지로 리다이렉트
- 403 Forbidden: 접근 거부 메시지 표시
- 500 Server Error: 서버 에러 메시지 표시
- 빈/null 데이터: 폴백으로 우아하게 처리

### 6. 로딩 상태
- 초기 로드: 스켈레톤 또는 스피너 표시
- 데이터 가져오기 완료: 사용자 정보 표시
- 에러 상태: 재시도 버튼이 있는 에러 메시지 표시

## 구현 파일

### 신규/수정 파일
1. **src/services/authAPI.js** (업데이트)
   - `getUserProfile()` 메서드 추가
   - 인증 헤더 처리

2. **src/pages/Mypage/MemberInfoA.jsx** (수정)
   - 하드코딩된 데이터 제거
   - API 연동 추가
   - 로딩/에러 상태 구현

3. **src/pages/Mypage/MemberInfoA.css** (선택사항 - 로딩 상태 스타일링 필요시)
   - 로딩 스피너 스타일
   - 에러 메시지 스타일

## 구현 예시

### authAPI.js 추가
```javascript
export const authAPI = {
  getUserProfile: async () => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/auth/mypage`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }
};
```

### MemberInfoA.jsx 업데이트
```javascript
const [userData, setUserData] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

useEffect(() => {
  const fetchUserProfile = async () => {
    try {
      setLoading(true);
      const response = await authAPI.getUserProfile();
      setUserData({
        name: response.user.username,
        phone: formatPhoneNumber(response.user.phone_number),
        password: '******'
      });
    } catch (err) {
      setError(err.message);
      if (err.message.includes('401')) {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };
  
  fetchUserProfile();
}, [navigate]);
```

## 수락 기준

1. 페이지 마운트 시 API에서 사용자 정보 로드
2. 데이터 가져오는 동안 로딩 스피너 표시
3. 성공적으로 가져온 후 사용자 데이터 올바르게 표시
4. 전화번호가 하이픈으로 포맷팅됨 (010-1234-5678)
5. 비밀번호는 '******'로 마스킹 유지
6. 401 에러는 로그인 페이지로 리다이렉트
7. 네트워크 에러는 사용자 친화적 에러 메시지 표시
8. 에러 시 재시도 메커니즘 제공
9. 컴포넌트에 하드코딩된 사용자 데이터 없음

## 테스트 요구사항

### 수동 테스트
1. 유효한 자격증명으로 로그인
2. /mypage/profile로 이동
3. 사용자 데이터가 올바르게 로드되는지 확인
4. 만료된 토큰으로 테스트 (로그인으로 리다이렉트되어야 함)
5. 네트워크 연결 끊고 테스트 (에러 표시되어야 함)
6. 에러 시 재시도 기능 테스트

### 엣지 케이스
- 전화번호가 없는 사용자
- 매우 긴 사용자명
- 사용자명에 특수문자 포함
- 세션 중 토큰 만료

## 보안 고려사항

- 토큰을 제외한 민감한 데이터는 localStorage에 저장하지 않음
- 토큰은 httpOnly 쿠키로 저장 (백엔드 지원 시)
- 로그아웃 시 토큰 삭제
- 토큰 갱신 메커니즘 구현
- 렌더링 전 모든 API 응답 검증

## 향후 개선사항

- 프로필 편집 기능 추가
- 프로필 사진 지원
- 마지막 로그인 시간 표시
- 계정 생성일 표시
- 비밀번호 변경 플로우 추가
