
import sys
from jira import JIRA
from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_TIMEOUT

# Force utf-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_KEY = "S14P11D108"

def connect_jira():
    return JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN), timeout=JIRA_TIMEOUT)

def update_epic_link(jira, issue, epic_key):
    fields_to_try = ['customfield_10014', 'customfield_10008', 'Epic Link']
    for field in fields_to_try:
        try:
            issue.update(fields={field: epic_key})
            print(f"  -> Linked to Epic {epic_key} using {field}")
            return
        except:
            continue
    print(f"  [WARNING] Failed to link to Epic {epic_key}")

def update_story_points(issue, points):
    fields_to_try = ['customfield_10016', 'customfield_10031']
    for field in fields_to_try:
        try:
            issue.update(fields={field: points})
            print(f"  -> Set points to {points} using {field}")
            return
        except:
            continue
            
    # If integer fails, try float
    for field in fields_to_try:
        try:
            issue.update(fields={field: float(points)})
            print(f"  -> Set points to {points} using {field}")
            return
        except:
            continue
    print(f"  [WARNING] Failed to set Story Points {points}")

def assign_issue(jira, issue, user_name):
    # Try to search for user
    try:
        users = jira.search_users(user=user_name)
        if users:
            # Pick first match
            account_id = users[0].accountId
            jira.assign_issue(issue.key, account_id)
            print(f"  -> Assigned to {users[0].displayName} ({user_name})")
        else:
            # Fallback: Assign to current user if exact match fails, or just log
            print(f"  [WARNING] User '{user_name}' not found. Leaving unassigned.")
            # jira.assign_issue(issue.key, jira.myself()['accountId']) # Optional fallback
    except Exception as e:
        print(f"  [WARNING] Failed to assign to {user_name}: {e}")

