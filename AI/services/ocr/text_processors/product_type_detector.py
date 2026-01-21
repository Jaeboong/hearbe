"""
제품 타입 정의 및 타입별 키워드 매핑 모듈 (Product Type Definition & Mapping)

OCR 텍스트 요약 시 제품 타입을 자동 감지하고,
타입에 맞는 키워드를 추출하기 위한 설정을 제공합니다.
"""

from enum import Enum
from typing import List, Dict


class ProductType(str, Enum):
    """
    지원하는 모든 제품 타입을 정의하는 열거형(Enum) 클래스입니다.
    문자열 값을 상속받아 JSON 직렬화가 용이하게 합니다.
    """
    
    # ==========================
    # 식품류 (Food & Beverage)
    # ==========================
    FOOD_SNACK = "FOOD_SNACK"          # 과자/스낵류
    FOOD_BEVERAGE = "FOOD_BEVERAGE"    # 음료/주류/커피
    FOOD_INSTANT = "FOOD_INSTANT"      # 라면/즉석식품/가공식품
    FOOD_FRESH = "FOOD_FRESH"          # 신선식품 (과일/채소/정육/수산)
    FOOD_DAIRY = "FOOD_DAIRY"          # 유제품 (우유/치즈/요거트)
    FOOD_CONDIMENT = "FOOD_CONDIMENT"  # 조미료/소스/장류
    FOOD_BAKERY = "FOOD_BAKERY"        # 베이커리 (빵/케이크)
    
    # ==========================
    # 건강 (Health)
    # ==========================
    HEALTH_SUPPLEMENT = "HEALTH_SUPPLEMENT"      # 건강기능식품/영양제
    HEALTH_MEDICINE = "HEALTH_MEDICINE"          # 의약품
    HEALTH_PERSONAL_CARE = "HEALTH_PERSONAL_CARE" # 개인위생용품 (치약/생리대 등)
    
    # ==========================
    # 생활/가전 (Home & Living)
    # ==========================
    HOME_KITCHEN = "HOME_KITCHEN"      # 주방용품
    HOME_CLEANING = "HOME_CLEANING"    # 청소/세탁용품
    HOME_LIVING = "HOME_LIVING"        # 일반 생활용품
    HOME_APPLIANCE = "HOME_APPLIANCE"  # 가전제품
    
    # ==========================
    # 패션 (Fashion)
    # ==========================
    FASHION_CLOTHING = "FASHION_CLOTHING"       # 의류
    FASHION_SHOES = "FASHION_SHOES"             # 신발
    FASHION_ACCESSORIES = "FASHION_ACCESSORIES" # 패션잡화
    
    # ==========================
    # 뷰티 (Beauty)
    # ==========================
    BEAUTY_COSMETICS = "BEAUTY_COSMETICS"  # 화장품 (스킨케어/메이크업)
    BEAUTY_HAIRCARE = "BEAUTY_HAIRCARE"    # 헤어케어 (샴푸/관련용품)
    
    # ==========================
    # 육아 (Baby)
    # ==========================
    BABY_FOOD = "BABY_FOOD"      # 유아식품 (분유/이유식)
    BABY_DIAPER = "BABY_DIAPER"  # 기저귀/물티슈
    BABY_CARE = "BABY_CARE"      # 기타 육아용품
    
    # ==========================
    # 반려동물 (Pet)
    # ==========================
    PET_FOOD = "PET_FOOD"         # 반려동물 사료/간식
    PET_SUPPLIES = "PET_SUPPLIES" # 반려동물 용품
    
    # ==========================
    # 기타 (Others)
    # ==========================
    BOOK = "BOOK"              # 도서
    STATIONERY = "STATIONERY"  # 문구류
    TOY = "TOY"                # 완구
    SPORTS = "SPORTS"          # 스포츠용품
    ELECTRONICS = "ELECTRONICS"# 전자기기 (가전 외 IT기기)
    OTHER = "OTHER"            # 분류 불가/기타


