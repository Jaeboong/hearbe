# -*- coding: utf-8 -*-
"""
LLM client wrapper.

Handles API calls, retries, and logging.
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional

from .llm_logging import log_llm_request, log_llm_response

logger = logging.getLogger(__name__)


def resolve_llm_api_key(explicit_key: Optional[str] = None) -> Optional[str]:
    """
    Resolve LLM API key based on environment configuration.

    Order:
    1) explicit_key (if provided)
    2) LLM_API_KEY_NAME -> env value
    3) GMS_API_KEY, GMS_KEY, OPENAI_API_KEY
    """
    if explicit_key:
        return explicit_key
    key_name = os.environ.get("LLM_API_KEY_NAME")
    if key_name:
        key_value = os.environ.get(key_name)
        if key_value:
            return key_value
    return (
        os.environ.get("GMS_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
    )


class LLMClient:
    """OpenAI client wrapper with retry + logging."""

    def __init__(
        self,
        api_key: Optional[str],
        base_url: str,
        model: str,
        max_tokens: int,
    ):
        self.api_key = resolve_llm_api_key(api_key)
        self.base_url = base_url
        self.model = model
        self.max_tokens = max_tokens
        self._client = None

    @property
    def client(self):
        """OpenAI client lazy loading."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                logger.error("openai 패키지가 설치되지 않았습니다: pip install openai")
                raise
        return self._client

    async def request(
        self,
        messages: List[Dict[str, str]],
        current_url: str = "",
        text_len: Optional[int] = None,
        label: str = "",
    ) -> str:
        if label:
            logger.info(
                "LLM request (%s): model=%s, msg_count=%d, url=%s",
                label,
                self.model,
                len(messages or []),
                current_url or "(empty)"
            )
        elif text_len is not None:
            logger.info(
                "LLM request: model=%s, text_len=%d, url=%s",
                self.model,
                text_len,
                current_url or "(empty)"
            )
        else:
            logger.info(
                "LLM request: model=%s, msg_count=%d, url=%s",
                self.model,
                len(messages or []),
                current_url or "(empty)"
            )

        token_param = "max_completion_tokens"
        log_llm_request(
            logger,
            model=self.model,
            base_url=self.base_url,
            messages=messages,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
            token_param=token_param,
        )

        content = None
        last_error = None
        for attempt in range(3):
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                max_completion_tokens=self.max_tokens,
            )
            content = response.choices[0].message.content
            logger.info("LLM response received: chars=%d", len(content or ""))
            log_llm_response(logger, response, content)
            if content:
                break
            last_error = "empty_response"
            if attempt < 2:
                logger.warning("Empty LLM response received, retrying (%d/2)", attempt + 1)

        if not content:
            raise ValueError(last_error or "empty_response")

        return content
