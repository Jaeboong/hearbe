# 프로필 관리 PRD (C형)

## 개요
C형 사용자의 개인 정보를 조회하고 수정하는 기능에 대한 명세입니다.

## 상세 기능
1. 프로필 조회
   - Endpoint: GET /members/profile
   - Headers: Authorization: Bearer {token}
   - 조회 항목: 아이디, 이름, 사용자 유형, 전화번호, 성별, 생년월일, 키, 몸무게, 상의/하의/신발 사이즈, 알레르기 정보

2. 프로필 수정
   - Endpoint: PUT /members/profile
   - Headers: Authorization: Bearer {token}
   - 수정 가능 항목: 성별, 생년월일, 키, 몸무게, 상의/하의/신발 사이즈, 알레르기 목록(배열), 기타 알레르기
