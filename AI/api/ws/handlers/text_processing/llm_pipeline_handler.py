# -*- coding: utf-8 -*-
"""
NLU/LLM pipeline handler.
"""

import logging

from core.interfaces import IntentType
from services.llm.planner.selection.option_select import coerce_option_clicks, is_option_request
from services.llm.feedback.fast_ack import FastAckGenerator
from services.llm.sites.site_manager import get_page_type

logger = logging.getLogger(__name__)


class LLMPipelineHandler:
    def __init__(self, nlu_service, llm_planner, flow_engine, sender, command_pipeline):
        self._nlu = nlu_service
        self._llm = llm_planner
        self._flow = flow_engine
        self._sender = sender
        self._command_pipeline = command_pipeline
        self._fast_ack = FastAckGenerator()

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

        if session and session.context:
            detail = session.context.get("product_detail")
            if isinstance(detail, dict) and detail.get("options_list"):
                options_list = detail.get("options_list") or {}
                option_keys = list(options_list.keys()) if isinstance(options_list, dict) else []
                logger.info(
                    "LLM context has options_list: session=%s keys=%s",
                    session_id,
                    option_keys,
                )

        response = await self._llm.generate_commands(
            resolved_text,
            intent,
            session
        )
        if interrupted():
            return ""

        if response and response.commands:
            allow_option = is_option_request(resolved_text)
            coerced_commands, changed = coerce_option_clicks(response.commands, session, allow_option)
            if changed:
                logger.info(
                    "Adjusted option commands (allow=%s): session=%s",
                    allow_option,
                    session_id,
                )
            response.commands = coerced_commands

        if response.requires_flow and self._flow:
            flow_type = response.flow_type
            site = session.current_site or "coupang"
            step = await self._flow.start_flow(flow_type, site, session)
            if interrupted():
                return ""
            await self._sender.send_flow_step(session_id, step)
            return ""

        allow_extract = bool(intent and intent.intent == IntentType.SEARCH)
        if not allow_extract and response.commands:
            allow_extract = any(
                (cmd.tool_name or "").startswith("extract")
                for cmd in response.commands
            )
        commands = self._command_pipeline.prepare_commands(
            session_id,
            response.commands,
            session.current_url or "",
            allow_extract=allow_extract,
        )
        if session:
            page_type = get_page_type(session.current_url or "") if session.current_url else None
        else:
            page_type = None
        ack_text = self._fast_ack.get_ack(
            resolved_text,
            page_type,
            intent.intent if intent else None,
            commands,
        )
        if ack_text:
            await self._sender.send_tts_response(session_id, ack_text)
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
