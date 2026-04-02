import sys
try:
    from jira import JIRA
    from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, PROJECT_KEY
except ImportError:
    sys.exit("Import Error")

# Setup JIRA connection
def connect_jira():
    return JIRA(
        server=JIRA_URL,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )

def main():
    jira = connect_jira()
    print("Connected to JIRA")

    # Defined Issues
    issues_map = {
        "258": "MyPage",
        "259": "MyPage",
        "260": "Cart",
        "261": "Shopping",
        "262": "Shopping",
        "263": "Shopping"
    }

    # Epic Keys Map
    # Shopping is known: S14P11D108-186
    epics_keys = {
        "Shopping": "S14P11D108-186",
        "MyPage": None,
        "Cart": None
    }

    # Helper to find or create epic
    def get_or_create_epic(name, summary):
        # Search first
        print(f"Searching for Epic '{summary}'...")
        found = jira.search_issues(f'project = {PROJECT_KEY} AND issuetype = Epic AND summary ~ "{summary}"')
        if found:
            print(f"  -> Found: {found[0].key}")
            return found[0].key
        else:
            print(f"  -> Not found. Creating Epic '{summary}'...")
            epic_dict = {
                'project': {'key': PROJECT_KEY},
                'summary': summary,
                'issuetype': {'name': 'Epic'},
                'customfield_10011': summary # Epic Name field usually required for Classic, but Next-Gen uses summary. Cloud often needs text field.
                # If customfield_10011 (Epic Name) is required, we find out.
            }
            try:
                new_epic = jira.create_issue(fields=epic_dict)
                print(f"  -> Created: {new_epic.key}")
                return new_epic.key
            except Exception as e:
                print(f"  -> Failed to create Epic: {e}")
                # Try without customfield
                if 'customfield_10011' in str(e):
                     del epic_dict['customfield_10011']
                     new_epic = jira.create_issue(fields=epic_dict)
                     print(f"  -> Created (retry): {new_epic.key}")
                     return new_epic.key
                return None

    # Get Keys
    epics_keys["MyPage"] = get_or_create_epic("MyPage", "마이페이지")
    epics_keys["Cart"] = get_or_create_epic("Cart", "장바구니")
    
    # Link Issues
    for issue_id_suffix, epic_type in issues_map.items():
        issue_key = f"{PROJECT_KEY}-{issue_id_suffix}"
        epic_key = epics_keys.get(epic_type)
        
        if not epic_key:
            print(f"Skipping {issue_key}: Epic key for {epic_type} missing.")
            continue
            
        print(f"Linking {issue_key} to {epic_key} ({epic_type})...")
        try:
            # Use add_issues_to_epic
            jira.add_issues_to_epic(epic_id=epic_key, issue_keys=[issue_key])
            print("  -> Success")
        except Exception as e:
            print(f"  -> Failed: {e}")

if __name__ == "__main__":
    main()
