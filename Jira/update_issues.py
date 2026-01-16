#!/usr/bin/env python3
"""
JIRA 이슈 수정 스크립트

사용법:
    python update_issues.py --key MCP-01 --status "In Progress"
    python update_issues.py --key MCP-01 --assign "김재환"
    python update_issues.py --key MCP-01 --comment "작업 진행 중"
"""

import argparse
from jira import JIRA
from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN


def connect_jira():
    """JIRA 서버에 연결"""
    return JIRA(
        server=JIRA_URL,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )


def update_issue_status(jira, issue_key, status):
    """이슈 상태 변경"""
    try:
        issue = jira.issue(issue_key)
        transitions = jira.transitions(issue)
        
        # 가능한 상태 전환 찾기
        target_transition = None
        for t in transitions:
            if t['name'].lower() == status.lower() or t['to']['name'].lower() == status.lower():
                target_transition = t['id']
                break
        
        if target_transition:
            jira.transition_issue(issue, target_transition)
            print(f"✅ {issue_key} 상태 변경: {status}")
        else:
            print(f"❌ 상태 '{status}'를 찾을 수 없습니다.")
            print("가능한 상태:")
            for t in transitions:
                print(f"  - {t['to']['name']}")
                
    except Exception as e:
        print(f"❌ 오류: {str(e)}")


def assign_issue(jira, issue_key, assignee):
    """이슈 담당자 할당"""
    try:
        issue = jira.issue(issue_key)
        
        # 담당자 검색
        if assignee.lower() == "me":
            assignee = None  # 현재 사용자
        
        jira.assign_issue(issue, assignee)
        print(f"✅ {issue_key} 담당자 할당: {assignee or '나'}")
        
    except Exception as e:
        print(f"❌ 오류: {str(e)}")


def add_comment(jira, issue_key, comment):
    """이슈에 코멘트 추가"""
    try:
        jira.add_comment(issue_key, comment)
        print(f"✅ {issue_key}에 코멘트 추가됨")
        
    except Exception as e:
        print(f"❌ 오류: {str(e)}")


def update_fields(jira, issue_key, **fields):
    """이슈 필드 업데이트"""
    try:
        issue = jira.issue(issue_key)
        issue.update(fields=fields)
        print(f"✅ {issue_key} 업데이트 완료")
        
    except Exception as e:
        print(f"❌ 오류: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='JIRA 이슈 수정')
    parser.add_argument('--key', required=True, help='이슈 키 (예: MCP-01)')
    parser.add_argument('--status', help='변경할 상태')
    parser.add_argument('--assign', help='담당자 (me = 나)')
    parser.add_argument('--comment', help='추가할 코멘트')
    parser.add_argument('--priority', help='우선순위 (High/Medium/Low)')
    
    args = parser.parse_args()
    
    print("🔗 JIRA 연결 중...")
    jira = connect_jira()
    print("✅ 연결 성공!\n")
    
    if args.status:
        update_issue_status(jira, args.key, args.status)
    
    if args.assign:
        assign_issue(jira, args.key, args.assign)
    
    if args.comment:
        add_comment(jira, args.key, args.comment)
    
    if args.priority:
        update_fields(jira, args.key, priority={'name': args.priority})


if __name__ == "__main__":
    main()
