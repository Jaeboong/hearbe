"""
Read 액션 핸들러

read 타입 인텐트의 TTS 출력 텍스트를 생성합니다.
- hardcoded: 페이지별 고정 설명
- context:*: 세션 컨텍스트에서 데이터 포맷팅
"""

import logging
from typing import Optional, Dict, Any, List

from config.actions import ActionDef

logger = logging.getLogger(__name__)

# ── 페이지별 고정 설명 ──────────────────────────────────────

PAGE_DESCRIPTIONS = {
    "coupang": {
        "main": "쿠팡 메인 페이지입니다. 검색, 장바구니, 로그인, 주문내역 확인이 가능합니다.",
        "search": "검색 결과 페이지입니다. 상품을 선택하거나, 검색 결과를 읽어달라고 말씀해 주세요.",
        "product": "상품 상세 페이지입니다. 장바구니 담기, 바로 구매, 옵션 변경, 리뷰 확인이 가능합니다.",
        "cart": "장바구니 페이지입니다. 상품 선택, 수량 변경, 결제하기가 가능합니다.",
        "login": "로그인 페이지입니다. 이메일 또는 휴대폰 번호로 로그인할 수 있습니다.",
        "checkout": "결제 페이지입니다. 결제하기 버튼을 눌러 결제를 진행할 수 있습니다.",
        "signup": "회원가입 페이지입니다. 이메일, 비밀번호, 이름, 휴대폰 번호를 입력해 주세요.",
        "orderlist": "주문 목록 페이지입니다. 주문 상세 보기, 배송 조회, 교환 반품 신청이 가능합니다.",
        "orderdetail": "주문 상세 페이지입니다. 배송 조회, 교환 반품 신청, 주문 취소가 가능합니다.",
    },
    "hearbe": {
        "main": "허비 메인 페이지입니다. 음성 안내 쇼핑, 큰 글씨 쇼핑, 일반 쇼핑, 공유 쇼핑 모드를 선택할 수 있습니다.",
        "login": "로그인 페이지입니다. 아이디와 비밀번호를 입력하고 로그인할 수 있습니다. 회원가입, 아이디 찾기, 비밀번호 찾기도 가능합니다.",
        "signup": "회원가입 페이지입니다. 아이디, 비밀번호, 이름, 이메일, 전화번호를 입력하고 가입할 수 있습니다.",
        "mall": "쇼핑몰 선택 페이지입니다. 쿠팡, 네이버 쇼핑, 11번가 중 원하시는 쇼핑몰을 말씀해 주세요.",
        "member_info": "회원 정보 페이지입니다. 비밀번호 변경, 회원 탈퇴, 주문 내역 확인이 가능합니다.",
        "order_history": "주문 내역 페이지입니다. 최근 주문, 자주 구매한 상품, 추천 상품을 확인할 수 있습니다.",
        "hearbe_cart": "장바구니 페이지입니다.",
    },
}