# =============================================================================
# 타입별 추출할 키워드 매핑 (Extraction Keywords)
#
# LLM에게 어떤 정보를 찾아야 하는지 알려주기 위한 리스트입니다.
# 제품군마다 중요한 정보(예: 식품은 알레르기, 가전은 사양)가 다릅니다.
# =============================================================================
TYPE_KEYWORDS: Dict[ProductType, List[str]] = {
    # --- 식품 ---
    ProductType.FOOD_SNACK: [
        "가격", "제품명", "브랜드", "중량/용량", "원재료/성분",
        "알레르기", "보관방법", "유통기한", "영양정보", "주의사항", "맛/특징"
    ],
    ProductType.FOOD_BEVERAGE: [
        "가격", "제품명", "브랜드", "중량/용량", "원재료/성분",
        "알레르기", "보관방법", "유통기한", "영양정보", "주의사항", "맛/특징", "카페인함량"
    ],
    ProductType.FOOD_INSTANT: [
        "가격", "제품명", "브랜드", "중량/용량", "원재료/성분",
        "알레르기", "보관방법", "유통기한", "영양정보", "주의사항", "조리방법"
    ],
    ProductType.FOOD_FRESH: [
        "가격", "제품명", "원산지", "중량/용량", "보관방법", "유통기한", "등급/품질"
    ],
    ProductType.FOOD_DAIRY: [
        "가격", "제품명", "브랜드", "중량/용량", "원재료/성분",
        "알레르기", "보관방법", "유통기한", "영양정보", "주의사항"
    ],
    ProductType.FOOD_CONDIMENT: [
        "가격", "제품명", "브랜드", "중량/용량", "원재료/성분",
        "알레르기", "보관방법", "유통기한", "사용방법"
    ],
    ProductType.FOOD_BAKERY: [
        "가격", "제품명", "브랜드", "중량/용량", "원재료/성분",
        "알레르기", "보관방법", "유통기한", "영양정보"
    ],
    
    # --- 건강 ---
    ProductType.HEALTH_SUPPLEMENT: [
        "가격", "제품명", "브랜드", "중량/용량", "성분/함량",
        "섭취방법", "섭취주의사항", "유통기한", "기능성내용", "보관방법"
    ],
    ProductType.HEALTH_MEDICINE: [
        "가격", "제품명", "효능/효과", "용법/용량", "성분",
        "사용상주의사항", "유통기한", "보관방법"
    ],
    ProductType.HEALTH_PERSONAL_CARE: [
        "가격", "제품명", "브랜드", "중량/용량", "성분",
        "사용방법", "주의사항", "유통기한"
    ],
    
    # --- 생활/가전 ---
    ProductType.HOME_KITCHEN: [
        "가격", "제품명", "브랜드", "재질", "크기/용량",
        "사용방법", "세척방법", "주의사항", "원산지"
    ],
    ProductType.HOME_CLEANING: [
        "가격", "제품명", "브랜드", "중량/용량", "성분",
        "사용방법", "주의사항", "용도"
    ],
    ProductType.HOME_LIVING: [
        "가격", "제품명", "브랜드", "재질", "크기/수량",
        "사용방법", "주의사항"
    ],
    ProductType.HOME_APPLIANCE: [
        "가격", "제품명", "브랜드", "모델명", "사양/스펙",
        "전력소비량", "크기/무게", "보증기간", "사용방법", "주의사항", "원산지"
    ],
    
    # --- 패션 ---
    ProductType.FASHION_CLOTHING: [
        "가격", "제품명", "브랜드", "사이즈", "소재/원단",
        "색상", "세탁방법", "원산지", "주의사항"
    ],
    ProductType.FASHION_SHOES: [
        "가격", "제품명", "브랜드", "사이즈", "소재",
        "색상", "관리방법", "원산지"
    ],
    ProductType.FASHION_ACCESSORIES: [
        "가격", "제품명", "브랜드", "재질", "크기",
        "색상", "관리방법", "원산지"
    ],
    
    # --- 뷰티 ---
    ProductType.BEAUTY_COSMETICS: [
        "가격", "제품명", "브랜드", "용량", "성분",
        "사용방법", "효능/효과", "유통기한", "주의사항", "피부타입"
    ],
    ProductType.BEAUTY_HAIRCARE: [
        "가격", "제품명", "브랜드", "용량", "성분",
        "사용방법", "효능/효과", "유통기한", "주의사항", "모발타입"
    ],
    
    # --- 육아 ---
    ProductType.BABY_FOOD: [
        "가격", "제품명", "브랜드", "중량/용량", "원재료/성분",
        "알레르기", "보관방법", "유통기한", "영양정보", "섭취방법", "적정월령"
    ],
    ProductType.BABY_DIAPER: [
        "가격", "제품명", "브랜드", "사이즈", "수량",
        "적용체중", "특징", "주의사항"
    ],
    ProductType.BABY_CARE: [
        "가격", "제품명", "브랜드", "재질", "크기",
        "사용방법", "주의사항", "적정연령"
    ],
    
    # --- 반려동물 ---
    ProductType.PET_FOOD: [
        "가격", "제품명", "브랜드", "중량/용량", "원재료/성분",
        "급여방법", "보관방법", "유통기한", "적정연령/체중", "주의사항"
    ],
    ProductType.PET_SUPPLIES: [
        "가격", "제품명", "브랜드", "재질", "크기",
        "사용방법", "주의사항", "적정크기/종"
    ],
    
    # --- 기타 ---
    ProductType.BOOK: [
        "가격", "제목", "저자", "출판사", "페이지수",
        "ISBN", "출판일", "내용소개"
    ],
    ProductType.STATIONERY: [
        "가격", "제품명", "브랜드", "재질", "크기/수량",
        "색상", "용도", "주의사항"
    ],
    ProductType.TOY: [
        "가격", "제품명", "브랜드", "재질", "크기",
        "적정연령", "주의사항", "KC인증"
    ],
    ProductType.SPORTS: [
        "가격", "제품명", "브랜드", "재질", "크기/사이즈",
        "용도", "사용방법", "주의사항"
    ],
    ProductType.ELECTRONICS: [
        "가격", "제품명", "브랜드", "모델명", "사양/스펙",
        "배터리/전력", "크기/무게", "보증기간", "사용방법", "주의사항"
    ],
    ProductType.OTHER: [
        "가격", "제품명", "브랜드", "특징", "사용방법", "주의사항"
    ],
}


