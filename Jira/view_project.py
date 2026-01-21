#!/usr/bin/env python3
"""S14P11D108 프로젝트 이슈 전체 조회"""

import sys
from jira import JIRA
from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN

# UTF-8 인코딩 강제 설정 (Windows 터미널 호환)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

print("="*80)
print("S14P11D108 프로젝트 이슈 목록")
print("="*80 + "\n")

issues = jira.search_issues('project = S14P11D108 ORDER BY key ASC', maxResults=100)

print(f"총 {len(issues)}개 이슈:\n")

for i, issue in enumerate(issues, 1):
    assignee = issue.fields.assignee.displayName if issue.fields.assignee else "미할당"
    print(f"{i:2d}. [{issue.key}] {issue.fields.summary}")
    print(f"     상태: {issue.fields.status.name:12s} | 담당: {assignee:10s} | 유형: {issue.fields.issuetype.name}")
    
print("\n" + "="*80)
