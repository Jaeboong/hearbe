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


def get_box_width(box: List[List[float]]) -> float:
    """박스의 너비 계산"""
    if not box or len(box) < 4:
        return 0.0
    return abs(box[2][0] - box[0][0])


# ============================================
# OCR 텍스트 교정 룰
# ============================================

# 헤더 오인식 교정 맵
HEADER_CORRECTION_MAP = {
    # 허리 오인식
    "I라우": "허리",
    "1라우": "허리",
    "라우": "허리",
    "허리단": "허리",
    # 엉덩이 오인식
    "10": "엉덩이",
    "엉덩0": "엉덩이",
    # 앞밑위 오인식
    "|": "앞밑위",
    "왓밀위": "앞밑위",
    "앞밀위": "앞밑위",
    # 뒷밑위 오인식
    "뜻밀위": "뒷밑위",
    "뒤밀위": "뒷밑위",
    "딧밀위": "뒷밑위",
    # 밑단 오인식
    "밀단": "밑단",
    "민단": "밑단",
    # 허벅지 오인식
    "허벅치": "허벅지",
    "허벅": "허벅지",
}

# 사이즈 라벨 오인식 교정 맵
SIZE_LABEL_CORRECTION_MAP = {
    "7": "L",
    "7X": "XL",
    "X7": "XL",
    "27L": "2XL",
    "2X7": "2XL",
    "3X7": "3XL",
    "F": "FREE",
}

# 잡음 토큰 (헤더 행에서만 제거, 데이터 행에서는 유지)
NOISE_TOKENS = {"|", "｜", "/", "\\", "-", "_", ".", ","}


def correct_header_text(text: str) -> str:
    """헤더 텍스트 오인식 교정"""
    text = text.strip()
    if text in HEADER_CORRECTION_MAP:
        return HEADER_CORRECTION_MAP[text]
    return text


def correct_size_label(text: str) -> str:
    """사이즈 라벨 오인식 교정"""
    text = text.strip().upper()
    if text in SIZE_LABEL_CORRECTION_MAP:
        return SIZE_LABEL_CORRECTION_MAP[text]
    return text


def is_noise_token(text: str) -> bool:
    """잡음 토큰인지 확인"""
    return text.strip() in NOISE_TOKENS


def is_header_row(row: List[Dict[str, Any]]) -> bool:
    """헤더 행인지 판단"""
    header_keywords = [
        # 하의 헤더
        "허리", "엉덩이", "앞밑위", "뒷밑위", "허벅지", "밑단", "총장",
        "I라우", "라우", "왓밀위", "뜻밀위", "밀단",
        # 상의 헤더
        "어깨", "가슴", "소매", "기장", "암홀", "가슴둘레", "어깨너비", "소매길이"
    ]
    row_text = " ".join(item["text"] for item in row)
    return any(kw in row_text for kw in header_keywords)


def is_size_data_row(row: List[Dict[str, Any]]) -> bool:
    """사이즈 데이터 행인지 판단 (M, L, XL 등으로 시작)"""
    if not row:
        return False
    first_text = row[0]["text"].strip().upper()
    size_labels = ["M", "L", "XL", "2XL", "3XL", "FREE", "F", "7", "7X", "S"]
    return first_text in size_labels


def correct_row_texts(row: List[Dict[str, Any]], is_header: bool = False) -> List[Dict[str, Any]]:
    """행 내 텍스트 교정"""
    corrected_row = []

    for cell in row:
        new_cell = cell.copy()
        text = cell["text"]

        if is_header:
            # 헤더 행: 헤더 교정 적용, 잡음 토큰 제거
            corrected_text = correct_header_text(text)
            if not is_noise_token(text) or corrected_text != text:
                new_cell["text"] = corrected_text
                new_cell["original_text"] = text  # 원본 보존
                corrected_row.append(new_cell)
        else:
            # 데이터 행: 첫 번째 셀(사이즈 라벨)만 교정
            if not corrected_row:  # 첫 번째 셀
                corrected_text = correct_size_label(text)
                new_cell["text"] = corrected_text
                new_cell["original_text"] = text
            corrected_row.append(new_cell)

    return corrected_row


