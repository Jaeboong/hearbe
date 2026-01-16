#!/usr/bin/env python3
"""
JIRA 이슈 검색 스크립트 (임시 파일 사용)

사용법:
    python search_issues.py --query "MCP"
    python search_issues.py --project S14P11D108 --filter "MCP"
"""

import sys
import argparse
import tempfile
import os
from jira import JIRA
from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, PROJECT_KEY

# UTF-8 인코딩 강제 설정 (Windows 터미널 호환)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def connect_jira():
    """JIRA 서버에 연결"""
    return JIRA(
        server=JIRA_URL,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )


def search_and_save(jira, jql, keyword=None):
    """이슈 검색 후 임시 파일에 저장"""
    
    # 임시 파일 생성
    temp_file = tempfile.NamedTemporaryFile(
        mode='w', 
        encoding='utf-8', 
        suffix='.md',
        delete=False
    )
    temp_path = temp_file.name
    
    try:
        # JIRA 검색
        issues = jira.search_issues(jql, maxResults=100)
        
        # 키워드 필터링
        if keyword:
            filtered = [i for i in issues if keyword.upper() in i.fields.summary.upper() 
                       or (i.fields.description and keyword.upper() in i.fields.description.upper())]
            issues = filtered
        
        # Markdown 작성
        temp_file.write("# JIRA 이슈 검색 결과\n\n")
        temp_file.write(f"**총 {len(issues)}개 이슈**\n\n")
        temp_file.write("---\n\n")
        
        for i, issue in enumerate(issues, 1):
            assignee = issue.fields.assignee.displayName if issue.fields.assignee else "미할당"
            temp_file.write(f"## {i}. [{issue.key}] {issue.fields.summary}\n\n")
            temp_file.write(f"- **상태**: {issue.fields.status.name}\n")
            temp_file.write(f"- **담당자**: {assignee}\n")
            temp_file.write(f"- **유형**: {issue.fields.issuetype.name}\n")
            if issue.fields.description:
                desc_preview = issue.fields.description[:200] + "..." if len(issue.fields.description) > 200 else issue.fields.description
                temp_file.write(f"- **설명**: {desc_preview}\n")
            temp_file.write("\n---\n\n")
        
        temp_file.close()
        
        # 파일 경로 출력 (AI가 읽을 수 있도록)
        print(f"TEMP_FILE_PATH:{temp_path}")
        print(f"ISSUE_COUNT:{len(issues)}")
        
        return temp_path
        
    except Exception as e:
        temp_file.close()
        os.unlink(temp_path)
        raise e


def main():
    parser = argparse.ArgumentParser(description='JIRA 이슈 검색 (임시 파일)')
    parser.add_argument('--project', default=PROJECT_KEY, help='프로젝트 키')
    parser.add_argument('--filter', help='필터 키워드 (예: MCP, AI)')
    parser.add_argument('--jql', help='직접 JQL 쿼리')
    
    args = parser.parse_args()
    
    jira = connect_jira()
    
    # JQL 구성
    if args.jql:
        jql = args.jql
    else:
        jql = f"project = {args.project} ORDER BY key ASC"
    
    # 검색 및 임시 파일 저장
    temp_path = search_and_save(jira, jql, keyword=args.filter)
    
    # 참고: 임시 파일은 AI가 읽은 후 자동 삭제됩니다


if __name__ == "__main__":
    main()
