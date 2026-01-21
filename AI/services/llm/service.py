"""
LLM Planner 서비스

규칙 기반 CommandGenerator + LLM fallback 통합
"""

import logging
import os
from typing import Optional, List

from core.interfaces import (
    ILLMPlanner, IntentResult, SessionState,
    LLMResponse, MCPCommand
)

from .command_generator import CommandGenerator, CommandResult
from .llm_generator import LLMGenerator, LLMResult
from .context_rules import GeneratedCommand

logger = logging.getLogger(__name__)


class LLMPlanner(ILLMPlanner):
    """
    LLM Planner 서비스

    1. 규칙 기반 CommandGenerator로 먼저 시도
    2. 매칭 실패 시 LLMGenerator로 fallback
    """

    def __init__(self, use_llm_fallback: bool = True):
        self._rule_generator: Optional[CommandGenerator] = None
        self._llm_generator: Optional[LLMGenerator] = None
        self._use_llm_fallback = use_llm_fallback

    async def initialize(self):
        """초기화"""
        self._rule_generator = CommandGenerator()
        
        # LLM fallback 활성화 시
        if self._use_llm_fallback:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                self._llm_generator = LLMGenerator(api_key=api_key)
                logger.info("LLMPlanner initialized with LLM fallback")
            else:
                logger.warning("OPENAI_API_KEY not set, LLM fallback disabled")
                self._use_llm_fallback = False
        else:
            logger.info("LLMPlanner initialized (rule-based only)")

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
        if not self._rule_generator:
            self._rule_generator = CommandGenerator()

        current_url = session.current_url if session else ""
        conversation_history = session.conversation_history if session else None

        # 1. 규칙 기반 시도
        result = self._rule_generator.generate(user_text, current_url)

        # 2. 규칙 매칭 실패 시 LLM fallback
        if result.matched_rule == "none" and self._use_llm_fallback and self._llm_generator:
            logger.info(f"규칙 매칭 실패, LLM fallback: '{user_text}'")
            
            llm_result = await self._llm_generator.generate(
                user_text=user_text,
                current_url=current_url,
                conversation_history=conversation_history
            )
            
            if llm_result.success and llm_result.commands:
                return self._llm_result_to_response(llm_result)
            else:
                # LLM도 실패하면 원래 규칙 기반 결과 반환
                logger.warning(f"LLM fallback 실패: {llm_result.error}")

        return self._to_response(result)

    def _to_response(self, result: CommandResult) -> LLMResponse:
        """CommandResult → LLMResponse 변환"""
        commands = [
            MCPCommand(
                tool_name=cmd.tool_name,
                arguments=cmd.arguments,
                description=cmd.description
            )
            for cmd in result.commands
        ]

        return LLMResponse(
            text=result.response_text,
            commands=commands,
            requires_flow=result.requires_flow,
            flow_type=result.flow_type
        )

    def _llm_result_to_response(self, result: LLMResult) -> LLMResponse:
        """LLMResult → LLMResponse 변환"""
        commands = [
            MCPCommand(
                tool_name=cmd.tool_name,
                arguments=cmd.arguments,
                description=cmd.description
            )
            for cmd in result.commands
        ]

        return LLMResponse(
            text=result.response_text,
            commands=commands,
            requires_flow=False,
            flow_type=None
        )

    async def shutdown(self):
        """리소스 정리"""
        self._rule_generator = None
        self._llm_generator = None
        logger.info("LLMPlanner shutdown")
