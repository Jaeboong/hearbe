# JIRA CLI Tools - LLM Guide

This directory contains JIRA CLI tools for managing JIRA issues. When the user requests JIRA-related information, use these scripts to fetch or modify data.

## Prerequisites

Before first use, install the required package:
```bash
pip install jira
```

## Important Notes

- Always change to the Jira directory before running scripts: `cd c:\ssafy\공통\Jira`
- **IMPORTANT: Always use search_issues.py instead of read_issues.py** - search_issues.py saves results to a markdown temp file which avoids UTF-8 encoding issues on Windows terminals
- When using search_issues.py, read the temporary file path from the output (TEMP_FILE_PATH)
- For multi-step operations, break them into individual script calls
- Present results in a user-friendly format, not raw JSON
- Use appropriate parameters based on user's natural language request

---

## Available Scripts

### 1. search_issues.py - Search and Save to Temp File (PRIMARY TOOL)

**USE THIS SCRIPT FOR ALL SEARCH/READ OPERATIONS**

Searches issues and saves results to a temporary markdown file. Avoids UTF-8 encoding issues.

Usage:
```bash
python search_issues.py [--project PROJECT_KEY] [--filter KEYWORD] [--jql JQL_QUERY]
```

Parameters:
- --project: Project key to search in
- --filter: Keyword filter (searches in summary and description)
- --jql: Custom JQL query for advanced searches

Output:
The script prints two lines:
- TEMP_FILE_PATH:/path/to/temp.md - Path to the generated markdown file
- ISSUE_COUNT:N - Number of issues found

Examples:
```bash
python search_issues.py --project S14P11D108
python search_issues.py --project S14P11D108 --filter "MCP"
python search_issues.py --jql "project = S14P11D108 AND issuetype = Epic"
python search_issues.py --jql "assignee = currentUser()"
```

After running, read the temporary file at TEMP_FILE_PATH to get formatted results.

---

### 2. create_issues.py - Create New Issues

Creates new JIRA issues interactively or programmatically.

Usage:
```bash
python create_issues.py --interactive
```

Interactive mode prompts for:
- Project key
- Issue summary (title)
- Issue description
- Issue type (Task/Story/Bug)
- Priority (High/Medium/Low)
- Story Points

For programmatic creation, modify the script to accept command-line arguments.

---

### 3. update_issues.py - Update Existing Issues

Updates issue status, assignee, comments, or priority.

Usage:
```bash
python update_issues.py --key ISSUE_KEY [--status STATUS] [--assign ASSIGNEE] [--comment COMMENT] [--priority PRIORITY]
```

Parameters:
- --key: Issue key (required, e.g., MCP-01)
- --status: New status (e.g., "In Progress", "Done")
- --assign: Assignee username or "me" for current user
- --comment: Add a comment to the issue
- --priority: Set priority (High/Medium/Low)

Examples:
```bash
python update_issues.py --key MCP-01 --status "In Progress"
python update_issues.py --key MCP-01 --assign me --comment "Started working on this"
python update_issues.py --key MCP-01 --priority High
```

---

### 4. read_issues.py - Read JIRA Issues (DO NOT USE - UTF-8 ISSUES)

**⚠️ DO NOT USE THIS SCRIPT - Use search_issues.py instead**

This script has UTF-8 encoding issues on Windows terminals. Always use search_issues.py.

---

### 5. list_all.py - List All Projects and Recent Issues

Lists all available projects and the 20 most recently updated issues across all projects.

Usage:
```bash
python list_all.py
```

No parameters required. Useful for getting an overview of the JIRA workspace.

---

### 6. save_issues.py - Save Project Issues to File

Saves all issues from project S14P11D108 to a text file named project_issues.txt.

Usage:
```bash
python save_issues.py
```

Output file: project_issues.txt in the current directory.

---

### 7. view_project.py - View Specific Project Issues

Displays issues for a specific project in the console.

Usage:
```bash
python view_project.py
```

Modify the script to change the target project.

---

## Common Workflow Examples

### 1. User asks: "Show me recent JIRA issues"
- Run: `python search_issues.py --project S14P11D108`
- Read the temp file at TEMP_FILE_PATH
- Present the formatted results from the markdown file

### 2. User asks: "Search for MCP issues"
- Run: `python search_issues.py --filter "MCP"`
- Read the temp file at TEMP_FILE_PATH
- Present the formatted results from the markdown file

### 3. User asks: "Create a new bug issue"
- Run: `python create_issues.py --interactive`
- Prompt user for required fields using the interactive mode

### 4. User asks: "Update MCP-01 to In Progress"
- Run: `python update_issues.py --key MCP-01 --status "In Progress"`
- Confirm the update

### 5. User asks: "Show issues assigned to me"
- Run: `python search_issues.py --jql "assignee = currentUser()"`
- Read the temp file at TEMP_FILE_PATH
- Present the formatted results from the markdown file

### 6. User asks: "Show all Epic issues"
- Run: `python search_issues.py --jql "project = S14P11D108 AND issuetype = Epic"`
- Read the temp file at TEMP_FILE_PATH
- Present the formatted results from the markdown file

### 7. User asks: "Search for WebSocket issues"
- Run: `python search_issues.py --filter "WebSocket"`
- Read the temp file at TEMP_FILE_PATH
- Present the formatted results from the markdown file

---

## Error Handling

Common errors:
- **Authentication failure**: Check JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN in config.py
- **IP not allowed**: Contact JIRA admin to whitelist the IP
- **Invalid JQL**: Ensure JQL queries are properly formatted
- **Story Points field error**: customfield_10016 may differ, check with JIRA admin
- **UTF-8 encoding error**: You're using read_issues.py - switch to search_issues.py

When errors occur, check the script output for error messages and verify the config.py settings.

---

## Quick Reference

**Default Project**: S14P11D108

**Most Common Commands**:
- List all issues: `python search_issues.py --project S14P11D108`
- Search by keyword: `python search_issues.py --filter "KEYWORD"`
- Filter by type: `python search_issues.py --jql "issuetype = Epic"`
- My issues: `python search_issues.py --jql "assignee = currentUser()"`
- Update status: `python update_issues.py --key KEY --status "STATUS"`
