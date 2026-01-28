# 좌표 기반 표 구조 복원
from typing import List, Dict, Tuple, Any, Optional


def get_box_center_y(box: List[List[float]]) -> float:
    """박스의 중심 Y좌표 계산"""
    if not box or len(box) < 2:
        return 0.0
    return (box[0][1] + box[2][1]) / 2 if len(box) >= 4 else box[0][1]


def get_box_center_x(box: List[List[float]]) -> float:
    """박스의 중심 X좌표 계산"""
    if not box or len(box) < 2:
        return 0.0
    return (box[0][0] + box[2][0]) / 2 if len(box) >= 4 else box[0][0]


def get_box_height(box: List[List[float]]) -> float:
    """박스의 높이 계산"""
    if not box or len(box) < 4:
        return 0.0
    return abs(box[2][1] - box[0][1])


def cluster_by_y_coordinate(
    texts: List[str],
    boxes: List[List[List[float]]],
    scores: List[float]
) -> List[List[Dict[str, Any]]]:
    """
    Y좌표 기반으로 행(Row) 클러스터링
    글자 높이의 0.6배를 기준으로 같은 행으로 묶음
    """
    if not texts or not boxes:
        return []

    # 텍스트, 박스, 스코어를 하나의 객체로 묶기
    items = []
    for i, (text, box, score) in enumerate(zip(texts, boxes, scores)):
        if not box:
            continue
        items.append({
            "text": text,
            "box": box,
            "score": score,
            "center_y": get_box_center_y(box),
            "center_x": get_box_center_x(box),
            "height": get_box_height(box),
            "index": i
        })

    if not items:
        return []

    # 평균 높이 계산
    avg_height = sum(item["height"] for item in items) / len(items)
    y_threshold = avg_height * 0.6  # 글자 높이의 0.6배

    # Y좌표로 정렬
    items.sort(key=lambda x: x["center_y"])

    # 클러스터링
    rows = []
    current_row = [items[0]]

    for item in items[1:]:
        # 현재 행의 평균 Y좌표
        current_row_y = sum(it["center_y"] for it in current_row) / len(current_row)

        # Y좌표 차이가 threshold 이내면 같은 행
        if abs(item["center_y"] - current_row_y) <= y_threshold:
            current_row.append(item)
        else:
            # 새로운 행 시작
            rows.append(current_row)
            current_row = [item]

    # 마지막 행 추가
    if current_row:
        rows.append(current_row)

    # 각 행 내에서 X좌표로 정렬
    for row in rows:
        row.sort(key=lambda x: x["center_x"])

    return rows


def find_size_table_region(rows: List[List[Dict[str, Any]]]) -> Optional[Tuple[int, int]]:
    """
    SIZE 표 영역 찾기
    SIZE 키워드가 있는 행부터 시작해서, 연속된 표 영역을 감지
    """
    size_row_index = None

    # SIZE 키워드가 있는 행 찾기
    for i, row in enumerate(rows):
        for item in row:
            if "SIZE" in item["text"].upper():
                size_row_index = i
                break
        if size_row_index is not None:
            break

    if size_row_index is None:
        return None

    # SIZE 다음 행부터 헤더와 데이터 행 찾기
    # 헤더는 보통 "허리", "엉덩이" 같은 키워드
    header_keywords = ["허리", "엉덩이", "왓밀위", "뜻밀위", "허벅지", "밀단", "총장", "I라우"]
    size_labels = ["M", "L", "XL", "2XL", "3XL", "FREE", "F", "7", "7X"]  # 7X는 XL 오타

    start_index = size_row_index
    end_index = size_row_index

    # 헤더 행과 데이터 행을 모두 포함하도록 영역 확장
    for i in range(size_row_index, len(rows)):
        row = rows[i]
        row_texts = [item["text"] for item in row]

        # 헤더나 사이즈 라벨이 있으면 표 영역으로 포함
        has_header = any(keyword in " ".join(row_texts) for keyword in header_keywords)
        has_size_label = any(label == item["text"].strip().upper() for item in row for label in size_labels)
        has_numbers = any(item["text"].replace(".", "").replace(",", "").isdigit() for item in row)

        if has_header or has_size_label or (has_numbers and i > size_row_index):
            end_index = i
        elif i > size_row_index + 1 and not has_header and not has_size_label and not has_numbers:
            # 표와 관련 없는 행이 나오면 종료
            break

    return (start_index, end_index + 1)


def format_table_as_text(rows: List[List[Dict[str, Any]]]) -> str:
    """
    표 구조를 텍스트로 변환
    """
    lines = []
    for row in rows:
        row_text = " | ".join(item["text"] for item in row)
        lines.append(row_text)
    return "\n".join(lines)


def reconstruct_size_table(
    texts: List[str],
    boxes: List[List[List[float]]],
    scores: List[float]
) -> Optional[str]:
    """
    SIZE 표를 좌표 기반으로 재구성
    반환: 구조화된 표 텍스트 (행별로 | 구분)
    """
    # 1. Y좌표 기반 행 클러스터링
    rows = cluster_by_y_coordinate(texts, boxes, scores)

    if not rows:
        return None

    # 2. SIZE 표 영역 찾기
    table_region = find_size_table_region(rows)

    if table_region is None:
        return None

    start_idx, end_idx = table_region
    table_rows = rows[start_idx:end_idx]

    # 3. 표를 텍스트로 변환
    table_text = format_table_as_text(table_rows)

    return table_text


def parse_size_table_to_dict(table_text: str) -> Dict[str, Any]:
    """
    구조화된 표 텍스트를 파싱해서 딕셔너리로 변환
    """
    lines = table_text.strip().split("\n")

    if not lines:
        return {}

    # 헤더 찾기 (허리, 엉덩이 등이 포함된 행)
    header_keywords = ["허리", "엉덩이", "왓밀위", "뜻밀위", "허벅지", "밀단", "총장"]
    header_line = None
    header_index = 0

    for i, line in enumerate(lines):
        if any(kw in line for kw in header_keywords):
            header_line = line
            header_index = i
            break

    if header_line is None:
        return {}

    # 헤더 파싱
    headers = [h.strip() for h in header_line.split("|")]

    # 사이즈 라벨 (M, L, XL 등)
    size_labels = ["M", "L", "XL", "2XL", "3XL", "FREE", "F"]

    sizes = {}

    # 헤더 다음 행부터 데이터 행 파싱
    for line in lines[header_index + 1:]:
        parts = [p.strip() for p in line.split("|")]

        # 첫 번째 항목이 사이즈 라벨인지 확인
        if not parts or parts[0].upper() not in size_labels:
            continue

        size_label = parts[0].upper()
        values = parts[1:]

        # 헤더와 값 매핑
        size_data = {}
        for i, value in enumerate(values):
            if i < len(headers) - 1:  # 첫 번째 헤더는 보통 SIZE
                header_name = headers[i + 1] if i + 1 < len(headers) else f"col_{i}"
                size_data[header_name] = value

        sizes[size_label] = size_data

    return {"headers": headers, "sizes": sizes}