# =============================================================================
# 타입 자동 감지를 위한 키워드 사전 (Detection Keywords)
#
# OCR로 인식된 텍스트에 이 단어들이 포함되어 있으면 해당 타입으로 분류합니다.
# =============================================================================
TYPE_DETECTION_KEYWORDS: Dict[ProductType, List[str]] = {
    # 과자류: 대표적인 과자 종류 나열
    ProductType.FOOD_SNACK: [
        "과자", "스낵", "비스킷", "쿠키", "초콜릿", "사탕", "젤리", "껌",
        "칩", "크래커", "웨하스", "파이", "캔디"
    ],
    # 음료: 마시는 모든 것
    ProductType.FOOD_BEVERAGE: [
        "음료", "주스", "커피", "차", "탄산", "물", "우유", "두유", "소주", "맥주", "와인", "주류",
        "이온음료", "에너지드링크", "음료수", "드링크"
    ],
    # 즉석식품: 간단 조리 식품
    ProductType.FOOD_INSTANT: [
        "라면", "즉석", "컵라면", "레토르트", "냉동", "즉석밥", "즉석국",
        "즉석식품", "간편식", "HMR"
    ],
    # 신선식품: 원물 그대로의 식품
    ProductType.FOOD_FRESH: [
        "신선", "과일", "채소", "육류", "수산물", "정육", "생선",
        "야채", "고기", "해산물",
        # 육류 상세 키워드
        "삼겹살", "오겹살", "목살", "갈비", "등심", "안심", "차돌박이",
        "돼지고기", "소고기", "닭고기", "한우", "수입산", "국내산", "양념육",
        "다짐육", "불고기", "제육", "스테이크", "돈까스용", "국거리", "찌개용",
        "앞다리살", "뒷다리살", "항정살", "가브리살", "살치살", "채끝", "부채살",
        # 수산물 상세 키워드
        "고등어", "오징어", "새우", "전복", "갈치", "조기", "굴비", "멸치",
        "김", "미역", "다시마", "낙지", "쭈꾸미", "문어", "게", "꽃게", "대게",
        "킹크랩", "랍스터", "회", "연어", "광어", "우럭",
        # 과일/채소 상세 키워드
        "사과", "배", "포도", "귤", "딸기", "바나나", "키위", "토마토",
        "감자", "고구마", "양파", "파", "마늘", "고추", "상추", "깻잎",
        "배추", "무", "당근", "버섯"
    ],
    # 유제품
    ProductType.FOOD_DAIRY: [
        "유제품", "우유", "요거트", "치즈", "버터", "생크림", "요구르트"
    ],
    # 조미료
    ProductType.FOOD_CONDIMENT: [
        "조미료", "소스", "간장", "고추장", "된장", "식초", "기름",
        "드레싱", "양념", "참기름", "케첩", "마요네즈"
    ],
    # 빵류
    ProductType.FOOD_BAKERY: [
        "빵", "케이크", "베이커리", "도넛", "머핀", "식빵", "크루아상"
    ],
    
    # 건강식품
    ProductType.HEALTH_SUPPLEMENT: [
        "영양제", "비타민", "건강기능식품", "프로바이오틱스", "오메가",
        "유산균", "홍삼", "보충제", "건강식품"
    ],
    # 의약품
    ProductType.HEALTH_MEDICINE: [
        "의약품", "약", "진통제", "감기약", "소화제", "연고", "파스"
    ],
    # 위생용품
    ProductType.HEALTH_PERSONAL_CARE: [
        "치약", "칫솔", "비누", "바디워시", "면도",
        "생리대", "위생용품", "구강", "데오드란트"
    ],
    
    # 주방용품
    ProductType.HOME_KITCHEN: [
        "주방", "냄비", "프라이팬", "그릇", "접시", "수저", "컵",
        "식기", "조리도구", "칼", "도마"
    ],
    # 청소용품
    ProductType.HOME_CLEANING: [
        "세제", "청소", "세탁", "표백제", "섬유유연제", "락스",
        "주방세제", "세정제", "클리너"
    ],
    # 생활용품
    ProductType.HOME_LIVING: [
        "수건", "타월", "휴지", "화장지", "물티슈", "쓰레기봉투",
        "행주", "키친타월", "생활용품"
    ],
    # 가전제품
    ProductType.HOME_APPLIANCE: [
        "가전", "전자레인지", "청소기", "선풍기", "에어컨", "냉장고",
        "세탁기", "건조기", "공기청정기", "가습기", "제습기"
    ],
    
    # 의류
    ProductType.FASHION_CLOTHING: [
        "의류", "옷", "티셔츠", "셔츠", "바지", "치마", "원피스",
        "자켓", "코트", "패딩", "니트", "후드"
    ],
    # 신발
    ProductType.FASHION_SHOES: [
        "신발", "운동화", "구두", "슬리퍼", "샌들", "부츠", "스니커즈"
    ],
    # 패션잡화
    ProductType.FASHION_ACCESSORIES: [
        "가방", "모자", "벨트", "지갑", "목도리", "장갑", "양말",
        "스카프", "넥타이"
    ],
    
    # 화장품
    ProductType.BEAUTY_COSMETICS: [
        "화장품", "스킨", "로션", "크림", "에센스", "세럼", "팩",
        "마스크", "선크림", "파운데이션", "립스틱", "아이섀도우",
        "메이크업", "코스메틱"
    ],
    # 헤어케어
    ProductType.BEAUTY_HAIRCARE: [
        "헤어", "샴푸", "린스", "트리트먼트", "헤어팩", "염색",
        "왁스", "스프레이", "헤어오일", "두피", "모발", "탈모",
        "스칼프", "케라틴", "컨디셔너", "헤어케어", "케어샴푸"
    ],
    
    # 유아식
    ProductType.BABY_FOOD: [
        "유아식", "분유", "이유식", "아기", "베이비", "유아"
    ],
    # 기저귀
    ProductType.BABY_DIAPER: [
        "기저귀", "밴드", "팬티형", "아기물티슈"
    ],
    # 육아용품
    ProductType.BABY_CARE: [
        "젖병", "젖꼭지", "유축기", "아기띠", "유모차", "카시트",
        "아기용품", "육아"
    ],
    
    # 반려동물 사료
    ProductType.PET_FOOD: [
        "사료", "강아지", "고양이", "반려동물", "펫", "간식"
    ],
    # 반려동물 용품
    ProductType.PET_SUPPLIES: [
        "애견", "애묘", "펫용품", "목줄", "장난감", "하우스", "화장실"
    ],
    
    # 도서
    ProductType.BOOK: [
        "도서", "책", "서적", "소설", "만화", "잡지", "교재"
    ],
    # 문구
    ProductType.STATIONERY: [
        "문구", "펜", "연필", "노트", "공책", "지우개", "자",
        "풀", "테이프", "스티커"
    ],
    # 완구
    ProductType.TOY: [
        "장난감", "완구", "인형", "블록", "레고", "피규어", "보드게임"
    ],
    # 운동
    ProductType.SPORTS: [
        "운동", "스포츠", "헬스", "요가", "수영", "등산", "자전거",
        "골프", "야구", "축구", "농구"
    ],
    # IT기기
    ProductType.ELECTRONICS: [
        "전자기기", "스마트폰", "태블릿", "이어폰", "헤드폰", "충전기",
        "케이블", "마우스", "키보드", "스피커"
    ],
}


