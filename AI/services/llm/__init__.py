"""
LLM 명령 생성 서비스

자연어를 MCP 실행 명령으로 변환
규칙 기반 + LLM fallback 지원
"""

from .service import LLMPlanner
from .command_generator import CommandGenerator, CommandResult, generate_commands
from .context_rules import GeneratedCommand
from .site_manager import get_site_manager, get_current_site, SiteConfig
from .llm_generator import LLMGenerator, LLMResult, get_llm_generator
from .context_builder import ContextBuilder, PageContext, get_page_context

__all__ = [
    # 서비스
    "LLMPlanner",
    # 규칙 기반 생성기
    "CommandGenerator",
    "CommandResult",
    "GeneratedCommand",
    "generate_commands",
    # LLM 생성기
    "LLMGenerator",
    "LLMResult",
    "get_llm_generator",
    # 컨텍스트
    "ContextBuilder",
    "PageContext",
    "get_page_context",
    # 사이트 관리
    "get_site_manager",
    "get_current_site",
    "SiteConfig",
]
