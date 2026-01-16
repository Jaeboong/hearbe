#!/usr/bin/env python3
"""
JIRA 프로젝트 및 이슈 전체 조회
"""

import sys
from jira import JIRA
from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN

# UTF-8 인코딩 강제 설정 (Windows 터미널 호환)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def list_all():
    jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))
    
    print("📂 프로젝트 목록:")
    projects = jira.projects()
    for project in projects:
        print(f"  - {project.key}: {project.name}")
    
    print("\n" + "="*70 + "\n")
    
    print("🔍 전체 이슈 조회 (최근 20개):")
    issues = jira.search_issues('project is not EMPTY ORDER BY updated DESC', maxResults=20)
    
    for i, issue in enumerate(issues, 1):
        assignee = issue.fields.assignee.displayName if issue.fields.assignee else "미할당"
        print(f"{i}. [{issue.key}] {issue.fields.summary}")
        print(f"   프로젝트: {issue.fields.project.key} | 상태: {issue.fields.status.name} | 담당: {assignee}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    list_all()