# =============================================================================
# 타입별 한글 설명 매핑 (Type Description)
# =============================================================================
TYPE_DESCRIPTIONS: Dict[ProductType, str] = {
    ProductType.FOOD_SNACK: "과자/스낵류",
    ProductType.FOOD_BEVERAGE: "음료",
    ProductType.FOOD_INSTANT: "즉석식품",
    ProductType.FOOD_FRESH: "신선식품",
    ProductType.FOOD_DAIRY: "유제품",
    ProductType.FOOD_CONDIMENT: "조미료/소스",
    ProductType.FOOD_BAKERY: "베이커리",
    ProductType.HEALTH_SUPPLEMENT: "건강기능식품/영양제",
    ProductType.HEALTH_MEDICINE: "의약품",
    ProductType.HEALTH_PERSONAL_CARE: "개인위생용품",
    ProductType.HOME_KITCHEN: "주방용품",
    ProductType.HOME_CLEANING: "청소용품",
    ProductType.HOME_LIVING: "생활용품",
    ProductType.HOME_APPLIANCE: "가전제품",
    ProductType.FASHION_CLOTHING: "의류",
    ProductType.FASHION_SHOES: "신발",
    ProductType.FASHION_ACCESSORIES: "패션잡화",
    ProductType.BEAUTY_COSMETICS: "화장품",
    ProductType.BEAUTY_HAIRCARE: "헤어케어",
    ProductType.BABY_FOOD: "유아식품",
    ProductType.BABY_DIAPER: "기저귀/물티슈",
    ProductType.BABY_CARE: "육아용품",
    ProductType.PET_FOOD: "반려동물 사료",
    ProductType.PET_SUPPLIES: "반려동물 용품",
    ProductType.BOOK: "도서",
    ProductType.STATIONERY: "문구류",
    ProductType.TOY: "완구",
    ProductType.SPORTS: "스포츠용품",
    ProductType.ELECTRONICS: "전자기기",
    ProductType.OTHER: "기타",
}


