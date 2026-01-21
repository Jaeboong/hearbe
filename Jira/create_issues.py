#!/usr/bin/env python3
"""
JIRA 이슈 생성 스크립트

사용법:
    python create_issues.py --file ../MCP/docs/JIRA_ISSUES.md   # 파일에서 이슈 생성
"""

import sys
import argparse
from jira import JIRA
from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_TIMEOUT

# UTF-8 인코딩 강제 설정 (Windows 터미널 호환)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def connect_jira():
    """JIRA 서버에 연결"""
    return JIRA(
        server=JIRA_URL,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        timeout=JIRA_TIMEOUT
    )


def create_issue(jira, project_key, summary, description, issuetype="Task", priority=None, story_points=None):
    """단일 이슈 생성"""
    try:
        issue_dict = {
            'project': {'key': project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issuetype},
        }
        
        if priority:
            issue_dict['priority'] = {'name': priority}
        
        new_issue = jira.create_issue(fields=issue_dict)
        
        # Story Points 설정 (customfield_10031이 웹 UI에 표시되는 필드)
        if story_points:
            try:
                new_issue.update(fields={'customfield_10031': story_points})
            except Exception as e:
                print(f"[WARNING] Story Points 설정 실패: {e}")

        print(f"[SUCCESS] 생성 완료: {new_issue.key} - {summary}")
        return new_issue

    except Exception as e:
        print(f"[ERROR] 생성 실패: {str(e)}")
        return None


def create_issue_interactive(jira):
    """대화형 이슈 생성"""
    print("\n" + "="*70)
    print("JIRA 이슈 대화형 생성")
    print("="*70 + "\n")
    
    project_key = input("프로젝트 키 (예: MCP): ").strip()
    summary = input("이슈 제목: ").strip()
    description = input("이슈 설명: ").strip()
    issuetype = input("이슈 유형 (Task/Story/Bug) [Task]: ").strip() or "Task"
    priority = input("우선순위 (High/Medium/Low) [Medium]: ").strip() or "Medium"
    
    try:
        story_points = int(input("Story Points [0]: ").strip() or "0")
    except:
        story_points = 0
    
    print("\n생성 중...")
    return create_issue(jira, project_key, summary, description, issuetype, priority, story_points if story_points > 0 else None)


def main():
    parser = argparse.ArgumentParser(description='JIRA 이슈 생성')
    parser.add_argument('--file', help='이슈 정의 파일 경로 (MD 형식)')
    parser.add_argument('--interactive', '-i', action='store_true', help='대화형 모드')
    parser.add_argument('--project', help='프로젝트 키 (예: S14P11D108)')
    parser.add_argument('--summary', help='이슈 제목')
    parser.add_argument('--description', help='이슈 설명')
    parser.add_argument('--type', default='Task', help='이슈 유형 (Task/Story/Bug)')
    parser.add_argument('--priority', help='우선순위 (High/Medium/Low)')
    parser.add_argument('--points', type=int, help='Story Points')

    args = parser.parse_args()

    # UTF-8 인코딩 문제 방지를 위해 이모지 제거
    print("JIRA 연결 중...")
    jira = connect_jira()
    print("연결 성공!\n")

    if args.file:
        print(f"파일에서 이슈 로드: {args.file}")
        print("아직 구현되지 않았습니다. --interactive 옵션을 사용하세요.")
    elif args.interactive:
        create_issue_interactive(jira)
    elif args.project and args.summary:
        # 커맨드라인 인자로 이슈 생성
        create_issue(
            jira,
            args.project,
            args.summary,
            args.description or "",
            args.type,
            args.priority,
            args.points
        )
    else:
        print("사용법: python create_issues.py --interactive")
        print("또는: python create_issues.py --project PROJECT --summary SUMMARY [옵션]")
        print("또는: python create_issues.py --file <파일경로>")


if __name__ == "__main__":
    main()