def apply_ocr_corrections(rows: List[List[Dict[str, Any]]]) -> List[List[Dict[str, Any]]]:
    """전체 행에 OCR 교정 적용"""
    corrected_rows = []

    for row in rows:
        is_header = is_header_row(row)
        corrected_row = correct_row_texts(row, is_header=is_header)
        corrected_rows.append(corrected_row)

    return corrected_rows


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


def cluster_column_centers(rows: List[List[Dict[str, Any]]]) -> List[float]:
    """
    모든 행의 셀에서 center_x를 수집하여 열 기준선(column centers) 생성
    """
    if not rows:
        return []

    # 모든 셀의 center_x와 width 수집
    all_cells = []
    for row in rows:
        for cell in row:
            all_cells.append({
                "center_x": cell["center_x"],
                "width": get_box_width(cell["box"]) if cell.get("box") else 0
            })

    if not all_cells:
        return []

    # 평균 너비 계산 (클러스터링 threshold로 사용)
    avg_width = sum(c["width"] for c in all_cells) / len(all_cells)
    x_threshold = avg_width * 0.5  # 너비의 절반을 threshold로

    # center_x 기준 정렬
    all_x = sorted([c["center_x"] for c in all_cells])

    # X좌표 클러스터링
    column_centers = []
    current_cluster = [all_x[0]]

    for x in all_x[1:]:
        # 현재 클러스터의 평균과 비교
        cluster_mean = sum(current_cluster) / len(current_cluster)

        if abs(x - cluster_mean) <= x_threshold:
            current_cluster.append(x)
        else:
            # 클러스터 완성 → 평균을 열 기준선으로
            column_centers.append(sum(current_cluster) / len(current_cluster))
            current_cluster = [x]

    # 마지막 클러스터
    if current_cluster:
        column_centers.append(sum(current_cluster) / len(current_cluster))

    return sorted(column_centers)


def assign_cells_to_columns(
    rows: List[List[Dict[str, Any]]],
    column_centers: List[float]
) -> List[List[Optional[Dict[str, Any]]]]:
    """
    각 셀을 가장 가까운 열 기준선에 배치
    빈 열은 None으로 유지
    """
    if not column_centers:
        return rows

    num_columns = len(column_centers)
    result_rows = []

    for row in rows:
        # 고정 열 개수의 빈 행 생성
        new_row = [None] * num_columns

        for cell in row:
            # 가장 가까운 열 찾기
            min_dist = float('inf')
            best_col = 0

            for col_idx, col_center in enumerate(column_centers):
                dist = abs(cell["center_x"] - col_center)
                if dist < min_dist:
                    min_dist = dist
                    best_col = col_idx

            # 해당 열에 셀 배치 (이미 있으면 덮어쓰지 않음)
            if new_row[best_col] is None:
                new_row[best_col] = cell

        result_rows.append(new_row)

    return result_rows


