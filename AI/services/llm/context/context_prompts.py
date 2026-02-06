# -*- coding: utf-8 -*-
"""
Prompt construction utilities for LLM context.
"""

import json
from typing import Any, Dict, List, Optional

from ..sites.site_manager import get_site_manager
from .context_formatters import (
    format_commands,
    format_selectors,
    format_search_results_section,
    format_product_detail_section,
    format_cart_items_section,
    format_order_detail_section,
    format_order_list_section,
    format_url_context,
)
from .context_models import PageContext, get_page_context


def _format_site_urls(site) -> str:
    if not site:
        return ""
    urls_dict = getattr(site, "urls", {}) or {}
    if not isinstance(urls_dict, dict) or not urls_dict:
        return ""

    # Keep commonly referenced URLs first, then list the rest (sorted) for platform-specific flows.
    preferred = ("home", "main", "login", "cart", "mypage")
    ordered_items = []
    seen = set()
    for key in preferred:
        url = urls_dict.get(key) or site.get_url(key)
        if url:
            ordered_items.append((key, url))
            seen.add(key)
    for key in sorted(urls_dict.keys()):
        if key in seen:
            continue
        url = urls_dict.get(key) or site.get_url(key)
        if url:
            ordered_items.append((key, url))

    if not ordered_items:
        return ""
    return "\n".join(["## Site URLs"] + [f"- {k}: {u}" for k, u in ordered_items])


def _build_login_constraints(site_id: str, page_type: str) -> str:
    # Keep login constraints scoped to login pages only to avoid bleeding platform-specific rules
    # into unrelated contexts (e.g., Hearbe mall pages).
    if page_type != "login":
        return ""

    if site_id == "coupang":
        return (
            "## Login constraints\n"
            "- When the user expresses login intent, go to the login page without asking extra questions.\n"
            "- Default method is email + password.\n"
            "- If the user simply says \"login\" on the login page, proceed with email + password (do not ask the method).\n"
            "- Only ask which method to use when the user has not specified a method and has just arrived on the login page.\n"
            "- If the user asks for phone login, switch to the phone login tab and request the phone number (OTP is via SMS only).\n"
            "- After entering OTP, click otp_submit_button (e.g., #loginWithSmsCode) if available.\n"
            "- Available methods: (1) email + password, (2) phone number + OTP.\n"
            "- Prefer concrete actions over follow-up questions when selectors exist.\n"
            "- Use only tools from the Available commands list; do not invent tools like 'submit_login'.\n"
            "- To submit login, click the login button selector (e.g., login_button/submit_button or button[type='submit']).\n"
        )

    if site_id == "hearbe":
        return (
            "## Login constraints\n"
            "- This is Hearbe (first-party) login. Use email + password only.\n"
            "- Prefer using provided selectors (email_input, password_input, login_button/submit_button).\n"
            "- If credentials are already filled by the browser, just click submit.\n"
            "- Use only tools from the Available commands list; do not invent tools.\n"
        )

    return (
        "## Login constraints\n"
        "- Use email + password by default.\n"
        "- Use only tools from the Available commands list.\n"
    )


def build_system_prompt(
    current_url: str,
    page_context: Optional[PageContext] = None,
    search_results: List[Any] = None,
    product_detail: Optional[Dict[str, Any]] = None,
    cart_items: List[Dict[str, Any]] = None,
    order_detail: Optional[Dict[str, Any]] = None,
    order_list: Optional[Any] = None,
    previous_url: Optional[str] = None,
) -> str:
    """Build the LLM system prompt for the current request."""
    if page_context is None:
        site = get_site_manager().get_site_by_url(current_url)
        page_context = get_page_context(current_url, site)
    else:
        site = get_site_manager().get_site_by_url(current_url)

    commands_doc = format_commands()
    selectors_doc = format_selectors(page_context.selectors)
    search_results_section = (
        format_search_results_section(search_results)
        if page_context.page_type == "search"
        else ""
    )
    product_detail_section = (
        format_product_detail_section(product_detail)
        if page_context.page_type == "product"
        else ""
    )
    cart_items_section = (
        format_cart_items_section(cart_items, current_url)
        if page_context.page_type == "cart"
        else ""
    )
    order_detail_section = (
        format_order_detail_section(order_detail)
        if page_context.page_type == "orderdetail"
        else ""
    )
    order_list_section = (
        format_order_list_section(order_list)
        if page_context.page_type == "orderlist"
        else ""
    )
    url_context_section = format_url_context(current_url, previous_url)
    site_urls_section = _format_site_urls(site)
    site_id = getattr(site, "site_id", "") if site else ""
    login_constraints = _build_login_constraints(site_id, page_context.page_type)

    output_example = json.dumps(
        {
            "response": "short message",
            "commands": [
                {"tool_name": "tool", "arguments": {}, "description": "description"}
            ],
        },
        ensure_ascii=True,
        indent=2,
    )
    fallback_example = json.dumps(
        {
            "response": "Sorry, I could not understand the request. Please rephrase.",
            "commands": [],
        },
        ensure_ascii=True,
        indent=2,
    )

    return f"""You are a shopping assistant that converts user requests into MCP tool calls.

## Current context
- Site: {page_context.site_name}
- Page type: {page_context.page_type}
- URL: {current_url}
- Available actions: {', '.join(page_context.available_actions)}
{url_context_section}

{site_urls_section}

## Available commands
{commands_doc}

## Page selectors
{selectors_doc}

{search_results_section}
{product_detail_section}
{cart_items_section}
{order_detail_section}
{order_list_section}
{login_constraints}
## Rules
1. Respond with JSON only.
2. Commands are executed in order.
3. If a selector is uncertain, use click_text.
4. Add wait before or after navigation when needed.
5. If the request is informational and can be answered from context, return an answer with an empty "commands" list.
6. If the request requires an action (click, input, navigation), include appropriate commands and a brief response.
7. If you lack necessary info, ask a clarification with empty commands.
8. Do not include URLs in the response text.

## Output format
{output_example}

If the request cannot be understood:
{fallback_example}
"""
