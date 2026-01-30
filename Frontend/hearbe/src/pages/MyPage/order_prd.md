# 주문 관리 PRD (C형)

## 개요
주문 생성 및 내 주문 목록 조회 기능에 대한 명세입니다.

## 상세 기능
1. 주문 생성
   - Endpoint: POST /orders
   - Payload: platformId, name, url, img_url, price, quantity

2. 내 주문 조회
   - Endpoint: GET /orders/me
   - Response: 주문 번호, 결제 상태, 주문 시간, 아이템 정보 포함 목록
