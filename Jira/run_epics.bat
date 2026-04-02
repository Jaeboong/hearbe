@echo off
"C:\Users\SSAFY\AppData\Local\Programs\Python\Python314\python.exe" search_issues.py --jql "project = S14P11D108 AND issuetype = Epic" > epics_list.txt 2>&1
