# 장바구니 관리 PRD (C형)

## 개요
장바구니 목록 조회, 추가, 수량 수정 및 삭제 기능에 대한 명세입니다.

## 상세 기능
1. 장바구니 담기
   - Endpoint: POST /cart
   - Payload: platformId, name, quantity, url, img_url, price

2. 장바구니 목록 조회
   - Endpoint: GET /cart
   - Response: 장바구니 아이템 목록 (ID, 이름, 수량, 가격 등)

3. 장바구니 수량 수정
   - Endpoint: PATCH /cart/{cart_item_id}
   - Payload: quantity

4. 장바구니 삭제
   - Endpoint: DELETE /cart/{cart_item_id}
