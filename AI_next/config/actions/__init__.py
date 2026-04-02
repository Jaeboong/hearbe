"""
선언적 액션 정의 데이터클래스 및 레지스트리

ActionStep: 단일 브라우저 액션 (click, fill, goto 등)
ActionDef: 하나의 인텐트에 대한 전체 액션 정의
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class ActionStep:
    """단일 브라우저 액션"""
    tool_name: str                       # "click" | "fill" | "press" | "goto" | "wait" | "wait_for_selector" | "extract" | "click_text"
    selector: Optional[str] = None       # CSS 셀렉터 직접 지정
    selector_key: Optional[str] = None   # config/sites JSON의 셀렉터 키 (실행 시 해석)
    value: Optional[str] = None          # fill 값, "{query}" 플레이스홀더 가능
    key: Optional[str] = None            # press 키 ("Enter" 등)
    url: Optional[str] = None            # goto URL 직접 지정
    url_key: Optional[str] = None        # sites/index.json의 URL 키 ("home", "login" 등)
    text: Optional[str] = None           # click_text 대상 텍스트
    frame: Optional[str] = None          # iframe 셀렉터
    ms: int = 0                          # wait 시간 (밀리초)
    timeout: int = 5000                  # wait_for_selector 타임아웃
    state: str = "visible"               # wait_for_selector 상태
    optional: bool = False               # True면 실패해도 무시
    description: str = ""


@dataclass
class ActionDef:
    """인텐트에 대한 액션 정의"""
    intent: str                                      # KoELECTRA 인텐트 이름
    action_type: str                                 # "action" | "read" | "composite"
    steps: List[ActionStep] = field(default_factory=list)
    required_pages: Optional[List[str]] = None       # 이 페이지에서만 유효 (None = 모든 페이지)
    params: Optional[List[str]] = None               # 필요한 파라미터 목록
    read_source: Optional[str] = None                # "context:search_results" | "hardcoded" 등
    tts_template: Optional[str] = None               # TTS 출력 템플릿
    tts_confirm: Optional[str] = None                # 액션 실행 시 확인 TTS


def get_action_registry() -> Dict[str, Dict[str, ActionDef]]:
    """사이트별 인텐트→액션 레지스트리 반환

    Returns:
        {"coupang": {"click_cart": ActionDef(...), ...}, "hearbe": {...}}
    """
    from .coupang import COUPANG_ACTIONS
    from .hearbe import HEARBE_ACTIONS

    registry = {}
    for site_id, actions_list in [("coupang", COUPANG_ACTIONS), ("hearbe", HEARBE_ACTIONS)]:
        registry[site_id] = {action.intent: action for action in actions_list}
    return registry
