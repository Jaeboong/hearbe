#!/usr/bin/env python3
"""
JIRA 이슈 읽기 테스트 스크립트

사용법:
python test_jira_read.py
"""

from jira import JIRA

# ===== JIRA 설정 =====
JIRA_URL = "https://ssafy.atlassian.net"
JIRA_EMAIL = "cbkjh0225@gmail.com"
JIRA_API_TOKEN = "ATATT3xFfGF0VH-lGpoFujFVE8AkInxnqLHmbRFiWnUDosRH30AHQBiTtys7-YSqP2rFLe2TDCNOcuFk4j0R_ntEsnvScEWEJsmko6dXuEoQ9d4OOhzVemaLx8TfB9re9lmBoW3KK_EEHJeRMo4zoFw9Jo9FyI_gYyJJywNTso24Q5zi-M1LiKQ=8C48F04D"
# ====================


def test_jira_connection():
    """JIRA 연결 및 이슈 읽기 테스트"""
    
    print("=" * 70)
    print("JIRA 연결 테스트")
    print("=" * 70)
    
    try:
        # JIRA 연결
        print(f"\n📡 JIRA 서버에 연결 중: {JIRA_URL}")
        jira = JIRA(
            server=JIRA_URL,
            basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
        )
        print("✅ JIRA 연결 성공!\n")
        
        # 프로젝트 목록 조회
        print("📂 프로젝트 목록 조회:")
        projects = jira.projects()
        for project in projects[:10]:  # 처음 10개만 출력
            print(f"  - {project.key}: {project.name}")
        print()
        
        # 내가 할당된 이슈 조회
        print("📋 나에게 할당된 이슈 조회:")
        try:
            my_issues = jira.search_issues('assignee = currentUser() ORDER BY updated DESC', maxResults=5)
            if my_issues:
                for issue in my_issues:
                    print(f"  - [{issue.key}] {issue.fields.summary}")
            else:
                print("  할당된 이슈가 없습니다.")
        except Exception as e:
            print(f"  ⚠️  조회 실패: {str(e)}")
        print()
        
        # 최근 업데이트된 이슈 조회
        print("🔍 최근 업데이트된 이슈 조회 (최대 10개):")
        try:
            recent_issues = jira.search_issues('project is not EMPTY ORDER BY updated DESC', maxResults=10)
            for issue in recent_issues:
                print(f"  - [{issue.key}] {issue.fields.summary}")
                print(f"    상태: {issue.fields.status.name} | 유형: {issue.fields.issuetype.name}")
        except Exception as e:
            print(f"  ⚠️  조회 실패: {str(e)}")
        print()
        
        print("=" * 70)
        print("✅ JIRA API 테스트 완료!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_jira_connection()