def create_work_items(jira):
    # 1. Epics (Sprint 1)
    epics_data = [
        {"summary": "인증", "desc": "Domain: Authentication (Login, Regist, Find ID/PW)", "priority": "High"},
        {"summary": "메인", "desc": "Domain: Main Page", "priority": "High"}
    ]
    
    epic_map = {} # Name -> Key
    
    print("--- Creating Epics ---")
    for e in epics_data:
        issue_dict = {
            'project': {'key': PROJECT_KEY},
            'summary': e['summary'],
            'description': e['desc'],
            'issuetype': {'name': 'Epic'},
            'priority': {'name': e['priority']}
        }
        try:
            new_epic = jira.create_issue(fields=issue_dict)
            print(f"Created Epic: {new_epic.key} ({e['summary']})")
            epic_map[e['summary']] = new_epic.key
        except Exception as err:
            print(f"[ERROR] Failed to create Epic {e['summary']}: {err}")
        
    # 2. Stories (Sprint 1)
    # Based on JIRA_TASK_ISSUES.md
    stories_data = [
        # Authentication Epic
        {"epic": "인증", "summary": "Feat: 로그인 (시각장애인용 A형)", "points": 5, "priority": "High", "assignee": "강한솔", 
         "desc": "[Role] 사용자는 서비스에 접속하기 위해 로그인 기능을 사용하고 싶다. \n완료조건:\n- 음성 입력(STT) 아이디/비밀번호\n- TTS 안내 기능\n- 노랑/검정 대비 UI"},
        
        {"epic": "인증", "summary": "Feat: 로그인 (일반용 B/C형)", "points": 3, "priority": "High", "assignee": "서해령",
         "desc": "[Role] 사용자는 서비스에 접속하기 위해 로그인 기능을 사용하고 싶다.\n완료조건:\n- 아이디/비밀번호 입력 폼\n- 로그인 유지 체크박스"},
        
        {"epic": "인증", "summary": "Feat: 회원가입 (시각장애인용)", "points": 8, "priority": "High", "assignee": "강한솔",
         "desc": "[Role] 사용자는 서비스를 이용하기 위해 회원가입 기능을 사용하고 싶다.\n완료조건:\n- 이름, 아이디, 비밀번호(6자리)\n- 장애인 복지 카드 등록 UI\n- 음성 입력/TTS 안내"},
        
        {"epic": "인증", "summary": "Feat: 회원가입 (일반용)", "points": 3, "priority": "High", "assignee": "서해령",
         "desc": "[Role] 사용자는 서비스를 이용하기 위해 회원가입 기능을 사용하고 싶다.\n완료조건:\n- 이름, 아이디, 비밀번호(8~12자리)\n- 약관 동의 체크박스"},
        
        {"epic": "인증", "summary": "Feat: 아이디 찾기 (시각장애인용)", "points": 5, "priority": "High", "assignee": "강한솔",
         "desc": "[Role] 사용자는 분실한 아이디를 찾기 위해 아이디 찾기 기능을 사용하고 싶다.\n완료조건:\n- 장애인 복지 카드 OCR 인증\n- 아이디 음성 안내(TTS)"},
        
        {"epic": "인증", "summary": "Feat: 아이디 찾기 (일반용)", "points": 3, "priority": "High", "assignee": "서해령",
         "desc": "[Role] 사용자는 분실한 아이디를 찾기 위해 아이디 찾기 기능을 사용하고 싶다.\n완료조건:\n- 이메일 입력 폼\n- 인증번호 전송/확인"},
        
        {"epic": "인증", "summary": "Feat: 비밀번호 찾기 (시각장애인용)", "points": 3, "priority": "High", "assignee": "강한솔",
         "desc": "[Role] 사용자는 분실한 비밀번호를 재설정하기 위해 비밀번호 찾기 기능을 사용하고 싶다.\n완료조건:\n- 비밀번호 6자리 변경\n- 음성/키패드 입력"},

        {"epic": "인증", "summary": "Feat: 비밀번호 찾기 (일반용)", "points": 3, "priority": "High", "assignee": "서해령",
         "desc": "[Role] 사용자는 분실한 비밀번호를 재설정하기 위해 비밀번호 찾기 기능을 사용하고 싶다.\n완료조건:\n- 이메일 인증 후 비밀번호 재설정"},

        {"epic": "인증", "summary": "Feat: 로그아웃", "points": 1, "priority": "Medium", "assignee": "강한솔",
         "desc": "[Role] 사용자는 서비스에서 안전하게 나가기 위해 로그아웃 기능을 사용하고 싶다.\n완료조건:\n- Bearer Token 제거\n- 로그인 페이지 리다이렉트"},

        # Main Epic
        {"epic": "메인", "summary": "Feat: 메인 페이지", "points": 5, "priority": "High", "assignee": "서해령",
         "desc": "[Role] 사용자는 서비스 타입을 선택하기 위해 메인 페이지를 사용하고 싶다.\n완료조건:\n- 마이크 권한 요청 팝업\n- A/B/C/S 버튼"}
    ]

    print("\n--- Creating Stories ---")
    
    for s in stories_data:
        issue_dict = {
            'project': {'key': PROJECT_KEY},
            'summary': s['summary'],
            'description': s['desc'],
            'issuetype': {'name': 'Story'},
            'priority': {'name': s['priority']},
            'labels': ['Sprint1']
        }
        try:
            new_story = jira.create_issue(fields=issue_dict)
            print(f"Created Story: {new_story.key} ({s['summary']})")
            
            # Assign
            if s.get('assignee'):
                assign_issue(jira, new_story, s['assignee'])
            
            # Link Epic
            if s['epic'] in epic_map:
                update_epic_link(jira, new_story, epic_map[s['epic']])
            else:
                print(f"  [WARNING] Epic '{s['epic']}' not found in created map.")

            # Points
            update_story_points(new_story, s['points'])
            
        except Exception as err:
            print(f"[ERROR] Failed to create Story {s['summary']}: {err}")

def main():
    print("Connecting to Jira...")
    jira = connect_jira()
    create_work_items(jira)
    print("\n[DONE] All Sprint 1 items created.")

if __name__ == "__main__":
    main()
