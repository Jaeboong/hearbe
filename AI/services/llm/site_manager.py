"""
사이트 관리자 모듈

각 쇼핑몰의 셀렉터, URL, 규칙을 로딩하고 관리합니다.
현재 URL 기반으로 어떤 사이트에 있는지 판단하고, 해당 사이트의 셀렉터를 반환합니다.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse


class SiteConfig:
    """단일 사이트 설정"""
    
    def __init__(self, data: Dict[str, Any]):
        self.site_id: str = data.get("site_id", "")
        self.name: str = data.get("name", "")
        self.domains: List[str] = data.get("domains", [])
        self.urls: Dict[str, str] = data.get("urls", {})
        self.selectors: Dict[str, Any] = data.get("selectors", {})
        self.patterns: Dict[str, str] = data.get("patterns", {})
    
    def get_selector(self, category: str, name: str) -> Optional[str]:
        """셀렉터 가져오기 (예: get_selector("search", "input"))"""
        category_selectors = self.selectors.get(category, {})
        return category_selectors.get(name)
    
    def get_url(self, name: str) -> Optional[str]:
        """URL 가져오기 (예: get_url("home"))"""
        return self.urls.get(name)
    
    def matches_domain(self, url: str) -> bool:
        """URL이 이 사이트에 속하는지 확인"""
        if not url:
            return False
        try:
            parsed = urlparse(url)
            host = parsed.netloc.lower()
            for domain in self.domains:
                if domain in host:
                    return True
        except Exception:
            pass
        return False


class SiteManager:
    """사이트 설정 관리자"""
    
    def __init__(self, sites_dir: Optional[str] = None):
        if sites_dir is None:
            # services/llm/ -> services/ -> AI/ -> sites/
            sites_dir = Path(__file__).parent.parent.parent / "sites"
        self.sites_dir = Path(sites_dir)
        self.sites: Dict[str, SiteConfig] = {}
        self._load_all_sites()
    
    def _load_all_sites(self) -> None:
        """모든 사이트 설정 로딩"""
        if not self.sites_dir.exists():
            return
        for json_file in self.sites_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    site = SiteConfig(data)
                    if site.site_id:
                        self.sites[site.site_id] = site
            except Exception as e:
                print(f"Failed to load {json_file}: {e}")
    
    def get_site(self, site_id: str) -> Optional[SiteConfig]:
        """사이트 ID로 설정 가져오기"""
        return self.sites.get(site_id)
    
    def get_site_by_url(self, url: str) -> Optional[SiteConfig]:
        """URL로 어떤 사이트인지 판단"""
        for site in self.sites.values():
            if site.matches_domain(url):
                return site
        return None
    
    def get_site_id_by_url(self, url: str) -> Optional[str]:
        """URL로 사이트 ID 가져오기"""
        site = self.get_site_by_url(url)
        return site.site_id if site else None
    
    def get_search_selectors(self, url: str) -> Optional[Dict[str, str]]:
        """현재 URL의 사이트 검색 셀렉터 반환"""
        site = self.get_site_by_url(url)
        if site:
            return site.selectors.get("search")
        return None
    
    def list_sites(self) -> List[str]:
        """등록된 모든 사이트 ID 목록"""
        return list(self.sites.keys())


# 싱글톤 인스턴스
_manager: Optional[SiteManager] = None


def get_site_manager() -> SiteManager:
    """SiteManager 싱글톤 인스턴스 반환"""
    global _manager
    if _manager is None:
        _manager = SiteManager()
    return _manager


def get_current_site(url: str) -> Optional[SiteConfig]:
    """현재 URL의 사이트 설정 반환 (편의 함수)"""
    return get_site_manager().get_site_by_url(url)


def get_selector(url: str, category: str, name: str) -> Optional[str]:
    """현재 URL 기반으로 셀렉터 가져오기 (편의 함수)"""
    site = get_current_site(url)
    if site:
        return site.get_selector(category, name)
    return None
