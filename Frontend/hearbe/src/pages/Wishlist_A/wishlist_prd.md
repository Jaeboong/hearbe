# Wishlist_A PRD

## 1. 개요

A형 찜한 상품 페이지. 사용자가 찜한 상품 목록을 플랫폼별로 그룹화하여 표시한다.

## 2. 현재 상태

### 2.1 파일 구조
```
Wishlist_A/
  - WishlistA.jsx    # 메인 컴포넌트
  - WishlistA.css    # 스타일
```

### 2.2 하드코딩된 데이터 (제거 대상)
- WishlistA.jsx line 11-46
- 쿠팡, 11번가, G마켓 등 더미 찜 데이터가 useState로 하드코딩됨
- API 호출 로직 없음

## 3. API 명세

### 3.1 찜한 상품 목록 조회
```
GET /wishlist
Authorization: Bearer {accessToken}
```

### 3.2 Response
```json
{
  "items": [
    {
      "wishlistItemId": 55,
      "productName": "에어맥스 270",
      "productUrl": "https://...",
      "platformName": "coupang",
      "createdAt": "2026-01-19T10:12:33",
      "imgUrl": "https://img.coupang.com/...",
      "liked": "true"
    }
  ]
}
```

### 3.3 Response 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| wishlistItemId | number | 찜 아이템 ID |
| productName | string | 상품명 |
| productUrl | string | 상품 URL |
| platformName | string | 플랫폼명 (coupang, naver, 11st, ssg 등) |
| createdAt | string | 찜한 날짜 (ISO 형식: YYYY-MM-DDTHH:mm:ss) |
| imgUrl | string | 상품 이미지 URL |
| liked | string | 찜 상태 ("true" / "false") |

### 3.4 찜 삭제 API
```
DELETE /wishlist/{wishlistItemId}
Authorization: Bearer {accessToken}
```

### 3.5 찜 삭제 Response
```json
{
  "code": 200,
  "message": "성공적으로 삭제되었습니다."
}
```

## 4. 구현 요구사항

### 4.1 API 서비스 (공통 로직)
- 위치: services/wishlistAPI.js
- A형, C형에서 공통으로 사용
- cartAPI.js, orderAPI.js와 동일한 패턴 적용

```javascript
// 사용법
import { wishlistAPI } from '../../services/wishlistAPI';

const response = await wishlistAPI.getWishlist();
// response.items 로 접근

await wishlistAPI.deleteWishlist(wishlistItemId);
```

### 4.2 에러 처리
| HTTP 상태 | 에러 메시지 |
|-----------|------------|
| 401 | 로그인이 필요합니다. |
| 403 | 접근 권한이 없습니다. |
| 404 | 찜한 상품을 찾을 수 없습니다. |
| 500+ | 서버 오류가 발생했습니다. |
| 네트워크 | 네트워크 연결을 확인해주세요. |

### 4.3 WishlistA.jsx 수정
- 하드코딩 데이터 제거
- useEffect로 API 호출
- 로딩/에러 상태 처리
- platformName을 기준으로 그룹화
- 날짜 포맷 변환 (YYYY-MM-DD -> YYYY.MM.DD)

### 4.4 데이터 변환 로직
```javascript
// API Response -> UI 데이터 변환
// platformName 매핑 (영문 -> 한글)
const platformDisplayNames = {
  'coupang': '쿠팡',
  'naver': '네이버',
  '11st': '11번가',
  'ssg': 'SSG',
  'gmarket': 'G마켓'
};

// 플랫폼별 그룹화
const groupedData = {};

response.items.forEach(item => {
  const platform = platformDisplayNames[item.platformName] || item.platformName;
  if (!groupedData[platform]) {
    groupedData[platform] = [];
  }
  groupedData[platform].push({
    id: item.wishlistItemId,
    image: item.imgUrl || 'https://via.placeholder.com/150',
    date: item.createdAt.split('T')[0], // ISO 형식에서 날짜만 추출
    name: item.productName,
    url: item.productUrl,
    liked: item.liked === 'true'
  });
});
```

### 4.5 삭제 기능
- 삭제 버튼 클릭 시 wishlistAPI.deleteWishlist 호출
- 삭제 성공 시 UI에서 해당 아이템 제거
- 삭제 실패 시 에러 메시지 표시

### 4.6 장바구니 담기 기능
- 장바구니 담기 버튼 클릭 시 cartAPI.addCart 호출
- 성공 시 안내 메시지 표시
- 실패 시 에러 메시지 표시

## 5. UI 상태

### 5.1 로딩 상태
- 스피너 또는 로딩 메시지 표시

### 5.2 에러 상태
- 에러 메시지 표시
- 재시도 버튼

### 5.3 빈 상태
- "찜한 상품이 없습니다." 메시지

### 5.4 데이터 표시
- 플랫폼별 섹션
- 상품 목록 (이미지, 상품명, 날짜)
- 장바구니 담기 버튼
- 삭제 버튼

## 6. 작업 체크리스트

- [x] services/wishlistAPI.js 생성
- [x] WishlistA.jsx 하드코딩 데이터 제거
- [x] API 호출 로직 추가 (useEffect)
- [x] 로딩 상태 UI 추가
- [x] 에러 상태 UI 추가
- [x] 응답 데이터 변환 로직 구현
- [x] 삭제 기능 API 연동
- [x] 장바구니 담기 기능 API 연동
