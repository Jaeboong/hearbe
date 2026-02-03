# -*- coding: utf-8 -*-
"""
MCP result handler: HTML/OCR summary -> TTS
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List

from core.event_bus import EventType, publish
from services.llm.sites.site_manager import get_page_type
from ..presenter.pages.search import build_search_list_tts, MORE_PROMPT_COUNT
from ..presenter.pages.cart import build_cart_summary_tts
from ..presenter.pages.login import build_captcha_prompt_tts
from ..presenter.pages.product import build_product_summary_tts, build_ocr_summary_tts
from ..utils.temp_file_manager import TempFileManager

# Summarizer imports (HTML parser + OCR integrator)
try:
    from services.summarizer import (
        parse_product_html,
        detect_site,
        get_ocr_integrator,
    )
    SUMMARIZER_AVAILABLE = True
except ImportError:
    SUMMARIZER_AVAILABLE = False

logger = logging.getLogger(__name__)


class MCPHandler:
    """Handles MCP execution results and summary pipeline."""

    def __init__(
        self,
        sender,
        session_manager,
        action_feedback,
        failure_notifier=None,
        login_guard=None,
        login_feedback=None,
        dom_fallback=None,
    ):
        self._sender = sender
        self._session = session_manager
        self._action_feedback = action_feedback
        self._failure_notifier = failure_notifier
        self._login_guard = login_guard
        self._login_feedback = login_feedback
        self._dom_fallback = dom_fallback
        self._file_manager = TempFileManager()  # Manages temporary JSON files

    async def handle_mcp_result(self, session_id: str, data: Dict[str, Any]):
        """
        Handle MCP execution result from client.

        처리 흐름 (스트리밍 방식):
        1. HTML 파싱 → TTS #1 (즉시, 빠른 응답)
        2. OCR 처리 → TTS #2, #3... (청크 단위, 순차 응답)
        """
        success = data.get("success", False)
        result = data.get("result", {})
        error = data.get("error")
        page_data = data.get("page_data") or {}
        tool_name = data.get("tool_name")
        arguments = data.get("arguments") or {}
        request_id = data.get("request_id")
        products = page_data.get("products") if isinstance(page_data, dict) else None
        if not products and isinstance(result, dict):
            products = result.get("products")
        cart_items = None
        cart_summary = None

        page_url = None
        if isinstance(page_data, dict):
            page_url = page_data.get("url")
        if not page_url and isinstance(result, dict):
            page_url = (
                result.get("current_url")
                or result.get("page_url")
                or result.get("url")
            )

        html_content = None
        detail_images = []
        if isinstance(page_data, dict):
            html_content = page_data.get("html")
            detail_images = page_data.get("detail_images") or []
        if not html_content and isinstance(result, dict):
            html_content = result.get("html")
        if not detail_images and isinstance(result, dict):
            detail_images = result.get("detail_images") or result.get("images") or []

        await publish(
            EventType.MCP_RESULT_RECEIVED,
            data={"success": success, "result": result, "error": error, "page_data": page_data},
            session_id=session_id
        )

        session = self._session.get_session(session_id) if self._session else None
        request_ts = _extract_request_ts(request_id)
        if session and tool_name == "wait_for_new_page":
            nav_ok = bool(result.get("new_page") or result.get("url_changed"))
            self._session.set_context(session_id, "nav_wait_ok", nav_ok)
            if request_ts:
                self._session.set_context(session_id, "nav_wait_ts", request_ts)
        interrupt_ts = None
        if self._session:
            interrupt_ts = self._session.get_context(session_id, "interrupt_ts")
        pre_interrupt = bool(interrupt_ts and request_ts and request_ts <= interrupt_ts)
        is_extract = bool(tool_name and tool_name.startswith("extract"))

        if pre_interrupt and not is_extract:
            logger.info(
                "Skipping MCP result due to interrupt: session=%s tool=%s request_id=%s",
                session_id,
                tool_name,
                request_id
            )
            return

        suppress_outputs = pre_interrupt

        if session and tool_name == "extract_detail":
            nav_wait_ok = self._session.get_context(session_id, "nav_wait_ok")
            nav_wait_ts = self._session.get_context(session_id, "nav_wait_ts")
            page_type = get_page_type(page_url or session.current_url or "")
            if nav_wait_ts and request_ts and request_ts >= nav_wait_ts:
                if not nav_wait_ok and page_type != "product":
                    logger.info(
                        "Skipping extract_detail (no navigation detected): session=%s url=%s",
                        session_id,
                        page_url or session.current_url or ""
                    )
                    return

        if not suppress_outputs and tool_name == "get_dom_snapshot" and self._dom_fallback:
            handled = await self._dom_fallback.handle_dom_snapshot(
                session_id=session_id,
                result=result if isinstance(result, dict) else {},
                current_url=page_url or (session.current_url if session else ""),
            )
            if handled:
                return

        handled = False
        if not suppress_outputs:
            handled = await self._action_feedback.handle_mcp_result(
                session_id=session_id,
                tool_name=tool_name,
                arguments=arguments,
                success=success,
                result=result
            )
            if self._failure_notifier:
                if self._dom_fallback:
                    triggered = await self._dom_fallback.maybe_trigger(
                        session_id=session_id,
                        tool_name=tool_name,
                        arguments=arguments,
                        error=error,
                        current_url=page_url or (session.current_url if session else ""),
                        success=success,
                    )
                    if triggered:
                        return
                await self._failure_notifier.handle_mcp_result(
                    session_id=session_id,
                    tool_name=tool_name,
                    arguments=arguments,
                    success=success,
                    handled=handled,
                    current_url=page_url or (session.current_url if session else "")
                )
        if session and self._session:
            self._session.set_context(session_id, "mcp_result", result)
            if isinstance(result, dict):
                detail = result.get("detail") or result.get("product_detail")
                if detail:
                    self._session.set_context(session_id, "product_detail", detail)
                    self._save_product_detail_to_file(detail, session_id)
                if detail_images:
                    self._session.set_context(session_id, "detail_images", detail_images)
                cart_items = result.get("cart_items")
                cart_summary = result.get("cart_summary") or {}
                if cart_items is not None:
                    self._session.set_context(session_id, "cart_items", cart_items)
                    self._session.set_context(session_id, "cart_summary", cart_summary)
                    self._save_cart_to_file(cart_items, cart_summary, session_id)
            previous_url = session.current_url
            if page_url:
                if previous_url and previous_url != page_url:
                    self._session.set_context(session_id, "previous_url", previous_url)
                session.current_url = page_url
                if self._login_feedback and not suppress_outputs:
                    await self._login_feedback.maybe_announce_login_success(
                        session_id,
                        previous_url,
                        page_url
                    )
            if cart_items is not None:
                if not suppress_outputs:
                    tts_text = build_cart_summary_tts(cart_items, cart_summary or {})
                    await self._sender.send_tts_response(session_id, tts_text)
                return

            if products:
                self._session.set_context(session_id, "search_results", products)
                self._session.set_context(session_id, "search_active_results", products)
                self._session.set_context(session_id, "search_active_label", "all")
                try:
                    payload = json.dumps(products, ensure_ascii=True)
                    self._session.add_to_history(
                        session_id,
                        "system",
                        f"SEARCH_RESULTS:{payload}"
                    )
                except Exception:
                    logger.warning("Failed to serialize search_results for history")

                # Save search results to JSON file
                self._save_search_results_to_file(products, session_id)

                product_count = len(products)
                signature = self._build_search_signature(products)
                prev_signature = self._session.get_context(session_id, "search_results_signature")
                if signature != prev_signature:
                    self._session.set_context(session_id, "search_read_index", 0)
                    self._session.set_context(session_id, "search_results_signature", signature)

                start_index = self._session.get_context(session_id, "search_read_index", 0)
                tts_text = ""
                next_index = start_index
                has_more = False
                if not suppress_outputs:
                    tts_text, next_index, has_more = build_search_list_tts(
                        products,
                        start_index=start_index,
                        count=4,
                        include_total=True,
                        more_prompt=MORE_PROMPT_COUNT
                    )
                self._session.set_context(session_id, "search_read_index", next_index)
                if next_index > 0:
                    last_item = products[next_index - 1]
                    name = last_item.get("name") or last_item.get("title") or last_item.get("product_name")
                    if name:
                        self._session.set_context(session_id, "last_mentioned_product", name)
                if not suppress_outputs:
                    await self._sender.send_tts_response(session_id, tts_text)

        if not suppress_outputs and tool_name == "check_login_status" and self._login_guard:
            handled = await self._login_guard.handle_login_check_result(
                session_id,
                result if isinstance(result, dict) else {},
                page_url or (session.current_url if session else "")
            )
            if handled:
                return

        if not suppress_outputs and tool_name == "handle_captcha_modal":
            if isinstance(result, dict) and result.get("captcha_found"):
                await self._sender.send_tts_response(
                    session_id,
                    build_captcha_prompt_tts()
                )
                return

        if not suppress_outputs and SUMMARIZER_AVAILABLE and html_content:
            try:
                site = detect_site(page_url or "")
                product_info = parse_product_html(html_content, site=site, url=page_url or "")

                if product_info.is_valid():
                    html_summary = build_product_summary_tts(product_info)
                    logger.info(f"HTML 파싱 완료: {product_info.product_name}")

                    if html_summary:
                        await self._sender.send_tts_response(session_id, html_summary)

                    if product_info.detail_images:
                        detail_images = product_info.detail_images

            except Exception as e:
                logger.error(f"HTML 파싱 실패: {e}")

        if not suppress_outputs and SUMMARIZER_AVAILABLE and detail_images:
            asyncio.create_task(
                self._process_ocr_batch(session_id, detail_images, page_url)
            )

    def _build_search_signature(self, products: List[Dict[str, Any]]) -> str:
        names = []
        for item in products:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or item.get("title") or item.get("product_name")
            if name:
                names.append(name)
        return f"{len(products)}|" + "|".join(names[:10])

    async def _process_ocr_batch(
        self,
        session_id: str,
        image_urls: List[str],
        page_url: Optional[str] = None
    ):
        """
        모든 이미지를 한번에 OCR 처리 후 LLM 요약
        """
        try:
            ocr_integrator = get_ocr_integrator()
            site = detect_site(page_url or "")

            logger.info(f"OCR 배치 처리 시작: {len(image_urls)}개 이미지")

            await self._sender.send_ocr_progress(session_id, "started", 0, len(image_urls))

            ocr_result = await ocr_integrator.process_single_batch(image_urls, site=site)

            await self._sender.send_ocr_progress(session_id, "ocr_completed", 50, len(image_urls))

            if ocr_result.error:
                logger.error(f"OCR 처리 오류: {ocr_result.error}")
                await self._sender.send_ocr_progress(
                    session_id,
                    "error",
                    0,
                    len(image_urls),
                    error=ocr_result.error
                )
                return

            if ocr_result.summary:
                tts_text = build_ocr_summary_tts(ocr_result)
                if tts_text:
                    await self._sender.send_tts_response(session_id, tts_text)

            session = self._session.get_session(session_id) if self._session else None
            if session and self._session:
                self._session.set_context(session_id, "ocr_result", ocr_result.to_dict())

            await self._sender.send_ocr_progress(session_id, "completed", 100, len(image_urls))
            logger.info(f"OCR 배치 처리 완료: {session_id}")

        except Exception as e:
            logger.error(f"OCR 배치 처리 실패: {e}")
            await self._sender.send_ocr_progress(
                session_id,
                "error",
                0,
                len(image_urls),
                error=str(e)
            )

    def _save_search_results_to_file(self, products: List[Dict[str, Any]], session_id: str):
        self._file_manager.save_json(
            data=products,
            session_id=session_id,
            category="search_results",
            filename_prefix="search_results"
        )

    def _save_product_detail_to_file(self, detail: Dict[str, Any], session_id: str):
        self._file_manager.save_json(
            data=detail,
            session_id=session_id,
            category="product_detail",
            filename_prefix="product_detail"
        )

    def _save_cart_to_file(self, items: List[Dict[str, Any]], summary: Dict[str, Any], session_id: str):
        payload = {
            "items": items,
            "summary": summary,
        }
        self._file_manager.save_json(
            data=payload,
            session_id=session_id,
            category="cart",
            filename_prefix="cart"
        )

    def cleanup_session(self, session_id: str):
        self._file_manager.cleanup_session(session_id)


def _extract_request_ts(request_id: Optional[str]) -> Optional[float]:
    if not request_id:
        return None
    parts = request_id.split("_")
    if len(parts) < 3:
        return None
    try:
        return float(parts[-2])
    except ValueError:
        return None
