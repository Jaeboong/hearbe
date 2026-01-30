"""
Selection helpers for session and conversation context.
"""

import json
from typing import Any, Dict, List, Optional


def select_search_results(
    session_context: Optional[Dict[str, Any]] = None,
    conversation_history: List[Dict[str, Any]] = None,
) -> List[Any]:
    if session_context:
        results = session_context.get("search_active_results") or session_context.get("search_results")
        if isinstance(results, list) and results:
            return results
    return _extract_search_results_from_history(conversation_history)


def _extract_search_results_from_history(
    conversation_history: List[Dict[str, Any]] = None,
) -> List[Any]:
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


def select_product_detail(
    session_context: Optional[Dict[str, Any]] = None,
    conversation_history: List[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    if session_context:
        detail = session_context.get("product_detail")
        if isinstance(detail, dict) and detail:
            return detail
    # Product detail is not stored in history currently.
    return None


def select_cart_items(
    session_context: Optional[Dict[str, Any]] = None,
    conversation_history: List[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    if session_context:
        items = session_context.get("cart_items")
        if isinstance(items, list) and items:
            return items
    return []
