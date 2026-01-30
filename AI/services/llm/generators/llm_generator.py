"""
LLM 기반 명령 생성기

규칙 기반 매칭 실패 시 OpenAI API를 사용하여 명령을 생성합니다.
"""

import logging
import os
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# .env 파일 로드 (프로젝트 루트인 AI 디렉토리 기준)
try:
    from dotenv import load_dotenv
    from pathlib import Path
    
    # services/llm/generators/llm_generator.py -> AI/.env
    env_path = Path(__file__).parent.parent.parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

from ..context.context_builder import ContextBuilder, get_page_context, PageContext
from ..context.context_rules import GeneratedCommand
from ..sites.site_manager import get_site_manager
from .llm_client import LLMClient, resolve_llm_api_key
from .llm_command_normalizer import LLMCommandNormalizer
from .llm_response_parser import LLMResponseParser
from .history_store import HistoryStore
from services.llm.errors.error_handler import LLMErrorHandler
from services.llm.errors.llm_errors import LLMError

logger = logging.getLogger(__name__)



@dataclass
class LLMResult:
    """LLM 생성 결과"""
    commands: List[GeneratedCommand]
    response_text: str
    success: bool = True
    error: Optional[str] = None


class LLMGenerator:
    """
    LLM 기반 명령 생성기
    
    OpenAI API를 사용하여 자연어를 MCP 명령으로 변환합니다.
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-5-mini"):
        # Allow env-based key selection
        self.api_key = resolve_llm_api_key(api_key)
        self.model = model
        self.base_url = os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1"
        try:
            self.max_tokens = int(os.environ.get("LLM_MAX_TOKENS", "1000"))
        except ValueError:
            self.max_tokens = 1000
        self.context_builder = ContextBuilder()
        self._client = LLMClient(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model,
            max_tokens=self.max_tokens,
        )
        self._normalizer = LLMCommandNormalizer()
        self._parser = LLMResponseParser(self._normalizer)
        self._history_store = HistoryStore(max_items=10)
        self._error_handler = LLMErrorHandler()
    
    async def generate(
        self,
        user_text: str,
        current_url: str = "",
        page_type: Optional[str] = None,
        available_selectors: Optional[Dict[str, str]] = None,
        conversation_history: List[Dict[str, str]] = None,
        session_context: Optional[Dict[str, Any]] = None,
    ) -> LLMResult:
        """
        LLM을 사용하여 명령 생성
        
        Args:
            user_text: 사용자 입력
            current_url: 현재 URL
            page_type: 페이지 타입 (main, product, checkout 등)
            available_selectors: 현재 페이지에서 사용 가능한 셀렉터 목록
            conversation_history: 대화 기록 (없으면 로컬 기록 사용)
        
        Returns:
            LLMResult: 생성된 명령 및 응답
        """
        # 대화 기록: 외부에서 전달받거나 로컬 기록 사용
        history = conversation_history if conversation_history is not None else self._history_store.get()
        
        # 페이지 컨텍스트 생성
        site = get_site_manager().get_site_by_url(current_url)
        page_context = get_page_context(current_url, site)
        
        # available_selectors가 전달되면 컨텍스트에 추가
        if page_type:
            page_context.page_type = page_type
        if available_selectors:
            page_context.selectors = available_selectors
        
        # 프롬프트 메시지 구성
        messages = self.context_builder.build_messages(
            user_text=user_text,
            current_url=current_url,
            conversation_history=history,
            page_context=page_context,
            session_context=session_context,
        )
        return await self._request_with_error_handling(
            messages=messages,
            current_url=current_url,
            text_len=len(user_text),
            user_text=user_text,
            conversation_history=conversation_history,
        )

    async def generate_with_messages(
        self,
        messages: List[Dict[str, str]],
        current_url: str = "",
    ) -> LLMResult:
        """Generate commands with pre-built messages."""
        return await self._request_with_error_handling(
            messages=messages,
            current_url=current_url,
            label="custom messages",
            user_text=None,
            conversation_history=None,
        )
    
    # use helpers in llm_logging.py for truncation/logging
    
    def clear_history(self):
        """로컬 대화 기록 초기화"""
        self._history_store.clear()
    
    def get_history(self) -> List[Dict[str, str]]:
        """현재 대화 기록 반환"""
        return self._history_store.get()

    async def _request_with_error_handling(
        self,
        messages: List[Dict[str, str]],
        current_url: str,
        text_len: Optional[int] = None,
        label: str = "",
        user_text: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> LLMResult:
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                content = await self._client.request(
                    messages=messages,
                    current_url=current_url,
                    text_len=text_len,
                    label=label,
                )
                parsed = self._parser.parse(content, current_url)
                result = LLMResult(
                    commands=parsed.commands,
                    response_text=parsed.response_text,
                    success=parsed.success,
                    error=parsed.error,
                )
                logger.info(
                    "LLM parsed: success=%s, commands=%d, response_text_len=%d",
                    result.success,
                    len(result.commands),
                    len(result.response_text or "")
                )
                if user_text and conversation_history is None:
                    self._history_store.add_user(user_text)
                    self._history_store.add_assistant(result.response_text)
                return result
            except LLMError as e:
                decision = self._error_handler.handle(e, attempt)
                if decision.retry and attempt < max_attempts - 1:
                    if decision.retry_delay_ms:
                        await asyncio.sleep(decision.retry_delay_ms / 1000)
                    continue
                return LLMResult(
                    commands=[],
                    response_text=decision.fallback_text,
                    success=False,
                    error=decision.error or e.message,
                )
            except Exception as e:
                logger.error(f"LLM 호출 실패: {e}")
                return LLMResult(
                    commands=[],
                    response_text="죄송합니다. 요청을 처리하는 중 오류가 발생했습니다.",
                    success=False,
                    error=str(e)
                )


# 편의 함수
_generator_instance: Optional[LLMGenerator] = None

def get_llm_generator() -> LLMGenerator:
    """싱글톤 LLMGenerator 반환"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = LLMGenerator()
    return _generator_instance
