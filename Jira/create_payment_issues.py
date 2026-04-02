import sys
import re
from jira import JIRA
from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_TIMEOUT

# UTF-8 Encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def connect_jira():
    return JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN), timeout=JIRA_TIMEOUT)

def parse_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    data = {
        "epic_key": None,
        "stories": []
    }

    # Extract Epic Key
    epic_match = re.search(r'\*\*OCR \((S14P11D108-\d+)\)\*\*', content)
    if epic_match:
        data["epic_key"] = epic_match.group(1)

    # Extract Stories (Split by "## Story")
    story_sections = re.split(r'## Story\n', content)[1:] # Skip empty first split
    
    for section in story_sections:
        title_match = re.search(r'\*\*Title\*\*: (.*)', section)
        if not title_match: 
            continue
            
        desc_start = section.find("**Description**:") + len("**Description**:")
        desc_end = section.find("**Story Points**")
        desc = section[desc_start:desc_end].strip() if desc_start > -1 and desc_end > -1 else ""
        
        points_match = re.search(r'\*\*Story Points\*\*: (\d+)', section)
        
        data["stories"].append({
            "title": title_match.group(1).strip(),
            "description": desc,
            "points": int(points_match.group(1)) if points_match else 0
        })
            
    return data

def create_issues(data):
    jira = connect_jira()
    print("✅ Jira Connected")
    
    epic_key = data.get("epic_key")
    if not epic_key:
        print("❌ Error: Could not find Epic Key in markdown.")
        return

    print(f"🔗 Linking to Epic: {epic_key}")

    for story_data in data["stories"]:
        project_key = epic_key.split('-')[0]
        story_fields = {
            'project': {'key': project_key},
            'summary': story_data["title"],
            'description': story_data["description"],
            'issuetype': {'name': 'Story'},
            'customfield_10031': story_data["points"],
            
            # Try linking to Epic via 'parent' (Team-managed) or 'customfield_10014' (Company-managed)
            # We'll try 'parent' first as it's cleaner for modern Jira
            'parent': {'key': epic_key}
        }
        
        print(f"Creating Story: {story_data['title']}...")
        try:
            story = jira.create_issue(fields=story_fields)
        except Exception as e:
            # Fallback: Create without link, then try to link
            print(f"⚠️ Direct linking failed ({e}), creating standalone and retrying link...")
            if 'parent' in story_fields:
                del story_fields['parent']
            
            story = jira.create_issue(fields=story_fields)
            
            try:
                # Try adding to epic
                jira.add_issues_to_epic(epic_key, [story.key])
                print(f"   -> Linked to Epic: {epic_key}")
            except Exception as link_err:
                 print(f"   -> ❌ Failed to link to Epic: {link_err}")

        print(f"   -> Created: {story.key}")

if __name__ == "__main__":
    file_path = r"c:\Users\SSAFY\.gemini\antigravity\brain\e237665f-98bf-4e8f-a1f5-ff9ceddb6285\ISSUES_PAYMENT_OCR_20260121.md"
    data = parse_markdown(file_path)
    # print(data) # Debug
    create_issues(data)

