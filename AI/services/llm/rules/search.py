"""
검색 규칙
"""

from typing import Optional
from . import BaseRule, RuleResult
from ..context.context_rules import (
    extract_search_query,
    detect_target_site,
    build_search_with_navigation_commands,
    build_extract_products_command
)


class SearchRule(BaseRule):
    """검색 규칙: '생수 검색', '쿠팡에서 물티슈 검색' 등"""
    
    def check(self, text: str, current_url: str, current_site) -> Optional[RuleResult]:
        if "검색" not in text:
            return None

        query = extract_search_query(text)
        if not query:
            return None

        target_site = detect_target_site(text, self.site_manager, current_site)
        if not target_site:
            return None

        needs_navigation = not target_site.matches_domain(current_url)
        commands = build_search_with_navigation_commands(
            target_site, query, needs_navigation, current_url
        )

        extract_cmd = build_extract_products_command(target_site, current_url)
        if extract_cmd:
            commands.append(extract_cmd)


        return RuleResult(
            matched=True,
            commands=commands,
            response_text=f"'{query}'를 {target_site.name}에서 검색합니다.",
            rule_name="search"
        )
