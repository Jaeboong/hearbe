"""
LLM Planner 서비스 구현

사용자 발화를 MCP 브라우저 자동화 명령으로 변환
"""

import logging
from typing import Dict, Any, Optional, List
from core.interfaces import (
    ILLMPlanner, IntentResult, IntentType, SessionState,
    LLMResponse, MCPCommand
)
from core.config import get_config

logger = logging.getLogger(__name__)


# MCP 도구 명령 템플릿
MCP_TEMPLATES = {
    "navigate": {
        "tool_name": "browser_navigate",
        "description": "URL로 이동"
    },
    "click": {
        "tool_name": "browser_click",
        "description": "요소 클릭"
    },
    "type": {
        "tool_name": "browser_type",
        "description": "텍스트 입력"
    },
    "screenshot": {
        "tool_name": "browser_screenshot",
        "description": "스크린샷 캡처"
    },
    "scroll": {
        "tool_name": "browser_scroll",
        "description": "페이지 스크롤"
    },
}

# 사이트별 URL 및 셀렉터
SITE_CONFIG = {
    "coupang": {
        "base_url": "https://www.coupang.com",
        "search_url": "https://www.coupang.com/np/search?q=",
        "selectors": {
            "search_input": "#headerSearchKeyword",
            "search_button": ".search-btn",
            "product_list": ".search-product",
            "product_name": ".name",
            "product_price": ".price-value",
        }
    },
    "naver": {
        "base_url": "https://shopping.naver.com",
        "search_url": "https://search.shopping.naver.com/search/all?query=",
        "selectors": {
            "product_list": ".basicList_item__0T9JD",
            "product_name": ".basicList_title__VfX3c",
            "product_price": ".price_num__S2p_v",
        }
    },
    "11st": {
        "base_url": "https://www.11st.co.kr",
        "search_url": "https://search.11st.co.kr/Search.tmall?kwd=",
        "selectors": {
            "product_list": ".c_prd_item",
            "product_name": ".c_prd_name",
            "product_price": ".c_prd_price",
        }
    }
}


