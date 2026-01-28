"""
Selection helpers for applying recent search results to user requests.
"""

from typing import Optional

from core.interfaces import LLMResponse, MCPCommand, SessionState
from core.korean_numbers import extract_ordinal_index
from .selection_extract import build_product_extract_command
from ...sites.site_manager import get_site_manager, get_current_site, get_selector


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

    ordinal_index = extract_ordinal_index(target)
    if ordinal_index is not None:
        if 0 <= ordinal_index < len(results):
            commands = _build_click_nth_result_commands(session, ordinal_index)
            if not commands:
                item = results[ordinal_index] if isinstance(results[ordinal_index], dict) else {}
                name = item.get("name") or item.get("title") or item.get("product_name")
                if name:
                    commands = [
                        MCPCommand(
                            tool_name="click_text",
                            arguments={"text": name},
                            description=f"search result click '{name}'"
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
            if commands:
                return LLMResponse(
                    text=f"{ordinal_index + 1}번째 상품을 선택합니다.",
                    commands=commands,
                    requires_flow=False,
                    flow_type=None
                )

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


def _build_click_nth_result_commands(
    session: Optional[SessionState],
    ordinal_index: int
) -> Optional[list[MCPCommand]]:
    if not session:
        return None

    current_url = session.current_url or ""
    site = None
    if session.current_site:
        site = get_site_manager().get_site(session.current_site)
    if not site and current_url:
        site = get_current_site(current_url)

    selectors = {}
    if site:
        page = site.get_page_selectors("search")
        selectors = page.selectors if page and page.selectors else {}

    product_list = (
        selectors.get("product_list")
        or (get_selector(current_url, "product_list") if current_url else None)
    )
    product_item = (
        selectors.get("product_item")
        or (get_selector(current_url, "product_item") if current_url else None)
    )

    target_selector = None
    if product_item and product_item.startswith("li") and " " in product_item:
        first, rest = product_item.split(" ", 1)
        target_selector = f"{first}:nth-of-type({ordinal_index + 1}) {rest}"
    elif product_list:
        target_selector = f"{product_list}:nth-of-type({ordinal_index + 1})"
    elif product_item:
        target_selector = f"{product_item}:nth-of-type({ordinal_index + 1})"

    if not target_selector:
        return None

    commands = [
        MCPCommand(
            tool_name="click",
            arguments={"selector": target_selector},
            description=f"click search result #{ordinal_index + 1}"
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

    return commands
