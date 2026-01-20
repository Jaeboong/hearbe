"""
LLM 명령 생성 테스트

담당: 김재환

CommandGenerator 및 관련 모듈 테스트 (FASTAPI_TO_APP.md 기준)
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# 프로젝트 루트 추가 (AI 디렉토리)
# 현재 위치: AI/services/llm/tests/test_llm.py
# AI 디렉토리로 가려면 4단계 위로
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from services.llm.command_generator import CommandGenerator, CommandResult, GeneratedCommand
from services.llm.site_manager import get_site_manager, get_current_site, SiteConfig


class TestCommandGenerator:
    """CommandGenerator 테스트"""

    # ---- 초기화 테스트 ----

    def test_init(self):
        """생성자 초기화"""
        generator = CommandGenerator()
        assert generator is not None

    # ---- 검색 명령 생성 테스트 ----

    def test_generate_search_coupang(self):
        """쿠팡 검색 명령 생성"""
        generator = CommandGenerator()
        
        result = generator.generate(
            "쿠팡에서 물티슈 검색해줘",
            "https://www.coupang.com/"
        )
        
        assert result.matched_rule == "search"
        assert len(result.commands) >= 1
        
        # 명령어 이름 검증 (FASTAPI_TO_APP.md 기준)
        action_names = [cmd.tool_name for cmd in result.commands]
        assert "click" in action_names or "fill" in action_names
        
        # 검색어가 포함되었는지
        fill_cmd = next((cmd for cmd in result.commands if cmd.tool_name == "fill"), None)
        if fill_cmd:
            assert "물티슈" in str(fill_cmd.arguments)

    def test_generate_search_naver(self):
        """네이버 검색 명령 생성"""
        generator = CommandGenerator()
        
        result = generator.generate(
            "네이버에서 이어폰 검색해줘",
            "https://shopping.naver.com/"
        )
        
        assert result.matched_rule == "search"
        assert len(result.commands) >= 1

    def test_generate_search_11st(self):
        """11번가 검색 명령 생성"""
        generator = CommandGenerator()
        
        result = generator.generate(
            "11번가에서 노트북 검색해줘",
            "https://www.11st.co.kr/"
        )
        
        assert result.matched_rule == "search"
        assert len(result.commands) >= 1

    # ---- 사이트 접속 명령 생성 테스트 ----

    def test_generate_site_access_coupang(self):
        """쿠팡 사이트 접속 명령 생성"""
        generator = CommandGenerator()
        
        result = generator.generate("쿠팡으로 가줘", "")
        
        assert result.matched_rule == "site_access"
        assert len(result.commands) >= 1
        
        # goto 명령에 쿠팡 URL 포함
        goto_cmd = result.commands[0]
        assert goto_cmd.tool_name == "goto"
        assert "coupang.com" in goto_cmd.arguments.get("url", "")

    def test_generate_site_access_naver(self):
        """네이버 사이트 접속 명령 생성"""
        generator = CommandGenerator()
        
        result = generator.generate("네이버쇼핑으로 이동해", "")
        
        assert result.matched_rule == "site_access"
        goto_cmd = result.commands[0]
        assert "naver.com" in goto_cmd.arguments.get("url", "")

    # ---- 로그인 명령 생성 테스트 ----

    def test_generate_login_from_homepage(self):
        """홈페이지에서 로그인 페이지 이동"""
        generator = CommandGenerator()
        
        result = generator.generate("로그인 해줘", "https://www.coupang.com/")
        
        assert result.matched_rule == "login"
        assert len(result.commands) >= 1
        
        # 로그인 페이지로 이동 명령
        goto_cmd = result.commands[0]
        assert goto_cmd.tool_name == "goto"
        assert "login" in goto_cmd.arguments.get("url", "").lower()

    def test_generate_login_submit_from_login_page(self):
        """로그인 페이지에서 로그인 버튼 클릭"""
        generator = CommandGenerator()
        
        result = generator.generate(
            "로그인 버튼 클릭",
            "https://login.coupang.com/login/login.pang"
        )
        
        assert result.matched_rule == "login_submit"
        assert len(result.commands) >= 1
        
        # 클릭 명령
        click_cmd = result.commands[0]
        assert click_cmd.tool_name == "click"

    # ---- 결제/회원가입 플로우 위임 테스트 ----

    def test_generate_checkout_requires_flow(self):
        """결제는 플로우 위임"""
        generator = CommandGenerator()
        
        result = generator.generate("이거 결제할게", "https://www.coupang.com/cart")
        
        # checkout_flow 규칙 매칭
        assert result.matched_rule == "checkout_flow"
        assert result.requires_flow is True

    @pytest.mark.skip(reason="회원가입 규칙 미구현")
    def test_generate_signup_requires_flow(self):
        """회원가입은 플로우 위임"""
        generator = CommandGenerator()
        
        result = generator.generate("회원가입 하고 싶어", "https://www.coupang.com/")
        
        assert result.requires_flow is True

    # ---- 알 수 없는 명령 테스트 ----

    def test_generate_unknown_command(self):
        """알 수 없는 명령"""
        generator = CommandGenerator()
        
        result = generator.generate("오늘 날씨 어때?", "https://www.coupang.com/")
        
        # 매칭 안되면 none
        assert result.matched_rule in ["none", "unknown"]


class TestGeneratedCommand:
    """GeneratedCommand 모델 테스트"""

    def test_to_dict(self):
        """딕셔너리 변환"""
        cmd = GeneratedCommand(
            tool_name="goto",
            arguments={"url": "https://www.coupang.com"},
            description="쿠팡 접속"
        )
        
        result = cmd.to_dict()
        
        assert result["tool_name"] == "goto"
        assert result["arguments"]["url"] == "https://www.coupang.com"
        assert result["description"] == "쿠팡 접속"

    def test_command_with_selector(self):
        """셀렉터 포함 명령"""
        cmd = GeneratedCommand(
            tool_name="click",
            arguments={"selector": "#searchBtn"},
            description="검색 버튼 클릭"
        )
        
        assert cmd.tool_name == "click"
        assert "selector" in cmd.arguments


class TestSiteManager:
    """SiteManager 테스트"""

    def test_get_current_site_coupang(self):
        """쿠팡 URL에서 사이트 인식"""
        site = get_current_site("https://www.coupang.com/np/search?q=test")
        
        assert site is not None
        assert site.id == "coupang"
        assert site.name == "쿠팡"

    def test_get_current_site_naver(self):
        """네이버 URL에서 사이트 인식"""
        site = get_current_site("https://shopping.naver.com/search")
        
        assert site is not None
        assert site.id == "naver"

    def test_get_current_site_11st(self):
        """11번가 URL에서 사이트 인식"""
        site = get_current_site("https://www.11st.co.kr/products")
        
        assert site is not None
        assert site.id == "11st"

    def test_get_current_site_unknown(self):
        """알 수 없는 URL"""
        site = get_current_site("https://www.google.com")
        
        assert site is None

    def test_list_sites(self):
        """등록된 사이트 목록"""
        manager = get_site_manager()
        sites = manager.list_sites()
        
        assert "coupang" in sites
        assert "naver" in sites
        assert "11st" in sites

    def test_site_selectors(self):
        """사이트별 셀렉터 확인"""
        manager = get_site_manager()
        site = manager.get_site("coupang")
        
        assert site is not None
        selectors = site.selectors
        
        assert "search_input" in selectors
        assert "search_button" in selectors


class TestCommandResult:
    """CommandResult 모델 테스트"""

    def test_command_result_basic(self):
        """기본 CommandResult 생성"""
        result = CommandResult(
            commands=[
                GeneratedCommand(tool_name="goto", arguments={"url": "https://test.com"})
            ],
            response_text="테스트 응답",
            matched_rule="test"
        )
        
        assert len(result.commands) == 1
        assert result.response_text == "테스트 응답"
        assert result.matched_rule == "test"
        assert result.requires_flow is False

    def test_command_result_with_flow(self):
        """플로우 필요한 CommandResult"""
        result = CommandResult(
            commands=[],
            response_text="결제를 진행합니다",
            matched_rule="checkout",
            requires_flow=True,
            flow_type="checkout"
        )
        
        assert result.requires_flow is True
        assert result.flow_type == "checkout"

