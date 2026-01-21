#!/usr/bin/env python3
"""JIRA 이슈를 에픽에 연결"""

import sys
import argparse
from jira import JIRA
from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN

# UTF-8 인코딩 강제 설정 (Windows 터미널 호환)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def connect_jira():
    """JIRA 서버에 연결"""
    return JIRA(
        server=JIRA_URL,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )


def link_to_epic(jira, issue_key, epic_key):
    """이슈를 에픽에 연결"""
    try:
        # Epic Link는 일반적으로 customfield_10014 또는 customfield_10008
        # 프로젝트에 따라 다를 수 있으므로 여러 시도

        issue = jira.issue(issue_key)

        # 방법 1: customfield_10014 시도
        try:
            issue.update(fields={'customfield_10014': epic_key})
            print(f"[SUCCESS] {issue_key} -> {epic_key} 연결 완료 (customfield_10014)")
            return
        except:
            pass

        # 방법 2: customfield_10008 시도
        try:
            issue.update(fields={'customfield_10008': epic_key})
            print(f"[SUCCESS] {issue_key} -> {epic_key} 연결 완료 (customfield_10008)")
            return
        except:
            pass

        # 방법 3: Epic Link 필드 이름으로 직접 시도
        try:
            issue.update(fields={'Epic Link': epic_key})
            print(f"[SUCCESS] {issue_key} -> {epic_key} 연결 완료 (Epic Link)")
            return
        except:
            pass

        # 모든 방법 실패
        print(f"[ERROR] Epic Link 필드를 찾을 수 없습니다. JIRA 관리자에게 문의하세요.")
        print(f"  Issue: {issue_key}, Epic: {epic_key}")

    except Exception as e:
        print(f"[ERROR] {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='JIRA 이슈를 에픽에 연결')
    parser.add_argument('--issue', required=True, help='연결할 이슈 키 (예: S14P11D108-82)')
    parser.add_argument('--epic', required=True, help='에픽 키 (예: S14P11D108-80)')

    args = parser.parse_args()

    print("JIRA 연결 중...")
    jira = connect_jira()
    print("연결 성공!\n")

    link_to_epic(jira, args.issue, args.epic)


if __name__ == "__main__":
    main()
