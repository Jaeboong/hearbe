"""
LLM 명령 생성 서비스

OpenAI GPT 기반 자연어 → MCP 명령 변환
담당: 김재환
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Intent(Enum):
    """사용자 의도 타입"""
    SEARCH = "search"           # 상품 검색
    ADD_TO_CART = "add_to_cart" # 장바구니 추가
    CHECKOUT = "checkout"       # 결제 진행
    SIGNUP = "signup"           # 회원가입
    NAVIGATE = "navigate"       # 사이트 이동
    COMPARE = "compare"         # 상품 비교
    INQUIRY = "inquiry"         # 상품 문의
    UNKNOWN = "unknown"         # 알 수 없음


@dataclass
class ToolCall:
    """MCP 도구 호출 데이터"""
    tool_name: str
    arguments: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "arguments": self.arguments
        }


@dataclass
class IntentResult:
    """의도 분석 결과"""
    intent: Intent
    site: Optional[str] = None      # coupang, naver, elevenst
    parameters: Dict[str, Any] = None
    confidence: float = 0.0
    requires_flow: bool = False     # 플로우 엔진 필요 여부

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class LLMService:
    """
    LLM 명령 생성 서비스

    사용자 자연어를 MCP 브라우저 명령으로 변환
    """

    SYSTEM_PROMPT = """
당신은 시각장애인을 위한 쇼핑 도우미입니다.
사용자의 자연어 요청을 브라우저 자동화 명령으로 변환합니다.

사용 가능한 도구:
- navigate_to_url(url): URL로 이동
- click_element(selector): 요소 클릭
- fill_input(selector, value): 입력 필드 채우기
- get_text(selector): 텍스트 추출
- take_screenshot(): 스크린샷 캡처
- scroll(direction, amount): 페이지 스크롤

