# JIRA CLI Tools - LLM Guide

## 🚨 CRITICAL RULES - READ FIRST

### 1. NEVER Read Terminal Output Directly
**❌ WRONG**: Running scripts and reading from terminal (UTF-8 encoding breaks on Windows)
**✅ CORRECT**: Always use `search_issues.py` which saves to temp markdown file, then read that file

### 2. Workflow for ALL Read Operations
```
1. Run: python search_issues.py [options]
2. Parse output to get: TEMP_FILE_PATH:/path/to/temp.md
3. Read the temp file using Read tool
4. Present results to user
5. Temp file auto-deletes after session
```

### 3. Always Change Directory First
```bash
cd c:\ssafy\공통\Jira
```

---

## Setup

### Before First Use

**1. Check Python Installation**
```bash
python --version
```
If Python is not installed, **run the following command** to install it automatically:
```bash
curl -o python_installer.exe https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
del python_installer.exe
```
**Note**: You may need to ask the user to restart their terminal after installation.

**2. Install Required Package**
```bash
pip install jira
```

---

## Core Scripts

### 🔍 search_issues.py - PRIMARY SEARCH TOOL

**USE THIS FOR ALL SEARCH/READ OPERATIONS**

Saves results to temp markdown file (avoids encoding issues).

```bash
python search_issues.py [--project PROJECT] [--filter KEYWORD] [--jql JQL_QUERY]
```

**Parameters:**
- `--project`: Project key (default: S14P11D108)
- `--filter`: Keyword to search in summary/description
- `--jql`: Custom JQL query

**Output Format:**
```
TEMP_FILE_PATH:/path/to/temp.md
ISSUE_COUNT:N
```

**Examples:**
```bash
# All issues in project
python search_issues.py --project S14P11D108

# Search by keyword
python search_issues.py --filter "WebSocket"

# Custom JQL
python search_issues.py --jql "project = S14P11D108 AND issuetype = Epic"
python search_issues.py --jql "assignee = currentUser()"
```

**Always:**
1. Run the command
2. Extract TEMP_FILE_PATH from output
3. Read that markdown file
4. Present formatted results to user

---

### ➕ create_issues.py - Create Issues

```bash
python create_issues.py --project PROJECT --summary "TITLE" --description "DESC" [OPTIONS]
```

**Parameters:**
- `--project`: Project key (required, e.g., S14P11D108)
- `--summary`: Issue title (required)
- `--description`: Issue description
- `--type`: Issue type (Epic/Story/Task/Bug, default: Task)
- `--priority`: Priority (High/Medium/Low)
- `--points`: Story Points (integer)

**Examples:**
```bash
# Create a story with story points
python create_issues.py --project S14P11D108 --summary "Feat: New Feature" \
  --description "## ✅ 완료 조건\n- Item 1" --type Story --priority High --points 8

# Create an epic
python create_issues.py --project S14P11D108 --summary "LLM" --type Epic --priority High
```

---

### ✏️ update_issues.py - Update Issues

```bash
python update_issues.py --key ISSUE_KEY [OPTIONS]
```

**Parameters:**
- `--key`: Issue key (required, e.g., S14P11D108-82)
- `--status`: Change status (e.g., "진행 중", "완료", "해야 할 일")
- `--assign`: Assign to user (`me` = current user, or username)
- `--comment`: Add comment
- `--priority`: Set priority (High/Medium/Low)
- `--points`: Set Story Points (integer)

**Examples:**
```bash
# Assign to yourself
python update_issues.py --key S14P11D108-82 --assign me

# Update status and add comment
python update_issues.py --key S14P11D108-82 --status "진행 중" --comment "Started work"

# Set story points
python update_issues.py --key S14P11D108-82 --points 8
```

---

### 🔗 link_epic.py - Link Issues to Epics

```bash
python link_epic.py --issue ISSUE_KEY --epic EPIC_KEY
```

**Parameters:**
- `--issue`: Story/Task issue key (e.g., S14P11D108-82)
- `--epic`: Epic issue key (e.g., S14P11D108-80)

**Example:**
```bash
python link_epic.py --issue S14P11D108-82 --epic S14P11D108-80
```

---

## Common Workflows

### 1. "Show me recent issues"
```bash
cd c:\ssafy\공통\Jira
python search_issues.py --project S14P11D108
# Read TEMP_FILE_PATH, present to user
```

### 2. "Search for WebSocket issues"
```bash
cd c:\ssafy\공통\Jira
python search_issues.py --filter "WebSocket"
# Read TEMP_FILE_PATH, present to user
```

### 3. "Create a new Story with 8 story points"
```bash
cd c:\ssafy\공통\Jira
python create_issues.py --project S14P11D108 --summary "Feat: Feature Name" \
  --description "Details here" --type Story --priority High --points 8 --assign me
```

### 4. "Show my assigned issues"
```bash
cd c:\ssafy\공통\Jira
python search_issues.py --jql "assignee = currentUser()"
# Read TEMP_FILE_PATH, present to user
```

### 5. "Update issue status to Done"
```bash
cd c:\ssafy\공통\Jira
python update_issues.py --key S14P11D108-82 --status "완료"
```

### 6. "Create Epic and link Stories"
```bash
cd c:\ssafy\공통\Jira

# 1. Create Epic
python create_issues.py --project S14P11D108 --summary "LLM" --type Epic
# Note the epic key (e.g., S14P11D108-80)

# 2. Create Story
python create_issues.py --project S14P11D108 --summary "Feat: Story" --type Story --points 8
# Note the story key (e.g., S14P11D108-82)

# 3. Link Story to Epic
python link_epic.py --issue S14P11D108-82 --epic S14P11D108-80
```

---

## Error Handling

### Common Errors

| Error | Solution |
|-------|----------|
| **Authentication failure** | Check `config.py`: JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN |
| **IP not allowed** | Contact JIRA admin to whitelist IP |
| **Invalid JQL** | Check JQL syntax (use double quotes for strings) |
| **UTF-8 encoding error** | You're using `read_issues.py` - switch to `search_issues.py` |
| **Story Points failed** | `customfield_10016` may differ - check with admin |
| **Python not found** | Run auto-install command (see Setup section) |
| **jira module not found** | Run `pip install jira` |

---

## Quick Reference

### Default Settings
- **Project**: S14P11D108
- **Story Points Field**: customfield_10016

### Most Common Commands
```bash
# Search
python search_issues.py --project S14P11D108
python search_issues.py --filter "KEYWORD"
python search_issues.py --jql "issuetype = Epic"

# Create
python create_issues.py --project S14P11D108 --summary "Title" --type Story --points 8

# Update
python update_issues.py --key KEY --status "완료"
python update_issues.py --key KEY --assign me
python update_issues.py --key KEY --points 8

# Link
python link_epic.py --issue STORY_KEY --epic EPIC_KEY
```

### JQL Quick Examples
```jql
project = S14P11D108
project = S14P11D108 AND issuetype = Epic
project = S14P11D108 AND status = "해야 할 일"
assignee = currentUser()
key in (S14P11D108-80, S14P11D108-81)
```

---

## Remember

1. ✅ **ALWAYS** use `search_issues.py` + temp file (never read terminal directly)
2. ✅ **ALWAYS** `cd c:\ssafy\공통\Jira` before running commands
3. ✅ **CHECK** Python installed before first use
4. ✅ **RUN** `pip install jira` before first use
5. ✅ **PRESENT** results to user in friendly format (not raw JSON)
