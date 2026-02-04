# -*- coding: utf-8 -*-
"""Checkout rule."""

from typing import Optional
from . import BaseRule, RuleResult
from ..context.context_rules import CHECKOUT_TRIGGERS, GeneratedCommand
from ..sites.site_manager import get_selector, get_page_type

# Avoid misrouting "order list" intents to checkout.
ORDER_LIST_PHRASES = (
    "\uc8fc\ubb38 \ubaa9\ub85d",
    "\uc8fc\ubb38\ubaa9\ub85d",
    "\uc8fc\ubb38 \ub0b4\uc5ed",
    "\uc8fc\ubb38\ub0b4\uc5ed",
    "\uc8fc\ubb38 \uc870\ud68c",
    "\uc8fc\ubb38\uc870\ud68c",
    "\uc8fc\ubb38 \ub9ac\uc2a4\ud2b8",
    "\uc8fc\ubb38\ub9ac\uc2a4\ud2b8",
)

ALLOWED_PAGE_TYPES = {"product", "cart", "checkout"}

MSG_BUY_NOW = "\ubc14\ub85c\uad6c\ub9e4"
MSG_CHECKOUT = "\uacb0\uc81c\ud558\uae30"
MSG_CART_CHECKOUT = "\uad6c\ub9e4\ud558\uae30"
MSG_PROCESSING_WAIT = "\ucc98\ub9ac \ub300\uae30"


class CheckoutRule(BaseRule):
    """Checkout rule: handles buy/checkout on product/cart/checkout pages only."""

    def check(self, text: str, current_url: str, current_site) -> Optional[RuleResult]:
        if any(phrase in text for phrase in ORDER_LIST_PHRASES):
            return None
        if not any(kw in text for kw in CHECKOUT_TRIGGERS):
            return None

        page_type = get_page_type(current_url) if current_url else None
        if page_type not in ALLOWED_PAGE_TYPES:
            return None

        selector = None
        button_name = MSG_CHECKOUT

        if page_type == "product":
            selector = get_selector(current_url, "buy_now")
            button_name = MSG_BUY_NOW
        elif page_type == "checkout":
            selector = get_selector(current_url, "pay_button")
            button_name = MSG_CHECKOUT
        elif page_type == "cart":
            selector = get_selector(current_url, "checkout_button")
            button_name = MSG_CART_CHECKOUT

        if not selector:
            selector = (
                "button:has-text('" + MSG_CHECKOUT + "'), "
                "button:has-text('" + MSG_BUY_NOW + "'), "
                "button:has-text('" + MSG_CART_CHECKOUT + "')"
            )

        commands = [
            GeneratedCommand(
                tool_name="click",
                arguments={"selector": selector},
                description=f"{button_name} \ubc84\ud2bc \ud074\ub9ad",
            ),
            GeneratedCommand(
                tool_name="wait",
                arguments={"ms": 2000},
                description=MSG_PROCESSING_WAIT,
            ),
        ]

        return RuleResult(
            matched=True,
            commands=commands,
            response_text=f"{button_name}\uc744(\ub97c) \uc9c4\ud589\ud569\ub2c8\ub2e4.",
            rule_name="checkout",
        )
