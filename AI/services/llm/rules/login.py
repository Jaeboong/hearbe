"""
Login rules (ASCII-only).
"""

import re
from typing import Optional

from . import BaseRule, RuleResult
from ..context.context_rules import (
    LOGIN_SUBMIT_TRIGGERS,
    build_click_command,
    build_goto_command,
    build_fill_command,
    build_login_page_commands,
    build_press_command,
    build_wait_command,
    build_wait_for_selector_command,
    detect_target_site,
    resolve_hearbe_typed_url,
)
from ..sites.site_manager import get_page_type, get_selector


class LoginRule(BaseRule):
    """Login rule: navigate or submit."""

    def check(self, text: str, current_url: str, current_site) -> Optional[RuleResult]:
        if get_page_type(current_url) == "login":
            if current_site and getattr(current_site, "site_id", "") == "hearbe":
                return _handle_hearbe_login(text, current_url, current_site)
            return None
        target_site = current_site or detect_target_site(text, self.site_manager, current_site)
        phone = _extract_phone_number(text)
        if phone and get_page_type(current_url) != "login":
            commands = build_login_page_commands(target_site, current_url=current_url)
            return RuleResult(
                matched=True,
                commands=commands,
                response_text="로그인 페이지로 이동합니다.",
                rule_name="login",
            )

        if "로그인" not in text and "login" not in text.lower():
            return None

        if any(kw in text for kw in LOGIN_SUBMIT_TRIGGERS):
            commands = build_login_page_commands(target_site, current_url=current_url)
            return RuleResult(
                matched=True,
                commands=commands,
                response_text="로그인 페이지로 이동합니다.",
                rule_name="login",
            )

        commands = build_login_page_commands(target_site, current_url=current_url)
        return RuleResult(
            matched=True,
            commands=commands,
            response_text="로그인 페이지로 이동합니다.",
            rule_name="login",
        )


class LoginPhoneRule(BaseRule):
    """Phone number input on login page."""

    def check(self, text: str, current_url: str, current_site) -> Optional[RuleResult]:
        if get_page_type(current_url) != "login":
            return None

        phone_digits = _extract_phone_digits(text)
        if not phone_digits:
            return None

        phone_selector = get_selector(current_url, "phone_input") if current_url else None
        if not phone_selector and current_site:
            phone_selector = current_site.get_selector("login", "phone_input")
        if not phone_selector:
            phone_selector = "input._phoneInput, input[type='tel']"

        submit_selector = get_selector(current_url, "phone_submit_button") if current_url else None
        if not submit_selector and current_site:
            submit_selector = current_site.get_selector("login", "phone_submit_button")

        commands = [
            build_wait_for_selector_command(
                phone_selector,
                state="visible",
                timeout=8000,
                description="휴대폰 번호 입력칸 대기",
            ),
            build_fill_command(phone_selector, phone_digits, "휴대폰 번호 입력"),
        ]
        if submit_selector:
            commands.append(
                build_wait_for_selector_command(
                    submit_selector,
                    state="visible",
                    timeout=8000,
                    description="인증번호 요청 버튼 대기",
                )
            )
            commands.append(build_click_command(submit_selector, "인증번호 요청"))

        return RuleResult(
            matched=True,
            commands=commands,
            response_text="휴대폰 번호를 입력하고 인증번호를 요청합니다.",
            rule_name="login",
        )


class LoginPhoneTabRule(BaseRule):
    """Switch to phone login tab on login page."""

    def check(self, text: str, current_url: str, current_site) -> Optional[RuleResult]:
        if get_page_type(current_url) != "login":
            return None

        if "휴대폰" not in text:
            return None

        tab_selector = get_selector(current_url, "tab_phone_login") if current_url else None
        if not tab_selector and current_site:
            tab_selector = current_site.get_selector("login", "tab_phone_login")
        if not tab_selector:
            return None

        phone_selector = get_selector(current_url, "phone_input") if current_url else None
        if not phone_selector and current_site:
            phone_selector = current_site.get_selector("login", "phone_input")
        if not phone_selector:
            phone_selector = "input._phoneInput, input[type='tel']"

        commands = [
            build_click_command(tab_selector, "휴대폰 로그인 탭 전환"),
            build_wait_for_selector_command(
                phone_selector,
                state="visible",
                timeout=8000,
                description="휴대폰 번호 입력칸 대기",
            ),
        ]
        return RuleResult(
            matched=True,
            commands=commands,
            response_text="휴대폰 로그인 탭으로 전환합니다, 휴대폰 번호를 불러주시면 대신 입력해 드릴게요.",
            rule_name="login",
        )


