"""
서비스 모듈 테스트
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

# 테스트 대상 모듈
from services.session import SessionManager
from services.nlu import NLUService
from core.interfaces import IntentType


class TestSessionManager:
    """SessionManager 테스트"""

    @pytest.fixture
    def session_manager(self):
        return SessionManager()

    def test_create_session(self, session_manager):
        """세션 생성 테스트"""
        session = session_manager.create_session()
        assert session is not None
        assert session.session_id is not None
        assert session.conversation_history == []

    def test_get_session(self, session_manager):
        """세션 조회 테스트"""
        session = session_manager.create_session()
        retrieved = session_manager.get_session(session.session_id)
        assert retrieved is not None
        assert retrieved.session_id == session.session_id

    def test_get_nonexistent_session(self, session_manager):
        """존재하지 않는 세션 조회"""
        result = session_manager.get_session("nonexistent-id")
        assert result is None

    def test_update_session(self, session_manager):
        """세션 업데이트 테스트"""
        session = session_manager.create_session()
        updated = session_manager.update_session(
            session.session_id,
            current_site="coupang"
        )
        assert updated.current_site == "coupang"

    def test_add_to_history(self, session_manager):
        """대화 기록 추가 테스트"""
        session = session_manager.create_session()
        session_manager.add_to_history(session.session_id, "user", "테스트 메시지")

        retrieved = session_manager.get_session(session.session_id)
        assert len(retrieved.conversation_history) == 1
        assert retrieved.conversation_history[0]["content"] == "테스트 메시지"

    def test_context_operations(self, session_manager):
        """컨텍스트 저장/조회 테스트"""
        session = session_manager.create_session()

        session_manager.set_context(session.session_id, "test_key", "test_value")
        value = session_manager.get_context(session.session_id, "test_key")

        assert value == "test_value"

    def test_delete_session(self, session_manager):
        """세션 삭제 테스트"""
        session = session_manager.create_session()
        session_manager.delete_session(session.session_id)

        result = session_manager.get_session(session.session_id)
        assert result is None


class TestNLUService:
    """NLUService 테스트"""

    @pytest.fixture
    def nlu_service(self):
        return NLUService()

    @pytest.mark.asyncio
    async def test_analyze_search_intent(self, nlu_service):
        """검색 의도 분석 테스트"""
        result = await nlu_service.analyze_intent("물티슈 찾아줘")
        assert result.intent == IntentType.SEARCH

    @pytest.mark.asyncio
    async def test_analyze_cart_intent(self, nlu_service):
        """장바구니 의도 분석 테스트"""
        result = await nlu_service.analyze_intent("장바구니에 담아줘")
        assert result.intent == IntentType.ADD_TO_CART

    @pytest.mark.asyncio
    async def test_analyze_checkout_intent(self, nlu_service):
        """결제 의도 분석 테스트"""
        result = await nlu_service.analyze_intent("결제할게")
        assert result.intent == IntentType.CHECKOUT

    @pytest.mark.asyncio
    async def test_extract_price_entity(self, nlu_service):
        """가격 개체명 추출 테스트"""
        entities = await nlu_service.extract_entities("10만원 이하로 찾아줘")
        price_entities = [e for e in entities if e.entity_type == "price"]
        assert len(price_entities) > 0

    @pytest.mark.asyncio
    async def test_resolve_ordinal_reference(self, nlu_service):
        """순서 참조 해석 테스트"""
        context = {
            "search_results": [
                {"name": "상품A"},
                {"name": "상품B"},
                {"name": "상품C"}
            ]
        }
        result = await nlu_service.resolve_reference("두 번째 거 보여줘", context)
        assert "상품B" in result


class TestEventBus:
    """EventBus 테스트"""

    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self):
        """구독 및 발행 테스트"""
        from core.event_bus import EventBus, EventType, Event

        bus = EventBus()
        received_events = []

        async def handler(event):
            received_events.append(event)

        bus.subscribe(EventType.STT_RESULT_READY, handler)
        await bus.start()

        event = Event(type=EventType.STT_RESULT_READY, data={"text": "테스트"})
        await bus.publish(event)

        # 이벤트 처리 대기
        await asyncio.sleep(0.1)
        await bus.stop()

        assert len(received_events) == 1
        assert received_events[0].data["text"] == "테스트"