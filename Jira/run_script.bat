@echo off
echo START > debug_bat.txt
"C:\Users\SSAFY\AppData\Local\Programs\Python\Python314\python.exe" create_sprint23_issues.py > python_out.txt 2>&1
echo END >> debug_bat.txt
