from __future__ import annotations

import csv
import random
import re
from collections import Counter
from pathlib import Path


RANDOM_SEED = 20260212
TARGET_PER_LABEL = 300
TRAIN_PER_LABEL = 240
TEST_PER_LABEL = 60
UNKNOWN_TOTAL = 450
UNKNOWN_TRAIN = 360
UNKNOWN_TEST = 90
NEGATIVE_UNKNOWN_TARGET = 180


LABEL_META = {
    68: ("go_hearbe", "히어비 홈페이지로 이동"),
    69: ("search_products", "상품 검색"),
    70: ("click_order_history", "주문내역 조회 클릭"),
    71: ("click_cart", "장바구니 조회 클릭"),
    72: ("click_login", "로그인 클릭"),
    73: ("click_logout", "로그아웃 클릭"),
    74: ("read_current_page_actions", "현재 페이지 정보 읽기"),
    75: ("read_search_results", "검색 결과 읽기"),
    76: ("select_search_result", "검색 결과 선택"),
    77: ("read_product_info", "상품 정보 읽기"),
    78: ("update_product_option", "상품 옵션 수정"),
    79: ("click_add_to_cart", "장바구니에 담기"),
    80: ("click_buy_now", "구매하기 클릭"),
    81: ("read_reviews", "리뷰 읽기"),
    82: ("click_wishlist", "찜하기"),
    83: ("read_cart_items", "장바구니 상품 읽기"),
    84: ("select_cart_item", "상품 선택"),
    85: ("unselect_cart_item", "상품 해제"),
    86: ("adjust_item_quantity", "상품 수량 조절"),
    87: ("read_order_amount", "주문 금액 읽기"),
    88: ("read_payment_order_info", "주문 정보 읽어주기"),
    89: ("submit_payment", "결제하기"),
    91: ("read_order_detail", "주문 상세 정보 읽기"),
    92: ("click_track_delivery", "배송조회 클릭"),
    93: ("request_exchange_return", "교환 및 반품 신청"),
    94: ("delete_order_history", "주문내역 삭제"),
    95: ("read_option_info", "옵션 정보 읽기"),
}


PREFIXES = [
    "",
    "지금 ",
    "바로 ",
    "일단 ",
    "먼저 ",
    "급한데 ",
    "잠깐 ",
    "이번엔 ",
]

CONTEXT_PREFIXES = [
    "",
    "현재 페이지에서 ",
    "지금 화면에서 ",
    "방금 본 상품 기준으로 ",
    "이번 주문 기준으로 ",
]

POSTFIXES = [
    "",
    "",
    " 해줘",
    " 해주세요",
    " 부탁해",
    " 부탁드립니다",
    " 좀",
    " 해줄래",
    " 가능해",
]

TAILS = ["", "", " 지금", " 먼저", " 바로", " 부탁", " 해봐", " 해주이소"]

ENDING_SWAPS = [
    ("해줘", "해주세요"),
    ("해줘", "해주라"),
    ("해줘", "해주이소"),
    ("해주세요", "해줘"),
    ("눌러줘", "눌러주세요"),
    ("눌러줘", "눌러주라"),
    ("읽어줘", "읽어주세요"),
    ("읽어줘", "읽어주라"),
    ("알려줘", "알려주세요"),
    ("알려줘", "알려주라"),
    ("바꿔줘", "바꿔주세요"),
    ("바꿔줘", "바꿔주라"),
    ("입력해줘", "입력해주세요"),
    ("선택해줘", "선택해주세요"),
]

TYPO_MAP = {
    "로그아웃": ["로가웃", "로과웃"],
    "로그인": ["로긴"],
    "장바구니": ["장바꾸니"],
    "옵션": ["옵선"],
    "배송조회": ["배송 조희", "배송 조회"],
    "주문내역": ["주문 내역", "주문내옉"],
    "결제": ["결재"],
    "비밀번호": ["비번"],
    "검색": ["검샥"],
    "리뷰": ["리부"],
    "상품": ["상픔"],
    "수량": ["수랑"],
}

SHOPPING_TOKENS = [
    "상품",
    "주문",
    "결제",
    "장바구니",
    "쿠팡",
    "히어비",
    "검색",
    "리뷰",
    "옵션",
    "배송",
    "구매",
    "찜",
    "로그인",
    "로그아웃",
    "카트",
    "주문내역",
]

NEGATION_TERMS = [
    "안 ",
    "말고",
    "하지마",
    "하지 말",
    "가지마",
    "가지 말",
    "금지",
    "취소",
    "멈춰",
]

