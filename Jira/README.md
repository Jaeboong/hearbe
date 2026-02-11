# JIRA CLI 도구

JIRA API를 사용하여 이슈를 조회, 생성, 수정하는 Python 스크립트 모음입니다.

사용자는 LLM에게 "JIRA 최근 이슈 알려줘"와 같이 요청하면, LLM이 이 도구를 사용하여 결과를 제공합니다.

---

## 사용자 가이드

### 설정

`config.py` 파일에 JIRA 정보를 입력하세요:

```python
JIRA_URL = "https://your-company.atlassian.net"
JIRA_EMAIL = "your-email@example.com"
JIRA_API_TOKEN = "your-api-token-here"
PROJECT_KEY = "S14P11D108"
```

Python 설치 필수!!

API 토큰 생성: https://id.atlassian.com/manage-profile/security/api-tokens

### LLM에게 요청하는 방법

다음과 같이 자연어로 요청하세요:

- "JIRA 최근 이슈 10개 알려줘"
- "MCP 프로젝트의 진행 중인 이슈 보여줘"
- "나에게 할당된 이슈 목록 확인해줘"
- "AI 관련 이슈만 검색해줘"
- "새로운 Task 이슈 만들어줘"
- "MCP-01 이슈 상태를 In Progress로 변경해줘"

LLM이 적절한 스크립트를 실행하여 결과를 제공합니다.

### LLM 사용 전 필수 설정

JIRA 도구를 사용하기 전에 LLM에게 다음 프롬프트를 먼저 제공하세요:

```
c:\ssafy\공통\Jira\LLM_GUIDE.md 파일을 읽고 JIRA 도구 사용법을 숙지해줘.
```

이후 자유롭게 JIRA 관련 요청을 하면 됩니다.

---

## 작업자 회고용 스크립트

`list_user_work_from_git.py` 1개만 사용합니다.

실행 시 markdown 결과물 3개를 생성합니다.

```bash
python list_user_work_from_git.py "김재환"
python list_user_work_from_git.py "cbkjh0225@gmail.com" --since "2026-01-01"
python list_user_work_from_git.py "서해령" --max-commits 300
```

- 첫 번째 파라미터(토큰): `이름`, `이메일`, `아이디 일부` 가능
- 토큰 매칭 기준:
  - Git: `git log --author=<토큰>`
  - Jira: `jira.search_users(query=<토큰>)`
- 생성 파일(기본: `Jira/reports/`):
  - `from_git_and_jira_git_log.md` (git log 전용)
  - `from_git_and_jira_jira.md` (jira 전용)
  - `from_git_and_jira_integrated.md` (통합)
- 주요 옵션:
  - `--since`, `--until`: 기간 제한
  - `--max-commits`: git 조회 커밋 수 제한
  - `--max-issues`: jira 조회 이슈 수 제한
  - `--out-dir`: 결과 md 출력 폴더 변경
  - `--out-prefix`: 결과 md 파일명 prefix (기본: `from_git_and_jira`)

추가 반영 사항:
- 각 md에 `수집 근거` 섹션 포함 (실행 위치, 명령어/필터, Jira API/JQL).
- 커밋 상세에 full commit hash 표기.
- Jira 이슈 키는 browse 링크 포함.
- 통합 md에 Story Points 합계/이슈별 Story Points 포함.
- 통합 md 마지막에 PMI/4Ls/Insight 회고 문항 포함.
