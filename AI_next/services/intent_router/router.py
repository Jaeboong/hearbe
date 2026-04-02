"""
IntentRouter: 핵심 오케스트레이션

텍스트 → KoELECTRA 분류 → 페이지 감지 → 액션 실행/TTS 생성
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

from config.actions import ActionDef, get_action_registry
from services.nlu.classifier import IntentClassifier
from services.nlu.param_extractor import ParamExtractor
from services.sites.site_manager import SiteManager
from .action_executor import ActionExecutor, GeneratedCommand
from .read_handler import ReadHandler

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.5


@dataclass
class IntentResult:
    """인텐트 라우터 처리 결과"""
    tts_text: str = ""
    commands: List[GeneratedCommand] = field(default_factory=list)
    intent: str = ""
    confidence: float = 0.0
    site_id: str = ""
    page_type: str = ""


class IntentRouter:
    """
    텍스트 → 의도 분류 → 액션 실행 파이프라인

    1. URL로 사이트 판별 → 어떤 모델 사용할지
    2. KoELECTRA로 의도 분류
    3. confidence < threshold 또는 unknown → TTS 안내
    4. 파라미터 추출
    5. 액션 정의 조회
    6. 페이지 제약 확인
    7. read → TTS 텍스트 생성
    8. action/composite → MCP 커맨드 빌드
    """

    def __init__(self, classifier: IntentClassifier, site_manager: SiteManager):
        self._classifier = classifier
        self._site_manager = site_manager
        self._param_extractor = ParamExtractor()
        self._action_executor = ActionExecutor(site_manager)
        self._read_handler = ReadHandler()
        self._action_registry = get_action_registry()

    async def process(self, text: str, session) -> IntentResult:
        """사용자 텍스트를 처리하여 MCP 커맨드 및 TTS 응답 생성"""
        text = text.strip()
        if not text:
            return IntentResult(tts_text="명령을 말씀해 주세요.")

        current_url = getattr(session, "current_url", "") or ""
        context = getattr(session, "context", {}) or {}

        # 1. 사이트 판별
        site_id = self._select_model(current_url)

        # 2. 의도 분류
        intent, confidence = self._classifier.classify(text, site_id)
        logger.info(
            "[NLU] site=%s intent=%s conf=%.3f text='%s'",
            site_id, intent, confidence, text[:80],
        )

        # 3. 저신뢰도 / unknown
        if confidence < CONFIDENCE_THRESHOLD or intent == "unknown":
            return IntentResult(
                tts_text="죄송합니다. 무슨 말씀이신지 잘 모르겠습니다. 다시 한번 말씀해 주세요.",
                intent=intent,
                confidence=confidence,
                site_id=site_id,
            )

        # 4. 파라미터 추출
        params = self._param_extractor.extract(intent, text)

        # 5. 액션 정의 조회
        action_def = self._find_action(site_id, intent)
        if not action_def:
            # 크로스사이트 인텐트 처리 (go_hearbe, go_coupang)
            cross = self._handle_cross_site(intent, site_id)
            if cross:
                return cross
            return IntentResult(
                tts_text="이 기능은 현재 지원하지 않습니다.",
                intent=intent,
                confidence=confidence,
                site_id=site_id,
            )

        # 6. 페이지 감지 + 제약 확인
        page_type = self._get_page_type(current_url, site_id)

        if not self._check_page_constraints(action_def, page_type):
            return IntentResult(
                tts_text="이 기능은 현재 페이지에서 사용할 수 없습니다. 해당 페이지로 먼저 이동해 주세요.",
                intent=intent,
                confidence=confidence,
                site_id=site_id,
                page_type=page_type or "",
            )

        # 7. 필수 파라미터 확인
        if action_def.params:
            missing = [p for p in action_def.params if not params.get(p)]
            if missing:
                return IntentResult(
                    tts_text=self._missing_param_prompt(missing),
                    intent=intent,
                    confidence=confidence,
                    site_id=site_id,
                    page_type=page_type or "",
                )

        # 8. 처리
        if action_def.action_type == "read":
            tts = self._read_handler.handle(action_def, site_id, page_type, context, params)
            return IntentResult(
                tts_text=tts or "정보를 읽을 수 없습니다.",
                intent=intent,
                confidence=confidence,
                site_id=site_id,
                page_type=page_type or "",
            )

        # action / composite → MCP 커맨드 빌드
        commands = self._action_executor.build_commands(
            action_def, site_id, page_type, current_url, params, context,
        )
        tts = self._build_confirm_tts(action_def, params)

        return IntentResult(
            tts_text=tts,
            commands=commands,
            intent=intent,
            confidence=confidence,
            site_id=site_id,
            page_type=page_type or "",
        )

    # ── 내부 메서드 ─────────────────────────────────────────

    def _select_model(self, url: str) -> str:
        site = self._site_manager.get_site_by_url(url)
        if site and self._classifier.is_ready(site.site_id):
            return site.site_id
        if self._classifier.is_ready("hearbe"):
            return "hearbe"
        if self._classifier.is_ready("coupang"):
            return "coupang"
        return "hearbe"

    def _find_action(self, site_id: str, intent: str) -> Optional[ActionDef]:
        site_actions = self._action_registry.get(site_id, {})
        return site_actions.get(intent)

    def _get_page_type(self, url: str, site_id: str) -> Optional[str]:
        site = self._site_manager.get_site(site_id)
        if site:
            return site.detect_page_type(url)
        return None

    def _check_page_constraints(self, action_def: ActionDef, page_type: Optional[str]) -> bool:
        if action_def.required_pages is None:
            return True
        if page_type is None:
            return True  # 페이지를 모르면 허용 (실행 시 실패할 수 있음)
        return page_type in action_def.required_pages

    def _handle_cross_site(self, intent: str, current_site_id: str) -> Optional[IntentResult]:
        if intent == "go_hearbe":
            return IntentResult(
                tts_text="허비 홈으로 이동합니다.",
                commands=[
                    GeneratedCommand("goto", {"url": "https://i14d108.p.ssafy.io/main"}, "허비 이동"),
                ],
                intent=intent,
                site_id=current_site_id,
            )
        if intent in ("go_coupang", "click_go_coupang"):
            return IntentResult(
                tts_text="쿠팡으로 이동합니다.",
                commands=[
                    GeneratedCommand("goto", {"url": "https://www.coupang.com/"}, "쿠팡 이동"),
                ],
                intent=intent,
                site_id=current_site_id,
            )
        return None

    def _build_confirm_tts(self, action_def: ActionDef, params: Dict[str, Any]) -> str:
        if action_def.tts_confirm:
            text = action_def.tts_confirm
            for key, value in params.items():
                if value is not None:
                    text = text.replace(f"{{{key}}}", str(value))
            return text
        return "요청을 처리하겠습니다."

    def _missing_param_prompt(self, missing: list) -> str:
        prompts = {
            "query": "검색할 내용을 말씀해 주세요.",
            "ordinal": "몇 번째 항목인지 말씀해 주세요.",
            "id_value": "아이디를 말씀해 주세요.",
            "password_value": "비밀번호를 말씀해 주세요.",
            "password_confirm_value": "비밀번호를 다시 말씀해 주세요.",
            "quantity": "수량을 말씀해 주세요.",
            "option_text": "원하시는 옵션을 말씀해 주세요.",
            "name_value": "이름을 말씀해 주세요.",
            "email_value": "이메일 주소를 말씀해 주세요.",
            "phone_value": "전화번호를 말씀해 주세요.",
        }
        if missing:
            return prompts.get(missing[0], "추가 정보를 말씀해 주세요.")
        return "추가 정보가 필요합니다."