출력 형식: JSON 배열로 tool_call 목록 반환
"""

    # 사이트별 URL 매핑
    SITE_URLS = {
        "coupang": "https://www.coupang.com",
        "naver": "https://shopping.naver.com",
        "elevenst": "https://www.11st.co.kr",
    }

    # 사이트별 검색 셀렉터
    SITE_SELECTORS = {
        "coupang": {
            "search_input": "#headerSearchKeyword",
            "search_button": ".search-btn",
        },
        "naver": {
            "search_input": "input[name='query']",
            "search_button": ".search_btn",
        },
        "elevenst": {
            "search_input": "#searchKeyWord",
            "search_button": ".search_btn",
        },
    }

    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        """
        Args:
            api_key: OpenAI API 키
            model: 사용할 모델 이름
        """
        self._api_key = api_key
        self._model = model
        self._client = None  # OpenAI 클라이언트

        logger.info(f"LLMService initialized with model: {model}")

    async def initialize(self):
        """OpenAI 클라이언트 초기화"""
        # TODO: OpenAI 클라이언트 초기화
        # from openai import AsyncOpenAI
        # self._client = AsyncOpenAI(api_key=self._api_key)
        logger.info("LLMService client initialized")

    async def analyze_intent(self, user_input: str, context: Dict[str, Any] = None) -> IntentResult:
        """
        사용자 발화에서 의도 분석

        Args:
            user_input: 사용자 입력 텍스트
            context: 현재 세션 컨텍스트

        Returns:
            IntentResult: 의도 분석 결과
        """
        # TODO: LLM을 통한 의도 분석 구현
        # 현재는 키워드 기반 간단한 분석

        user_input_lower = user_input.lower()

        # 사이트 감지
        site = None
        for site_name in self.SITE_URLS.keys():
            if site_name in user_input_lower or self._get_site_alias(site_name) in user_input_lower:
                site = site_name
                break

        # 의도 감지
        intent = Intent.UNKNOWN
        requires_flow = False

        if any(kw in user_input_lower for kw in ["검색", "찾아", "찾고"]):
            intent = Intent.SEARCH
        elif any(kw in user_input_lower for kw in ["장바구니", "담아", "추가"]):
            intent = Intent.ADD_TO_CART
        elif any(kw in user_input_lower for kw in ["결제", "구매", "주문"]):
            intent = Intent.CHECKOUT
            requires_flow = True
        elif any(kw in user_input_lower for kw in ["회원가입", "가입"]):
            intent = Intent.SIGNUP
            requires_flow = True
        elif any(kw in user_input_lower for kw in ["이동", "가줘", "열어"]):
            intent = Intent.NAVIGATE

        # 검색어 추출 (간단한 구현)
        parameters = {}
        if intent == Intent.SEARCH:
            # "쿠팡에서 물티슈 검색해줘" -> "물티슈"
            keywords = self._extract_search_keyword(user_input)
            if keywords:
                parameters["keyword"] = keywords

        result = IntentResult(
            intent=intent,
            site=site,
            parameters=parameters,
            confidence=0.8,  # TODO: LLM으로 계산
            requires_flow=requires_flow
        )

        logger.info(f"Intent analyzed: {result}")
        return result

    def _get_site_alias(self, site_name: str) -> str:
        """사이트 별칭 반환"""
        aliases = {
            "coupang": "쿠팡",
            "naver": "네이버",
            "elevenst": "11번가",
        }
        return aliases.get(site_name, "")

    def _extract_search_keyword(self, user_input: str) -> Optional[str]:
        """검색어 추출 (간단한 규칙 기반)"""
        # TODO: LLM으로 개선
        # "쿠팡에서 물티슈 검색해줘" -> "물티슈"

        remove_words = [
            "쿠팡에서", "네이버에서", "11번가에서",
            "검색해줘", "찾아줘", "검색해", "찾아",
            "좀", "해줘", "줘"
        ]

        result = user_input
        for word in remove_words:
            result = result.replace(word, "")

        return result.strip() if result.strip() else None

    async def generate_commands(
        self,
        user_input: str,
        context: Dict[str, Any] = None
    ) -> List[ToolCall]:
        """
        자연어를 MCP 명령으로 변환

        Args:
            user_input: 사용자 입력 텍스트
            context: 현재 세션 컨텍스트

        Returns:
            List[ToolCall]: MCP 도구 호출 목록
        """
        # 의도 분석
        intent_result = await self.analyze_intent(user_input, context)

        commands = []

        # 의도에 따른 명령 생성
        if intent_result.intent == Intent.SEARCH:
            commands = self._generate_search_commands(intent_result)
        elif intent_result.intent == Intent.NAVIGATE:
            commands = self._generate_navigate_commands(intent_result)
        elif intent_result.intent == Intent.ADD_TO_CART:
            commands = self._generate_add_to_cart_commands(intent_result)
        # TODO: 다른 의도에 대한 명령 생성

        logger.info(f"Generated {len(commands)} commands for intent: {intent_result.intent}")
        return commands

    def _generate_search_commands(self, intent_result: IntentResult) -> List[ToolCall]:
        """검색 명령 생성"""
        commands = []
        site = intent_result.site or "coupang"  # 기본값: 쿠팡
        keyword = intent_result.parameters.get("keyword", "")

        if not keyword:
            logger.warning("No search keyword found")
            return commands

        # 1. 사이트 이동
        commands.append(ToolCall(
            tool_name="navigate_to_url",
            arguments={"url": self.SITE_URLS[site]}
        ))

        # 2. 검색어 입력
        selectors = self.SITE_SELECTORS[site]
        commands.append(ToolCall(
            tool_name="fill_input",
            arguments={
                "selector": selectors["search_input"],
                "value": keyword
            }
        ))

        # 3. 검색 버튼 클릭
        commands.append(ToolCall(
            tool_name="click_element",
            arguments={"selector": selectors["search_button"]}
        ))

        return commands

    def _generate_navigate_commands(self, intent_result: IntentResult) -> List[ToolCall]:
        """사이트 이동 명령 생성"""
        commands = []
        site = intent_result.site

        if site and site in self.SITE_URLS:
            commands.append(ToolCall(
                tool_name="navigate_to_url",
                arguments={"url": self.SITE_URLS[site]}
            ))

        return commands

    def _generate_add_to_cart_commands(self, intent_result: IntentResult) -> List[ToolCall]:
        """장바구니 추가 명령 생성"""
        # TODO: 사이트별 장바구니 버튼 셀렉터 구현
        commands = []

        # 일반적인 장바구니 버튼 클릭
        commands.append(ToolCall(
            tool_name="click_element",
            arguments={"selector": ".add-to-cart, .cart-btn, [class*='cart']"}
        ))

        return commands

    def should_use_flow(self, intent_result: IntentResult) -> bool:
        """플로우 엔진 사용 여부 판단"""
        return intent_result.requires_flow

    async def close(self):
        """리소스 정리"""
        if self._client:
            # OpenAI 클라이언트 정리
            pass
        logger.info("LLMService closed")
