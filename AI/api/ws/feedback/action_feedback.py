# -*- coding: utf-8 -*-
"""
Action feedback manager

Tracks actions that require confirmation and adjusts TTS to avoid
overstating success when the real outcome is unknown.
"""

import logging
from dataclasses import dataclass
from typing import Dict, Optional, List, Any

from services.llm.sites.site_manager import get_selector
from services.llm.sites.site_manager import get_site_manager
from core.interfaces import MCPCommand
from ..utils.temp_file_manager import TempFileManager

logger = logging.getLogger(__name__)


@dataclass
class PendingAction:
    """Pending action requiring confirmation."""
    action_type: str
    selector: Optional[str]
    tool_name: str
    current_url: Optional[str] = None


class ActionFeedbackManager:
    """Tracks pending actions and emits safer feedback."""

    def __init__(self, sender):
        self._sender = sender
        self._pending: Dict[str, PendingAction] = {}
        self._file_manager = TempFileManager()

    def register_commands(self, session_id: str, commands: List, current_url: str) -> Optional[str]:
        """
        Inspect commands and register pending actions that need confirmation.

        Returns:
            Optional processing message to speak immediately.
        """
        if not commands:
            return None

        selector = get_selector(current_url, "add_to_cart") if current_url else None

        for cmd in commands:
            tool = cmd.tool_name
            args = cmd.arguments or {}

            if tool in ("click", "click_element"):
                if selector and args.get("selector") == selector:
                    self._pending[session_id] = PendingAction(
                        action_type="add_to_cart",
                        selector=selector,
                        tool_name=tool,
                        current_url=current_url
                    )
                    return "장바구니 담기를 시도합니다. 결과를 확인 중입니다."

            if tool == "click_text":
                text = (args.get("text") or "").strip()
                if text in ("장바구니 담기", "장바구니"):
                    self._pending[session_id] = PendingAction(
                        action_type="add_to_cart",
                        selector=None,
                        tool_name=tool,
                        current_url=current_url
                    )
                    return "장바구니 담기를 시도합니다. 결과를 확인 중입니다."

        return None

    async def handle_mcp_result(
        self,
        session_id: str,
        tool_name: Optional[str],
        arguments: Optional[dict],
        success: bool,
        result: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Handle MCP tool result to emit confirmation-safe feedback."""
        pending = self._pending.get(session_id)
        if not pending:
            return False

        # Verification phase: check cart contents after navigation/extract
        if pending.action_type == "add_to_cart_verify":
            if tool_name == "extract_cart":
                products = (result or {}).get("cart_items") or []
                self._file_manager.save_json(
                    data={
                        "success": success,
                        "products": products,
                        "page_url": (result or {}).get("page_url"),
                    },
                    session_id=session_id,
                    category="cart_verify",
                    filename_prefix="cart_verify"
                )
                if success and products:
                    await self._sender.send_tts_response(
                        session_id,
                        "장바구니에서 상품이 확인되었습니다."
                    )
                else:
                    await self._sender.send_tts_response(
                        session_id,
                        "장바구니에서 상품을 확인하지 못했습니다."
                    )
                self._pending.pop(session_id, None)
                return True
            return False

        if tool_name not in ("click", "click_element", "click_text"):
            return False

        if pending.selector:
            if not arguments or arguments.get("selector") != pending.selector:
                return False

        if not success:
            await self._sender.send_tts_response(
                session_id,
                "장바구니 담기 버튼 클릭에 실패했습니다. 다시 시도해주세요."
            )
            self._pending.pop(session_id, None)
            return True

        verify_commands = self._build_verify_add_to_cart_commands(pending.current_url or "")
        if verify_commands:
            await self._sender.send_tts_response(
                session_id,
                "장바구니 반영 여부를 확인하기 위해 장바구니로 이동합니다."
            )
            await self._sender.send_tool_calls(session_id, verify_commands)
            self._pending[session_id] = PendingAction(
                action_type="add_to_cart_verify",
                selector=None,
                tool_name="extract_cart",
                current_url=pending.current_url
            )
            return True
        else:
            await self._sender.send_tts_response(
                session_id,
                "버튼 클릭은 완료되었습니다. 장바구니 반영은 수동 확인이 필요합니다."
            )
            self._pending.pop(session_id, None)
            return True

    
    
    def _build_verify_add_to_cart_commands(self, current_url: str) -> List[MCPCommand]:
        site = get_site_manager().get_site_by_url(current_url)
        if not site:
            return []

        cart_url = site.get_url("cart")
        if not cart_url:
            return []

        commands = [
            MCPCommand(
                tool_name="goto",
                arguments={"url": cart_url},
                description="Go to cart page"
            ),
            MCPCommand(
                tool_name="wait",
                arguments={"ms": 1500},
                description="Wait for cart page load"
            ),
            MCPCommand(
                tool_name="extract_cart",
                arguments={},
                description="Extract cart items"
            )
        ]
        return commands

    def clear_pending(self, session_id: str):
        """Clear pending actions for a session."""
        self._pending.pop(session_id, None)