class LoginOtpRule(BaseRule):
    """OTP code input on login page."""

    def check(self, text: str, current_url: str, current_site) -> Optional[RuleResult]:
        if get_page_type(current_url) != "login":
            return None

        code = _extract_otp_code(text)
        if not code:
            return None

        selector = get_selector(current_url, "otp_input") if current_url else None
        if not selector and current_site:
            selector = current_site.get_selector("login", "otp_input")
        if not selector:
            selector = (
                "input[autocomplete='one-time-code'], "
                "input[name*='otp' i], input[id*='otp' i], "
                "input[name*='code' i], input[id*='code' i], "
                "input[placeholder*='인증'], "
                "input[type='text']"
            )

        commands = [
            build_wait_for_selector_command(
                selector,
                state="visible",
                timeout=8000,
                description="인증번호 입력칸 대기",
            ),
            build_fill_command(selector, code, "인증번호 입력"),
            build_press_command(selector, "Enter", "인증번호 적용"),
        ]
        return RuleResult(
            matched=True,
            commands=commands,
            response_text="인증번호를 입력합니다.",
            rule_name="login",
        )


def _extract_otp_code(text: str) -> Optional[str]:
    if not text:
        return None
    keywords = ("인증", "번호", "코드", "otp", "입력")
    lowered = text.lower()
    has_keyword = any((k in lowered) if k == "otp" else (k in text) for k in keywords)

    digits = _extract_all_digits(text)
    if 4 <= len(digits) <= 8:
        # Accept if keywords present or text is mostly digits/spaces/hyphens
        if has_keyword or re.fullmatch(r"[0-9\\s\\-]+", text.strip()):
            return digits
    return None


def _extract_phone_number(text: str) -> Optional[str]:
    if not text:
        return None
    match = re.search(r"(010|011|016|017|018|019)[\\s\\-]?[0-9]{3,4}[\\s\\-]?[0-9]{4}", text)
    if not match:
        return None
    return match.group(0)


def _extract_phone_digits(text: str) -> Optional[str]:
    digits = _extract_all_digits(text)
    if len(digits) in (10, 11):
        if digits.startswith(("010", "011", "016", "017", "018", "019")):
            return digits
        return digits
    return None


def _extract_all_digits(text: str) -> str:
    return re.sub(r"\\D", "", text or "")


