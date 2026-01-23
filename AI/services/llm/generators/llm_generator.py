"""
LLM 기반 명령 생성기

규칙 기반 매칭 실패 시 OpenAI API를 사용하여 명령을 생성합니다.
"""

import json
import logging
import os
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
        # GMS_API_KEY 우선, 없으면 OPENAI_API_KEY 사용
        self.api_key = api_key or os.environ.get("GMS_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.base_url = "https://gms.ssafy.io/gmsapi/api.openai.com/v1"
        self.context_builder = ContextBuilder()
        self._client = None
        
        # 로컬 대화 기록 (테스트용)
        self._local_history: List[Dict[str, str]] = []
    
    @property
    def client(self):
        """OpenAI 클라이언트 lazy 로딩 (GMS 프록시 사용)"""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                logger.error("openai 패키지가 설치되지 않았습니다: pip install openai")
                raise
        return self._client
    
    async def generate(
        self,
        user_text: str,
        current_url: str = "",
        page_type: Optional[str] = None,
        available_selectors: Optional[Dict[str, str]] = None,
        conversation_history: List[Dict[str, str]] = None
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
        history = conversation_history if conversation_history is not None else self._local_history
        
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
            page_context=page_context
        )
        
        try:
            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                max_completion_tokens=1000
            )
            
            # 응답 파싱
            content = response.choices[0].message.content
            result = self._parse_response(content)
            
            # 로컬 기록 모드면 대화 추가
            if conversation_history is None:
                self._local_history.append({"role": "user", "content": user_text})
                self._local_history.append({"role": "assistant", "content": result.response_text})
                # 최근 10개만 유지
                if len(self._local_history) > 10:
                    self._local_history = self._local_history[-10:]
            
            return result
            
        except Exception as e:
            logger.error(f"LLM 호출 실패: {e}")
            return LLMResult(
                commands=[],
                response_text="죄송합니다. 요청을 처리하는 중 오류가 발생했습니다.",
                success=False,
                error=str(e)
            )
    
    def _parse_response(self, content: str) -> LLMResult:
        """LLM 응답 JSON 파싱"""
        try:
            data = json.loads(content)
            
            response_text = data.get("response", "")
            commands_data = data.get("commands", [])
            
            commands = []
            for cmd in commands_data:
                action = cmd.get("action", "")
                args = cmd.get("args", {})
                desc = cmd.get("desc", "")
                
                # 유효한 명령인지 검증
                if self._validate_command(action, args):
                    commands.append(GeneratedCommand(
                        tool_name=action,
                        arguments=args,
                        description=desc
                    ))
                else:
                    logger.warning(f"유효하지 않은 명령 무시: {cmd}")
            
            return LLMResult(
                commands=commands,
                response_text=response_text,
                success=True
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}, content: {content[:200]}")
            return LLMResult(
                commands=[],
                response_text="응답을 처리할 수 없습니다.",
                success=False,
                error=f"JSON 파싱 실패: {e}"
            )
    
    def _validate_command(self, action: str, args: Dict[str, Any]) -> bool:
        """명령 유효성 검증"""
        valid_actions = [
            "goto",
            "click",
            "fill",
            "press",
            "wait",
            "click_text",
            "scroll",
            "extract",
        ]
        
        if action not in valid_actions:
            return False
        
        # 필수 인자 검증
        if action == "goto" and "url" not in args:
            return False
        if action == "click" and "selector" not in args:
            return False
        if action == "fill" and ("selector" not in args or "text" not in args):
            return False
        if action == "click_text" and "text" not in args:
            return False
        if action == "extract" and "selector" not in args:
            return False

        return True
    
    def clear_history(self):
        """로컬 대화 기록 초기화"""
        self._local_history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """현재 대화 기록 반환"""
        return self._local_history.copy()


# 편의 함수
_generator_instance: Optional[LLMGenerator] = None

def get_llm_generator() -> LLMGenerator:
    """싱글톤 LLMGenerator 반환"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = LLMGenerator()
    return _generator_instance
