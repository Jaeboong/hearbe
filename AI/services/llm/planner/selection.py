"""
Selection helpers for applying recent search results to user requests.
"""

from typing import Optional

from core.interfaces import LLMResponse, MCPCommand, SessionState
from .selection_extract import build_product_extract_command


def select_from_results(
    user_text: str,
    session: Optional[SessionState]
) -> Optional[LLMResponse]:
    if not session or not session.context:
        return None
    results = session.context.get("search_results")
    if not isinstance(results, list) or not results:
        return None

    target = user_text.strip().lower()
    if not target:
        return None

    matched_name = None
    for item in results:
        if not isinstance(item, dict):
            continue
        name = item.get("name") or item.get("title") or item.get("product_name")
        if not name:
            continue
        name_lower = name.lower()
        if target in name_lower or name_lower in target:
            matched_name = name
            break

    if not matched_name:
        return None

    commands = [
        MCPCommand(
            tool_name="click_text",
            arguments={"text": matched_name},
            description=f"search result click '{matched_name}'"
        ),
        MCPCommand(
            tool_name="wait_for_new_page",
            arguments={"timeout_ms": 1500, "focus": True},
            description="detect new tab and focus"
        ),
        MCPCommand(
            tool_name="wait",
            arguments={"ms": 1500},
            description="wait for product page"
        )
    ]
    extract_command = build_product_extract_command(session)
    if extract_command:
        commands.append(extract_command)

    return LLMResponse(
        text=f"selecting '{matched_name}' from search results",
        commands=commands,
        requires_flow=False,
        flow_type=None
    )
