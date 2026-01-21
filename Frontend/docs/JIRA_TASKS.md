# Frontend 개발 지라 이슈 작업 목록

> 생성일: 2026-01-21  
> 기반 문서: Frontend/docs 기능명세서 및 API 명세서

---

## 문서 개요

본 문서는 Frontend/docs 디렉토리에 있는 기능명세서와 API 명세서를 분석하여 지라 이슈로 등록할 작업 목록을 정리한 문서입니다.

### 분석된 문서
- **기능명세서**: 142개 기능 항목 (PAGE, MCP, AI 시스템 포함)
- **API 명세서**: 7개 카테고리 API 정의
- **와이어프레임**: 36개 PDF 화면 설계서

---

## 1. 인증/사용자 관리 (Authentication & User Management)

### 우선순위: 높음

#### API-AUTH-001: 로그인 기능
- **담당자**: 강한솔
- **설명**: 사용자 로그인 API 구현
- **API**: `POST /auth/login`
- **Request**: RequestLogin
- **상태**: 해야 할 일
- **참조**: PAGE-201

#### API-AUTH-002: 로그아웃 기능
- **담당자**: 강한솔
- **설명**: 사용자 로그아웃 API 구현
- **API**: `POST /auth/logout`
- **상태**: 해야 할 일

#### API-AUTH-003: 사용자 정보 조회
- **담당자**: 강한솔
- **설명**: 마이페이지 사용자 정보 조회 API
- **API**: `GET /auth/mypage`
- **Response**: ResponseMypage
- **상태**: 해야 할 일
- **참조**: PAGE-401

#### API-AUTH-004: 회원가입 (시각장애인용)
- **담당자**: 강한솔
- **설명**: 시각장애인용 회원가입 페이지 및 API
- **API**: `POST /auth/regist`
- **Request**: RequestUserRegist
- **Response**: ResponseRegist
- **특징**: 
  - 음성 입력 지원
  - 숫자 6자리 비밀번호
  - 장애인 복지 카드 등록
- **상태**: 해야 할 일
- **참조**: PAGE-301

#### API-AUTH-005: 회원가입 (일반용)
- **담당자**: 서해령
- **설명**: 일반 사용자용 회원가입 페이지 및 API
- **API**: `POST /auth/regist`
- **특징**: 
  - 8~12자리 영문+숫자 비밀번호
  - 비밀번호 확인 필드
- **상태**: 해야 할 일
- **참조**: PAGE-302

#### API-AUTH-006: 비밀번호 찾기
- **담당자**: 강한솔 (시각장애인용), 서해령 (일반용)
- **API**: `POST /user/findPassword`
- **참조**: PAGE-204, PAGE-205

#### API-AUTH-007: 아이디 찾기
- **담당자**: 강한솔 (시각장애인용), 서해령 (일반용)
- **API**: `POST /user/findId`
- **특징**:
  - 시각장애인용: 장애인 복지 카드 OCR 인증
  - 일반용: 이메일 인증번호
- **참조**: PAGE-202, PAGE-203

#### API-AUTH-008: 프로필 수정
- **API**: `PATCH /users/{id}`
- **Request**: RequestUpdateProfile

#### API-AUTH-009: 로그인 ID 변경
- **API**: `PATCH /users/{id}/login_id`
- **Request**: RequestUpdateId

#### API-AUTH-010: 비밀번호 변경
- **API**: `PATCH /users/{id}/password`
- **Request**: RequestUpdatePassword

---

## 2. 상품 검색 및 플랫폼 (Product & Platform)

### 우선순위: 높음

#### API-PRODUCT-001: 상품 상세 조회
- **설명**: 개별 상품의 상세 정보 조회
- **API**: `GET /products/{product_id}`
- **Response**: ResponseProduct

#### API-PRODUCT-002: 플랫폼별 상품 동기화
- **설명**: 외부 쇼핑몰 상품 정보 동기화 (쿠팡, 네이버 등)
- **API**: `POST /products/sync`
- **Request**: RequestSyncProducts
- **Response**: ResponseSyncProducts
- **특징**: last_synced_at 기반 갱신

#### API-PRODUCT-003: 플랫폼 목록 조회
- **설명**: 지원 가능한 쇼핑몰 목록 조회
- **API**: `GET /platforms`
- **Response**: ResponsePlatforms
- **지원 플랫폼**: 쿠팡, 네이버쇼핑, 11번가, G마켓, 컬리

