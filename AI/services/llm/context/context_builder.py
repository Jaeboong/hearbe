"""
LLM 프롬프트용 컨텍스트 빌더

현재 페이지 정보, 대화 기록, 사용 가능한 명령어를 프롬프트로 구성합니다.
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

from ..sites.site_manager import SiteConfig, get_site_manager


# =============================================================================
# 데이터 클래스
# =============================================================================

@dataclass
class PageContext:
    """현재 페이지 컨텍스트"""
    site_name: str
    page_type: str  # home, search, product, cart, login
    available_actions: List[str]
    selectors: Dict[str, str]


# =============================================================================
# 사용 가능한 명령어 스펙
# =============================================================================

AVAILABLE_COMMANDS = {
    "goto": {
        "description": "Navigate to a URL",
        "args": {"url": "Destination URL"},
        "example": """{"tool_name": "goto", "arguments": {"url": "https://www.coupang.com/"}, "description": "Go to Coupang"}"""
    },
    "click": {
        "description": "Click an element by CSS selector",
        "args": {
            "selector": "CSS selector",
            "frame_selector": "iframe CSS selector (optional)"
        },
        "example": """{"tool_name": "click", "arguments": {"selector": "#login-btn"}, "description": "Click login button"}"""
    },
    "fill": {
        "description": "Fill text into an input",
        "args": {
            "selector": "CSS selector",
            "text": "Text to input",
            "frame_selector": "iframe CSS selector (optional)"
        },
        "example": """{"tool_name": "fill", "arguments": {"selector": "input[name=q]", "text": "ramen"}, "description": "Type search keyword"}"""
    },
    "press": {
        "description": "Press a key in an input",
        "args": {
            "selector": "CSS selector",
            "key": "Key name (Enter, Tab, etc.)",
            "frame_selector": "iframe CSS selector (optional)"
        },
        "example": """{"tool_name": "press", "arguments": {"selector": "input", "key": "Enter"}, "description": "Submit input"}"""
    },
    "wait": {
        "description": "Wait for a given time",
        "args": {"ms": "Milliseconds"},
        "example": """{"tool_name": "wait", "arguments": {"ms": 1000}, "description": "Wait 1 second"}"""
    },
    "click_text": {
        "description": "Find and click by visible text",
        "args": {"text": "Text to match"},
        "example": """{"tool_name": "click_text", "arguments": {"text": "Cart"}, "description": "Click text"}"""
    },
    "scroll": {
        "description": "Scroll the page",
        "args": {"direction": "up or down", "amount": "Pixels (optional)"},
        "example": """{"tool_name": "scroll", "arguments": {"direction": "down", "amount": 500}, "description": "Scroll down"}"""
    },
    "extract": {
        "description": "Extract product data from a list",
        "args": {
            "selector": "CSS selector for items",
            "fields": "List of fields (name, price, rating, review_count)",
            "field_selectors": "Optional field->selector mapping",
            "limit": "Max items"
        },
        "example": """{"tool_name": "extract", "arguments": {"selector": ".search-product", "fields": ["name", "price"], "limit": 20}, "description": "Extract search results"}"""
    },
    "get_text": {
        "description": "Get text content from an element",
        "args": {
            "selector": "CSS selector",
            "frame_selector": "iframe CSS selector (optional)",
            "frame_name": "iframe name (optional)",
            "frame_url": "iframe URL match (optional)",
            "frame_index": "iframe index (optional)"
        },
        "example": """{"tool_name": "get_text", "arguments": {"selector": ".total-price"}, "description": "Read total price"}"""
    },
    "get_visible_buttons": {
        "description": "Get visible clickable buttons on the page",
        "args": {"max_items": "Max number of buttons (optional)"},
        "example": """{"tool_name": "get_visible_buttons", "arguments": {"max_items": 200}, "description": "List visible buttons"}"""
    },
    "get_pages": {
        "description": "List open browser pages/tabs",
        "args": {},
        "example": """{"tool_name": "get_pages", "arguments": {}, "description": "List open tabs"}"""
    }
}

PAGE_ACTIONS = {
    "home": ["search", "login", "navigate", "go_to_cart"],
    "search": ["select_product", "scroll", "next_page", "filter", "sort"],
    "product": ["add_to_cart", "buy_now", "view_reviews", "scroll"],
    "cart": ["checkout", "remove_item", "change_quantity", "continue_shopping"],
    "login": ["submit_login", "find_id", "find_password", "signup"],
    "unknown": ["navigate", "scroll", "click"]
}


# =============================================================================
# 페이지 타입 감지
# =============================================================================

def detect_page_type(url: str) -> str:
    """URL에서 페이지 타입 감지"""
    url_lower = url.lower()
    
    if "login" in url_lower or "signin" in url_lower:
        return "login"
    elif "/search" in url_lower or "query=" in url_lower or "keyword=" in url_lower:
        return "search"
    elif "/vp/" in url_lower or "/products/" in url_lower or "/item" in url_lower:
        return "product"
    elif "/cart" in url_lower:
        return "cart"
    elif "/checkout" in url_lower or "/order" in url_lower:
        return "checkout"
    else:
        return "home"


def get_page_context(url: str, site: Optional[SiteConfig] = None) -> PageContext:
    """URL과 사이트 정보로 페이지 컨텍스트 생성"""
    page_type = detect_page_type(url)
    
    site_name = site.name if site else "알 수 없음"
    
    # 새 구조: get_page_selectors 사용
    selectors = {}
    if site:
        page_selectors = site.get_page_selectors(page_type)
        if page_selectors:
            selectors = page_selectors.selectors
    
    available_actions = PAGE_ACTIONS.get(page_type, PAGE_ACTIONS["unknown"])
    
    return PageContext(
        site_name=site_name,
        page_type=page_type,
        available_actions=available_actions,
        selectors=selectors
    )


# =============================================================================
# 컨텍스트 빌더
# =============================================================================

class ContextBuilder:
    """LLM 프롬프트용 컨텍스트 빌더"""
    
    def build_messages(
        self,
        user_text: str,
        current_url: str,
        conversation_history: List[Dict[str, str]] = None,
        page_context: PageContext = None
    ) -> List[Dict[str, str]]:
        """
        Build OpenAI messages for the current request.
        """
        search_results = self._extract_search_results(conversation_history)
        system_prompt = self._build_system_prompt(current_url, page_context, search_results)

        messages = [{"role": "system", "content": system_prompt}]

        # Keep the most recent conversation turns.
        if conversation_history:
            for msg in conversation_history[-5:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        messages.append({"role": "user", "content": user_text})
        return messages

    def _build_system_prompt(
        self,
        current_url: str,
        page_context: PageContext = None,
        search_results: List[Any] = None
    ) -> str:
        """Build the system prompt."""
        if page_context is None:
            site = get_site_manager().get_site_by_url(current_url)
            page_context = get_page_context(current_url, site)

        commands_doc = self._format_commands()
        selectors_doc = self._format_selectors(page_context.selectors)
        search_results_section = self._format_search_results_section(search_results)

        output_example = json.dumps(
            {
                "response": "short message",
                "commands": [
                    {"tool_name": "tool", "arguments": {}, "description": "description"}
                ]
            },
            ensure_ascii=True,
            indent=2
        )
        fallback_example = json.dumps(
            {
                "response": "Sorry, I could not understand the request. Please rephrase.",
                "commands": []
            },
            ensure_ascii=True,
            indent=2
        )

        return f"""You are a shopping assistant that converts user requests into MCP tool calls.

