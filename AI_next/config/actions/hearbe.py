"""
허비 39개 인텐트 액션 정의

KoELECTRA hearbe_v1.2 모델의 인텐트와 1:1 매핑
"""

from . import ActionDef, ActionStep

HEARBE_ACTIONS = [
    # ─── unknown ────────────────────────────────────────────
    ActionDef(
        intent="unknown",
        action_type="read",
        read_source="hardcoded",
        tts_template="죄송합니다, 무슨 말씀이신지 잘 모르겠습니다. 다시 한번 말씀해 주세요.",
    ),

    # ─── 네비게이션 (사이트 간) ──────────────────────────────
    ActionDef(
        intent="go_hearbe",
        action_type="action",
        tts_confirm="허비 홈으로 이동합니다.",
        steps=[
            ActionStep(tool_name="goto", url="https://i14d108.p.ssafy.io/main", description="허비 메인 이동"),
            ActionStep(tool_name="wait", ms=1500),
        ],
    ),
    ActionDef(
        intent="go_coupang",
        action_type="action",
        tts_confirm="쿠팡으로 이동합니다.",
        steps=[
            ActionStep(tool_name="goto", url="https://www.coupang.com/", description="쿠팡 메인 이동"),
            ActionStep(tool_name="wait", ms=1500),
        ],
    ),

    # ─── 허비 내부 네비게이션 ────────────────────────────────
    ActionDef(
        intent="go_mall",
        action_type="action",
        tts_confirm="쇼핑몰 선택 페이지로 이동합니다.",
        steps=[
            ActionStep(tool_name="goto", url_key="mall", description="쇼핑몰 페이지 이동"),
            ActionStep(tool_name="wait", ms=1200),
        ],
    ),
    ActionDef(
        intent="go_order_history",
        action_type="action",
        tts_confirm="주문 내역으로 이동합니다.",
        steps=[
            ActionStep(tool_name="goto", url_key="order_history", description="주문 내역 이동"),
            ActionStep(tool_name="wait", ms=1500),
        ],
    ),
    ActionDef(
        intent="click_cart",
        action_type="action",
        tts_confirm="장바구니로 이동합니다.",
        steps=[
            ActionStep(tool_name="goto", url_key="cart", description="장바구니 이동"),
            ActionStep(tool_name="wait", ms=1200),
        ],
    ),
    ActionDef(
        intent="click_my_page",
        action_type="action",
        tts_confirm="마이페이지로 이동합니다.",
        steps=[
            ActionStep(tool_name="goto", url_key="member_info", description="마이페이지 이동"),
            ActionStep(tool_name="wait", ms=1200),
        ],
    ),

    # ─── 메인 페이지 기능 ───────────────────────────────────
    ActionDef(
        intent="click_shared_shopping_entry",
        action_type="action",
        required_pages=["main"],
        tts_confirm="공유 쇼핑을 시작합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="mode_sharing", description="공유 쇼핑 모드 선택"),
            ActionStep(tool_name="wait", ms=1500),
        ],
    ),
    ActionDef(
        intent="click_app_download",
        action_type="read",
        read_source="hardcoded",
        tts_template="앱 다운로드는 현재 지원하지 않습니다.",
    ),

    # ─── 로그인 ─────────────────────────────────────────────
    ActionDef(
        intent="input_id",
        action_type="action",
        required_pages=["login"],
        params=["id_value"],
        tts_confirm="아이디를 입력합니다.",
        steps=[
            ActionStep(tool_name="fill", selector_key="id_input", value="{id_value}", description="아이디 입력"),
        ],
    ),
    ActionDef(
        intent="input_password",
        action_type="action",
        required_pages=["login"],
        params=["password_value"],
        tts_confirm="비밀번호를 입력합니다.",
        steps=[
            ActionStep(tool_name="fill", selector_key="password_input", value="{password_value}", description="비밀번호 입력"),
        ],
    ),
    ActionDef(
        intent="check_keep_login",
        action_type="action",
        required_pages=["login"],
        tts_confirm="로그인 유지를 체크합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="remember_me_checkbox", description="로그인 유지 체크"),
        ],
    ),
    ActionDef(
        intent="uncheck_keep_login",
        action_type="action",
        required_pages=["login"],
        tts_confirm="로그인 유지를 해제합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="remember_me_checkbox", description="로그인 유지 해제"),
        ],
    ),
    ActionDef(
        intent="click_login",
        action_type="action",
        required_pages=["login"],
        tts_confirm="로그인합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="login_button", description="로그인 버튼 클릭"),
            ActionStep(tool_name="wait", ms=2000),
        ],
    ),
    ActionDef(
        intent="click_find_id",
        action_type="action",
        required_pages=["login"],
        tts_confirm="아이디 찾기로 이동합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="find_id_link", description="아이디 찾기 클릭"),
            ActionStep(tool_name="wait", ms=1500),
        ],
    ),
    ActionDef(
        intent="click_find_password",
        action_type="action",
        required_pages=["login"],
        tts_confirm="비밀번호 찾기로 이동합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="find_password_link", description="비밀번호 찾기 클릭"),
            ActionStep(tool_name="wait", ms=1500),
        ],
    ),
    ActionDef(
        intent="click_signup",
        action_type="action",
        required_pages=["login"],
        tts_confirm="회원가입 페이지로 이동합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="signup_link", description="회원가입 클릭"),
            ActionStep(tool_name="wait", ms=1500),
        ],
    ),

    # ─── 회원가입 ───────────────────────────────────────────
    ActionDef(
        intent="click_check_id_duplicate",
        action_type="action",
        required_pages=["signup"],
        tts_confirm="아이디 중복 확인을 합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="username_check_button", description="중복확인 버튼 클릭"),
            ActionStep(tool_name="wait", ms=1000),
        ],
    ),
    ActionDef(
        intent="input_name",
        action_type="action",
        required_pages=["signup"],
        params=["name_value"],
        tts_confirm="이름을 입력합니다.",
        steps=[
            ActionStep(tool_name="fill", selector_key="name_input", value="{name_value}", description="이름 입력"),
        ],
    ),
    ActionDef(
        intent="input_email",
        action_type="action",
        required_pages=["signup"],
        params=["email_value"],
        tts_confirm="이메일을 입력합니다.",
        steps=[
            ActionStep(tool_name="fill", selector_key="email_input", value="{email_value}", description="이메일 입력"),
        ],
    ),
    ActionDef(
        intent="input_phone_number",
        action_type="action",
        required_pages=["signup"],
        params=["phone_value"],
        tts_confirm="전화번호를 입력합니다.",
        steps=[
            ActionStep(tool_name="fill", selector_key="phone_input", value="{phone_value}", description="전화번호 입력"),
        ],
    ),
    ActionDef(
        intent="input_password_confirm",
        action_type="action",
        required_pages=["signup"],
        params=["password_confirm_value"],
        tts_confirm="비밀번호를 다시 입력합니다.",
        steps=[
            ActionStep(tool_name="fill", selector_key="password_confirm_input", value="{password_confirm_value}", description="비밀번호 확인 입력"),
        ],
    ),
    ActionDef(
        intent="click_view_terms",
        action_type="action",
        required_pages=["signup"],
        tts_confirm="약관을 확인합니다.",
        steps=[
            ActionStep(tool_name="click_text", text="약관", description="약관 보기 클릭"),
            ActionStep(tool_name="wait", ms=1000),
        ],
    ),
    ActionDef(
        intent="check_terms_agreement",
        action_type="action",
        required_pages=["signup"],
        tts_confirm="약관에 동의합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="terms_checkbox", description="약관 전체 동의 체크"),
        ],
    ),
    ActionDef(
        intent="submit_signup",
        action_type="action",
        required_pages=["signup"],
        tts_confirm="회원가입을 완료합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="submit_button", description="회원가입 버튼 클릭"),
            ActionStep(tool_name="wait", ms=2000),
            ActionStep(tool_name="click", selector_key="modal_confirm", description="완료 확인 모달", optional=True),
        ],
    ),

    # ─── 읽기 ───────────────────────────────────────────────
    ActionDef(
        intent="read_current_page_actions",
        action_type="read",
        read_source="hardcoded",
    ),
    ActionDef(
        intent="read_hearbe_guide",
        action_type="read",
        read_source="hardcoded",
        tts_template="허비는 시각장애인을 위한 음성 기반 쇼핑 서비스입니다. 음성으로 상품 검색, 주문, 결제를 할 수 있습니다.",
    ),
    ActionDef(
        intent="read_terms",
        action_type="read",
        read_source="hardcoded",
        tts_template="이용약관 내용을 확인하시려면 약관 보기 버튼을 눌러주세요.",
    ),
    ActionDef(
        intent="read_available_marketplaces",
        action_type="read",
        required_pages=["mall"],
        read_source="hardcoded",
        tts_template="이용 가능한 쇼핑몰은 쿠팡, 네이버 쇼핑, 11번가입니다. 원하시는 쇼핑몰을 말씀해 주세요.",
    ),
    ActionDef(
        intent="read_page",
        action_type="read",
        read_source="hardcoded",
    ),
    ActionDef(
        intent="read_order_history_recent",
        action_type="read",
        required_pages=["order_history"],
        read_source="context:hearbe_order_history",
        tts_template="최근 주문 내역을 읽어드리겠습니다.",
    ),
    ActionDef(
        intent="read_frequent_products",
        action_type="read",
        required_pages=["order_history"],
        read_source="context:hearbe_frequent_products",
        tts_template="자주 구매한 상품을 읽어드리겠습니다.",
    ),
    ActionDef(
        intent="read_recommended_products",
        action_type="read",
        required_pages=["order_history"],
        read_source="context:hearbe_recommended_products",
        tts_template="추천 상품을 읽어드리겠습니다.",
    ),

    # ─── 쇼핑몰 선택 ───────────────────────────────────────
    ActionDef(
        intent="click_go_coupang",
        action_type="action",
        required_pages=["mall"],
        tts_confirm="쿠팡으로 이동합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="open_coupang", description="쿠팡 선택"),
            ActionStep(tool_name="wait", ms=2000),
        ],
    ),
    ActionDef(
        intent="click_product_view",
        action_type="action",
        tts_confirm="상품을 확인합니다.",
        steps=[
            ActionStep(tool_name="click_text", text="상품", description="상품 보기 클릭"),
            ActionStep(tool_name="wait", ms=1500),
        ],
    ),

    # ─── 마이페이지 기능 ────────────────────────────────────
    ActionDef(
        intent="click_logout",
        action_type="action",
        tts_confirm="로그아웃합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="logout", description="로그아웃 클릭", optional=True),
            ActionStep(tool_name="click_text", text="로그아웃", description="로그아웃 텍스트 클릭", optional=True),
            ActionStep(tool_name="wait", ms=1000),
            ActionStep(tool_name="click", selector_key="logout_confirm", description="로그아웃 확인", optional=True),
        ],
    ),
    ActionDef(
        intent="click_change_password",
        action_type="action",
        required_pages=["member_info"],
        tts_confirm="비밀번호 변경 페이지로 이동합니다.",
        steps=[
            ActionStep(tool_name="click_text", text="비밀번호 변경", description="비밀번호 변경 클릭"),
            ActionStep(tool_name="wait", ms=1500),
        ],
    ),
    ActionDef(
        intent="click_delete_account",
        action_type="action",
        required_pages=["member_info"],
        tts_confirm="회원 탈퇴 페이지로 이동합니다.",
        steps=[
            ActionStep(tool_name="click_text", text="회원 탈퇴", description="회원 탈퇴 클릭"),
            ActionStep(tool_name="wait", ms=1500),
        ],
    ),
    ActionDef(
        intent="click_order_detail",
        action_type="action",
        required_pages=["order_history"],
        params=["ordinal"],
        tts_confirm="{ordinal}번 주문 상세를 확인합니다.",
        steps=[
            ActionStep(tool_name="click", selector_key="order_detail_link", value="{ordinal}", description="주문 상세 클릭"),
            ActionStep(tool_name="wait", ms=1500),
        ],
    ),
]
