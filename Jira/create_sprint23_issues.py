import sys

# Logging setup
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("execution_log_bat.txt", "w", encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = Logger()
sys.stderr = sys.stdout

try:
    from jira import JIRA
    from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, PROJECT_KEY as JIRA_PROJECT_KEY
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Setup Error: {e}")
    sys.exit(1)

# Setup JIRA connection
def connect_jira():
    return JIRA(
        server=JIRA_URL,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )

def main():
    jira = connect_jira()
    print("Connected to JIRA")

    # 1. Find User '서해령'
    print("Searching for user '서해령'...")
    users = jira.search_users(query="서해령")
    if not users:
        print("Error: User '서해령' not found.")
        sys.exit(1)
    # Prefer exact match or first one
    target_user = users[0]
    print(f"Found User: {target_user.displayName} ({target_user.accountId})")

    # 2. Find Epics to get Keys
    # We need keys for: 마이페이지, 장바구니, 쇼핑
    print("Searching for Epics...")
    epic_names = ["마이페이지", "장바구니", "쇼핑"]
    epics_map = {}
    
    # Search all Epics in project
    issues = jira.search_issues(f'project = {JIRA_PROJECT_KEY} AND issuetype = Epic', maxResults=50)
    for issue in issues:
        # Check summary for keywords
        summary = issue.fields.summary
        for name in epic_names:
            if name in summary:
                epics_map[name] = issue.key
                print(f"Mapped Epic '{name}' -> {issue.key} ({summary})")
    
    # Verify all needed epics found
    missing_epics = [name for name in epic_names if name not in epics_map]
    if missing_epics:
        print(f"Warning: Could not find Epics for: {missing_epics}")
        # Decide whether to proceed or stop. User said "create issues", linking is part of it. 
        # I'll proceed creating issues and skip linking if epic missing, but print error.

    # 3. Define Tasks
    # Sprint 2
    # 1. Feat: 마이페이지 (일반용/확대용) -> Epic: 마이페이지
    # 2. Feat: 회원정보 수정 -> Epic: 마이페이지
    # 3. Feat: 통합 장바구니 (확대용) -> Epic: 장바구니
    # Sprint 3
    # 4. Feat: 쇼핑사이트 선택 (일반용) -> Epic: 쇼핑
    # 5. Feat: 쇼핑사이트 선택 (확대용) -> Epic: 쇼핑
    # 6. Feat: 확대 쇼핑 뷰 -> Epic: 쇼핑

    tasks = [
        {
            "summary": "Feat: 마이페이지 (일반용/확대용)",
            "description": "[FE] 사용자는 내 정보를 확인하기 위해 마이페이지를 사용하고 싶다\n\n**완료 조건**:\n- [ ] 위시리스트, 자주찾는상품, 나의 취향 정보 표시\n- [ ] GET /auth/mypage API 연동",
            "points": 3,
            "epic": "마이페이지",
            "sprint": "Sprint 2" # Just for log, Jira sprint assignment usually requires sprint ID, user asked to put in 'backlog' (which is default).
        },
        {
            "summary": "Feat: 회원정보 수정",
            "description": "[FE] 사용자는 개인정보를 변경하기 위해 회원정보 수정 기능을 사용하고 싶다\n\n**완료 조건**:\n- [ ] 비밀번호 변경\n- [ ] 프로필 수정\n- [ ] PATCH /users/{id}, PATCH /users/{id}/password API 연동",
            "points": 3,
            "epic": "마이페이지",
            "sprint": "Sprint 2"
        },
        {
            "summary": "Feat: 통합 장바구니 (확대용)",
            "description": "[FE] 사용자는 큰 화면으로 장바구니를 보기 위해 확대 장바구니를 사용하고 싶다\n\n**완료 조건**:\n- [ ] 쇼핑몰별 구분선 굵게\n- [ ] 한 화면 최대 2개 버튼 (오클릭 방지)\n- [ ] GET /cart API 연동",
            "points": 3,
            "epic": "장바구니",
            "sprint": "Sprint 2"
        },
        {
            "summary": "Feat: 쇼핑사이트 선택 (일반용)",
            "description": "[FE] 사용자는 원하는 쇼핑몰에서 구매하기 위해 쇼핑사이트 선택 기능을 사용하고 싶다\n\n**완료 조건**:\n- [ ] 쇼핑사이트 버튼 목록\n- [ ] GET /platforms API 연동",
            "points": 3,
            "epic": "쇼핑",
            "sprint": "Sprint 3"
        },
        {
            "summary": "Feat: 쇼핑사이트 선택 (확대용)",
            "description": "[FE] 사용자는 큰 화면으로 쇼핑하기 위해 쇼핑사이트 선택 기능을 사용하고 싶다\n\n**완료 조건**:\n- [ ] 로고 → 텍스트 버튼 대체\n- [ ] 클릭 시 음성 사이트명 안내\n- [ ] GET /platforms API 연동",
            "points": 3,
            "epic": "쇼핑",
            "sprint": "Sprint 3"
        },
        {
            "summary": "Feat: 확대 쇼핑 뷰",
            "description": "[FE] 사용자는 상품을 크게 보기 위해 확대 쇼핑 뷰를 사용하고 싶다\n\n**완료 조건**:\n- [ ] 상품 이미지/가격 화면 80% 이상 확대\n- [ ] 공유 코드 4자리 크게 표시 + TTS",
            "points": 5,
            "epic": "쇼핑",
            "sprint": "Sprint 3"
        }
    ]

    # 4. Create Issues
    print(f"\nCreating {len(tasks)} issues...")
    for task in tasks:
        print(f"\nProcessing: {task['summary']}")
        
        # Check if already exists? (Optional, but good practice. For now, just create)
        
        issue_dict = {
            'project': {'key': JIRA_PROJECT_KEY},
            'summary': task['summary'],
            'description': task['description'],
            'issuetype': {'name': 'Story'}, # Docs say 'Story'
            'priority': {'name': 'Medium'}, 
             # Assignee can be set here? Yes if field supported.
            'assignee': {'id': target_user.accountId}
        }
        
        try:
            new_issue = jira.create_issue(fields=issue_dict)
            print(f"  -> Created Issue: {new_issue.key}")

            # Set Story Points
            # Default field for story points usually customfield_10031 as seen in create_issues.py
            # But LLM_GUIDE says customfield_10016. Check config? 
            # create_issues.py uses customfield_10031. 
            # LLM_GUIDE "Quick Reference" says: Story Points Field: customfield_10016.
            # CONFLICT! create_issues.py (line 44) uses 10031. LLM_GUIDE (line 237) says 10016.
            # I will try both or check specific project config.
            # Safe bet: try 10031 first (as per script), if fail, try 10016.
            
            sp_fields = ['customfield_10031', 'customfield_10016']
            sp_set = False
            for sp_field in sp_fields:
                try:
                    new_issue.update(fields={sp_field: task['points']})
                    print(f"  -> Set Story Points to {task['points']} (Field: {sp_field})")
                    sp_set = True
                    break
                except Exception as e:
                    # print(f"    (Failed {sp_field}: {e})")
                    pass
            if not sp_set:
                print("  -> WARNING: Failed to set Story Points")

            # Link Epic
            epic_key = epics_map.get(task['epic'])
            if epic_key:
                # Add to Epic
                # Jira Cloud uses 'parent' field for Next-Gen, but 'Epic Link' (customfield) for Classic.
                # Or 'add_issues_to_epic' method?
                # link_epic.py uses: jira.add_issues_to_epic(epic_id=epic_key, issue_keys=[issue_key])
                try:
                    jira.add_issues_to_epic(epic_id=epic_key, issue_keys=[new_issue.key])
                    print(f"  -> Linked to Epic: {epic_key} ({task['epic']})")
                except Exception as e:
                    print(f"  -> Failed to link Epic: {e}")
            
            # Add Label 'Frontend'
            new_issue.update(fields={"labels": ["Frontend"]})
            print("  -> Added Label: Frontend")

        except Exception as e:
            print(f"  -> FAILED: {e}")

if __name__ == "__main__":
    main()
