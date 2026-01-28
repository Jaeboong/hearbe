"""
Site-specific extraction dispatchers.
"""

from __future__ import annotations

from typing import List, Dict, Any

from .coupang_search import extract_coupang_search_results


async def extract_search_results_dynamic(page, url: str | None = None) -> List[Dict[str, Any]]:
    """
    Dispatch dynamic extraction by site.
    """
    page_url = url or getattr(page, "url", "") or ""
    if "coupang.com" in page_url:
        return await extract_coupang_search_results(page)
    return []