NUM_TO_KOR = {
    "0": "영",
    "1": "일",
    "2": "이",
    "3": "삼",
    "4": "사",
    "5": "오",
    "6": "육",
    "7": "칠",
    "8": "팔",
    "9": "구",
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def load_seed_lines(path: Path) -> list[str]:
    seen = set()
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        s = normalize(raw)
        if s and s not in seen:
            seen.add(s)
            lines.append(s)
    return lines


def to_korean_digits(num_text: str) -> str:
    return " ".join(NUM_TO_KOR[ch] for ch in num_text if ch in NUM_TO_KOR)


def asr_normalize(text: str) -> str:
    s = text

    # common english tokens used in shopping/options
    eng_map = {
        "xxl": "엑스엑스엘",
        "xl": "엑스엘",
        "lg": "엘지",
        "kg": "킬로그램",
        "ml": "밀리리터",
        "l": "리터",
        "pin": "핀",
    }
    for k, v in eng_map.items():
        s = re.sub(rf"(?i)\b{k}\b", v, s)

    # symbolic numbers: +1, -1
    s = re.sub(r"\+\s*(\d+)", lambda m: "플러스 " + to_korean_digits(m.group(1)), s)
    s = re.sub(r"-\s*(\d+)", lambda m: "마이너스 " + to_korean_digits(m.group(1)), s)

    # remaining symbols that appear in model data
    s = s.replace("+", " 플러스 ")
    s = s.replace("-", " 마이너스 ")
    s = s.replace("/", " ")
    s = s.replace("&", " ")

    # plain numbers -> korean reading per digit
    s = re.sub(r"\d+", lambda m: to_korean_digits(m.group(0)), s)

    # remove punctuation/specials
    s = re.sub(r"[^0-9A-Za-z가-힣\s]", " ", s)

    # remove remaining english
    s = re.sub(r"[A-Za-z]", " ", s)

    s = normalize(s)
    return s


def mutate(base: str) -> str:
    s = base

    if random.random() < 0.75:
        s = random.choice(PREFIXES) + s
    if random.random() < 0.55:
        s = random.choice(CONTEXT_PREFIXES) + s

    if random.random() < 0.55:
        a, b = random.choice(ENDING_SWAPS)
        if a in s:
            s = s.replace(a, b, 1)

    if random.random() < 0.70:
        s += random.choice(POSTFIXES)

    if random.random() < 0.45:
        s += random.choice(TAILS)

    if random.random() < 0.50:
        keys = [k for k in TYPO_MAP if k in s]
        random.shuffle(keys)
        for k in keys[:2]:
            if random.random() < 0.70:
                s = s.replace(k, random.choice(TYPO_MAP[k]), 1)

    # ASR spacing perturbation
    r = random.random()
    if r < 0.10:
        s = s.replace(" ", "")
    elif r < 0.20:
        idx = [i for i, ch in enumerate(s) if ch == " "]
        if idx:
            i = random.choice(idx)
            s = s[:i] + s[i + 1 :]

    return asr_normalize(s)


def is_negative_command(text: str) -> bool:
    t = normalize(text)
    return any(term in t for term in NEGATION_TERMS)


def strip_command_tail(text: str) -> str:
    t = normalize(text)
    tails = [
        "해줘",
        "해주세요",
        "부탁해",
        "부탁드립니다",
        "해줄래",
        "가능해",
        "해봐",
        "해주이소",
        "부탁",
        "좀",
        "지금",
        "바로",
        "먼저",
    ]
    changed = True
    while changed:
        changed = False
        for tail in tails:
            if t.endswith(" " + tail):
                t = t[: -len(tail) - 1].strip()
                changed = True
            elif t.endswith(tail):
                t = t[: -len(tail)].strip()
                changed = True
    return normalize(t)


def generate_label_samples(
    seeds: list[str], target: int, global_seen: set[str]
) -> list[str]:
    out: list[str] = []
    local_seen: set[str] = set()

    for seed in seeds:
        s = asr_normalize(seed)
        if len(s) < 2:
            continue
        if s not in local_seen and s not in global_seen:
            out.append(s)
            local_seen.add(s)
            global_seen.add(s)

    guard = 0
    while len(out) < target and guard < 1_500_000:
        guard += 1
        cand = mutate(random.choice(seeds))
        if len(cand) < 2:
            continue
        if not re.search(r"[가-힣]", cand):
            continue
        if cand in local_seen or cand in global_seen:
            continue
        local_seen.add(cand)
        global_seen.add(cand)
        out.append(cand)

    # deterministic fallback
    fallback_words = [
        "한번",
        "두번",
        "세번",
        "네번",
        "다섯번",
        "여섯번",
        "일곱번",
        "여덟번",
        "아홉번",
        "열번",
    ]
    idx = 0
    while len(out) < target and idx < 10000:
        for seed in seeds:
            tail = fallback_words[idx % len(fallback_words)]
            cand = asr_normalize(f"{random.choice(CONTEXT_PREFIXES)}{seed} {tail}")
            if cand in local_seen or cand in global_seen:
                continue
            if not re.search(r"[가-힣]", cand):
                continue
            local_seen.add(cand)
            global_seen.add(cand)
            out.append(cand)
            if len(out) >= target:
                break
        idx += 1

    if len(out) < target:
        raise RuntimeError(f"label generation failed: {len(out)}/{target}")

    random.shuffle(out)
    return out[:target]


def valid_unknown(text: str) -> bool:
    if len(text) < 4:
        return False
    if not bool(re.search(r"[가-힣]", text)):
        return False
    if is_negative_command(text):
        return True
    if any(tok in text for tok in SHOPPING_TOKENS):
        return False
    return True


def generate_negative_unknown_samples(
    seed_pool: list[str], target: int, global_seen: set[str]
) -> list[str]:
    if target <= 0:
        return []

    templates = [
        "{s} 하지마",
        "{s} 하지 말아",
        "{s} 하지 말라고",
        "{s}는 하지마",
        "{s}는 하지 말고",
        "{s} 금지",
        "{s} 취소해",
        "{s} 하면 안돼",
        "{s}는 안 해",
        "{s}는 하지마라",
    ]
    prefixes = ["", "절대 ", "지금 ", "그거 ", "아예 "]

    out: list[str] = []
    local_seen: set[str] = set()
    cleaned = [strip_command_tail(asr_normalize(s)) for s in seed_pool if normalize(s)]
    cleaned = [c for c in cleaned if c]

    # fixed hard negatives from observed errors
    fixed = [
        "리뷰 읽지마",
        "읽지 말라고 리뷰",
        "쿠팡 가지마",
        "히어비 가지마",
        "히어비 가지말라고",
        "히어비 가면 안돼",
        "장바구니 열지마",
        "주문내역 보지마",
    ]
    for s in fixed:
        c = asr_normalize(s)
        if valid_unknown(c) and c not in local_seen and c not in global_seen:
            out.append(c)
            local_seen.add(c)
            global_seen.add(c)

    guard = 0
    while len(out) < target and guard < 1_000_000:
        guard += 1
        base = random.choice(cleaned)
        cand = random.choice(prefixes) + random.choice(templates).format(s=base)
        cand = asr_normalize(cand)
        if random.random() < 0.20:
            cand = cand.replace(" ", "")
            cand = normalize(cand)
        if not valid_unknown(cand):
            continue
        if cand in local_seen or cand in global_seen:
            continue
        out.append(cand)
        local_seen.add(cand)
        global_seen.add(cand)

    if len(out) < target:
        raise RuntimeError(f"negative unknown generation failed: {len(out)}/{target}")

    random.shuffle(out)
    return out[:target]


def generate_unknown_samples(target: int, global_seen: set[str]) -> list[str]:
    fixed = [
        "오늘 비 오는지 알려줘",
        "내일 일정 정리해줘",
        "오후 회의 시간 확인해줘",
        "지금 알람 하나 맞춰줘",
        "이번 주 운동 계획 세워줘",
        "내일 아침 버스 시간 알려줘",
        "이번 달 지출 합계 계산해줘",
        "주말에 볼 영화 추천해줘",
        "오늘 수면 시간 기록해줘",
        "다음 주 할 일 목록 정리해줘",
    ]

    slot1 = [
        "오늘",
        "내일",
        "이번 주",
        "다음 주",
        "주말",
        "오후",
        "아침",
        "저녁",
        "지금",
        "잠깐",
    ]
    slot2 = [
        "날씨",
        "일정",
        "알람",
        "운동 계획",
        "회의 시간",
        "버스 시간",
        "지하철 시간",
        "식단",
        "수면 기록",
        "공부 계획",
    ]
    slot3 = [
        "알려줘",
        "정리해줘",
        "확인해줘",
        "기록해줘",
        "요약해줘",
        "체크해줘",
        "계산해줘",
    ]

    out: list[str] = []
    local_seen: set[str] = set()

    for s in fixed:
        c = asr_normalize(s)
        if valid_unknown(c) and c not in local_seen and c not in global_seen:
            out.append(c)
            local_seen.add(c)
            global_seen.add(c)

    guard = 0
    while len(out) < target and guard < 1_000_000:
        guard += 1
        c = asr_normalize(
            f"{random.choice(slot1)} {random.choice(slot2)} {random.choice(slot3)}"
        )
        if random.random() < 0.18:
            c = c.replace(" ", "")
            c = normalize(c)
        if not valid_unknown(c):
            continue
        if c in local_seen or c in global_seen:
            continue
        out.append(c)
        local_seen.add(c)
        global_seen.add(c)

    if len(out) < target:
        raise RuntimeError(f"unknown generation failed: {len(out)}/{target}")

    random.shuffle(out)
    return out[:target]


def main() -> None:
    random.seed(RANDOM_SEED)

    root = Path("C:/ssafy") / "공통설계" / "coupang"
    seed_dir = root / "func_per_example"
    out_dir = root / "func_data"
    out_dir.mkdir(parents=True, exist_ok=True)

    labels = []
    for label_id, (label, desc) in sorted(LABEL_META.items()):
        if (seed_dir / f"{label}.txt").exists():
            labels.append((label_id, label, desc))

    global_seen: set[str] = set()
    train_rows: list[dict[str, str | int]] = []
    test_rows: list[dict[str, str | int]] = []
    map_meta = {0: ("unknown", "무관/일상질의")}
    all_seed_pool: list[str] = []

    for label_id, label, desc in labels:
        seeds = load_seed_lines(seed_dir / f"{label}.txt")
        all_seed_pool.extend(seeds)
        samples = generate_label_samples(seeds, TARGET_PER_LABEL, global_seen)
        tr = samples[:TRAIN_PER_LABEL]
        te = samples[TRAIN_PER_LABEL : TRAIN_PER_LABEL + TEST_PER_LABEL]

        for t in tr:
            train_rows.append({"text": t, "label_id": label_id, "label": label})
        for t in te:
            test_rows.append({"text": t, "label_id": label_id, "label": label})

        map_meta[label_id] = (label, desc)

    negative_unknown = generate_negative_unknown_samples(
        all_seed_pool, min(NEGATIVE_UNKNOWN_TARGET, UNKNOWN_TOTAL), global_seen
    )
    generic_unknown = generate_unknown_samples(
        UNKNOWN_TOTAL - len(negative_unknown), global_seen
    )
    unknown_samples = negative_unknown + generic_unknown
    random.shuffle(unknown_samples)
    for t in unknown_samples[:UNKNOWN_TRAIN]:
        train_rows.append({"text": t, "label_id": 0, "label": "unknown"})
    for t in unknown_samples[UNKNOWN_TRAIN : UNKNOWN_TRAIN + UNKNOWN_TEST]:
        test_rows.append({"text": t, "label_id": 0, "label": "unknown"})

    random.shuffle(train_rows)
    random.shuffle(test_rows)

    train_counts = Counter(row["label"] for row in train_rows)
    test_counts = Counter(row["label"] for row in test_rows)
    labels_all = sorted(set(train_counts) | set(test_counts))

    with (out_dir / "train.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["text", "label_id", "label"], quoting=csv.QUOTE_ALL
        )
        w.writeheader()
        w.writerows(train_rows)

    with (out_dir / "test.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["text", "label_id", "label"], quoting=csv.QUOTE_ALL
        )
        w.writeheader()
        w.writerows(test_rows)

    summary_rows = []
    for lb in labels_all:
        tr = train_counts.get(lb, 0)
        te = test_counts.get(lb, 0)
        summary_rows.append({"label": lb, "train": tr, "test": te, "total": tr + te})
    summary_rows.sort(key=lambda x: x["label"])

    with (out_dir / "summary.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["label", "train", "test", "total"], quoting=csv.QUOTE_ALL
        )
        w.writeheader()
        w.writerows(summary_rows)

    label_map_rows = []
    for label_id, (label, desc) in sorted(map_meta.items(), key=lambda x: x[0]):
        tr = train_counts.get(label, 0)
        te = test_counts.get(label, 0)
        if tr == 0 and te == 0:
            continue
        label_map_rows.append(
            {
                "label_id": label_id,
                "label": label,
                "description_ko": desc,
                "total": tr + te,
                "train": tr,
                "test": te,
            }
        )

    with (out_dir / "label_map.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["label_id", "label", "description_ko", "total", "train", "test"],
            quoting=csv.QUOTE_ALL,
        )
        w.writeheader()
        w.writerows(label_map_rows)

    print("DONE")
    print(f"labels={len(labels)}")
    print(f"train_rows={len(train_rows)} unknown_train={train_counts.get('unknown', 0)}")
    print(f"test_rows={len(test_rows)} unknown_test={test_counts.get('unknown', 0)}")


if __name__ == "__main__":
    main()
