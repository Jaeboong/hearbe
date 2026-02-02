# -*- coding: utf-8 -*-
"""
Text queue manager: per-session queue + dedup + interrupt clearing.
"""

import asyncio
import logging
import time
from collections import deque
from typing import Deque, Dict, Tuple, Optional

from .text_normalizer import normalize_text

logger = logging.getLogger(__name__)

MAX_TEXT_QUEUE_SIZE = 20  # Max pending text messages per session
DEDUP_WINDOW_SEC = 1.5    # Drop duplicate inputs within this window
DEDUP_RECENT_LIMIT = 8    # Track a small recent window per session


class TextQueueManager:
    def __init__(
        self,
        max_queue_size: int = MAX_TEXT_QUEUE_SIZE,
        dedup_window_sec: float = DEDUP_WINDOW_SEC,
        dedup_recent_limit: int = DEDUP_RECENT_LIMIT,
    ):
        self._max_queue_size = max_queue_size
        self._dedup_window_sec = dedup_window_sec
        self._dedup_recent_limit = dedup_recent_limit

        self._queues: Dict[str, asyncio.Queue] = {}
        self._pending_texts: Dict[str, Deque[str]] = {}
        self._recent_texts: Dict[str, Deque[Tuple[str, float]]] = {}

    def create_session(self, session_id: str) -> asyncio.Queue:
        queue = asyncio.Queue(maxsize=self._max_queue_size)
        self._queues[session_id] = queue
        self._pending_texts[session_id] = deque()
        self._recent_texts[session_id] = deque(maxlen=self._dedup_recent_limit)
        return queue

    def get_queue(self, session_id: str) -> Optional[asyncio.Queue]:
        return self._queues.get(session_id)

    def cleanup_session(self, session_id: str) -> None:
        self._queues.pop(session_id, None)
        self._pending_texts.pop(session_id, None)
        self._recent_texts.pop(session_id, None)

    def interrupt(self, session_id: str) -> None:
        queue = self._queues.get(session_id)
        if queue:
            while not queue.empty():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
        pending = self._pending_texts.get(session_id)
        if pending is not None:
            pending.clear()
        recent = self._recent_texts.get(session_id)
        if recent is not None:
            recent.clear()

    def enqueue_text(self, session_id: str, text: str) -> bool:
        queue = self._queues.get(session_id)
        if not queue:
            logger.warning(f"No text queue for session: {session_id}")
            return False

        normalized = normalize_text(text)
        if not normalized:
            return False
        if self._is_duplicate_text(session_id, normalized):
            logger.info("Dropping duplicate text input: session=%s text='%s'", session_id, normalized[:80])
            return False

        try:
            queue.put_nowait(text)
            self._track_enqueued(session_id, normalized)
            return True
        except asyncio.QueueFull:
            logger.warning(f"Text queue full, dropping oldest: {session_id}")
            try:
                dropped = queue.get_nowait()
                self._mark_dequeued(session_id, dropped)
                queue.put_nowait(text)
                self._track_enqueued(session_id, normalized)
                return True
            except asyncio.QueueEmpty:
                return False

    def mark_dequeued(self, session_id: str, text: str) -> None:
        self._mark_dequeued(session_id, text)

    def _is_duplicate_text(self, session_id: str, normalized: str) -> bool:
        pending = self._pending_texts.get(session_id)
        if pending and normalized in pending:
            return True

        recent = self._recent_texts.get(session_id)
        if not recent:
            return False

        now = time.monotonic()
        while recent and (now - recent[0][1]) > self._dedup_window_sec:
            recent.popleft()

        for text, ts in recent:
            if text == normalized and (now - ts) <= self._dedup_window_sec:
                return True
        return False

    def _track_enqueued(self, session_id: str, normalized: str) -> None:
        pending = self._pending_texts.get(session_id)
        if pending is not None:
            pending.append(normalized)
        recent = self._recent_texts.get(session_id)
        if recent is not None:
            recent.append((normalized, time.monotonic()))

    def _mark_dequeued(self, session_id: str, text: str) -> None:
        normalized = normalize_text(text)
        if not normalized:
            return
        pending = self._pending_texts.get(session_id)
        if not pending:
            return
        try:
            pending.remove(normalized)
        except ValueError:
            pass
