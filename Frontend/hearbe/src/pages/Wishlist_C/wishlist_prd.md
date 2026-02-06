# 찜(Wishlist) 관리 PRD (C형)

## 개요
상품 브라우저에서 상품을 찜 목록에 추가하거나 목록을 조회 및 삭제하는 기능에 대한 명세입니다.

## 상세 기능
1. 찜 추가
   - Endpoint: POST /wishlist
   - Payload: platformId, name, price, url, img_url

2. 찜 목록 조회
   - Endpoint: GET /wishlist
   - Response: 찜 아이템 목록

3. 찜 삭제
   - Endpoint: DELETE /wishlist/{wishlist_item_id}
