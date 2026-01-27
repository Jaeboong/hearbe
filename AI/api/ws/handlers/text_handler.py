# -*- coding: utf-8 -*-
"""
Text handler: user_input -> NLU/LLM/Flow -> TTS/tool_calls
"""

import asyncio
import logging
import re
from typing import Dict, Any, Optional, Tuple

from core.interfaces import ASRResult
from ..search_reader import build_search_read_tts

logger = logging.getLogger(__name__)

MAX_TEXT_QUEUE_SIZE = 20  # Max pending text messages per session


class TextHandler:
    """Handles text input pipeline and flow steps."""

    def __init__(self, nlu_service, llm_planner, flow_engine, session_manager, sender, action_feedback):
        self._nlu = nlu_service
        self._llm = llm_planner
        self._flow = flow_engine
        self._session = session_manager
        self._sender = sender
        self._action_feedback = action_feedback

        self._text_queues: Dict[str, asyncio.Queue] = {}
        self._text_tasks: Dict[str, asyncio.Task] = {}

    async def create_session(self, session_id: str):
        self._text_queues[session_id] = asyncio.Queue(maxsize=MAX_TEXT_QUEUE_SIZE)
        self._text_tasks[session_id] = asyncio.create_task(self._text_worker(session_id))

    async def cleanup_session(self, session_id: str):
        task = self._text_tasks.pop(session_id, None)
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        self._text_queues.pop(session_id, None)

    async def handle_user_input(self, session_id: str, text: str):
        result = ASRResult(
            text=text,
            confidence=1.0,
            language="ko",
            duration=0.0,
            is_final=True,
            segment_id="text_input"
        )
        await self._sender.send_asr_result(session_id, result)
        await self.enqueue_text(session_id, text)

    async def handle_user_confirm(self, session_id: str, data: Dict[str, Any]):
        confirmed = data.get("confirmed", False)
        await self.enqueue_text(session_id, "yes" if confirmed else "no")

    async def handle_cancel(self, session_id: str):
        session = self._session.get_session(session_id) if self._session else None
        if session and self._flow:
            await self._flow.cancel_flow(session)

        await self._sender.send_status(session_id, "cancelled", "Cancelled")

        await self._sender.send_tts_response(session_id, "Cancelled")

    async def enqueue_text(self, session_id: str, text: str):
        queue = self._text_queues.get(session_id)
        if not queue:
            logger.warning(f"No text queue for session: {session_id}")
            return
        if not text:
            return

        try:
            queue.put_nowait(text)
        except asyncio.QueueFull:
            logger.warning(f"Text queue full, dropping oldest: {session_id}")
            try:
                queue.get_nowait()
                queue.put_nowait(text)
            except asyncio.QueueEmpty:
                pass

    async def _text_worker(self, session_id: str):
        queue = self._text_queues.get(session_id)
        if not queue:
            return

        logger.debug(f"Text worker started: {session_id}")
        try:
            while True:
                try:
                    text = await asyncio.wait_for(queue.get(), timeout=30.0)
                except asyncio.TimeoutError:
                    continue
                await self._process_text_input(session_id, text)
        except asyncio.CancelledError:
            logger.debug(f"Text worker cancelled: {session_id}")
        except Exception as e:
            logger.error(f"Text worker error: {session_id}: {e}")

    async def _process_text_input(self, session_id: str, text: str):
        try:
            session = self._session.get_session(session_id) if self._session else None
            if not session:
                return

            if self._session:
                self._session.add_to_history(session_id, "user", text)

            if self._flow and self._flow.is_flow_active(session_id):
                await self._handle_flow_input(session_id, text)
                return

            # Search results readout handling (before NLU/LLM)
            handled = await self._handle_search_read_request(session_id, text, session)
            if handled:
                return

            intent = None
            resolved_text = text

            if self._nlu:
                context = session.context
                intent = await self._nlu.analyze_intent(text, context)
                resolved_text = await self._nlu.resolve_reference(text, context)

            if self._llm:
                response = await self._llm.generate_commands(
                    resolved_text,
                    intent,
                    session
                )

                if response.requires_flow and self._flow:
                    flow_type = response.flow_type
                    site = session.current_site or "coupang"
                    step = await self._flow.start_flow(flow_type, site, session)
                    await self._sender.send_flow_step(session_id, step)
                else:
                    if response.commands:
                        await self._sender.send_tool_calls(session_id, response.commands)
                    else:
                        logger.info(
                            "No commands generated for session=%s text='%s'",
                            session_id,
                            resolved_text[:80]
                        )

                pending_msg = None
                if response.commands:
                    pending_msg = self._action_feedback.register_commands(
                        session_id,
                        response.commands,
                        session.current_url or ""
                    )

                if pending_msg:
                    logger.info(f"Sending pending TTS response: '{pending_msg[:80]}...'")
                    await self._sender.send_tts_response(session_id, pending_msg)
                    if self._session:
                        self._session.add_to_history(session_id, "assistant", pending_msg)
                elif response.text:
                    logger.info(f"Sending TTS response: '{response.text[:80]}...'")
                    await self._sender.send_tts_response(session_id, response.text)
                    if self._session:
                        self._session.add_to_history(session_id, "assistant", response.text)

                # If no response text and no pending message, keep silent.

        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            await self._sender.send_error(session_id, "Processing error")

    async def _handle_search_read_request(
        self,
        session_id: str,
        text: str,
        session
    ) -> bool:
        """
        Handle commands like:
        - "현재 페이지 모든 상품 읽어줘"
        - "전체 읽어줘"
        - "n개 더 읽어줘"
        """
        results = session.context.get("search_results") if session else None
        if not isinstance(results, list) or not results:
            return False

        normalized = text.strip().lower()
        if not normalized:
            return False

        if not self._is_read_request(normalized):
            return False

        mode, count = self._parse_read_request(normalized)
        total = len(results)
        start_index = session.context.get("search_read_index", 0)

        if mode == "all":
            start_index = 0
            count = total
        elif mode == "more":
            count = count or 4
        else:
            return False

        tts_text, next_index, has_more = build_search_read_tts(
            results,
            start_index=start_index,
            count=count,
            include_total=(mode == "all" and start_index == 0)
        )
        self._session.set_context(session_id, "search_read_index", next_index)

        if has_more:
            tts_text += " 더 읽어드릴까요? 'n개 더 읽어줘' 또는 '전체 읽어줘'라고 말해 주세요."
        await self._sender.send_tts_response(session_id, tts_text)
        return True

    def _is_read_request(self, normalized: str) -> bool:
        keywords = ["읽어", "읽어줘", "읽어주", "읽어줄래", "들려", "들려줘"]
        target = ["상품", "검색", "검색결과", "결과", "전체", "모든", "현재"]
        return any(k in normalized for k in keywords) and any(t in normalized for t in target)

    def _parse_read_request(self, normalized: str) -> Tuple[Optional[str], Optional[int]]:
        if "전체" in normalized or "모든" in normalized:
            return "all", None
        if "더" in normalized:
            match = re.search(r"(\\d+)\\s*개", normalized)
            if match:
                return "more", int(match.group(1))
            return "more", None
        return None, None

    async def _handle_flow_input(self, session_id: str, text: str):
        session = self._session.get_session(session_id) if self._session else None
        if not session:
            return

        user_input = {"text": text}
        next_step = await self._flow.next_step(session, user_input)
        await self._sender.send_flow_step(session_id, next_step)

        if next_step.prompt:
            await self._sender.send_tts_response(session_id, next_step.prompt)
