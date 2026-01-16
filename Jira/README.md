# JIRA CLI 도구

JIRA API를 사용하여 이슈를 읽고, 생성하고, 수정하는 Python 스크립트 모음입니다.

## 📋 목차

- [설치](#설치)
- [설정](#설정)
- [사용법](#사용법)
  - [이슈 읽기](#이슈-읽기)
  - [이슈 생성](#이슈-생성)
  - [이슈 수정](#이슈-수정)
- [파일 구조](#파일-구조)
- [문제 해결](#문제-해결)

---

## 🚀 설치

### 1. Python 라이브러리 설치

```bash
pip install jira
```

### 2. API 토큰 생성

1. https://id.atlassian.com/manage-profile/security/api-tokens 접속
2. "Create API token" 클릭
3. 토큰 이름 입력 (예: "JIRA CLI")
4. 생성된 토큰 복사

---

## ⚙️ 설정

`config.py` 파일을 열어서 JIRA 정보를 입력하세요:

```python
JIRA_URL = "https://your-company.atlassian.net"
JIRA_EMAIL = "your-email@example.com"
JIRA_API_TOKEN = "your-api-token-here"
DEFAULT_PROJECT_KEY = "MCP"  # 기본 프로젝트
```

---

## 📖 사용법

### 이슈 읽기 (`read_issues.py`)

**최근 이슈 10개 조회:**
```bash
python read_issues.py
```

**특정 프로젝트 이슈 조회:**
```bash
python read_issues.py --project MCP
python read_issues.py --project AI
```

**특정 이슈 상세 조회:**
```bash
python read_issues.py --key MCP-01
```

**나에게 할당된 이슈 조회:**
```bash
python read_issues.py --assignee currentUser()
```

**조회 개수 지정:**
```bash
python read_issues.py --project MCP --max 20
```

---

### 이슈 생성 (`create_issues.py`)

**대화형 모드 (추천):**
```bash
python create_issues.py --interactive
```

프롬프트에 따라 입력:
- 프로젝트 키 (예: MCP)
- 이슈 제목
- 이슈 설명
- 이슈 유형 (Task/Story/Bug)
- 우선순위 (High/Medium/Low)
- Story Points

**파일에서 생성 (TODO):**
```bash
python create_issues.py --file ../MCP/docs/JIRA_ISSUES.md
```

---

### 이슈 수정 (`update_issues.py`)

**상태 변경:**
```bash
python update_issues.py --key MCP-01 --status "In Progress"
python update_issues.py --key MCP-01 --status "Done"
```

**담당자 할당:**
```bash
python update_issues.py --key MCP-01 --assign "김재환"
python update_issues.py --key MCP-01 --assign me
```

**코멘트 추가:**
```bash
python update_issues.py --key MCP-01 --comment "작업 진행 중입니다"
```

**우선순위 변경:**
```bash
python update_issues.py --key MCP-01 --priority High
```

**다중 업데이트:**
```bash
python update_issues.py --key MCP-01 --status "In Progress" --assign me --comment "작업 시작"
```

---

## 📁 파일 구조

```
Jira/
├── config.py           # JIRA 연결 설정
├── read_issues.py      # 이슈 읽기 스크립트
├── create_issues.py    # 이슈 생성 스크립트
├── update_issues.py    # 이슈 수정 스크립트
└── README.md          # 이 파일
```

---

## 🔧 문제 해결

### "IP가 허용되지 않음" 오류

JIRA 보안 설정에서 IP 제한이 설정된 경우입니다.
- JIRA 관리자에게 문의하여 IP를 화이트리스트에 추가하세요.

### "무제한 JQL 쿼리" 오류

JQL 쿼리에 `maxResults` 제한을 추가하세요.
- 모든 스크립트는 이미 제한을 포함하고 있습니다.

### "Story Points 설정 실패"

Story Points 필드 ID가 다를 수 있습니다.
- `customfield_10016`을 다른 값으로 변경해보세요.
- JIRA 관리자에게 Story Points 필드 ID를 확인하세요.

### 인증 실패

- API 토큰이 올바른지 확인하세요.
- 이메일 주소가 JIRA 계정과 일치하는지 확인하세요.
- JIRA URL이 정확한지 확인하세요 (https 포함, 마지막 / 제외).

---

## 💡 팁

1. **JQL (JIRA Query Language) 활용**
   - `read_issues.py`를 수정하여 복잡한 JQL 쿼리 사용 가능
   - 예: `project = MCP AND status = "In Progress" AND assignee = currentUser()`

2. **일괄 작업**
   - 여러 이슈를 한 번에 처리하려면 스크립트 수정
   - 예: CSV 파일에서 읽어서 일괄 생성

3. **자동화**
   - cron job 또는 Task Scheduler와 결합하여 자동화 가능
   - 예: 매일 아침 나에게 할당된 이슈 목록 이메일 발송

---

**작성일**: 2026-01-16  
**버전**: 1.0
