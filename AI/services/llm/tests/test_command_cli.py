"""
LLM 명령 생성 및 MCP API 실행 CLI

자연어 입력을 MCP 명령어로 변환하고 API 서버에 전송하여 실행합니다.

사용법:
    cd c:\\ssafy\\공통\\AI
    python services/llm/tests/test_command_cli.py

API 서버 (localhost:8000)가 실행 중이어야 합니다.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

# 프로젝트 루트를 path에 추가 (AI 디렉토리)
# 현재 위치: AI/services/llm/tests/test_command_cli.py
# AI 디렉토리로 가려면 3단계 위로 (tests -> llm -> services -> AI)
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from services.llm.command_generator import CommandGenerator, CommandResult
from services.llm.context_rules import GeneratedCommand
from services.llm.site_manager import get_site_manager, get_current_site

# LLM Generator (선택적)
try:
    from services.llm.llm_generator import LLMGenerator
    HAS_LLM = True
except ImportError:
    HAS_LLM = False


@dataclass
class TestSession:
    """테스트용 세션 (서버의 SessionState와 동일한 구조)"""
    session_id: str = "test-cli-session"
    current_url: str = "https://www.coupang.com/"
    conversation_history: List[Dict[str, str]] = field(default_factory=list)

    def add_message(self, role: str, content: str):
        """대화 기록 추가"""
        self.conversation_history.append({"role": role, "content": content})
        # 최근 10개만 유지
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]

# MCP API 서버 주소
MCP_API_URL = "http://localhost:8000"


def convert_to_api_format(commands: List[GeneratedCommand]) -> Dict[str, Any]:
    """명령을 MCP API 형식으로 변환 (FASTAPI_TO_APP.md 기준)"""
    return {
        "type": "tool_calls",
        "data": {
            "commands": [
                {
                    "action": cmd.tool_name,
                    "args": cmd.arguments,
                    "desc": cmd.description or ""
                }
                for cmd in commands
            ]
        }
    }


def execute_on_mcp(commands: List[GeneratedCommand]) -> Optional[Dict[str, Any]]:
    """MCP API 서버에 명령 실행 요청"""
    if not HAS_REQUESTS:
        print("[ERROR] requests 모듈이 없습니다. pip install requests")
        return None

    payload = convert_to_api_format(commands)

    try:
        response = requests.post(
            f"{MCP_API_URL}/execute",
            json=payload,
            timeout=30
        )
        return response.json()
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] MCP API 서버에 연결할 수 없습니다 ({MCP_API_URL})")
        print("        Chrome CDP 모드와 API 서버를 먼저 실행하세요.")
        return None
    except Exception as e:
        print(f"[ERROR] API 요청 실패: {e}")
        return None


def print_result(result: CommandResult, verbose: bool = True, json_mode: bool = False) -> None:
    """결과 출력"""
    if json_mode:
        print_json_result(result)
        return

    print("\n" + "=" * 60)
    print(f"[RULE] {result.matched_rule}")
    print(f"[RESP] {result.response_text}")

    if result.requires_flow:
        print(f"[FLOW] {result.flow_type}")

    print("-" * 60)
    print(f"[CMD] 생성된 명령 ({len(result.commands)}개):")

    if not result.commands:
        print("       (명령 없음)")
    else:
        for i, cmd in enumerate(result.commands, 1):
            print(f"\n       [{i}] {cmd.tool_name}")
            if verbose:
                args_str = json.dumps(cmd.arguments, ensure_ascii=False, indent=12)
                print(f"           args: {args_str}")
            if cmd.description:
                print(f"           desc: {cmd.description}")

    print("=" * 60)


def print_json_result(result: CommandResult) -> None:
    """MCP API 형식 JSON 출력"""
    payload = convert_to_api_format(result.commands)
    print("\n[JSON] MCP API 요청:")
    print("-" * 40)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("-" * 40)


def print_api_result(api_result: Dict[str, Any]) -> None:
    """API 실행 결과 출력"""
    print("\n" + "=" * 60)
    print("[EXEC] MCP 실행 결과:")
    print("-" * 60)

    # 전체 에러 체크
    if api_result.get("error"):
        print(f"       [FAIL] 전체 에러: {api_result.get('error')}")

    # 개별 결과 출력
    results = api_result.get("results", [])
    if results:
        for r in results:
            desc = r.get('desc', '명령')
            if r.get("success"):
                print(f"       [OK] {desc}: {r.get('result', 'OK')}")
            else:
                error_msg = r.get('error', 'unknown error')
                print(f"       [FAIL] {desc}: {error_msg}")
    elif not api_result.get("success") and not api_result.get("error"):
        print("       [FAIL] 알 수 없는 오류 발생")

    print("=" * 60)


def interactive_mode(initial_url: str, auto_execute: bool = False, use_llm: bool = False) -> None:
    """대화형 모드"""
    generator = CommandGenerator()
    llm_generator = None

    # LLM fallback 초기화
    if use_llm and HAS_LLM:
        import os
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            llm_generator = LLMGenerator(api_key=api_key)
            print("[INFO] LLM fallback 활성화됨")
        else:
            print("[WARN] OPENAI_API_KEY 없음, LLM fallback 비활성화")

    # 세션 생성
    session = TestSession(current_url=initial_url)
    json_mode = False
    execute_mode = auto_execute
    llm_mode = use_llm and llm_generator is not None

    print("\n" + "=" * 60)
    print("LLM 명령 생성 CLI + MCP API 실행")
    print("=" * 60)

    # MCP 브라우저 자동 연결
    if HAS_REQUESTS:
        print("[INFO] MCP 브라우저 연결 중...")
        try:
            resp = requests.post(f"{MCP_API_URL}/start", timeout=10)
            if resp.ok and resp.json().get("success"):
                print("[OK] 브라우저 연결 성공")
                # 현재 URL 가져오기
                url_resp = requests.get(f"{MCP_API_URL}/url", timeout=5)
                if url_resp.ok:
                    fetched_url = url_resp.json().get("url", "")
                    if fetched_url:
                        session.current_url = fetched_url
            else:
                print("[WARN] 브라우저 연결 실패 - Chrome CDP 모드로 실행되어 있는지 확인하세요")
        except requests.exceptions.ConnectionError:
            print(f"[WARN] MCP 서버 연결 불가 ({MCP_API_URL})")
            print("       api_server.py가 실행 중인지 확인하세요")
        except Exception as e:
            print(f"[WARN] 연결 오류: {e}")

    print("-" * 60)
    print("명령어:")
    print("  - 자연어 입력 -> 명령 생성 (및 실행)")
    print("  - /url <URL>  -> 현재 URL 변경")
    print("  - /exec       -> API 실행 모드 토글")
    print("  - /llm        -> LLM fallback 토글")
    print("  - /history    -> 대화 기록 보기")
    print("  - /clear      -> 대화 기록 초기화")
    print("  - /json       -> JSON 출력 모드 토글")
    print("  - /status     -> MCP 서버 상태 확인")
    print("  - /sites      -> 등록된 사이트 목록")
    print("  - /buttons    -> 현재 페이지 클릭 가능 요소 조회")
    print("  - /pages      -> 열린 페이지 목록")
    print("  - /q          -> 종료")
    print("=" * 60)

    site = get_current_site(session.current_url)
    site_name = site.name if site else "알 수 없음"
    print(f"[SITE] {site_name}")
    print(f"[URL] {session.current_url}")
    print(f"[EXEC] API 실행 모드: {'ON' if execute_mode else 'OFF'}")
    print(f"[LLM] LLM fallback: {'ON' if llm_mode else 'OFF'}")
    print(f"[HIST] 대화 기록: {len(session.conversation_history)}개")

    while True:
        try:
            user_input = input("\n명령> ").strip()

            if not user_input:
                continue

            # 특수 명령어
            if user_input.startswith("/"):
                cmd_parts = user_input.split(maxsplit=1)
                cmd = cmd_parts[0].lower()

                if cmd in ["/quit", "/q"]:
                    print("종료합니다.")
                    break

                elif cmd == "/url":
                    if len(cmd_parts) > 1:
                        session.current_url = cmd_parts[1]
                        site = get_current_site(session.current_url)
                        site_name = site.name if site else "알 수 없음"
                        print(f"[OK] URL 변경: {session.current_url}")
                        print(f"[SITE] {site_name}")
                    else:
                        print(f"[URL] {session.current_url}")

                elif cmd == "/exec":
                    execute_mode = not execute_mode
                    status = "ON (명령 생성 후 바로 실행)" if execute_mode else "OFF (명령 생성만)"
                    print(f"[OK] API 실행 모드: {status}")

                elif cmd == "/json":
                    json_mode = not json_mode
                    print(f"[OK] JSON 출력 모드: {'ON' if json_mode else 'OFF'}")

                elif cmd == "/llm":
                    if HAS_LLM:
                        if llm_generator is None:
                            import os
                            api_key = os.environ.get("OPENAI_API_KEY")
                            if api_key:
                                llm_generator = LLMGenerator(api_key=api_key)
                                llm_mode = True
                                print("[OK] LLM fallback: ON")
                            else:
                                print("[ERROR] OPENAI_API_KEY가 설정되지 않았습니다")
                        else:
                            llm_mode = not llm_mode
                            print(f"[OK] LLM fallback: {'ON' if llm_mode else 'OFF'}")
                    else:
                        print("[ERROR] LLM 모듈을 사용할 수 없습니다 (openai 설치 필요)")

                elif cmd == "/history":
                    print("[HIST] 대화 기록:")
                    if not session.conversation_history:
                        print("       (기록 없음)")
                    else:
                        for i, msg in enumerate(session.conversation_history, 1):
                            role = "USER" if msg["role"] == "user" else "ASST"
                            content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
                            print(f"       {i}. [{role}] {content}")

                elif cmd == "/clear":
                    session.conversation_history = []
                    if llm_generator:
                        llm_generator.clear_history()
                    print("[OK] 대화 기록 초기화됨")

                elif cmd == "/status":
                    if HAS_REQUESTS:
                        try:
                            resp = requests.get(f"{MCP_API_URL}/status", timeout=5)
                            status = resp.json()
                            print("[STATUS] MCP 서버 상태:")
                            print(f"         브라우저 연결: {'OK' if status.get('browser_connected') else 'NO'}")
                            print(f"         페이지 준비: {'OK' if status.get('page_ready') else 'NO'}")
                            print(f"         현재 URL: {status.get('current_url', 'N/A')}")
                        except:
                            print(f"[ERROR] MCP 서버 연결 불가 ({MCP_API_URL})")
                    else:
                        print("[ERROR] requests 모듈 필요 (pip install requests)")

                elif cmd == "/sites":
                    manager = get_site_manager()
                    print("[SITES] 등록된 사이트:")
                    for site_id in manager.list_sites():
                        site = manager.get_site(site_id)
                        print(f"        - {site.name} ({site_id})")

                elif cmd == "/buttons":
                    if HAS_REQUESTS:
                        try:
                            resp = requests.get(f"{MCP_API_URL}/buttons", timeout=10)
                            data = resp.json()
                            if data.get("success"):
                                buttons = data.get("buttons", [])
                                print(f"[BUTTONS] 클릭 가능 요소 ({len(buttons)}개):")
                                print("-" * 50)
                                for i, btn in enumerate(buttons, 1):
                                    btn_type = btn.get("type", "unknown")
                                    text = btn.get("text", "(텍스트 없음)")[:40]
                                    selector = btn.get("selector", "")
                                    print(f"  [{i:2}] [{btn_type:15}] {text}")
                                    if selector:
                                        print(f"        selector: {selector}")
                                print("-" * 50)
                            else:
                                print(f"[ERROR] 버튼 조회 실패: {data.get('error')}")
                        except requests.exceptions.ConnectionError:
                            print(f"[ERROR] MCP 서버 연결 불가 ({MCP_API_URL})")
                        except Exception as e:
                            print(f"[ERROR] 오류: {e}")
                    else:
                        print("[ERROR] requests 모듈 필요 (pip install requests)")

                elif cmd == "/pages":
                    if HAS_REQUESTS:
                        try:
                            resp = requests.get(f"{MCP_API_URL}/pages", timeout=5)
                            data = resp.json()
                            pages = data.get("pages", [])
                            print(f"[PAGES] 열린 페이지 ({len(pages)}개):")
                            print("-" * 50)
                            for p in pages:
                                marker = " *" if p.get("is_current") else "  "
                                print(f"  [{p['index']}]{marker} {p['url'][:60]}")
                            print("-" * 50)
                            print("  (* = 현재 활성 페이지, 자동 추적됨)")
                        except requests.exceptions.ConnectionError:
                            print(f"[ERROR] MCP 서버 연결 불가 ({MCP_API_URL})")
                        except Exception as e:
                            print(f"[ERROR] 오류: {e}")
                    else:
                        print("[ERROR] requests 모듈 필요")

                else:
                    print(f"[ERROR] 알 수 없는 명령: {cmd}")

            else:
                # 자연어 -> 명령 생성
                print(f"\n[INPUT] \"{user_input}\"")

                # 대화 기록에 추가
                session.add_message("user", user_input)

                # 규칙 기반 먼저 시도
                result = generator.generate(user_input, session.current_url)

                # 규칙 매칭 실패 시 LLM fallback
                if result.matched_rule == "none" and llm_mode and llm_generator:
                    print("        규칙 매칭 실패, LLM fallback...")
                    import asyncio
                    llm_result = asyncio.run(llm_generator.generate(
                        user_text=user_input,
                        current_url=session.current_url,
                        conversation_history=session.conversation_history
                    ))
                    if llm_result.success and llm_result.commands:
                        # LLM 결과를 CommandResult로 변환
                        result = CommandResult(
                            commands=llm_result.commands,
                            response_text=llm_result.response_text,
                            matched_rule="llm_fallback"
                        )

                print_result(result, json_mode=json_mode)

                # 응답을 대화 기록에 추가
                session.add_message("assistant", result.response_text)

                # API 실행 모드면 바로 실행
                if execute_mode and result.commands:
                    print("\n[EXEC] MCP API로 실행 중...")
                    api_result = execute_on_mcp(result.commands)
                    if api_result:
                        print_api_result(api_result)
                        # 실행 후 현재 URL 업데이트
                        try:
                            url_resp = requests.get(f"{MCP_API_URL}/url", timeout=5)
                            if url_resp.ok:
                                session.current_url = url_resp.json().get("url", session.current_url)
                        except:
                            pass

        except KeyboardInterrupt:
            print("\n종료합니다.")
            break
        except Exception as e:
            print(f"[ERROR] 오류: {e}")
            import traceback
            traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(description="LLM 명령 생성 + MCP API 실행 CLI")
    parser.add_argument(
        "--url",
        default="https://www.coupang.com/",
        help="초기 URL (기본: 쿠팡)"
    )
    parser.add_argument(
        "--exec", "-e",
        action="store_true",
        help="API 실행 모드로 시작"
    )
    parser.add_argument(
        "--llm",
        action="store_true",
        help="LLM fallback 활성화"
    )
    parser.add_argument(
        "--input", "-i",
        help="단일 명령어 테스트"
    )

    args = parser.parse_args()

    if args.input:
        generator = CommandGenerator()
        result = generator.generate(args.input, args.url)
        print(f"[INPUT] \"{args.input}\"")
        print_result(result)

        if getattr(args, 'exec', False) and result.commands:
            print("\n[EXEC] MCP API로 실행 중...")
            api_result = execute_on_mcp(result.commands)
            if api_result:
                print_api_result(api_result)
    else:
        interactive_mode(
            args.url,
            auto_execute=getattr(args, 'exec', False),
            use_llm=getattr(args, 'llm', False)
        )


if __name__ == "__main__":
    main()
