"""
JIRA 설정 파일

환경 변수(.env 파일)에서 JIRA 연결 정보를 읽어옵니다.
.env 파일이 없으면 .env.example을 복사해서 만드세요.
"""

import os
from pathlib import Path

# .env 파일 로드
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print("Warning: python-dotenv not installed. Run: pip install python-dotenv")

# JIRA 연결 정보 (환경 변수에서 로드)
JIRA_URL = os.environ.get("JIRA_URL", "https://ssafy.atlassian.net")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.environ.get("JIRA_API_TOKEN", "")
PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY", "S14P11D108")

# 기본 프로젝트 키
DEFAULT_PROJECT_KEY = "MCP"

# 타임아웃 (초)
JIRA_TIMEOUT = 10