---

## 3. 장바구니 (Shopping Cart)

### 우선순위: 높음

#### API-CART-001: 장바구니 담기
- **담당자**: 강한솔
- **API**: `POST /cart`
- **Request**: RequestCart
- **Response**: ResponseCart

#### API-CART-002: 장바구니 목록 조회
- **담당자**: 강한솔
- **설명**: 플랫폼 통합 장바구니 목록 조회
- **API**: `GET /cart`
- **Response**: ResponseCartList
- **참조**: PAGE-501

#### API-CART-003: 장바구니 수량 조절
- **담당자**: 강한솔
- **설명**: 음성 명령으로 상품 수량 변경
- **API**: `PATCH /cart/{cart_item_id}`
- **Request**: RequestCartUpdate
- **Response**: ResponseCartUpdate
- **특징**: 음성 명령 지원 (예: "물티슈 수량 2개로 늘려줘")
- **참조**: PAGE-503

#### API-CART-004: 장바구니 삭제
- **담당자**: 강한솔
- **API**: `DELETE /cart/{cart_item_id}`

---

## 4. 찜 목록 (Wishlist)

### 우선순위: 중간

#### API-WISH-001: 찜 추가
- **API**: `POST /wishlist`
- **Request**: RequestWishlistCreate
- **Response**: ResponseWishlistCreate

#### API-WISH-002: 찜 목록 조회
- **API**: `GET /wishlist`
- **Response**: ResponseWishlist
- **인증**: Bearer Token 필요

#### API-WISH-003: 찜 삭제
- **API**: `DELETE /wishlist/{wishlistItemId}`
- **인증**: Bearer Token 필요

#### API-WISH-004: 상품 찜 여부 확인
- **API**: `GET /wishlist/check`
- **Response**: ResponseWishlistCheck

---

## 5. 즐겨찾기 (Favorites)

### 우선순위: 높음

#### API-FAV-001: 즐겨찾기 등록
- **담당자**: 강한솔
- **설명**: One-touch 재구매를 위한 즐겨찾기 등록
- **API**: `POST /favorites`
- **Request**: RequestFavorites
- **Response**: ResponseFavorites
- **특징**: 최근 12개월 동안 2번 이상 구매한 상품 자동 추천
- **참조**: PAGE-402

#### API-FAV-002: 즐겨찾기 목록 조회
- **API**: `GET /favorites`
- **Response**: ResponseFavoriteList

#### API-FAV-003: 즐겨찾기 실행
- **설명**: 음성 명령으로 즐겨찾기 상품 재구매
- **API**: `POST /favorites/{id}/execute`
- **Request**: RequestExecute
- **Response**: ResponseExecute

#### API-FAV-004: 즐겨찾기 해제
- **API**: `DELETE /favorites/{id}`

---

## 6. 주문 및 결제 (Orders & Payment)

### 우선순위: 높음

#### API-ORDER-001: 주문 생성
- **담당자**: 강한솔
- **API**: `POST /orders`
- **Request**: RequestOrders
- **Response**: ResponseOrders
- **특징**:
  - 시각장애인용: 비밀번호 앞 4자리 또는 지문 결제
  - 일반용: 간편 비밀번호 음성 인식
- **참조**: PAGE-405, PAGE-624, PAGE-724

#### API-ORDER-002: 주문 내역 조회
- **담당자**: 강한솔
- **API**: `GET /orders/me`
- **Response**: ResponseMe

#### PAGE-502: 선택적 구매 기능
- **담당자**: 강한솔
- **설명**: 특정 판매처별 구매 또는 개별 상품 선택 제어
- **예시**: "쿠팡 장바구니만 결제해줘"

#### PAGE-504: 전체 구매 기능
- **담당자**: 강한솔
- **설명**: 모든 플랫폼의 장바구니 상품 순차 결제

---

## 7. 보호자 공유 세션 (Sharing Session)

### 우선순위: 높음

#### API-SHARE-001: 공유 세션 시작
- **담당자**: 서해령
- **설명**: WebRTC 실시간 화면 공유 시작
- **API**: `POST /sharing/sessions`
- **Request**: RequestSessions
- **Response**: ResponseSessions (4자리 공유 코드 발급)
- **참조**: PAGE-816

