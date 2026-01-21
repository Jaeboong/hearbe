#!/usr/bin/env python3
"""
JIRA 이슈 레이블 일괄 추가 스크립트
"""

import sys
from jira import JIRA
from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN

# UTF-8 인코딩 강제 설정
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def connect_jira():
    """JIRA 서버에 연결"""
    return JIRA(
        server=JIRA_URL,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )


def add_labels(jira, issue_key, labels):
    """이슈에 레이블 추가"""
    try:
        issue = jira.issue(issue_key)
        # 기존 레이블에 새 레이블 추가
        current_labels = list(issue.fields.labels)
        for label in labels:
            if label not in current_labels:
                current_labels.append(label)
        
        issue.update(fields={'labels': current_labels})
        print(f"✅ {issue_key} 레이블 추가: {', '.join(labels)}")
        
    except Exception as e:
        print(f"❌ {issue_key} 오류: {str(e)}")


def main():
    print("🔗 JIRA 연결 중...")
    jira = connect_jira()
    print("✅ 연결 성공!\n")

    # 의도 분석 (2개)
    intent_labels = ["AI", "NLU", "Intent", "LLM"]
    add_labels(jira, "S14P11D108-134", intent_labels)
    add_labels(jira, "S14P11D108-135", intent_labels + ["NER"])

    # LLM 명령 생성 (3개)
    llm_labels = ["AI", "LLM", "Command-Generation", "Prompting"]
    add_labels(jira, "S14P11D108-136", llm_labels + ["Selector", "DB"])
    add_labels(jira, "S14P11D108-137", llm_labels + ["Few-Shot", "Prompt"])
    add_labels(jira, "S14P11D108-138", llm_labels + ["Tool-Calls"])

    # 플로우 엔진 (7개)
    flow_labels = ["AI", "Flow", "Workflow"]
    add_labels(jira, "S14P11D108-139", flow_labels + ["Pydantic", "Model"])
    add_labels(jira, "S14P11D108-140", flow_labels + ["State-Machine", "Engine"])
    add_labels(jira, "S14P11D108-141", flow_labels + ["Action", "Executor"])
    add_labels(jira, "S14P11D108-142", flow_labels + ["Validation"])
    add_labels(jira, "S14P11D108-143", flow_labels + ["Coupang", "JSON"])
    add_labels(jira, "S14P11D108-144", flow_labels + ["Naver", "11st", "JSON"])
    add_labels(jira, "S14P11D108-145", flow_labels + ["Error-Handling", "Retry"])

    print(f"\n✅ 총 12개 이슈에 레이블 추가 완료!")


if __name__ == "__main__":
    main()
