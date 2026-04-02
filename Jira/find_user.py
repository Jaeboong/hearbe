from jira import JIRA
from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN

jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))
users = jira.search_users(user="서해령")
for user in users:
    print(f"User: {user.displayName}, AccountID: {user.accountId}, Email: {user.emailAddress}")
