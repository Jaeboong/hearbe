# -*- coding: utf-8 -*-
"""
NLU/LLM pipeline handler.
"""

import logging

logger = logging.getLogger(__name__)


class LLMPipelineHandler:
    def __init__(self, nlu_service, llm_planner, flow_engine, sender, command_pipeline):
        self._nlu = nlu_service
        self._llm = llm_planner
        self._flow = flow_engine
        self._sender = sender
        self._command_pipeline = command_pipeline

    async def handle(self, session_id: str, text: str, session, interrupted) -> str:
        """
        Handle text through NLU/LLM pipeline.

        Returns the TTS text that was sent (if any).
        """
        if interrupted():
            return ""
        intent = None
        resolved_text = text

        # NLU processing
        if self._nlu:
            context = session.context
            intent = await self._nlu.analyze_intent(text, context)
            resolved_text = await self._nlu.resolve_reference(text, context)

        if not self._llm:
            return ""

        response = await self._llm.generate_commands(
            resolved_text,
            intent,
            session
        )
        if interrupted():
            return ""

        if response.requires_flow and self._flow:
            flow_type = response.flow_type
            site = session.current_site or "coupang"
            step = await self._flow.start_flow(flow_type, site, session)
            if interrupted():
                return ""
            await self._sender.send_flow_step(session_id, step)
            return ""

        commands = self._command_pipeline.prepare_commands(
            session_id,
            response.commands,
            session.current_url or "",
            allow_extract=False,
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
            interrupted,
        )
        return tts_text or ""
