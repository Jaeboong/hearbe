"""
쿠팡 28개 인텐트 액션 정의

KoELECTRA coupang_v1.1 모델의 인텐트와 1:1 매핑
"""

from . import ActionDef, ActionStep

COUPANG_ACTIONS = [
    # ─── unknown ────────────────────────────────────────────
    ActionDef(
        intent="unknown",
        action_type="read",
        read_source="hardcoded",
        tts_template="죄송합니다, 무슨 말씀이신지 잘 모르겠습니다. 다시 한번 말씀해 주세요.",
    ),

    # ─── 네비게이션 ─────────────────────────────────────────
    ActionDef(
        intent="go_hearbe",
        action_type="action",
        tts_confirm="허비 홈으로 이동합니다.",
        steps=[
            ActionStep(tool_name="goto", url="https://i14d108.p.ssafy.io/main", description="허비 홈 이동"),
            ActionStep(tool_name="wait", ms=1500),
        ],
    ),
    ActionDef(
        intent="click_order_history",
        action_type="action",
        tts_confirm="주문 내역으로 이동합니다.",
        steps=[
            ActionStep(tool_name="goto", url_key="mypage", description="마이쿠팡(주문내역) 이동"),
            ActionStep(tool_name="wait", ms=2000),
        ],
    ),
    ActionDef(
        intent="click_cart",
        action_type="action",
        tts_confirm="장바구니로 이동합니다.",
        steps=[
            ActionStep(tool_name="goto", url_key="cart", description="장바구니 이동"),
            ActionStep(tool_name="wait", ms=1500),
        ],
    ),
    ActionDef(
        intent="click_login",
        action_type="action",
        tts_confirm="로그인 페이지로 이동합니다.",
        steps=[
            ActionStep(tool_name="goto", url_key="login", description="로그인 페이지 이동"),
            ActionStep(tool_name="wait", ms=1500),
        ],
    ),
    ActionDef(
        intent="click_logout",
        action_type="action",
        tts_confirm="로그아웃합니다.",
        steps=[
            ActionStep(tool_name="click_text", text="로그아웃", description="로그아웃 클릭"),
        ],
    ),

    # ─── 검색 ───────────────────────────────────────────────
    ActionDef(
        intent="search_products",
        action_type="composite",
        params=["query"],
        tts_confirm="'{query}'를 검색합니다.",
        steps=[
            ActionStep(tool_name="goto", url_key="home", description="쿠팡 메인 이동", optional=True),
            ActionStep(tool_name="wait", ms=1000, optional=True),
            ActionStep(tool_name="fill", selector_key="search_input", value="{query}", description="검색어 입력"),
            ActionStep(tool_name="press", selector_key="search_input", key="Enter", description="검색 실행"),
            ActionStep(tool_name="wait", ms=2000),
        ],
    ),

    # ─── 검색 결과 ──────────────────────────────────────────
    ActionDef(
        intent="read_search_results",
        action_type="read",
        required_pages=["search"],
        read_source="context:search_results",
        tts_template="검색 결과를 읽어드리겠습니다.",
    ),
    ActionDef(
        intent="select_search_result",
        action_type="composite",
        required_pages=["search"],
        params=["ordinal"],
        tts_confirm="{ordinal}번 상품을 선택합니다.",
        steps=[
            ActionStep(
                tool_name="click",
                selector_key="product_item",
                value="{ordinal}",  # executor에서 nth-of-type로 변환
                description="검색 결과 N번째 상품 클릭",
            ),
            ActionStep(tool_name="wait", ms=2000),
        ],
    ),

    # ─── 상품 상세 ──────────────────────────────────────────
    ActionDef(
        intent="read_product_info",
        action_type="read",
        required_pages=["product"],
        read_source="context:product_detail",
        tts_template="상품 정보를 읽어드리겠습니다.",
    ),
    ActionDef(
        intent="update_product_option",
        action_type="composite",
        required_pages=["product"],
        params=["option_text"],
        tts_confirm="옵션을 변경합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="option_select", description="옵션 선택 열기", optional=True),
            ActionStep(tool_name="wait", ms=500, optional=True),
            ActionStep(tool_name="click_text", text="{option_text}", description="옵션 선택"),
            ActionStep(tool_name="wait", ms=1000),
        ],
    ),
    ActionDef(
        intent="click_add_to_cart",
        action_type="action",
        required_pages=["product"],
        tts_confirm="장바구니에 담겠습니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="add_to_cart", description="장바구니 담기 클릭"),
            ActionStep(tool_name="wait", ms=1500),
        ],
    ),
    ActionDef(
        intent="click_buy_now",
        action_type="action",
        required_pages=["product"],
        tts_confirm="바로 구매를 진행합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="buy_now", description="바로 구매 클릭"),
            ActionStep(tool_name="wait", ms=2000),
        ],
    ),
    ActionDef(
        intent="read_reviews",
        action_type="read",
        required_pages=["product"],
        read_source="context:reviews",
        tts_template="리뷰를 읽어드리겠습니다.",
    ),
    ActionDef(
        intent="click_wishlist",
        action_type="action",
        required_pages=["product"],
        tts_confirm="찜 목록에 추가합니다.",
        steps=[
            ActionStep(tool_name="click_text", text="찜", description="찜하기 클릭"),
            ActionStep(tool_name="wait", ms=1000),
        ],
    ),
    ActionDef(
        intent="read_option_info",
        action_type="read",
        required_pages=["product"],
        read_source="context:product_detail",
        tts_template="옵션 정보를 읽어드리겠습니다.",
    ),

    # ─── 장바구니 ───────────────────────────────────────────
    ActionDef(
        intent="read_cart_items",
        action_type="read",
        required_pages=["cart"],
        read_source="context:cart_items",
        tts_template="장바구니 내용을 읽어드리겠습니다.",
    ),
    ActionDef(
        intent="select_cart_item",
        action_type="action",
        required_pages=["cart"],
        params=["ordinal"],
        tts_confirm="{ordinal}번 상품을 선택합니다.",
        steps=[
            ActionStep(
                tool_name="click",
                selector_key="item_checkbox",
                value="{ordinal}",
                description="장바구니 N번째 상품 체크",
            ),
        ],
    ),
    ActionDef(
        intent="unselect_cart_item",
        action_type="action",
        required_pages=["cart"],
        params=["ordinal"],
        tts_confirm="{ordinal}번 상품 선택을 해제합니다.",
        steps=[
            ActionStep(
                tool_name="click",
                selector_key="item_checkbox",
                value="{ordinal}",
                description="장바구니 N번째 상품 체크 해제",
            ),
        ],
    ),
    ActionDef(
        intent="adjust_item_quantity",
        action_type="composite",
        required_pages=["cart"],
        params=["quantity"],
        tts_confirm="수량을 {quantity}개로 변경합니다.",
        steps=[
            # executor에서 현재 수량 대비 +/- 버튼 클릭 횟수 계산
            ActionStep(tool_name="click", selector_key="quantity_plus", value="{quantity}", description="수량 변경"),
        ],
    ),

    # ─── 결제 ───────────────────────────────────────────────
    ActionDef(
        intent="read_order_amount",
        action_type="read",
        required_pages=["cart", "checkout"],
        read_source="context:order_amount",
        tts_template="결제 금액을 읽어드리겠습니다.",
    ),
    ActionDef(
        intent="read_payment_order_info",
        action_type="read",
        required_pages=["checkout"],
        read_source="context:payment_info",
        tts_template="주문 정보를 읽어드리겠습니다.",
    ),
    ActionDef(
        intent="submit_payment",
        action_type="action",
        required_pages=["checkout"],
        tts_confirm="결제를 진행합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="pay_button", description="결제하기 버튼 클릭"),
            ActionStep(tool_name="wait", ms=3000),
        ],
    ),

    # ─── 주문 내역 ──────────────────────────────────────────
    ActionDef(
        intent="read_order_detail",
        action_type="read",
        required_pages=["orderlist", "orderdetail"],
        read_source="context:order_list",
        tts_template="주문 내역을 읽어드리겠습니다.",
    ),
    ActionDef(
        intent="click_track_delivery",
        action_type="action",
        required_pages=["orderdetail"],
        tts_confirm="배송 조회를 합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="track_delivery", description="배송 조회 클릭"),
            ActionStep(tool_name="wait", ms=2000),
        ],
    ),
    ActionDef(
        intent="request_exchange_return",
        action_type="action",
        required_pages=["orderdetail"],
        tts_confirm="교환 반품을 신청합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="exchange_return", description="교환/반품 신청 클릭"),
            ActionStep(tool_name="wait", ms=2000),
        ],
    ),
    ActionDef(
        intent="delete_order_history",
        action_type="action",
        required_pages=["orderdetail"],
        tts_confirm="주문 내역을 삭제합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="delete_order", description="주문 내역 삭제 클릭"),
            ActionStep(tool_name="wait", ms=1000),
        ],
    ),

    # ─── 현재 페이지 정보 ───────────────────────────────────
    ActionDef(
        intent="read_current_page_actions",
        action_type="read",
        read_source="hardcoded",
    ),
]