#### API-SHARE-002: 세션 참가
- **담당자**: 서해령
- **API**: `POST /sharing/sessions/join`
- **Request**: RequestSessionsJoin
- **Response**: ResponseSessionsJoin

#### API-SHARE-003: 세션 종료
- **담당자**: 서해령
- **API**: `PATCH /sharing/sessions/{id}/end`
- **Response**: ResponseSessionsEnd

---

## 8. 페이지 개발 (Pages)

### 8.1 메인 페이지

#### PAGE-101: 메인 페이지
- **담당자**: 서해령
- **우선순위**: 중요
- **기능**:
  - 마이크 권한 요청 팝업
  - A(Audio): 시각장애인용 회원가입
  - B(Big), C(Common): 일반용 회원가입
  - S(Sharing): 원격 공유 페이지

### 8.2 마이페이지

#### PAGE-401: 마이페이지 메인
- **담당자**: 강한솔
- **우선순위**: 중요
- **기능**: "OO님 안녕하세요, 배송 중인 상품이 1건 있습니다" TTS 안내

#### PAGE-402: 즐겨찾기 / 찜한 상품
- **담당자**: 강한솔
- **우선순위**: 중요

#### PAGE-403: 사이즈 정보 (기억 정보)
- **담당자**: 강한솔
- **우선순위**: 보통
- **기능**: 사용자 키, 몸무게, 평소 사이즈 저장 → 적합 사이즈 자동 추천

#### PAGE-405: 배송/결제 정보
- **담당자**: 강한솔
- **우선순위**: 보통
- **기능**: 
  - 지문/비밀번호 앞 4자리 결제
  - 주소 별칭 관리 ('우리집', '회사' 등)

#### PAGE-611: 회원정보 (시각장애인용)
- **담당자**: 강한솔
- **우선순위**: 보통

#### PAGE-612: 마이페이지 상세
- **담당자**: 강한솔
- **우선순위**: 보통

### 8.3 쇼핑 페이지

#### PAGE-621: 쇼핑사이트 선택 (시각장애인용)
- **담당자**: 강한솔
- **우선순위**: 보통
- **기능**:
  - 노랑/검정 대비 버튼 (시각장애인 시야 인식 최적화)
  - TTS 쇼핑사이트 음성 안내
  - STT 음성 선택

#### PAGE-622: 쇼핑사이트 화면
- **담당자**: 강한솔
- **우선순위**: 보통
- **기능**:
  - 공유 버튼: WebRTC 실시간 화면 전송
  - MCP 서버 연결된 쇼핑사이트 창
  - 장바구니 URL DB 저장

#### PAGE-623: 장바구니 화면
- **담당자**: 강한솔
- **우선순위**: 보통

#### PAGE-624: 결제창 (시각장애인용)
- **담당자**: 강한솔
- **우선순위**: 보통
- **기능**:
  - 첫 결제: 장애인 복지 카드 인식
  - 이후 결제: 간편 비밀번호 4자리

### 8.4 일반용 페이지

#### PAGE-711: 회원가입 및 로그인
- **담당자**: 서해령
- **우선순위**: 보통

#### PAGE-712: 회원정보
- **담당자**: 서해령
- **우선순위**: 보통

#### PAGE-713: 마이페이지
- **담당자**: 서해령
- **우선순위**: 보통

#### PAGE-721 ~ 724: 쇼핑 플로우
- **담당자**: 서해령
- **우선순위**: 보통

### 8.5 확대 버전 (B형)

#### PAGE-801 ~ 802: 회원정보 & 마이페이지
- **담당자**: 서해령
- **우선순위**: 보통

#### PAGE-811: 쇼핑몰 선택 (확대)
- **담당자**: 서해령
- **우선순위**: 보통
- **기능**: 로고 → 텍스트 버튼, 클릭 시 음성 안내

#### PAGE-812: 확대 쇼핑 뷰
- **담당자**: 서해령
- **우선순위**: 보통
- **기능**: 
  - 상품 이미지/가격 화면의 80% 이상 확대
  - 공유 코드 4자리 크게 표시 + TTS

#### PAGE-813: 통합 장바구니
- **담당자**: 서해령
- **우선순위**: 보통
- **기능**: 
  - 쇼핑몰별 구분선 굵게
  - 한 화면에 최대 2개 버튼 (오클릭 방지)

