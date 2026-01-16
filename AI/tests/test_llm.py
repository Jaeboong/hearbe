"""
LLMService 유닛 테스트

담당: 김재환
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from services.llm import LLMService, Intent, IntentResult, ToolCall


class TestLLMService:
    """LLMService 테스트"""

    # ---- 초기화 테스트 ----

    def test_init(self):
        """서비스 초기화"""
        service = LLMService(api_key="test-key", model="gpt-4o-mini")

        assert service._api_key == "test-key"
        assert service._model == "gpt-4o-mini"
        assert service._client is None

    @pytest.mark.asyncio
    async def test_initialize(self):
        """클라이언트 초기화"""
        service = LLMService()
        await service.initialize()
        # TODO: OpenAI 클라이언트 Mock 테스트

    # ---- 의도 분석 테스트 ----

    @pytest.mark.asyncio
    async def test_analyze_intent_search(self):
        """검색 의도 분석"""
        service = LLMService()

        result = await service.analyze_intent("쿠팡에서 물티슈 검색해줘")

        assert result.intent == Intent.SEARCH
        assert result.site == "coupang"
        assert "keyword" in result.parameters
        assert result.requires_flow is False

    @pytest.mark.asyncio
    async def test_analyze_intent_checkout(self):
        """결제 의도 분석"""
        service = LLMService()

        result = await service.analyze_intent("이거 결제할게")

        assert result.intent == Intent.CHECKOUT
        assert result.requires_flow is True

    @pytest.mark.asyncio
    async def test_analyze_intent_signup(self):
        """회원가입 의도 분석"""
        service = LLMService()

        result = await service.analyze_intent("회원가입 하고 싶어")

        assert result.intent == Intent.SIGNUP
        assert result.requires_flow is True

    @pytest.mark.asyncio
    async def test_analyze_intent_navigate(self):
        """사이트 이동 의도 분석"""
        service = LLMService()

        result = await service.analyze_intent("네이버 쇼핑으로 가줘")

        assert result.intent == Intent.NAVIGATE
        assert result.site == "naver"

    @pytest.mark.asyncio
    async def test_analyze_intent_unknown(self):
        """알 수 없는 의도"""
        service = LLMService()

        result = await service.analyze_intent("오늘 날씨 어때?")

        assert result.intent == Intent.UNKNOWN

    # ---- 명령 생성 테스트 ----

    @pytest.mark.asyncio
    async def test_generate_commands_search(self):
        """검색 명령 생성"""
        service = LLMService()

        commands = await service.generate_commands("쿠팡에서 물티슈 검색해줘")

        assert len(commands) == 3

        # 1. 사이트 이동
        assert commands[0].tool_name == "navigate_to_url"
        assert "coupang.com" in commands[0].arguments["url"]

        # 2. 검색어 입력
        assert commands[1].tool_name == "fill_input"
        assert "물티슈" in commands[1].arguments["value"]

        # 3. 검색 버튼 클릭
        assert commands[2].tool_name == "click_element"

    @pytest.mark.asyncio
    async def test_generate_commands_navigate(self):
        """사이트 이동 명령 생성"""
        service = LLMService()

        commands = await service.generate_commands("11번가로 이동해")

        assert len(commands) == 1
        assert commands[0].tool_name == "navigate_to_url"
        assert "11st.co.kr" in commands[0].arguments["url"]

    @pytest.mark.asyncio
    async def test_generate_commands_empty_keyword(self):
        """검색어 없는 경우"""
        service = LLMService()

        commands = await service.generate_commands("쿠팡에서 검색해")

        # 검색어가 없으면 명령 생성 안함
        assert len(commands) == 0

    # ---- 플로우 필요 여부 테스트 ----

    def test_should_use_flow_checkout(self):
        """결제는 플로우 필요"""
        service = LLMService()

        intent_result = IntentResult(
            intent=Intent.CHECKOUT,
            requires_flow=True
        )

        assert service.should_use_flow(intent_result) is True

    def test_should_use_flow_search(self):
        """검색은 플로우 불필요"""
        service = LLMService()

        intent_result = IntentResult(
            intent=Intent.SEARCH,
            requires_flow=False
        )

        assert service.should_use_flow(intent_result) is False

    # ---- 사이트별 셀렉터 테스트 ----

    def test_site_selectors_coupang(self):
        """쿠팡 셀렉터 확인"""
        service = LLMService()

        selectors = service.SITE_SELECTORS["coupang"]

        assert "search_input" in selectors
        assert "search_button" in selectors

    def test_site_selectors_naver(self):
        """네이버 셀렉터 확인"""
        service = LLMService()

        selectors = service.SITE_SELECTORS["naver"]

        assert "search_input" in selectors
        assert "search_button" in selectors

    # ---- 리소스 정리 테스트 ----

    @pytest.mark.asyncio
    async def test_close(self):
        """리소스 정리"""
        service = LLMService()
        await service.close()
        # 에러 없이 완료되면 성공


class TestToolCall:
    """ToolCall 모델 테스트"""

    def test_to_dict(self):
        """딕셔너리 변환"""
        tool_call = ToolCall(
            tool_name="navigate_to_url",
            arguments={"url": "https://example.com"}
        )

        result = tool_call.to_dict()

        assert result["tool_name"] == "navigate_to_url"
        assert result["arguments"]["url"] == "https://example.com"
