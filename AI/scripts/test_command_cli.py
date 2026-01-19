#!/usr/bin/env python3
"""
LLM 명령 생성 및 MCP API 실행 CLI

자연어 입력을 MCP 명령어로 변환하고 API 서버에 전송하여 실행합니다.

사용법:
    cd c:\\ssafy\\공통\\AI
    python scripts/test_command_cli.py
    
API 서버 (localhost:8000)가 실행 중이어야 합니다.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# 프로젝트 루트를 path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from services.llm.command_generator import CommandGenerator, CommandResult, GeneratedCommand
from services.llm.site_manager import get_site_manager, get_current_site

# MCP API 서버 주소
MCP_API_URL = "http://localhost:8000"


def convert_to_api_format(commands: List[GeneratedCommand]) -> Dict[str, Any]:
    """명령을 MCP API 형식으로 변환"""
    return {
        "actions": [
            {
                "action": cmd.tool_name,
                "args": cmd.arguments,
                "desc": cmd.description or ""
            }
            for cmd in commands
        ]
    }


def execute_on_mcp(commands: List[GeneratedCommand]) -> Optional[Dict[str, Any]]:
    """MCP API 서버에 명령 실행 요청"""
    if not HAS_REQUESTS:
        print("❌ requests 모듈이 없습니다. pip install requests")
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
        print(f"❌ MCP API 서버에 연결할 수 없습니다 ({MCP_API_URL})")
        print("   Chrome CDP 모드와 API 서버를 먼저 실행하세요.")
        return None
    except Exception as e:
        print(f"❌ API 요청 실패: {e}")
        return None


def print_result(result: CommandResult, verbose: bool = True, json_mode: bool = False) -> None:
    """결과 출력"""
    if json_mode:
        print_json_result(result)
        return
    
    print("\n" + "=" * 60)
    print(f"📦 매칭된 규칙: {result.matched_rule}")
    print(f"💬 응답: {result.response_text}")
    
    if result.requires_flow:
        print(f"🔄 Flow 위임: {result.flow_type}")
    
    print("-" * 60)
    print(f"🛠️  생성된 명령 ({len(result.commands)}개):")
    
    if not result.commands:
        print("   (명령 없음)")
    else:
        for i, cmd in enumerate(result.commands, 1):
            print(f"\n   [{i}] {cmd.tool_name}")
            if verbose:
                args_str = json.dumps(cmd.arguments, ensure_ascii=False, indent=8)
                print(f"       args: {args_str}")
            if cmd.description:
                print(f"       desc: {cmd.description}")
    
    print("=" * 60)


def print_json_result(result: CommandResult) -> None:
    """MCP API 형식 JSON 출력"""
    payload = convert_to_api_format(result.commands)
    print("\n📋 MCP API 요청 JSON:")
    print("-" * 40)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("-" * 40)


def print_api_result(api_result: Dict[str, Any]) -> None:
    """API 실행 결과 출력"""
    print("\n" + "=" * 60)
    print("🚀 MCP 실행 결과:")
    print("-" * 60)
    
    if api_result.get("success"):
        for r in api_result.get("results", []):
            if r.get("success"):
                print(f"   ✅ {r.get('desc', '')}: {r.get('result', '')}")
            else:
                print(f"   ❌ {r.get('desc', '')}: {r.get('error', 'unknown error')}")
    else:
        print(f"   ❌ 에러: {api_result.get('error', 'unknown error')}")
    
    print("=" * 60)


def interactive_mode(initial_url: str, auto_execute: bool = False) -> None:
    """대화형 모드"""
    generator = CommandGenerator()
    current_url = initial_url
    json_mode = False
    execute_mode = auto_execute  # API 실행 모드
    
    print("\n" + "=" * 60)
    print("🤖 LLM 명령 생성 CLI + MCP API 실행")
    print("=" * 60)
    
    # MCP 브라우저 자동 연결
    if HAS_REQUESTS:
        print("🔌 MCP 브라우저 연결 중...")
        try:
            resp = requests.post(f"{MCP_API_URL}/start", timeout=10)
            if resp.ok and resp.json().get("success"):
                print("✅ 브라우저 연결 성공!")
                # 현재 URL 가져오기
                url_resp = requests.get(f"{MCP_API_URL}/url", timeout=5)
                if url_resp.ok:
                    current_url = url_resp.json().get("url", current_url) or current_url
            else:
                print("⚠️ 브라우저 연결 실패 - Chrome CDP 모드로 실행되어 있는지 확인하세요")
        except requests.exceptions.ConnectionError:
            print(f"⚠️ MCP 서버 연결 불가 ({MCP_API_URL})")
            print("   api_server.py가 실행 중인지 확인하세요")
        except Exception as e:
            print(f"⚠️ 연결 오류: {e}")
    
    print("-" * 60)
    print("명령어:")
    print("  - 자연어 입력 → 명령 생성 (및 실행)")
    print("  - /url <URL>  → 현재 URL 변경")
    print("  - /exec       → API 실행 모드 토글")
    print("  - /json       → JSON 출력 모드 토글")
    print("  - /status     → MCP 서버 상태 확인")
    print("  - /sites      → 등록된 사이트 목록")
    print("  - /q          → 종료")
    print("=" * 60)
    
    site = get_current_site(current_url)
    site_name = site.name if site else "알 수 없음"
    print(f"📍 현재 사이트: {site_name}")
    print(f"🌐 URL: {current_url}")
    exec_status = "ON" if execute_mode else "OFF"
    print(f"🚀 API 실행 모드: {exec_status}")
    
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
                    print("👋 종료합니다.")
                    break
                
                elif cmd == "/url":
                    if len(cmd_parts) > 1:
                        current_url = cmd_parts[1]
                        site = get_current_site(current_url)
                        site_name = site.name if site else "알 수 없음"
                        print(f"✅ URL 변경: {current_url}")
                        print(f"📍 사이트: {site_name}")
                    else:
                        print(f"현재 URL: {current_url}")
                
                elif cmd == "/exec":
                    execute_mode = not execute_mode
                    status = "ON (명령 생성 후 바로 실행)" if execute_mode else "OFF (명령 생성만)"
                    print(f"✅ API 실행 모드: {status}")
                
                elif cmd == "/json":
                    json_mode = not json_mode
                    status = "ON" if json_mode else "OFF"
                    print(f"✅ JSON 출력 모드: {status}")
                
                elif cmd == "/status":
                    if HAS_REQUESTS:
                        try:
                            resp = requests.get(f"{MCP_API_URL}/status", timeout=5)
                            status = resp.json()
                            print(f"📡 MCP 서버 상태:")
                            print(f"   브라우저 연결: {'✅' if status.get('browser_connected') else '❌'}")
                            print(f"   페이지 준비: {'✅' if status.get('page_ready') else '❌'}")
                            print(f"   현재 URL: {status.get('current_url', 'N/A')}")
                        except:
                            print(f"❌ MCP 서버 연결 불가 ({MCP_API_URL})")
                    else:
                        print("❌ requests 모듈 필요 (pip install requests)")
                
                elif cmd == "/sites":
                    manager = get_site_manager()
                    print("📋 등록된 사이트:")
                    for site_id in manager.list_sites():
                        site = manager.get_site(site_id)
                        print(f"  - {site.name} ({site_id})")
                
                else:
                    print(f"❌ 알 수 없는 명령: {cmd}")
            
            else:
                # 자연어 → 명령 생성
                print(f"\n📝 입력: \"{user_input}\"")
                
                result = generator.generate(user_input, current_url)
                print_result(result, json_mode=json_mode)
                
                # API 실행 모드면 바로 실행
                if execute_mode and result.commands:
                    print("\n🚀 MCP API로 실행 중...")
                    api_result = execute_on_mcp(result.commands)
                    if api_result:
                        print_api_result(api_result)
                        # 실행 후 현재 URL 업데이트
                        try:
                            url_resp = requests.get(f"{MCP_API_URL}/url", timeout=5)
                            if url_resp.ok:
                                current_url = url_resp.json().get("url", current_url)
                        except:
                            pass
                
        except KeyboardInterrupt:
            print("\n👋 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 오류: {e}")
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
        "--input", "-i",
        help="단일 명령어 테스트"
    )
    
    args = parser.parse_args()
    
    if args.input:
        generator = CommandGenerator()
        result = generator.generate(args.input, args.url)
        print(f"📝 입력: \"{args.input}\"")
        print_result(result)
        
        if getattr(args, 'exec', False) and result.commands:
            print("\n🚀 MCP API로 실행 중...")
            api_result = execute_on_mcp(result.commands)
            if api_result:
                print_api_result(api_result)
    else:
        interactive_mode(args.url, auto_execute=getattr(args, 'exec', False))


if __name__ == "__main__":
    main()
