"""
ActionDef → MCP 커맨드 변환

selector_key를 실제 CSS 셀렉터로 해석하고,
{param} 플레이스홀더를 치환하여 MCPCommand 리스트를 생성합니다.
"""

import logging
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

from config.actions import ActionDef, ActionStep
from services.sites.site_manager import SiteManager, SiteConfig

logger = logging.getLogger(__name__)


class GeneratedCommand:
    """MCP로 전송할 커맨드"""

    def __init__(self, tool_name: str, arguments: Dict[str, Any], description: str = ""):
        self.tool_name = tool_name
        self.arguments = arguments
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "description": self.description,
        }


class ActionExecutor:
    """ActionDef를 실제 MCP 커맨드로 변환"""

    def __init__(self, site_manager: SiteManager):
        self._site_manager = site_manager

    def build_commands(
        self,
        action_def: ActionDef,
        site_id: str,
        page_type: Optional[str],
        current_url: str,
        params: Dict[str, Any],
        session_context: Dict[str, Any],
    ) -> List[GeneratedCommand]:
        site = self._site_manager.get_site(site_id)
        if not site:
            logger.warning("No site config for %s", site_id)
            return []

        commands = []
        for step in action_def.steps:
            cmd = self._resolve_step(step, site, page_type, current_url, params, session_context)
            if cmd:
                commands.append(cmd)
        return commands

    def _resolve_step(
        self,
        step: ActionStep,
        site: SiteConfig,
        page_type: Optional[str],
        current_url: str,
        params: Dict[str, Any],
        session_context: Dict[str, Any],
    ) -> Optional[GeneratedCommand]:
        arguments: Dict[str, Any] = {}

        # ── 셀렉터 해석 ──
        selector = step.selector
        if step.selector_key and not selector:
            selector = self._resolve_selector(step.selector_key, site, page_type, current_url)
        if selector:
            selector = self._substitute(selector, params)

            # ordinal 처리: select_search_result 등에서 nth-of-type
            if step.value and step.value.startswith("{") and step.value.endswith("}"):
                param_name = step.value[1:-1]
                ordinal = params.get(param_name)
                if ordinal is not None and step.tool_name == "click":
                    selector = f"{selector}:nth-of-type({ordinal})"

            arguments["selector"] = selector

        # ── URL 해석 ──
        url = step.url
        if step.url_key and not url:
            url = site.get_url(step.url_key)
            if not url and site.site_id == "hearbe":
                url = self._resolve_hearbe_url(site, step.url_key, current_url)
        if url:
            url = self._substitute(url, params)
            arguments["url"] = url

        # ── fill 값 ──
        if step.value is not None and step.tool_name == "fill":
            arguments["text"] = self._substitute(step.value, params)

        # ── press 키 ──
        if step.key:
            arguments["key"] = step.key

        # ── click_text 텍스트 ──
        if step.text:
            arguments["text"] = self._substitute(step.text, params)

        # ── wait 시간 ──
        if step.ms > 0:
            arguments["ms"] = step.ms

        # ── iframe ──
        if step.frame:
            arguments["frame"] = step.frame

        # ── wait_for_selector ──
        if step.tool_name == "wait_for_selector":
            arguments["state"] = step.state
            arguments["timeout"] = step.timeout

        return GeneratedCommand(
            tool_name=step.tool_name,
            arguments=arguments,
            description=step.description,
        )

    def _resolve_selector(
        self, key: str, site: SiteConfig, page_type: Optional[str], current_url: str
    ) -> Optional[str]:
        if page_type:
            sel = site.get_selector(page_type, key)
            if sel:
                return sel
        sel = site.get_selector_by_url(current_url, key)
        if sel:
            return sel
        for _pt, page_sels in site.pages.items():
            sel = page_sels.get_selector(key)
            if sel:
                return sel
        return None

    def _resolve_hearbe_url(
        self, site: SiteConfig, url_key: str, current_url: str
    ) -> Optional[str]:
        resolved_type = "C"
        if current_url:
            path = urlparse(current_url).path or ""
            if path.startswith("/A/"):
                resolved_type = "A"
            elif path.startswith("/B/"):
                resolved_type = "B"
            elif path.startswith("/C/"):
                resolved_type = "C"
            elif path.startswith("/S/"):
                resolved_type = "S"

        key_to_path = {
            "login": "/login",
            "signup": "/signup",
            "mall": "/mall",
            "cart": "/cart",
            "member_info": "/member-info",
            "order_history": "/order-history",
            "home": "/mall",
        }
        suffix = key_to_path.get(url_key)
        if not suffix:
            return None

        base_url = None
        for u in site.urls.values():
            try:
                parsed = urlparse(u)
                base_url = f"{parsed.scheme}://{parsed.netloc}"
                break
            except Exception:
                pass

        if base_url:
            return f"{base_url}/{resolved_type}{suffix}"
        return None

    @staticmethod
    def _substitute(template: str, params: Dict[str, Any]) -> str:
        if not params:
            return template
        result = template
        for key, value in params.items():
            if value is not None:
                result = result.replace(f"{{{key}}}", str(value))
        return result