class ReadHandler:
    """read 타입 인텐트의 TTS 텍스트 생성"""

    def handle(
        self,
        action_def: ActionDef,
        site_id: str,
        page_type: Optional[str],
        session_context: Dict[str, Any],
        params: Dict[str, Any],
    ) -> Optional[str]:
        source = action_def.read_source or ""

        # hardcoded 또는 read_current_page_actions
        if source == "hardcoded" or action_def.intent in ("read_current_page_actions", "read_page"):
            text = self._read_hardcoded(site_id, page_type, action_def)
            return text

        # 컨텍스트 기반
        if source.startswith("context:"):
            context_key = source.split(":", 1)[1]
            return self._read_from_context(context_key, action_def, session_context, params)

        # 템플릿만 있는 경우
        if action_def.tts_template:
            return self._substitute(action_def.tts_template, params)

        return None

    def _read_hardcoded(self, site_id: str, page_type: Optional[str], action_def: ActionDef) -> str:
        # 액션에 고정 템플릿이 있으면 우선 사용
        if action_def.tts_template:
            return action_def.tts_template

        site_descs = PAGE_DESCRIPTIONS.get(site_id, {})
        desc = site_descs.get(page_type or "", None)
        if desc:
            return desc
        return "현재 페이지에서 어떤 작업을 원하시나요?"

    def _read_from_context(
        self,
        context_key: str,
        action_def: ActionDef,
        session_context: Dict[str, Any],
        params: Dict[str, Any],
    ) -> Optional[str]:
        data = session_context.get(context_key)
        if not data:
            return "현재 표시된 데이터가 없습니다. 먼저 해당 페이지로 이동해 주세요."

        if context_key == "search_results":
            return self._format_search_results(data)
        elif context_key == "cart_items":
            return self._format_cart_items(data)
        elif context_key == "product_detail":
            return self._format_product_detail(data)
        elif context_key == "order_list":
            return self._format_order_list(data)
        elif context_key in ("hearbe_order_history", "hearbe_frequent_products", "hearbe_recommended_products"):
            return self._format_list_data(data, context_key)

        return str(data)

    def _format_search_results(self, results: List[Dict]) -> str:
        if not results:
            return "검색 결과가 없습니다."
        total = len(results)
        max_read = 5
        lines = []
        for idx, item in enumerate(results[:max_read], 1):
            name = item.get("name", "상품")
            price = item.get("price", "")
            line = f"{idx}번. {name}"
            if price:
                line += f", 가격 {price}"
            lines.append(line)
        text = f"검색 결과 {total}개 중 상위 {min(total, max_read)}개입니다. "
        text += ". ".join(lines) + "."
        return text

    def _format_cart_items(self, items: List[Dict]) -> str:
        if not items:
            return "장바구니가 비어 있습니다."
        lines = []
        for idx, item in enumerate(items, 1):
            name = item.get("name", "상품")
            price = item.get("price", "")
            qty = item.get("quantity", 1)
            line = f"{idx}번. {name}"
            if price:
                line += f", {price}원"
            if qty and int(qty) > 1:
                line += f", {qty}개"
            lines.append(line)
        return f"장바구니에 {len(items)}개 상품이 있습니다. " + ". ".join(lines) + "."

    def _format_product_detail(self, detail: Dict) -> str:
        name = detail.get("name") or detail.get("title", "상품")
        price = detail.get("price", "")
        discount = detail.get("discount_rate", "")
        delivery = detail.get("delivery", "")
        text = f"상품명은 {name}입니다."
        if price:
            text += f" 가격은 {price}원입니다."
        if discount:
            text += f" 할인율 {discount}."
        if delivery:
            text += f" 배송 정보: {delivery}."
        options = detail.get("options_list") or detail.get("options")
        if options and isinstance(options, list):
            text += f" 선택 가능한 옵션이 {len(options)}개 있습니다."
        return text

    def _format_order_list(self, orders: List[Dict]) -> str:
        if not orders:
            return "주문 내역이 없습니다."
        lines = []
        for idx, order in enumerate(orders[:5], 1):
            name = order.get("name", "상품")
            date = order.get("ordered_at") or order.get("date", "")
            status = order.get("status", "")
            line = f"{idx}번. {name}"
            if date:
                line += f", {date}"
            if status:
                line += f", {status}"
            lines.append(line)
        return f"주문 내역이 {len(orders)}건 있습니다. " + ". ".join(lines) + "."

    def _format_list_data(self, data: Any, key: str) -> str:
        if isinstance(data, list):
            if not data:
                return "데이터가 없습니다."
            lines = []
            for idx, item in enumerate(data[:5], 1):
                if isinstance(item, dict):
                    name = item.get("name") or item.get("product_name", "상품")
                    lines.append(f"{idx}번. {name}")
                else:
                    lines.append(f"{idx}번. {item}")
            return ". ".join(lines) + "."
        return str(data)

    @staticmethod
    def _substitute(template: str, params: Dict[str, Any]) -> str:
        if not params:
            return template
        result = template
        for key, value in params.items():
            if value is not None:
                result = result.replace(f"{{{key}}}", str(value))
        return result
