#!/usr/bin/env python3
"""
JIRA 이슈 읽기 스크립트

사용법:
    python read_issues.py                           # 최근 이슈 10개 조회
    python read_issues.py --project MCP             # MCP 프로젝트 이슈 조회
    python read_issues.py --key MCP-01              # 특정 이슈 상세 조회
    python read_issues.py --assignee currentUser()  # 나에게 할당된 이슈
"""

import argparse
from jira import JIRA
from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, DEFAULT_PROJECT_KEY


def connect_jira():
    """JIRA 서버에 연결"""
    return JIRA(
        server=JIRA_URL,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )


def read_issue_detail(jira, issue_key):
    """특정 이슈의 상세 정보 조회"""
    try:
        issue = jira.issue(issue_key)
        print(f"\n{'='*70}")
        print(f"이슈 키: {issue.key}")
        print(f"제목: {issue.fields.summary}")
        print(f"상태: {issue.fields.status.name}")
        print(f"유형: {issue.fields.issuetype.name}")
        print(f"우선순위: {issue.fields.priority.name if issue.fields.priority else 'N/A'}")
        print(f"담당자: {issue.fields.assignee.displayName if issue.fields.assignee else '미할당'}")
        print(f"\n설명:")
        print(issue.fields.description or "설명 없음")
        print(f"{'='*70}\n")
        return issue
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        return None


def list_issues(jira, project=None, assignee=None, max_results=10):
    """이슈 목록 조회"""
    jql_parts = []
    
    if project:
        jql_parts.append(f"project = {project}")
    else:
        jql_parts.append("project is not EMPTY")
    
    if assignee:
        jql_parts.append(f"assignee = {assignee}")
    
    jql = " AND ".join(jql_parts) + " ORDER BY updated DESC"
    
    print(f"\n🔍 JQL: {jql}")
    print(f"{'='*70}\n")
    
    try:
        issues = jira.search_issues(jql, maxResults=max_results)
        
        if not issues:
            print("조회된 이슈가 없습니다.")
            return
        
        print(f"총 {len(issues)}개의 이슈:")
        for i, issue in enumerate(issues, 1):
            assignee = issue.fields.assignee.displayName if issue.fields.assignee else "미할당"
            print(f"{i}. [{issue.key}] {issue.fields.summary}")
            print(f"   상태: {issue.fields.status.name} | 담당: {assignee}")
        
        print(f"\n{'='*70}\n")
        
    except Exception as e:
        print(f"❌ 오류: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='JIRA 이슈 읽기')
    parser.add_argument('--key', help='조회할 이슈 키 (예: MCP-01)')
    parser.add_argument('--project', help=f'프로젝트 키 (기본값: {DEFAULT_PROJECT_KEY})')
    parser.add_argument('--assignee', help='담당자 (예: currentUser())')
    parser.add_argument('--max', type=int, default=10, help='최대 조회 개수 (기본값: 10)')
    
    args = parser.parse_args()
    
    print("🔗 JIRA 연결 중...")
    jira = connect_jira()
    print("✅ 연결 성공!\n")
    
    if args.key:
        # 특정 이슈 상세 조회
        read_issue_detail(jira, args.key)
    else:
        # 이슈 목록 조회
        project = args.project or DEFAULT_PROJECT_KEY
        list_issues(jira, project=project, assignee=args.assignee, max_results=args.max)


if __name__ == "__main__":
    main()