#### PAGE-814: 간편결제 (확대)
- **담당자**: 서해령
- **우선순위**: 보통
- **기능**: 
  - 대형 4자리 숫자 패드
  - 입력 시 시각 효과 + 음성 안내

#### PAGE-815: 포커스 가이드
- **담당자**: 서해령
- **우선순위**: 중요
- **기능**: 보호자가 특정 위치 지정 → 자동 스크롤 + 외곽선 강조

#### PAGE-816: 1:1 공유 화면 (S형)
- **담당자**: 서해령
- **우선순위**: 중요
- **기능**:
  - user1 공유화면을 user2가 원격 제어
  - 마지막 키워드 기반 관련 설명 정리
  - user2 음성 → 텍스트 변환

---

## 9. 추가 고려 사항

### 미정 사항

#### MISC-01: 결제 전 최종 확인
- **설명**: 결제/회원가입 전 최종 확인 단계 강제 삽입
- **비고**: OCR 이후 정보 제공 등 복합 단위 고려 필요
- **단위 시스템 지정 필요**

#### MISC-02: 세션 관리
- **설명**: 세션 상태 저장 (사이트/진행단계/검색기록) + 대명사 참조
- **비고**: 세션 위치와 저장 방식 결정 필요
- **단위 시스템 지정 필요**

---

## 10. 와이어프레임 참조 (36개 PDF)

### A형 (시각장애인용)
- 로그인/회원가입: a형-로그인, a형 회원가입1, a형 회원가입2
- 아이디/비밀번호 찾기: A형 아이디찾기1~4, A형-비밀번호2~4
- 쇼핑: a형 쇼핑창 1~1-2, A_shopping
- 마이페이지: A_mypage1~2
- 주문/결제: A_order1~2, A형 결제2
- 즐겨찾기: A_favorite1, A_fvorite2, A_frequence1~2
- 기억: A_remember1_1, A_remember2_2
- 장바구니: A_mycart
- 기타 이미지: image 16, 28, 31~33, 36, 43

---

## 11. 작업 우선순위 요약

### 최우선 (Sprint 1)
1. **인증 시스템 페이지**: 로그인, 회원가입 (시각장애인용/일반용)
2. **메인 페이지**: 마이크 권한, 타입 선택 (A/B/C/S)
3. **API 연동 기반**: 인증, 플랫폼 목록 조회
4. **쇼핑사이트 선택 페이지**: 플랫폼 버튼, TTS/STT 지원

### 높음 (Sprint 2)
1. **장바구니 페이지**: 통합 장바구니, 수량 조절, 삭제
2. **즐겨찾기 페이지**: One-touch 재구매 기능
3. **주문/결제 페이지**: 간편 결제, 주문 내역
4. **공유 세션 페이지**: WebRTC 화면 공유, 1:1 원격 제어

### 보통 (Sprint 3 이후)
1. **찜 목록 페이지**: CRUD 기능
2. **마이페이지**: 사이즈 정보, 배송 정보, 회원정보 수정
3. **확대 버전 (B형)**: 대형 UI, 간편 결제 숫자 패드
4. **포커스 가이드**: 보호자 지정 영역 자동 스크롤

---

## 12. 참고사항

- **담당자 구분**:
  - **강한솔**: 시각장애인용(A형) 페이지 및 기능
  - **서해령**: 일반용(B, C형) 페이지 및 공유 기능

- **페이지 버전**:
  - **A형 (Audio)**: 시각장애인용 - 음성 중심, 노랑/검정 대비, TTS/STT 지원
  - **B형 (Big)**: 확대 버전 - 대형 UI, 80% 이상 확대 표시
  - **C형 (Common)**: 일반 사용자용 - 표준 UI
  - **S형 (Sharing)**: 공유 기능 - WebRTC 실시간 화면 공유

- **API 상태 코드**:
  - 200: 성공
  - 201: 생성 성공
  - 400: 잘못된 요청
  - 401: 인증 실패
  - 403: 권한 없음
  - 404: 리소스 없음
  - 500: 서버 오류

- **주요 기술**:
  - WebRTC (화면 공유)
  - TTS/STT (음성 인터페이스)
  - 반응형 디자인 (확대/축소)
  - 접근성 (WCAG 준수)