def _handle_hearbe_login(text: str, current_url: str, current_site) -> Optional[RuleResult]:
    if not text:
        return None

    if _is_signup_intent(text):
        if current_site and getattr(current_site, "site_id", "") == "hearbe":
            signup_url = resolve_hearbe_typed_url(current_site, "/signup", current_url=current_url)
            if signup_url:
                commands = [build_goto_command(signup_url, "?뚯썝媛???섏씠吏 ?대룞")]
                return RuleResult(
                    matched=True,
                    commands=commands,
                    response_text="?뚯썝媛???섏씠吏濡??대룞?⑸땲??",
                    rule_name="login",
                )
        selector = (
            get_selector(current_url, "signup_link")
            or current_site.get_selector("login", "signup_link")
            or "a[href*='/signup']"
        )
        commands = [build_click_command(selector, "회원가입 페이지 이동")]
        return RuleResult(
            matched=True,
            commands=commands,
            response_text="회원가입 페이지로 이동합니다.",
            rule_name="login",
        )

    if _is_find_id_intent(text):
        selector = (
            get_selector(current_url, "find_id_link")
            or current_site.get_selector("login", "find_id_link")
            or "a[href*='/findId']"
        )
        commands = [build_click_command(selector, "아이디 찾기 페이지 이동")]
        return RuleResult(
            matched=True,
            commands=commands,
            response_text="아이디 찾기로 이동합니다.",
            rule_name="login",
        )

    if _is_find_password_intent(text):
        selector = (
            get_selector(current_url, "find_password_link")
            or current_site.get_selector("login", "find_password_link")
            or "a[href*='/findPassword']"
        )
        commands = [build_click_command(selector, "비밀번호 재설정 페이지 이동")]
        return RuleResult(
            matched=True,
            commands=commands,
            response_text="비밀번호 재설정으로 이동합니다.",
            rule_name="login",
        )

    login_intent = _is_login_intent(text)
    login_id, login_password = _extract_hearbe_credentials(text)
    if not login_intent and not (login_id or login_password):
        return None

    id_selector = get_selector(current_url, "id_input") or get_selector(current_url, "email_input")
    if not id_selector and current_site:
        id_selector = current_site.get_selector("login", "id_input") or current_site.get_selector("login", "email_input")
    password_selector = get_selector(current_url, "password_input") if current_url else None
    if not password_selector and current_site:
        password_selector = current_site.get_selector("login", "password_input")
    login_selector = (
        get_selector(current_url, "login_button")
        or get_selector(current_url, "submit_button")
        or (current_site.get_selector("login", "login_button") if current_site else None)
        or "button[type='submit']"
    )

    commands = []
    if login_id and id_selector:
        commands.append(build_wait_for_selector_command(id_selector, state="visible", timeout=8000, description="아이디 입력칸 대기"))
        commands.append(build_fill_command(id_selector, login_id, "아이디 입력"))
    if login_password and password_selector:
        commands.append(build_wait_for_selector_command(password_selector, state="visible", timeout=8000, description="비밀번호 입력칸 대기"))
        commands.append(build_fill_command(password_selector, login_password, "비밀번호 입력"))
    if login_intent or (login_id and login_password):
        commands.append(build_click_command(login_selector, "로그인 버튼 클릭"))
        commands.append(build_wait_command(1500, "로그인 처리 대기"))
        response_text = "로그인을 진행합니다."
    else:
        commands.append(build_click_command(login_selector, "로그인 버튼 클릭"))
        response_text = "로그인 버튼을 눌러 진행합니다."

    if not commands:
        return None

    return RuleResult(
        matched=True,
        commands=commands,
        response_text=response_text,
        rule_name="login",
    )


def _is_signup_intent(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    if "signup" in lowered or "sign up" in lowered:
        return True
    if "회원가입" in text:
        return True
    if "가입" in text and "회원" in text:
        return True
    if text.strip().endswith("가입"):
        return True
    return False


def _is_find_id_intent(text: str) -> bool:
    if not text:
        return False
    if "아이디" in text and ("찾" in text or "찾기" in text):
        return True
    return False


def _is_find_password_intent(text: str) -> bool:
    if not text:
        return False
    if ("비밀번호" in text or "비번" in text) and ("찾" in text or "재설정" in text):
        return True
    return False


def _is_login_intent(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    return "login" in lowered or "로그인" in text


def _extract_hearbe_credentials(text: str) -> tuple[Optional[str], Optional[str]]:
    if not text:
        return None, None
    login_id = _extract_labeled_alnum(text, ("아이디", "id"), 4, 20)
    login_password = _extract_labeled_alnum(text, ("비밀번호", "비번", "패스워드", "password", "pw"), 4, 20)
    return login_id, login_password


def _extract_labeled_alnum(text: str, labels: tuple[str, ...], min_len: int, max_len: int) -> Optional[str]:
    label_pattern = "|".join(re.escape(label) for label in labels)
    pattern = rf"(?:{label_pattern})\s*(?:은|는|:)?\s*([A-Za-z0-9\\s]+)"
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None
    value = re.sub(r"\\s+", "", match.group(1))
    return _sanitize_alnum(value, min_len, max_len)


def _sanitize_alnum(value: str, min_len: int, max_len: int) -> Optional[str]:
    if not value:
        return None
    value = re.sub(r"[^A-Za-z0-9]", "", value)
    if len(value) < min_len or len(value) > max_len:
        return None
    return value
