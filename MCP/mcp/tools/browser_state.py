"""
Browser state helpers (login status, etc.).
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class BrowserStateMixin:
    """State inspection helpers."""

    async def check_login_status(self) -> Dict[str, Any]:
        """
        Check login status by detecting login/signup or logout UI.

        Returns:
            {"success": bool, "logged_in": bool|None, "login_link": bool, "signup_link": bool, "logout_link": bool}
        """
        page = await self._get_active_page()
        if not page:
            return {"success": False, "error": "Not connected to browser"}

        script = """
          () => {
            const isVisible = (el) => {
              if (!el) return false;
              const rect = el.getBoundingClientRect();
              if (!rect || rect.width === 0 || rect.height === 0) return false;
              const style = window.getComputedStyle(el);
              if (!style) return false;
              if (style.display === "none" || style.visibility === "hidden" || style.opacity === "0") return false;
              return true;
            };

            const loginLink = document.querySelector(
              'a[title="로그인"], a[href*="login.coupang.com"], a[href*="login.pang"], a[href*="/login"]'
            );
            const signupLink = document.querySelector(
              'a[title="회원가입"], a[href*="memberJoin"], a[href*="/signup"], a[href*="/join"]'
            );

            let logoutLink = null;
            const candidates = Array.from(document.querySelectorAll("a, button"));
            for (const el of candidates) {
              const text = (el.innerText || el.textContent || "").trim();
              if (!text) continue;
              if (text.includes("로그아웃") || /logout/i.test(text)) {
                logoutLink = el;
                break;
              }
            }

            const loginVisible = isVisible(loginLink);
            const signupVisible = isVisible(signupLink);
            const logoutVisible = isVisible(logoutLink);

            let loggedIn = null;
            if (logoutVisible) {
              loggedIn = true;
            } else if (loginVisible || signupVisible) {
              loggedIn = false;
            }

            return {
              logged_in: loggedIn,
              login_link: loginVisible,
              signup_link: signupVisible,
              logout_link: logoutVisible
            };
          }
        """

        try:
            result = await page.evaluate(script)
            if isinstance(result, dict):
                return {"success": True, **result}
            return {"success": True, "logged_in": None}
        except Exception as e:
            logger.error(f"Login status check failed: {e}")
            return {"success": False, "error": str(e)}