def find_size_table_region(rows: List[List[Dict[str, Any]]]) -> Optional[Tuple[int, int]]:
    """
    SIZE 표 영역 찾기
    SIZE 키워드 또는 헤더 패턴이 있는 행부터 시작해서, 연속된 표 영역을 감지
    """
    size_row_index = None

    # 헤더 키워드 (SIZE 없이도 표 감지용)
    header_patterns = [
        # 하의 헤더
        "허리", "엉덩이", "앞밑위", "뒷밑위", "허벅지", "밑단", "총장",
        "I라우", "라우", "왓밀위", "뜻밀위", "밀단",
        # 상의 헤더
        "어깨", "가슴", "소매", "기장", "암홀", "가슴둘레", "어깨너비", "소매길이"
    ]

    # SIZE 키워드 또는 헤더 패턴이 있는 행 찾기
    for i, row in enumerate(rows):
        row_text = " ".join(item["text"] for item in row)
        row_text_upper = row_text.upper()

        # 1순위: SIZE/size/사이즈 키워드
        if "SIZE" in row_text_upper or "size" in row_text.lower() or "사이즈" in row_text:
            size_row_index = i
            break

        # 2순위: 헤더 패턴 (허리, 엉덩이, 어깨 등)
        if any(pattern in row_text for pattern in header_patterns):
            size_row_index = i
            break

    if size_row_index is None:
        return None

    # SIZE 다음 행부터 헤더와 데이터 행 찾기
    # 헤더는 보통 "허리", "엉덩이" 같은 키워드
    header_keywords = [
        # 하의 헤더
        "허리", "엉덩이", "왓밀위", "뜻밀위", "허벅지", "밀단", "총장", "I라우",
        # 상의 헤더
        "어깨", "가슴", "소매", "기장", "암홀", "가슴둘레", "어깨너비", "소매길이"
    ]
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
    표 구조를 텍스트로 변환 (기존 방식 - 열 클러스터링 없음)
    """
    lines = []
    for row in rows:
        row_text = " | ".join(item["text"] for item in row)
        lines.append(row_text)
    return "\n".join(lines)


def format_table_with_fixed_columns(
    rows: List[List[Optional[Dict[str, Any]]]]
) -> str:
    """
    고정 열 개수의 표를 텍스트로 변환
    빈 셀은 빈 문자열로 표시
    """
    lines = []
    for row in rows:
        row_texts = []
        for cell in row:
            if cell is None:
                row_texts.append("")
            else:
                row_texts.append(cell["text"])
        row_text = " | ".join(row_texts)
        lines.append(row_text)
    return "\n".join(lines)


def reconstruct_size_table(
    texts: List[str],
    boxes: List[List[List[float]]],
    scores: List[float],
    use_column_clustering: bool = True,
    use_ocr_correction: bool = True
) -> Optional[str]:
    """
    SIZE 표를 좌표 기반으로 재구성
    반환: 구조화된 표 텍스트 (행별로 | 구분)

    Args:
        use_column_clustering: True면 X좌표 기반 열 클러스터링 적용 (빈칸 보정)
        use_ocr_correction: True면 OCR 오인식 텍스트 교정 적용
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

    # 3. OCR 오인식 교정 (선택적)
    if use_ocr_correction and table_rows:
        table_rows = apply_ocr_corrections(table_rows)

    # 4. X좌표 기반 열 클러스터링 (선택적)
    if use_column_clustering and table_rows:
        # 열 기준선 생성
        column_centers = cluster_column_centers(table_rows)

        # 각 셀을 열에 배치
        aligned_rows = assign_cells_to_columns(table_rows, column_centers)

        # 고정 열 개수로 표 변환
        table_text = format_table_with_fixed_columns(aligned_rows)
    else:
        # 기존 방식
        table_text = format_table_as_text(table_rows)

    return table_text


def parse_size_table_to_dict(table_text: str) -> Dict[str, Any]:
    """
    구조화된 표 텍스트를 파싱해서 딕셔너리로 변환
    """
    lines = table_text.strip().split("\n")

    if not lines:
        return {}

    # 헤더 찾기 (교정된 헤더 포함)
    header_keywords = [
        # 하의 헤더
        "허리", "엉덩이", "앞밑위", "뒷밑위", "허벅지", "밑단", "총장",
        # 오인식 버전도 포함 (교정 전 데이터 호환)
        "왓밀위", "뜻밀위", "밀단", "I라우", "라우",
        # 상의 헤더
        "어깨", "가슴", "소매", "기장", "암홀", "가슴둘레", "어깨너비", "소매길이"
    ]
    header_line = None
    header_index = 0

    for i, line in enumerate(lines):
        if any(kw in line for kw in header_keywords):
            header_line = line
            header_index = i
            break

    if header_line is None:
        return {}

    # 헤더 파싱 (교정 적용)
    headers = []
    for h in header_line.split("|"):
        h = h.strip()
        corrected = correct_header_text(h)
        headers.append(corrected)

    # 사이즈 라벨 (교정된 라벨 포함)
    size_labels = ["S", "M", "L", "XL", "2XL", "3XL", "FREE", "F"]

    sizes = {}

    # 헤더 다음 행부터 데이터 행 파싱
    for line in lines[header_index + 1:]:
        parts = [p.strip() for p in line.split("|")]

        if not parts:
            continue

        # 첫 번째 항목에 사이즈 라벨 교정 적용
        first_part = correct_size_label(parts[0])

        if first_part.upper() not in size_labels:
            continue

        size_label = first_part.upper()
        values = parts[1:]

        # 헤더와 값 매핑
        size_data = {}
        for i, value in enumerate(values):
            if i < len(headers) - 1:  # 첫 번째 헤더는 보통 SIZE
                header_name = headers[i + 1] if i + 1 < len(headers) else f"col_{i}"
                size_data[header_name] = value

        sizes[size_label] = size_data

    return {"headers": headers, "sizes": sizes}