## Current context
- Site: {page_context.site_name}
- Page type: {page_context.page_type}
- URL: {current_url}
- Available actions: {', '.join(page_context.available_actions)}

## Available commands
{commands_doc}

## Page selectors
{selectors_doc}

{search_results_section}
## Rules
1. Respond with JSON only.
2. Commands are executed in order.
3. If a selector is uncertain, use click_text.
4. Add wait before or after navigation when needed.
5. Always include a "commands" array. If no command is needed, return an empty list and ask a clarifying question in "response".

## Output format
{output_example}

If the request cannot be understood:
{fallback_example}
"""

    def _format_commands(self) -> str:
        """명령어 문서 포맷"""
        lines = []
        for name, spec in AVAILABLE_COMMANDS.items():
            lines.append(f"- {name}: {spec['description']}")
            lines.append(f"  예시: {spec['example']}")
        return "\n".join(lines)
    
    def _format_selectors(self, selectors: Dict[str, str]) -> str:
        """셀렉터 문서 포맷"""
        if not selectors:
            return "(셀렉터 정보 없음 - click_text 사용 권장)"
        
        lines = []
        for name, selector in selectors.items():
            lines.append(f"- {name}: {selector}")
        return "\n".join(lines)

    def _extract_search_results(self, conversation_history: List[Dict[str, Any]] = None) -> List[Any]:
        if not conversation_history:
            return []

        results: List[Any] = []
        for msg in conversation_history:
            if not isinstance(msg, dict):
                continue
            if isinstance(msg.get("search_results"), list):
                results = msg.get("search_results") or []
                continue
            content = msg.get("content")
            if not isinstance(content, str):
                continue
            if not content.startswith("SEARCH_RESULTS:"):
                continue
            payload = content[len("SEARCH_RESULTS:"):].strip()
            try:
                data = json.loads(payload)
            except Exception:
                continue
            if isinstance(data, list):
                results = data
        return results

    def _format_search_results_section(self, search_results: List[Any] = None) -> str:
        if not search_results:
            return ""

        names: List[str] = []
        for item in search_results:
            if isinstance(item, dict):
                name = item.get("name") or item.get("title") or item.get("product_name")
            else:
                name = str(item)
            if name:
                names.append(name.strip())

        if not names:
            return ""

        max_items = 15
        lines = ["## Search Results (most recent)"]
        for name in names[:max_items]:
            lines.append(f"- {name}")
        if len(names) > max_items:
            lines.append(f"... and {len(names) - max_items} more")

        lines.append("")
        lines.append("## Selection Rule")
        lines.append("- If user text matches an item above, prefer click_text with that name.")
        lines.append("- Do not run a new search when a match exists.")
        lines.append("- If no match and the intent is search, run a new search.")
        return "\n".join(lines)
