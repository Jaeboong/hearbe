#!/usr/bin/env python3
"""
MCP 테스트용 API 서버

test_command_cli.py에서 생성된 명령을 받아 Playwright로 실행합니다.

사용법:
    1. Chrome을 CDP 모드로 실행:
       chrome.exe --remote-debugging-port=9222
    
    2. 이 서버 실행:
       cd c:\\ssafy\\공통\\AI
       python services/llm/tests/mcp_api_server.py
    
    3. test_command_cli.py 실행:
       python services/llm/tests/test_command_cli.py --exec
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Playwright
try:
    from playwright.async_api import async_playwright, Browser, Page, Playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("⚠️ playwright 모듈이 없습니다. pip install playwright && playwright install chromium")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# Pydantic 모델
# =============================================================================

class CommandItem(BaseModel):
    action: str
    args: Dict[str, Any] = {}
    desc: str = ""


class ExecuteRequest(BaseModel):
    type: str = "tool_calls"
    data: Dict[str, Any] = {}


class ExecuteResponse(BaseModel):
    success: bool
    results: List[Dict[str, Any]] = []
    error: Optional[str] = None


# =============================================================================
# 브라우저 관리
# =============================================================================

class BrowserManager:
    """Playwright 브라우저 관리 - 항상 최신 활성 페이지 자동 추적"""

    def __init__(self):
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._cdp_url = "http://127.0.0.1:9222"

    @property
    def is_connected(self) -> bool:
        return self._browser is not None and self._browser.is_connected()

    @property
    def _page(self) -> Optional[Page]:
        """항상 가장 최근(마지막) 페이지 반환 - 새 탭/창 열리면 자동 전환"""
        if not self._browser:
            return None
        all_pages = []
        for ctx in self._browser.contexts:
            all_pages.extend(ctx.pages)
        return all_pages[-1] if all_pages else None

    @property
    def current_url(self) -> Optional[str]:
        page = self._page
        return page.url if page else None

    def get_all_pages(self) -> List[Dict[str, Any]]:
        """모든 열린 페이지 목록 반환"""
        pages = []
        if not self._browser:
            return pages
        current = self._page
        for ctx in self._browser.contexts:
            for page in ctx.pages:
                pages.append({
                    "index": len(pages),
                    "url": page.url,
                    "title": page.url.split("/")[2] if "/" in page.url else page.url,
                    "is_current": page == current
                })
        return pages

    async def connect(self) -> bool:
        """CDP로 Chrome에 연결"""
        if not HAS_PLAYWRIGHT:
            return False

        if self.is_connected:
            return True

        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.connect_over_cdp(self._cdp_url)

            # 페이지가 없으면 새로 생성
            if not self._page:
                context = await self._browser.new_context()
                await context.new_page()

            logger.info(f"브라우저 연결 성공: {self.current_url}")
            return True
        except Exception as e:
            logger.error(f"브라우저 연결 실패: {e}")
            return False

    async def disconnect(self):
        """연결 해제"""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        logger.info("브라우저 연결 해제")

    async def execute_command(self, cmd: CommandItem) -> Dict[str, Any]:
        """단일 명령 실행 - 항상 현재 활성 페이지에서 실행"""
        page = self._page
        if not page:
            return {"success": False, "error": "페이지 없음", "desc": cmd.desc}

        action = cmd.action
        args = cmd.args

        try:
            result = None

            if action == "goto":
                url = args.get("url", "")
                await page.goto(url, wait_until="domcontentloaded")
                result = f"이동: {url}"

            elif action == "click":
                selector = args.get("selector", "")
                await page.click(selector, timeout=5000)
                result = f"클릭: {selector}"

            elif action == "fill":
                selector = args.get("selector", "")
                text = args.get("text", "")
                await page.fill(selector, text)
                result = f"입력: {text}"

            elif action == "press":
                selector = args.get("selector", "")
                key = args.get("key", "Enter")
                await page.press(selector, key)
                result = f"키 입력: {key}"

            elif action == "wait":
                ms = args.get("ms", 1000)
                await asyncio.sleep(ms / 1000)
                result = f"대기: {ms}ms"

            elif action == "scroll":
                direction = args.get("direction", "down")
                amount = args.get("amount", 500)
                if direction == "down":
                    await page.evaluate(f"window.scrollBy(0, {amount})")
                else:
                    await page.evaluate(f"window.scrollBy(0, -{amount})")
                result = f"스크롤: {direction}"

            elif action == "screenshot":
                path = args.get("path", "screenshot.png")
                await page.screenshot(path=path)
                result = f"스크린샷: {path}"

            elif action == "click_text":
                text = args.get("text", "")
                import sys
                sys.path.insert(0, r"c:\ssafy\공통\MCP")
                from browser.action_utils import click_text as click_text_util

                click_result = await click_text_util(page, text)
                if click_result["success"]:
                    result = click_result["result"]
                else:
                    return {"success": False, "error": click_result["error"], "desc": cmd.desc}
            
            else:
                return {"success": False, "error": f"알 수 없는 액션: {action}", "desc": cmd.desc}
            
            return {"success": True, "result": result, "desc": cmd.desc}
        
        except Exception as e:
            return {"success": False, "error": str(e), "desc": cmd.desc}


# =============================================================================
# FastAPI 앱
# =============================================================================

browser = BrowserManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MCP Test API Server 시작")
    yield
    await browser.disconnect()
    logger.info("MCP Test API Server 종료")


app = FastAPI(
    title="MCP Test API Server",
    description="test_command_cli.py 테스트용 API 서버",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "name": "MCP Test API Server",
        "status": "running",
        "browser_connected": browser.is_connected
    }


@app.post("/start")
async def start_browser():
    """브라우저 연결"""
    success = await browser.connect()
    return {"success": success}


@app.get("/status")
async def get_status():
    """상태 확인"""
    return {
        "browser_connected": browser.is_connected,
        "page_ready": browser._page is not None,
        "current_url": browser.current_url
    }


@app.get("/url")
async def get_url():
    """현재 URL"""
    return {"url": browser.current_url}


@app.get("/pages")
async def get_pages():
    """열린 모든 페이지 목록 (현재 활성 페이지 표시)"""
    pages = browser.get_all_pages()
    return {"success": True, "pages": pages, "count": len(pages)}


@app.get("/buttons")
async def get_buttons():
    """현재 활성 페이지의 클릭 가능한 요소들 조회"""
    page = browser._page
    if not browser.is_connected or not page:
        return {"success": False, "error": "브라우저 연결 안됨", "buttons": []}

    try:
        # 클릭 가능한 요소들 수집
        elements = await page.evaluate("""
            () => {
                const results = [];

                // 버튼 요소
                document.querySelectorAll('button').forEach((el, i) => {
                    if (el.offsetParent !== null) {  // visible check
                        results.push({
                            type: 'button',
                            text: el.innerText.trim().substring(0, 50),
                            selector: el.id ? `#${el.id}` : (el.className ? `button.${el.className.split(' ')[0]}` : `button:nth-of-type(${i+1})`),
                            visible: true
                        });
                    }
                });

                // input[type=submit], input[type=button]
                document.querySelectorAll('input[type="submit"], input[type="button"]').forEach((el, i) => {
                    if (el.offsetParent !== null) {
                        results.push({
                            type: 'input-button',
                            text: el.value || el.placeholder || '',
                            selector: el.id ? `#${el.id}` : `input[type="${el.type}"]:nth-of-type(${i+1})`,
                            visible: true
                        });
                    }
                });

                // 주요 링크 (role="button" 또는 특정 클래스)
                document.querySelectorAll('a[role="button"], a.btn, a.button, [role="button"]').forEach((el, i) => {
                    if (el.offsetParent !== null && el.innerText.trim()) {
                        results.push({
                            type: 'link-button',
                            text: el.innerText.trim().substring(0, 50),
                            selector: el.id ? `#${el.id}` : null,
                            visible: true
                        });
                    }
                });

                // 구매/장바구니 관련 요소 (쇼핑몰 특화)
                const shoppingSelectors = [
                    '.prod-buy-btn', '.add-cart', '.buy-btn', '.cart-btn',
                    '[class*="purchase"]', '[class*="buy"]', '[class*="cart"]',
                    '[class*="order"]', '[class*="checkout"]'
                ];
                shoppingSelectors.forEach(sel => {
                    document.querySelectorAll(sel).forEach(el => {
                        if (el.offsetParent !== null && el.innerText.trim()) {
                            const exists = results.some(r => r.text === el.innerText.trim().substring(0, 50));
                            if (!exists) {
                                results.push({
                                    type: 'shopping-action',
                                    text: el.innerText.trim().substring(0, 50),
                                    selector: sel,
                                    visible: true
                                });
                            }
                        }
                    });
                });

                return results.slice(0, 30);  // 최대 30개
            }
        """)

        return {"success": True, "buttons": elements, "count": len(elements)}

    except Exception as e:
        logger.error(f"buttons 조회 실패: {type(e).__name__}: {e}")
        return {"success": False, "error": f"{type(e).__name__}: {e}", "buttons": []}


@app.post("/execute", response_model=ExecuteResponse)
async def execute_commands(request: ExecuteRequest):
    """명령 실행"""
    if not browser.is_connected:
        return ExecuteResponse(success=False, error="브라우저 연결 안됨")
    
    commands_data = request.data.get("commands", [])
    if not commands_data:
        return ExecuteResponse(success=False, error="명령 없음")
    
    results = []
    all_success = True
    
    for cmd_data in commands_data:
        cmd = CommandItem(**cmd_data)
        result = await browser.execute_command(cmd)
        results.append(result)
        if not result.get("success"):
            all_success = False
    
    return ExecuteResponse(success=all_success, results=results)


@app.post("/stop")
async def stop_browser():
    """브라우저 연결 해제"""
    await browser.disconnect()
    return {"success": True}


# =============================================================================
# 메인
# =============================================================================

def main():
    print("=" * 60)
    print("MCP Test API Server")
    print("=" * 60)
    print("Chrome CDP 모드로 실행 후 이 서버를 시작하세요:")
    print("  chrome.exe --remote-debugging-port=9222")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()
