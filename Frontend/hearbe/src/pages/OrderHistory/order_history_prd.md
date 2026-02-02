# OrderHistory_A PRD

## 1. 개요

A형 주문내역 페이지. 사용자의 주문 이력을 플랫폼별로 그룹화하여 표시한다.

## 2. 현재 상태

### 2.1 파일 구조
```
OrderHistory_A/
  - OrderHistoryA.jsx    # 메인 컴포넌트
  - OrderHistoryA.css    # 스타일
```

### 2.2 하드코딩된 데이터 (제거 대상)
- OrderHistoryA.jsx line 11-59
- 쿠팡, 네이버 등 더미 주문 데이터가 useState로 하드코딩됨
- API 호출 로직 없음

## 3. API 명세

### 3.1 주문내역 조회
```
GET /orders/me
Authorization: Bearer {accessToken}
```

### 3.2 Response
```json
{
  "code": 200,
  "message": "성공적으로 처리되었습니다.",
  "data": {
    "orders": [
      {
        "order_id": 3,
        "ordered_at": "2026-01-29",
        "order_url": "https://www.coupang.com/vp/products/123",
        "platform_id": 1,
        "items": [
          {
            "name": "오뚜기 진라면 5입",
            "price": 4000,
            "quantity": 5,
            "url": "https://www.coupang.com/vp/products/123",
            "img_url": "https://img.coupang.com/ramen.jpg",
            "deliver_url": null
          }
        ]
      }
    ]
  }
}
```

### 3.3 Response 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| order_id | number | 주문 ID |
| ordered_at | string | 주문일자 (YYYY-MM-DD) |
| order_url | string | 주문 상세 페이지 URL |
| platform_id | number | 플랫폼 ID (1:쿠팡, 2:네이버, 3:11번가, 4:SSG) |
| items | array | 주문 상품 목록 |
| items[].name | string | 상품명 |
| items[].price | number | 상품 가격 |
| items[].quantity | number | 수량 |
| items[].url | string | 상품 URL |
| items[].img_url | string | 상품 이미지 URL |
| items[].deliver_url | string/null | 배송조회 URL (null이면 배송조회 불가) |

## 4. 구현 요구사항

### 4.1 API 서비스 (공통 로직)
- 위치: services/orderAPI.js
- A형, C형에서 공통으로 사용
- cartAPI.js와 동일한 패턴 적용

```javascript
// 사용법
import { orderAPI } from '../../services/orderAPI';

const response = await orderAPI.getOrders();
// response.data.orders 로 접근
```

### 4.2 에러 처리
| HTTP 상태 | 에러 메시지 |
|-----------|------------|
| 401 | 로그인이 필요합니다. |
| 403 | 접근 권한이 없습니다. |
| 404 | 주문내역을 찾을 수 없습니다. |
| 500+ | 서버 오류가 발생했습니다. |
| 네트워크 | 네트워크 연결을 확인해주세요. |

### 4.3 OrderHistoryA.jsx 수정
- 하드코딩 데이터 제거
- useEffect로 API 호출
- 로딩/에러 상태 처리
- platform_id를 플랫폼명으로 변환
- 날짜별, 플랫폼별 그룹화

### 4.4 데이터 변환 로직
```javascript
// API Response -> UI 데이터 변환
// platform_id 매핑
const platformNames = {
  1: '쿠팡',
  2: '네이버',
  3: '11번가',
  4: 'SSG'
};

// 플랫폼별 그룹화
response.data.orders를 platform_id별로 그룹화
```

### 4.5 배송조회 기능
- deliver_url이 null이 아니면 배송조회 버튼 활성화
- 클릭 시 deliver_url로 이동 (새 탭)

## 5. UI 상태

### 5.1 로딩 상태
- 스피너 또는 로딩 메시지 표시

### 5.2 에러 상태
- 에러 메시지 표시
- 재시도 버튼

### 5.3 빈 상태
- "주문내역이 없습니다." 메시지

### 5.4 데이터 표시
- 플랫폼별 섹션 (접기/펼치기 기능)
- 주문일자별 그룹
- 상품 목록 (이미지, 상품명, 가격, 수량)
- 배송조회 버튼

## 6. 작업 체크리스트

- [x] services/orderAPI.js 생성
- [x] OrderHistoryA.jsx 하드코딩 데이터 제거
- [x] API 호출 로직 추가 (useEffect)
- [x] 로딩 상태 UI 추가
- [x] 에러 상태 UI 추가
- [x] 응답 데이터 변환 로직 구현
- [x] 배송조회 버튼 deliver_url 연동