# =============================================================================
# 핵심 키워드 가중치 (Weighted Keywords)
#
# 단순 키워드 매칭만으로 구분하기 어려운 경우(예: 화장품 vs 샴푸)
# 특정 핵심 단어에 더 높은 가중치를 부여하여 정확도를 높입니다.
# =============================================================================
CORE_KEYWORD_WEIGHTS: Dict[ProductType, Dict[str, int]] = {
    # 샴푸는 화장품으로도 인식될 수 있으므로 전용 키워드에 높은 점수를 부여합니다.
    ProductType.BEAUTY_HAIRCARE: {
        "샴푸": 5, "린스": 5, "트리트먼트": 5, "두피": 4, "모발": 4,
        "탈모": 4, "스칼프": 4, "헤어케어": 5, "케어샴푸": 5, "컨디셔너": 5,
        "헤어": 3, "헤어팩": 4, "염색": 3, "케라틴": 4, "헤어오일": 4,
    },
    # 개인위생용품도 화장품과 겹칠 수 있어 가중치를 둡니다.
    ProductType.HEALTH_PERSONAL_CARE: {
        "치약": 5, "칫솔": 5, "비누": 4, "바디워시": 4, "면도": 5,
        "생리대": 5, "위생용품": 4, "구강": 4, "데오드란트": 5,
    },
}


