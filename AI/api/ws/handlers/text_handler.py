# -*- coding: utf-8 -*-
"""
Text handler: user_input -> NLU/LLM/Flow -> TTS/tool_calls

Coordinates text processing pipeline and delegates to specialized handlers.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any

from core.interfaces import ASRResult, MCPCommand
from .search_query_handler import SearchQueryHandler
from .command_pipeline import CommandPipeline

logger = logging.getLogger(__name__)

MAX_TEXT_QUEUE_SIZE = 20  # Max pending text messages per session


def _try_load_ai_next_router():
    """Best-effort AI_next router loader (no hard dependency)."""
    try:
        repo_root = Path(__file__).resolve().parents[4]
        ai_next_root = repo_root / "AI_next"
        if not ai_next_root.exists():
            return None
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        from AI_next.core.decision.router import RuleRouter  # type: ignore
        return RuleRouter()
    except Exception:
        return None


class TextHandler:
    """
    Handles text input pipeline and flow steps.

    Responsibilities:
    - Queue/worker management for text inputs
    - Routing to appropriate handlers (Flow, Search, LLM)
    - Coordinating NLU/LLM pipeline
    """

    def __init__(
        self,
        nlu_service,
        llm_planner,
        flow_engine,
        session_manager,
        sender,
        action_feedback,
        login_guard=None,
        login_feedback=None,
    ):
        self._nlu = nlu_service
        self._llm = llm_planner
        self._flow = flow_engine
        self._session = session_manager
        self._sender = sender
        self._action_feedback = action_feedback
        self._login_guard = login_guard
        self._login_feedback = login_feedback
        self._ai_next_router = _try_load_ai_next_router()
        self._command_pipeline = CommandPipeline(
            sender=sender,
            action_feedback=action_feedback,
            login_guard=login_guard,
            login_feedback=login_feedback,
        )

        # Specialized handlers
        self._search_query_handler = SearchQueryHandler(session_manager, sender)

        # Queue management
        self._text_queues: Dict[str, asyncio.Queue] = {}
        self._text_tasks: Dict[str, asyncio.Task] = {}
        self._interrupt_epochs: Dict[str, int] = {}

    async def create_session(self, session_id: str):
        """Create text processing queue and worker for session."""
        self._text_queues[session_id] = asyncio.Queue(maxsize=MAX_TEXT_QUEUE_SIZE)
        self._text_tasks[session_id] = asyncio.create_task(self._text_worker(session_id))

    async def cleanup_session(self, session_id: str):
        """Clean up session resources."""
        task = self._text_tasks.pop(session_id, None)
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        self._text_queues.pop(session_id, None)
        self._interrupt_epochs.pop(session_id, None)

    async def interrupt(self, session_id: str):
        """Interrupt current processing and prioritize new input."""
        self._interrupt_epochs[session_id] = self._interrupt_epochs.get(session_id, 0) + 1

        queue = self._text_queues.get(session_id)
        if queue:
            while not queue.empty():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

        session = self._session.get_session(session_id) if self._session else None
        if session and self._flow and self._flow.is_flow_active(session_id):
            await self._flow.cancel_flow(session)

    async def handle_user_input(self, session_id: str, text: str):
        """Handle text input from user."""
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
        """Handle user confirmation (yes/no)."""
        confirmed = data.get("confirmed", False)
        await self.enqueue_text(session_id, "yes" if confirmed else "no")

    async def handle_cancel(self, session_id: str):
        """Handle cancellation request."""
        session = self._session.get_session(session_id) if self._session else None
        if session and self._flow:
            await self._flow.cancel_flow(session)

        await self._sender.send_status(session_id, "cancelled", "Cancelled")
        await self._sender.send_tts_response(session_id, "Cancelled")

    async def enqueue_text(self, session_id: str, text: str):
        """Enqueue text for processing."""
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
        """Background worker that processes queued text inputs."""
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
        """
        Process text input through the pipeline.

        Flow:
        1. Check if flow is active -> delegate to flow handler
        2. Check if search query -> delegate to search query handler
        3. Otherwise -> NLU/LLM pipeline
        """
        try:
            session = self._session.get_session(session_id) if self._session else None
            if not session:
                return
            epoch = self._interrupt_epochs.get(session_id, 0)

            if self._session:
                self._session.add_to_history(session_id, "user", text)

            # Flow handling (highest priority)
            if self._flow and self._flow.is_flow_active(session_id):
                await self._handle_flow_input(session_id, text)
                return

            # Search query handling (second priority, before LLM)
            handled = await self._search_query_handler.handle_query(session_id, text, session)
            if handled:
                return

            if self._is_interrupted(session_id, epoch):
                return

            # AI_next router (before LLM)
            handled = await self._handle_ai_next_rules(session_id, text, session, epoch)
            if handled:
                return

            # NLU/LLM pipeline (default)
            await self._handle_llm_pipeline(session_id, text, session, epoch)

        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            await self._sender.send_error(session_id, "Processing error")

    async def _handle_llm_pipeline(self, session_id: str, text: str, session, epoch: int):
        """
        Handle text through NLU/LLM pipeline.

        Steps:
        1. NLU: intent analysis & reference resolution
        2. LLM: command generation
        3. Send commands or start flow
        4. Send TTS response
        """
        intent = None
        resolved_text = text

        # NLU processing
        if self._nlu:
            context = session.context
            intent = await self._nlu.analyze_intent(text, context)
            resolved_text = await self._nlu.resolve_reference(text, context)

        # LLM processing
        if not self._llm:
            return

        response = await self._llm.generate_commands(
            resolved_text,
            intent,
            session
        )
        if self._is_interrupted(session_id, epoch):
            return

        # Flow or command execution
        if response.requires_flow and self._flow:
            flow_type = response.flow_type
            site = session.current_site or "coupang"
            step = await self._flow.start_flow(flow_type, site, session)
            if self._is_interrupted(session_id, epoch):
                return
            await self._sender.send_flow_step(session_id, step)
        else:
            commands = self._command_pipeline.prepare_commands(
                session_id,
                response.commands,
                session.current_url or ""
            )
            if not commands:
                logger.info(
                    "No commands generated for session=%s text='%s'",
                    session_id,
                    resolved_text[:80]
                )
            tts_text = await self._command_pipeline.dispatch(
                session_id,
                commands,
                response.text,
                session.current_url or "",
                lambda: self._is_interrupted(session_id, epoch),
            )
            if tts_text and self._session:
                self._session.add_to_history(session_id, "assistant", tts_text)

    async def _handle_ai_next_rules(self, session_id: str, text: str, session, epoch: int) -> bool:
        if not self._ai_next_router:
            return False
        try:
            result = self._ai_next_router.route(text, session.current_url or "")
        except Exception:
            return False
        if not result:
            return False

        commands = [
            MCPCommand(tool_name=c.tool_name, arguments=c.arguments, description=c.description)
            for c in result.commands
        ]

        commands = self._command_pipeline.prepare_commands(
            session_id,
            commands,
            session.current_url or ""
        )
        tts_text = await self._command_pipeline.dispatch(
            session_id,
            commands,
            result.response_text,
            session.current_url or "",
            lambda: self._is_interrupted(session_id, epoch),
        )
        if tts_text and self._session:
            self._session.add_to_history(session_id, "assistant", tts_text)

        return True

    async def _handle_flow_input(self, session_id: str, text: str):
        """Handle input when flow is active."""
        session = self._session.get_session(session_id) if self._session else None
        if not session:
            return

        user_input = {"text": text}
        next_step = await self._flow.next_step(session, user_input)
        await self._sender.send_flow_step(session_id, next_step)

        if next_step.prompt:
            await self._sender.send_tts_response(session_id, next_step.prompt)

    def _is_interrupted(self, session_id: str, epoch: int) -> bool:
        return self._interrupt_epochs.get(session_id, 0) != epoch
