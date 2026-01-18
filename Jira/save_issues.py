#!/usr/bin/env python3
"""S14P11D108 프로젝트 이슈를 파일로 저장"""

import sys
from jira import JIRA
from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN

# UTF-8 인코딩 강제 설정 (Windows 터미널 호환)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

issues = jira.search_issues('project = S14P11D108 ORDER BY key ASC', maxResults=100)

with open('project_issues.txt', 'w', encoding='utf-8') as f:
    f.write("="*80 + "\n")
    f.write("S14P11D108 프로젝트 이슈 목록\n")
    f.write("="*80 + "\n\n")
    f.write(f"총 {len(issues)}개 이슈:\n\n")
    
    for i, issue in enumerate(issues, 1):
        assignee = issue.fields.assignee.displayName if issue.fields.assignee else "미할당"
        f.write(f"{i:2d}. [{issue.key}] {issue.fields.summary}\n")
        f.write(f"     상태: {issue.fields.status.name:15s} | 담당: {assignee:15s} | 유형: {issue.fields.issuetype.name}\n\n")
    
    f.write("="*80 + "\n")

print(f"✅ {len(issues)}개 이슈를 project_issues.txt에 저장했습니다.")