def detect_product_type(texts: List[str]) -> ProductType:
    """
    OCR로 읽은 텍스트 내용을 바탕으로 제품 타입을 자동으로 감지합니다.
    일반 매칭과 가중치 기반 스코어링을 통해 가장 적합한 카테고리를 찾습니다.
    
    Args:
        texts: OCR로 추출된 텍스트 리스트
        
    Returns:
        감지된 ProductType (감지 실패 시 ProductType.OTHER 반환)
    """
    # 1. 모든 텍스트를 하나로 합치고 소문자로 변환하여 검색 준비
    combined_text = " ".join(texts).lower()
    
    # 각 타입별로 점수를 계산할 딕셔너리
    scores: Dict[ProductType, float] = {}
    
    # 2. 모든 타입의 키워드 검사
    for ptype, keywords in TYPE_DETECTION_KEYWORDS.items():
        score = 0.0
        # 해당 타입에 가중치 매핑이 있다면 가져오고 없으면 빈 딕셔너리
        weights = CORE_KEYWORD_WEIGHTS.get(ptype, {})
        
        for keyword in keywords:
            if keyword in combined_text:
                # 가중치 테이블에 있는 키워드면 해당 점수, 아니면 기본 1점
                weight = weights.get(keyword, 1)
                score += weight
        
        # 하나라도 매칭된 키워드가 있으면 점수 기록
        if score > 0:
            scores[ptype] = score
    
    # 3. 가장 높은 점수를 받은 타입 반환
    if scores:
        # 딕셔너리의 value(점수)가 가장 큰 key(타입)를 찾습니다.
        detected_type = max(scores, key=scores.get)
        return detected_type
    
    # 아무것도 매칭되지 않았으면 '기타' 반환
    return ProductType.OTHER


def get_keywords_for_type(product_type: ProductType) -> List[str]:
    """
    제품 타입에 맞는 키워드 리스트를 반환합니다.
    (예: FOOD_SNACK -> ['가격', '유통기한', '알레르기' ...])
    
    Args:
        product_type: 제품 타입
        
    Returns:
        해당 타입의 키워드 리스트
    """
    # 딕셔너리에서 가져오되, 없으면 OTHER의 키워드를 기본값으로 사용
    return TYPE_KEYWORDS.get(product_type, TYPE_KEYWORDS[ProductType.OTHER])


def get_type_description(product_type: ProductType) -> str:
    """
    제품 타입에 대한 사용자 친화적인 한글 설명을 반환합니다.
    (예: FOOD_SNACK -> "과자/스낵류")
    
    Args:
        product_type: 제품 타입
        
    Returns:
        한글 설명 문자열
    """
    return TYPE_DESCRIPTIONS.get(product_type, "기타")


def is_keyword_valid_for_type(product_type: ProductType, keyword: str) -> bool:
    """
    특정 키워드가 해당 제품 타입에서 유의미한지 확인합니다.
    
    Args:
        product_type: 제품 타입
        keyword: 확인할 키워드 (예: "카페인함량")
        
    Returns:
        bool: 유효하면 True, 아니면 False
    """
    valid_keywords = get_keywords_for_type(product_type)
    return keyword in valid_keywords
