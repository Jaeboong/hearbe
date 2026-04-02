#!/usr/bin/env python3
"""
단일 스크립트:
- Git log 전용 보고서(md)
- Jira 전용 보고서(md)
- 통합 보고서(md)
총 3개 markdown 파일을 생성한다.

토큰 기준:
- Git: git log --author=<token>
- Jira: jira.search_users(query=<token>)
"""

import argparse
import datetime as dt
import re
import subprocess
import sys
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from jira import JIRA

from config import JIRA_API_TOKEN, JIRA_EMAIL, JIRA_TIMEOUT, JIRA_URL, PROJECT_KEY


if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


ISSUE_KEY_PATTERN = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b", re.IGNORECASE)
JIRA_BROWSE_BASE = JIRA_URL.rstrip("/")


def _run_git(cmd: List[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        stderr = result.stderr.strip() or "unknown git error"
        raise RuntimeError(f"git 명령 실행 실패: {stderr}")
    return result.stdout


def _format_cmd(cmd: List[str]) -> str:
    parts = []
    for part in cmd:
        if " " in part:
            parts.append(f'"{part}"')
        else:
            parts.append(part)
    return " ".join(parts)


def _base_git_log_cmd(
    author_token: str,
    since: Optional[str],
    until: Optional[str],
    max_commits: int,
    include_merges: bool,
) -> List[str]:
    cmd = [
        "git",
        "log",
        "--all",
        f"--max-count={max_commits}",
        f"--author={author_token}",
        "--date=short",
    ]
    if since:
        cmd.append(f"--since={since}")
    if until:
        cmd.append(f"--until={until}")
    if not include_merges:
        cmd.append("--no-merges")
    return cmd


def _get_commit_files(commit_hash: str) -> List[str]:
    out = _run_git(["git", "show", "--name-only", "--pretty=format:", commit_hash])
    files = []
    seen = set()
    for line in out.splitlines():
        path = line.strip()
        if not path:
            continue
        if path not in seen:
            seen.add(path)
            files.append(path)
    return files


def _extract_issue_keys(text: str) -> List[str]:
    keys = []
    seen = set()
    for match in ISSUE_KEY_PATTERN.findall(text or ""):
        key = match.upper()
        if key not in seen:
            seen.add(key)
            keys.append(key)
    return keys


def run_git_log(
    author_token: str,
    since: Optional[str],
    until: Optional[str],
    max_commits: int,
    include_merges: bool,
) -> List[Dict[str, object]]:
    fmt = "%H%x1f%an%x1f%ae%x1f%ad%x1f%s%x1f%b%x1e"
    cmd = _base_git_log_cmd(author_token, since, until, max_commits, include_merges)
    cmd.append(f"--pretty=format:{fmt}")
    out = _run_git(cmd)

    commits: List[Dict[str, object]] = []
    for raw in out.strip("\n\x1e").split("\x1e"):
        if not raw.strip():
            continue
        fields = raw.split("\x1f")
        if len(fields) < 6:
            continue
        commit_hash, author_name, author_email, commit_date, subject, body = fields[:6]
        commit_hash = commit_hash.strip()
        subject = subject.strip()
        body = body.strip()
        message = f"{subject}\n{body}".strip()
        commits.append(
            {
                "hash": commit_hash,
                "author_name": author_name.strip(),
                "author_email": author_email.strip(),
                "date": commit_date.strip(),
                "subject": subject,
                "issue_keys": _extract_issue_keys(message),
                "files": _get_commit_files(commit_hash),
            }
        )
    return commits


def connect_jira() -> JIRA:
    return JIRA(
        server=JIRA_URL,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        timeout=JIRA_TIMEOUT,
        max_retries=1,
    )


def _normalize(value: str) -> str:
    return (value or "").strip().lower()


def find_best_jira_user(jira: JIRA, token: str) -> Optional[object]:
    try:
        candidates = jira.search_users(query=token, maxResults=20)
    except Exception:
        return None
    if not candidates:
        return None

    token_norm = _normalize(token)

    def score_user(user) -> Tuple[int, int]:
        display = _normalize(getattr(user, "displayName", ""))
        email = _normalize(getattr(user, "emailAddress", ""))
        account_id = _normalize(getattr(user, "accountId", ""))
        score = 0
        for value in (display, email, account_id):
            if value == token_norm:
                score += 100
            elif value.startswith(token_norm):
                score += 60
            elif token_norm in value:
                score += 30
        return score, -len(display or account_id or email)

    candidates = sorted(candidates, key=score_user, reverse=True)
    best = candidates[0]
    return best if score_user(best)[0] > 0 else None


def fetch_assignee_issues(jira: JIRA, account_id: str, project_key: str, max_issues: int) -> List[object]:
    if not account_id:
        return []
    jql = f'project = {project_key} AND assignee = "{account_id}" ORDER BY updated DESC'
    return jira.search_issues(jql, maxResults=max_issues)


def fetch_issues_by_keys(jira: JIRA, issue_keys: List[str], project_key: str) -> Dict[str, object]:
    issues_by_key = {}
    if not issue_keys:
        return issues_by_key
    chunk_size = 50
    for idx in range(0, len(issue_keys), chunk_size):
        chunk = issue_keys[idx : idx + chunk_size]
        jql = f"key in ({','.join(chunk)})"
        if project_key:
            jql += f" AND project = {project_key}"
        issues = jira.search_issues(jql, maxResults=len(chunk))
        for issue in issues:
            issues_by_key[issue.key] = issue
    return issues_by_key


def _story_points(issue: object) -> Optional[float]:
    value = getattr(issue.fields, "customfield_10016", None)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _issue_link(issue_key: str) -> str:
    return f"{JIRA_BROWSE_BASE}/browse/{issue_key}"


def _collect_file_stats(commits: List[Dict[str, object]]) -> List[Tuple[str, int]]:
    counter = Counter()
    for commit in commits:
        for path in commit["files"]:
            counter[path] += 1
    return counter.most_common()


def _build_git_report_md(
    token: str,
    commits: List[Dict[str, object]],
    since: Optional[str],
    until: Optional[str],
    max_commits: int,
    include_merges: bool,
    execution_dir: str,
) -> str:
    file_stats = _collect_file_stats(commits)
    issue_commit_count = len([c for c in commits if c["issue_keys"]])

    lines = []
    lines.append("# Git Log 전용 작업 보고서")
    lines.append("")
    lines.append(f"- 생성시각: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 작업자 토큰: `{token}`")
    lines.append("- 토큰 기준: `git log --author=<token>`")
    lines.append(f"- 조회 옵션: `since={since or '-'}, until={until or '-'}, max_commits={max_commits}`")
    lines.append("")
    lines.append("## 수집 근거 (명령어/필터/위치)")
    lines.append(f"- 실행 위치: `{execution_dir}`")
    cmd = _base_git_log_cmd(token, since, until, max_commits, include_merges) + ["--pretty=format:%H|%an|%ae|%ad|%s|%b"]
    lines.append(f"- Git 수집 명령어: `{_format_cmd(cmd)}`")
    lines.append("- 적용 필터:")
    lines.append(f"  - author filter: `{token}`")
    lines.append(f"  - date filter: `since={since or '-'}, until={until or '-'}`")
    lines.append(f"  - merges: `{'include' if include_merges else 'exclude'}`")
    lines.append("")
    lines.append("## 요약")
    lines.append(f"- 커밋 수: {len(commits)}")
    lines.append(f"- 이슈 키 포함 커밋: {issue_commit_count}")
    lines.append(f"- 수정 파일 종류: {len(file_stats)}")
    lines.append("")

    lines.append("## 수정 파일 TOP 30")
    if file_stats:
        for path, count in file_stats[:30]:
            lines.append(f"- `{path}` ({count} commits)")
    else:
        lines.append("- 없음")
    lines.append("")

    lines.append("## 커밋 상세 (최근 50개)")
    if commits:
        for commit in commits[:50]:
            keys = ", ".join(commit["issue_keys"]) if commit["issue_keys"] else "-"
            lines.append(f"- {commit['date']} `{commit['hash']}` [{keys}] {commit['subject']}")
            files = commit["files"][:10]
            lines.append(f"  - files: {', '.join(files) if files else '-'}")
    else:
        lines.append("- 조회된 커밋 없음")
    lines.append("")

    return "\n".join(lines)


def _build_jira_report_md(
    token: str,
    project_key: str,
    matched_user: Optional[object],
    assignee_issues: List[object],
    jira_error: Optional[str],
    max_issues: int,
    execution_dir: str,
) -> str:
    lines = []
    lines.append("# Jira 전용 작업 보고서")
    lines.append("")
    lines.append(f"- 생성시각: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 작업자 토큰: `{token}`")
    lines.append("- 토큰 기준: `jira.search_users(query=<token>)`")
    lines.append(f"- 프로젝트: `{project_key}`")
    lines.append(f"- 최대 이슈 조회수: {max_issues}")
    lines.append("")
    lines.append("## 수집 근거 (명령어/필터/위치)")
    lines.append(f"- 실행 위치: `{execution_dir}`")
    lines.append("- Jira API 호출:")
    lines.append(f"  - `search_users(query=\"{token}\", maxResults=20)`")
    if matched_user:
        account_id = getattr(matched_user, "accountId", "")
        lines.append(
            f"  - `search_issues(\"project = {project_key} AND assignee = \\\"{account_id}\\\" ORDER BY updated DESC\", maxResults={max_issues})`"
        )
    else:
        lines.append(f"  - `search_issues(\"project = {project_key} AND assignee = \\\"<accountId>\\\" ORDER BY updated DESC\")`")
    lines.append("")

    if jira_error:
        lines.append("## Jira 연결 상태")
        lines.append(f"- 실패: `{jira_error}`")
        lines.append("")
        return "\n".join(lines)

    lines.append("## 사용자 매칭")
    if not matched_user:
        lines.append("- 매칭 실패")
        lines.append("")
        lines.append("## 이슈 목록")
        lines.append("- 없음")
        lines.append("")
        return "\n".join(lines)

    lines.append(f"- displayName: {matched_user.displayName}")
    lines.append(f"- accountId: {getattr(matched_user, 'accountId', '-')}")
    lines.append("")
    lines.append("## 이슈 목록")
    if not assignee_issues:
        lines.append("- 없음")
        lines.append("")
        return "\n".join(lines)

    for idx, issue in enumerate(assignee_issues, start=1):
        assignee = issue.fields.assignee.displayName if issue.fields.assignee else "미할당"
        updated = (getattr(issue.fields, "updated", "") or "-")[:10]
        points = _story_points(issue)
        points_text = f"{points:g}" if points is not None else "-"
        lines.append(f"{idx}. [{issue.key}]({_issue_link(issue.key)}) {issue.fields.summary}")
        lines.append(
            f"   - 상태: {issue.fields.status.name} | 담당자: {assignee} | 유형: {issue.fields.issuetype.name} | Story Points: {points_text} | 업데이트: {updated}"
        )
    lines.append("")
    return "\n".join(lines)


def _build_combined_report_md(
    token: str,
    project_key: str,
    commits: List[Dict[str, object]],
    issues_by_key: Dict[str, object],
    matched_user: Optional[object],
    assignee_issues: List[object],
    jira_error: Optional[str],
    since: Optional[str],
    until: Optional[str],
    max_commits: int,
    max_issues: int,
    include_merges: bool,
    execution_dir: str,
) -> str:
    file_stats = _collect_file_stats(commits)
    ordered_keys = OrderedDict()
    for commit in commits:
        for key in commit["issue_keys"]:
            ordered_keys[key] = None
    commit_issue_keys = list(ordered_keys.keys())
    commit_issue_sp = 0.0
    commit_issue_sp_count = 0
    for key in commit_issue_keys:
        issue = issues_by_key.get(key)
        if issue:
            sp = _story_points(issue)
            if sp is not None:
                commit_issue_sp += sp
                commit_issue_sp_count += 1

    assignee_sp = 0.0
    assignee_sp_count = 0
    for issue in assignee_issues:
        sp = _story_points(issue)
        if sp is not None:
            assignee_sp += sp
            assignee_sp_count += 1

    lines = []
    lines.append("# 통합 작업 보고서 (Git + Jira)")
    lines.append("")
    lines.append(f"- 생성시각: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 작업자 토큰: `{token}`")
    lines.append(f"- 프로젝트: `{project_key}`")
    lines.append("")
    lines.append("## 수집 근거 (명령어/필터/위치)")
    lines.append(f"- 실행 위치: `{execution_dir}`")
    git_cmd = _base_git_log_cmd(token, since, until, max_commits, include_merges) + ["--pretty=format:%H|%an|%ae|%ad|%s|%b"]
    lines.append(f"- Git 명령어: `{_format_cmd(git_cmd)}`")
    lines.append("- Jira API/JQL:")
    lines.append(f"  - `search_users(query=\"{token}\", maxResults=20)`")
    lines.append(f"  - `search_issues(\"project = {project_key} AND assignee = \\\"<accountId>\\\" ORDER BY updated DESC\", maxResults={max_issues})`")
    lines.append("  - `search_issues(\"key in (<ISSUE_KEYS>) AND project = <PROJECT>\")`")
    lines.append("- 필터:")
    lines.append(f"  - author token: `{token}`")
    lines.append(f"  - 기간: `since={since or '-'}, until={until or '-'}`")
    lines.append(f"  - merges: `{'include' if include_merges else 'exclude'}`")
    lines.append("")
    lines.append("## 요약")
    lines.append(f"- Git 커밋 수: {len(commits)}")
    lines.append(f"- Git 수정 파일 종류: {len(file_stats)}")
    lines.append(f"- 커밋 메시지에서 추출한 Jira 키 수: {len(commit_issue_keys)}")
    lines.append(f"- assignee Jira 이슈 수: {len(assignee_issues)}")
    lines.append(f"- 커밋 키 매핑 이슈 Story Points 합계: {commit_issue_sp:g} (확인된 이슈 {commit_issue_sp_count}개)")
    lines.append(f"- assignee 이슈 Story Points 합계: {assignee_sp:g} (확인된 이슈 {assignee_sp_count}개)")
    if jira_error:
        lines.append(f"- Jira 연결: 실패 (`{jira_error}`)")
    elif matched_user:
        lines.append(f"- Jira 사용자 매칭: {matched_user.displayName} ({getattr(matched_user, 'accountId', '-')})")
    else:
        lines.append("- Jira 사용자 매칭: 실패")
    lines.append("")

    lines.append("## Git 수정 파일 TOP 20")
    if file_stats:
        for path, count in file_stats[:20]:
            lines.append(f"- `{path}` ({count} commits)")
    else:
        lines.append("- 없음")
    lines.append("")

    lines.append("## 최근 커밋 해시 (근거)")
    if commits:
        for commit in commits[:30]:
            lines.append(f"- `{commit['hash']}` | {commit['date']} | {commit['subject']}")
    else:
        lines.append("- 없음")
    lines.append("")

    lines.append("## 커밋 키 기반 Jira 매핑")
    if commit_issue_keys:
        for idx, key in enumerate(commit_issue_keys, start=1):
            linked = [c for c in commits if key in c["issue_keys"]]
            linked_count = len(linked)
            last_date = linked[0]["date"] if linked else "-"
            issue = issues_by_key.get(key)
            if not issue:
                lines.append(f"{idx}. [{key}]({_issue_link(key)}) Jira 조회 실패/프로젝트 불일치")
                lines.append(f"   - 연결 커밋: {linked_count}개, 마지막 커밋일: {last_date}")
                continue
            assignee = issue.fields.assignee.displayName if issue.fields.assignee else "미할당"
            points = _story_points(issue)
            points_text = f"{points:g}" if points is not None else "-"
            lines.append(f"{idx}. [{issue.key}]({_issue_link(issue.key)}) {issue.fields.summary}")
            lines.append(
                f"   - 상태: {issue.fields.status.name} | 담당자: {assignee} | 유형: {issue.fields.issuetype.name} | Story Points: {points_text} | 연결 커밋: {linked_count}개 | 마지막 커밋일: {last_date}"
            )
    else:
        lines.append("- 커밋 메시지에서 Jira 키를 찾지 못함")
    lines.append("")

    lines.append("## assignee 기준 Jira 이슈")
    if assignee_issues:
        for idx, issue in enumerate(assignee_issues, start=1):
            assignee = issue.fields.assignee.displayName if issue.fields.assignee else "미할당"
            points = _story_points(issue)
            points_text = f"{points:g}" if points is not None else "-"
            lines.append(f"{idx}. [{issue.key}]({_issue_link(issue.key)}) {issue.fields.summary}")
            lines.append(f"   - 상태: {issue.fields.status.name} | 담당자: {assignee} | 유형: {issue.fields.issuetype.name} | Story Points: {points_text}")
    else:
        lines.append("- 없음")
    lines.append("")

    lines.append("## 회고 문항 (PMI / 4Ls / Insight)")
    lines.append("### PMI")
    lines.append("1. Plus: 이번 기간에 가장 효과적이었던 작업 방식/결정은 무엇이었나?")
    lines.append("2. Minus: 반복되거나 비용이 컸던 병목(코드/협업/환경)은 무엇이었나?")
    lines.append("3. Interesting: 예상과 다르게 성과가 좋았거나 나빴던 실험은 무엇이었나?")
    lines.append("")
    lines.append("### 4Ls")
    lines.append("1. Liked: 만족스러웠던 협업/구현 포인트는 무엇인가?")
    lines.append("2. Learned: 이번 스프린트에서 새로 학습한 기술/도메인은 무엇인가?")
    lines.append("3. Lacked: 부족했던 정보/리소스/자동화는 무엇인가?")
    lines.append("4. Longed for: 다음 스프린트에서 꼭 개선하고 싶은 점은 무엇인가?")
    lines.append("")
    lines.append("### Insight")
    lines.append("1. 데이터 기반 인사이트: 커밋 빈도, 파일 집중도, 이슈 상태에서 보이는 패턴은?")
    lines.append("2. 실행 인사이트: 다음 스프린트에 유지할 것 1개/중단할 것 1개/새로 도입할 것 1개는?")
    lines.append("3. 리스크 인사이트: 일정/품질/협업 관점의 잠재 리스크와 선제 대응은?")
    lines.append("")
    lines.append("### 졸업 프로젝트 마무리 3문항")
    lines.append("1. 우리가 만든 결과물 중 '지속 운영 가능'한 부분과 '데모용'인 부분은 무엇인가?")
    lines.append("2. 6주를 다시 한다면 1주차에 반드시 바꿀 의사결정 1개는 무엇인가?")
    lines.append("3. 각자 포트폴리오에 넣을 대표 기여 1개와 근거(커밋 해시/Jira 이슈)는 무엇인가?")
    lines.append("")

    return "\n".join(lines)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="작업자 회고 보고서 생성 (md 3개)")
    parser.add_argument("author_token", help="작업자 토큰 (이름/이메일/아이디 일부)")
    parser.add_argument("--project", default=PROJECT_KEY, help=f"Jira 프로젝트 키 (기본값: {PROJECT_KEY})")
    parser.add_argument("--since", default=None, help="git log 시작일 (예: 2026-01-01)")
    parser.add_argument("--until", default=None, help="git log 종료일 (예: 2026-02-11)")
    parser.add_argument("--max-commits", type=int, default=500, help="최대 커밋 조회 수")
    parser.add_argument("--max-issues", type=int, default=100, help="Jira 이슈 최대 조회 수")
    parser.add_argument("--include-merges", action="store_true", help="merge 커밋 포함")
    parser.add_argument("--out-dir", default="reports", help="보고서 출력 폴더 (기본: reports)")
    parser.add_argument("--out-prefix", default="from_git_and_jira", help="보고서 파일명 prefix")
    return parser.parse_args()


def main():
    args = parse_args()
    commits = run_git_log(
        author_token=args.author_token,
        since=args.since,
        until=args.until,
        max_commits=args.max_commits,
        include_merges=args.include_merges,
    )

    jira_error = None
    matched_user = None
    assignee_issues = []
    issues_by_key = {}

    ordered_keys = OrderedDict()
    for commit in commits:
        for key in commit["issue_keys"]:
            ordered_keys[key] = None
    commit_issue_keys = list(ordered_keys.keys())

    try:
        jira = connect_jira()
        matched_user = find_best_jira_user(jira, args.author_token)
        if matched_user:
            assignee_issues = fetch_assignee_issues(
                jira=jira,
                account_id=getattr(matched_user, "accountId", ""),
                project_key=args.project,
                max_issues=args.max_issues,
            )
        if commit_issue_keys:
            issues_by_key = fetch_issues_by_keys(jira, commit_issue_keys, args.project)
    except Exception as exc:
        jira_error = str(exc)

    git_md = _build_git_report_md(
        token=args.author_token,
        commits=commits,
        since=args.since,
        until=args.until,
        max_commits=args.max_commits,
        include_merges=args.include_merges,
        execution_dir=str(Path.cwd()),
    )
    jira_md = _build_jira_report_md(
        token=args.author_token,
        project_key=args.project,
        matched_user=matched_user,
        assignee_issues=assignee_issues,
        jira_error=jira_error,
        max_issues=args.max_issues,
        execution_dir=str(Path.cwd()),
    )
    combined_md = _build_combined_report_md(
        token=args.author_token,
        project_key=args.project,
        commits=commits,
        issues_by_key=issues_by_key,
        matched_user=matched_user,
        assignee_issues=assignee_issues,
        jira_error=jira_error,
        since=args.since,
        until=args.until,
        max_commits=args.max_commits,
        max_issues=args.max_issues,
        include_merges=args.include_merges,
        execution_dir=str(Path.cwd()),
    )

    base_dir = Path(__file__).resolve().parent / args.out_dir
    prefix = args.out_prefix.strip() or "from_git_and_jira"
    git_path = base_dir / f"{prefix}_git_log.md"
    jira_path = base_dir / f"{prefix}_jira.md"
    combined_path = base_dir / f"{prefix}_integrated.md"
    _write_text(git_path, git_md)
    _write_text(jira_path, jira_md)
    _write_text(combined_path, combined_md)

    print("보고서 생성 완료:")
    print(f"- {git_path}")
    print(f"- {jira_path}")
    print(f"- {combined_path}")


if __name__ == "__main__":
    main()