class LLMPlanner(ILLMPlanner):
    """
    LLM 기반 명령 생성기

    Features:
    - 자연어 → MCP 명령 변환
    - 대화형 쇼핑 플로우 지원
    - Flow Engine 위임 판단
    """

    def __init__(self):
        self._config = get_config().llm
        self._client = None

    async def initialize(self):
        """LLM 클라이언트 초기화"""
        try:
            # TODO: OpenAI 또는 다른 LLM 클라이언트 초기화
            # import openai
            # openai.api_key = self._config.api_key
            logger.info(f"LLM Planner initialized: {self._config.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise

    async def generate_commands(
        self,
        user_text: str,
        intent: IntentResult,
        session: SessionState
    ) -> LLMResponse:
        """
        사용자 발화를 MCP 명령으로 변환

        Args:
            user_text: 사용자 발화 텍스트
            intent: 의도 분석 결과
            session: 현재 세션 상태

        Returns:
            LLMResponse: 생성된 명령 및 응답
        """
        commands: List[MCPCommand] = []
        response_text = ""
        requires_flow = False
        flow_type = None

        # 현재 사이트 설정
        site = session.current_site or "coupang"
        site_config = SITE_CONFIG.get(site, SITE_CONFIG["coupang"])

        # 의도별 명령 생성
        if intent.intent == IntentType.SEARCH:
            query = intent.entities.get("product_name", user_text)
            commands = self._generate_search_commands(site_config, query)
            response_text = f"'{query}' 검색 결과를 찾고 있습니다."

        elif intent.intent == IntentType.ADD_TO_CART:
            commands = self._generate_add_to_cart_commands(site_config, session)
            response_text = "장바구니에 추가하고 있습니다."

        elif intent.intent == IntentType.CHECKOUT:
            requires_flow = True
            flow_type = "checkout"
            response_text = "결제를 진행하시겠습니까? 결제 전 상품 정보를 확인해 드리겠습니다."

        elif intent.intent == IntentType.SIGNUP:
            requires_flow = True
            flow_type = "signup"
            response_text = "회원가입을 진행하시겠습니까?"

        elif intent.intent == IntentType.SELECT_ITEM:
            # 이전 검색 결과에서 선택
            commands = self._generate_select_commands(site_config, intent, session)
            response_text = "선택한 상품의 상세 정보를 불러오고 있습니다."

        elif intent.intent == IntentType.ASK_INFO:
            # 현재 페이지에서 정보 추출
            commands = [MCPCommand(
                tool_name="browser_screenshot",
                arguments={},
                description="현재 페이지 스크린샷"
            )]
            response_text = "상품 정보를 확인하고 있습니다."

        elif intent.intent == IntentType.NAVIGATE:
            # 특정 사이트로 이동
            target_site = intent.entities.get("site", site)
            target_config = SITE_CONFIG.get(target_site, site_config)
            commands = [MCPCommand(
                tool_name="browser_navigate",
                arguments={"url": target_config["base_url"]},
                description=f"{target_site}으로 이동"
            )]
            response_text = f"{target_site}으로 이동합니다."

        else:
            response_text = "요청을 이해하지 못했습니다. 다시 말씀해 주세요."

        return LLMResponse(
            text=response_text,
            commands=commands,
            requires_flow=requires_flow,
            flow_type=flow_type
        )

    def _generate_search_commands(
        self,
        site_config: Dict[str, Any],
        query: str
    ) -> List[MCPCommand]:
        """검색 명령 생성"""
        search_url = site_config["search_url"] + query
        return [
            MCPCommand(
                tool_name="browser_navigate",
                arguments={"url": search_url},
                description=f"'{query}' 검색"
            ),
            MCPCommand(
                tool_name="browser_screenshot",
                arguments={},
                description="검색 결과 캡처"
            )
        ]

    def _generate_add_to_cart_commands(
        self,
        site_config: Dict[str, Any],
        session: SessionState
    ) -> List[MCPCommand]:
        """장바구니 추가 명령 생성"""
        # TODO: 사이트별 장바구니 버튼 셀렉터 사용
        return [
            MCPCommand(
                tool_name="browser_click",
                arguments={"selector": ".add-to-cart-btn, .cart-btn, [class*='cart']"},
                description="장바구니 버튼 클릭"
            ),
            MCPCommand(
                tool_name="browser_screenshot",
                arguments={},
                description="장바구니 추가 결과 확인"
            )
        ]

    def _generate_select_commands(
        self,
        site_config: Dict[str, Any],
        intent: IntentResult,
        session: SessionState
    ) -> List[MCPCommand]:
        """상품 선택 명령 생성"""
        # 순서 기반 선택
        ordinal_map = {
            "첫 번째": 0, "두 번째": 1, "세 번째": 2, "네 번째": 3
        }
        index = 0
        for key in ordinal_map:
            if key in intent.raw_text:
                index = ordinal_map[key]
                break

        product_selector = site_config["selectors"]["product_list"]
        return [
            MCPCommand(
                tool_name="browser_click",
                arguments={
                    "selector": f"{product_selector}:nth-child({index + 1}) a"
                },
                description=f"{index + 1}번째 상품 선택"
            ),
            MCPCommand(
                tool_name="browser_screenshot",
                arguments={},
                description="상품 상세 페이지 캡처"
            )
        ]

    async def generate_response(self, context: Dict[str, Any]) -> str:
        """
        사용자에게 전달할 응답 텍스트 생성

        Args:
            context: 현재 컨텍스트 (검색 결과, 상품 정보 등)

        Returns:
            str: 응답 텍스트
        """
        # TODO: LLM을 사용해 자연스러운 응답 생성
        # 현재는 템플릿 기반

        if "search_results" in context:
            results = context["search_results"]
            count = len(results)
            if count > 0:
                first_item = results[0]
                return (
                    f"총 {count}개의 상품을 찾았습니다. "
                    f"첫 번째 상품은 {first_item.get('name', '')}이고, "
                    f"가격은 {first_item.get('price', '')}원입니다. "
                    f"자세히 보시겠어요?"
                )
            else:
                return "검색 결과가 없습니다. 다른 검색어를 시도해 보세요."

        if "product_detail" in context:
            product = context["product_detail"]
            return (
                f"상품명: {product.get('name', '')}. "
                f"가격: {product.get('price', '')}원. "
                f"평점: {product.get('rating', '')}점. "
                f"장바구니에 담을까요?"
            )

        return "어떤 도움이 필요하신가요?"

    async def should_delegate_to_flow(self, intent: IntentResult) -> Optional[str]:
        """
        Flow Engine 위임 여부 판단

        Args:
            intent: 의도 분석 결과

        Returns:
            str: 위임할 플로우 타입 (signup, checkout) 또는 None
        """
        flow_intents = {
            IntentType.CHECKOUT: "checkout",
            IntentType.SIGNUP: "signup",
        }
        return flow_intents.get(intent.intent)

    async def shutdown(self):
        """리소스 정리"""
        self._client = None
        logger.info("LLM Planner shutdown")
