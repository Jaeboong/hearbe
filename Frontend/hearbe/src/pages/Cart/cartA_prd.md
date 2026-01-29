# 장바구니 API 연동 PRD

## 개요
하드코딩된 장바구니 데이터를 백엔드 API 연동으로 교체

## 현재 상태 분석

### Cart 디렉토리 파일 구성
- `CartA.jsx`: 하드코딩된 데이터를 사용하는 메인 장바구니 컴포넌트
- `CartA.css`: 스타일 파일

### 현재 구현의 문제점
1. 장바구니 데이터가 컴포넌트 state에 하드코딩됨 (11-37번째 줄)
2. 장바구니 조회 및 추가를 위한 API 연동 없음
3. 수량 변경 및 삭제가 로컬 state만 업데이트
4. 데이터 영속성 없음 (새로고침 시 데이터 손실)

## API 명세

### Base URL
환경변수 `VITE_API_BASE_URL` 사용

### 1. 장바구니에 상품 추가
**엔드포인트**: `/cart`
**메서드**: POST
**헤더**: 
- `Content-Type: application/json`
- `Authorization: Bearer {token}`

**요청 본문**:
```json
{
  "platformId": 1,
  "name": "농심 신라면 5입",
  "url": "https://www.coupang.com/vp/products/123",
  "img_url": "https://img.coupang.com/ramen.jpg",
  "price": 4500
}
```

**응답 (200)**:
```json
{
  "code": 200,
  "message": "장바구니에 추가되었습니다.",
  "data": {
    "cart_item_id": 1,
    "user_id": 1,
    "platform_id": 1,
    "name": "농심 신라면 5입",
    "price": 4500
  }
}
```

### 2. 장바구니 목록 조회
**엔드포인트**: `/cart`
**메서드**: GET
**헤더**: 
- `Authorization: Bearer {token}`

**응답 (200)**:
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [
      {
        "cart_item_id": 1,
        "user_id": 1,
        "platform_id": 1,
        "name": "농심 신라면 5입",
        "price": 4500
      }
    ]
  }
}
```

## 구현 변경사항

### 1. cartAPI.js 서비스 생성
위치: `src/services/cartAPI.js`
- `addToCart(itemData)` 메서드 구현
- `getCartItems()` 메서드 구현
- localStorage에서 인증 토큰 처리
- API 실패 시 에러 처리

### 2. CartA.jsx 업데이트
위치: `src/pages/Cart/CartA.jsx`
- 하드코딩된 장바구니 데이터 제거 (11-37번째 줄)
- 수량 관련 기능 제거 (quantity state, handleQuantityChange 함수, 수량 조절 버튼)
- 각 상품 이미지 앞에 체크박스 추가
- 사이트 이름 오른쪽에 "선택상품 결제하기" 버튼 추가
- "총 결제예정금액" 버튼 제거
- cartAPI 서비스를 사용한 API 연동 추가
- 컴포넌트 마운트 시 `getCartItems()`로 장바구니 아이템 조회
- API 응답을 현재 데이터 구조에 맞게 변환
- API 호출 중 로딩 상태 추가
- 에러 처리 및 사용자 피드백 추가

### 3. 데이터 변환
백엔드 응답을 현재 UI 구조에 맞게 변환 필요:
- `platform_id` 또는 플랫폼 이름으로 아이템 그룹화
- `cart_item_id`를 `id`로 매핑
- `img_url`을 `image`로 매핑
- 체크박스 선택 상태 관리를 위한 state 추가

## 검증 계획

### 수동 테스트
1. 장바구니 페이지 로드 시 API에서 아이템을 가져오는지 확인
2. 조회 중 로딩 상태가 표시되는지 확인
3. API 실패 시 에러 처리가 작동하는지 확인
4. 장바구니 아이템이 플랫폼별로 올바르게 그룹화되어 표시되는지 확인
5. 각 상품의 체크박스가 정상 작동하는지 확인
6. "선택상품 결제하기" 버튼이 체크된 상품만 처리하는지 확인
7. 삭제 버튼이 작동하는지 확인

### 브라우저 콘솔 검증
- Network 탭에서 `/cart` GET 요청 확인
- Authorization 헤더가 포함되어 있는지 확인
- 응답 데이터 구조가 명세와 일치하는지 확인
- 콘솔 에러가 없는지 확인
