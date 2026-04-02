#!/usr/bin/env python3
"""
JIRA Epic 목록 조회
"""

import sys
from jira import JIRA
from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN

# UTF-8 인코딩 강제 설정 (Windows 터미널 호환)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def list_epics():
    try:
        jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        
        print("📂 에픽(Epic) 목록 조회:")
        epics = jira.search_issues('issuetype = Epic ORDER BY created DESC', maxResults=50)
        
        if not epics:
            print("  - 에픽이 없습니다.")
            return

        for i, epic in enumerate(epics, 1):
            # 에픽 이름 (Custom Field) 확인 필요, 보통 Summary를 사용하거나 'Epic Name' 필드가 있을 수 있음
            # 일단 Summary 출력
            print(f"{i}. [{epic.key}] {epic.fields.summary} (Status: {epic.fields.status.name})")
        
        print("\n" + "="*70)

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    list_epics()
