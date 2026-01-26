# 🚧 OCR 미구현 부분 상세 가이드

> **팀원 분들께**: 이 문서는 OCR 파이프라인과 연동이 필요한 미구현 기능들을 상세히 설명합니다.

---

## 📋 미구현 기능 요약

| 기능 | 우선순위 | 담당 예상 |
|------|---------|----------|
| 웹 연동 (자동 OCR 트리거) | ⭐⭐⭐ 높음 | 프론트엔드 / Playwright |
| MCP Playwright 통합 | ⭐⭐⭐ 높음 | Playwright |
| REST API 인터페이스 | ⭐⭐ 중간 | 백엔드 |
| 실시간 WebSocket 연동 | ⭐ 낮음 | 백엔드 (선택) |

---

## 1. 웹 연동 - 자동 OCR 트리거

### 현재 상태

```python
# 현재는 수동으로 함수를 호출해야 함
from ocr_pipeline import process_product_from_urls

result = process_product_from_urls(
    image_urls=["https://...", "https://..."],
    site="coupang"
)
print(result["summary"])  # TTS용 요약
```

### 필요한 구현

#### 1-1. URL 패턴 감지 함수

상품 페이지인지 아닌지 판별하는 로직이 필요합니다.

```python
import re

# 상품 페이지 URL 패턴 정의
PRODUCT_PAGE_PATTERNS = {
    "coupang": [
        r"coupang\.com/vp/products/\d+",      # 상품 상세
        r"coupang\.com/np/products/\d+",      # 상품 상세 (다른 형식)
    ],
    "naver": [
        r"smartstore\.naver\.com/.+/products/\d+",  # 스마트스토어
        r"shopping\.naver\.com/product/\d+",        # 네이버 쇼핑
    ],
}

# 제외할 URL 패턴 (검색 결과, 카테고리 등)
EXCLUDE_PATTERNS = [
    r"/search",
    r"/category",
    r"/cart",
    r"/login",
    r"/order",
]

def is_product_page(url: str) -> tuple[bool, str]:
    """
    URL이 상품 페이지인지 판별합니다.
    
    Returns:
        (is_product: bool, site_name: str)
    """
    # 제외 패턴 체크
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return False, ""
    
    # 상품 페이지 패턴 체크
    for site, patterns in PRODUCT_PAGE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True, site
    
    return False, ""

# 사용 예시
is_product, site = is_product_page("https://www.coupang.com/vp/products/123456")
# (True, "coupang")

is_product, site = is_product_page("https://www.coupang.com/np/search?q=샴푸")
# (False, "")
```

#### 1-2. 트리거 조건

**옵션 A: 페이지 로드 완료 시 자동 실행**
```javascript
// 브라우저 확장 또는 Electron 앱에서
if (isProductPage(window.location.href)) {
    // OCR 파이프라인 호출
    triggerOCR(window.location.href);
}
```

**옵션 B: 사용자 버튼 클릭 시 실행 (권장)**
```javascript
// 사용자가 "상품 정보 읽기" 버튼을 누르면 실행
document.getElementById('ocr-button').addEventListener('click', () => {
    triggerOCR(window.location.href);
});
```

**옵션 C: 음성 명령으로 실행**
```
사용자: "이 상품 설명해줘"
→ STT가 인식
→ OCR 파이프라인 실행
→ TTS로 결과 읽기
```

---

## 2. MCP Playwright 통합

### 현재 상태

CSS 셀렉터는 이미 정의되어 있습니다 (`image_fetcher.py`):

```python
SITE_CONFIGS = {
    "coupang": {
        "selector": ".product-detail-content-inside img",  # 상품 상세 이미지
        "exclude_patterns": ["/banner/", "/ad/", "/icon/", ...],
    },
    "naver": {
        "selector": "#INTRODUCE img",  # 상품 소개 이미지
        "exclude_patterns": ["/ad/", "/banner/", ...],
    },
}
```

### 필요한 구현

#### 2-1. Playwright로 이미지 URL 추출

```python
from playwright.async_api import async_playwright
from image_fetcher import get_selector, filter_product_images

async def extract_product_images(page_url: str, site: str = "auto") -> list[str]:
    """
    Playwright로 상품 페이지에서 이미지 URL을 추출합니다.
    
    Args:
        page_url: 상품 페이지 URL
        site: 사이트 이름 ("coupang", "naver", "auto")
    
    Returns:
        필터링된 이미지 URL 리스트
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 1. 페이지 접속
        await page.goto(page_url, wait_until="networkidle")
        
        # 2. 사이트 자동 감지
        if site == "auto":
            if "coupang" in page_url:
                site = "coupang"
            elif "naver" in page_url:
                site = "naver"
        
        # 3. CSS 셀렉터로 이미지 추출
        selector = get_selector(site)  # image_fetcher.py에서 가져옴
        
        if not selector:
            # 셀렉터가 없으면 모든 이미지 가져오기
            selector = "img"
        
        # 4. 이미지 URL 추출
        images = await page.query_selector_all(selector)
        image_urls = []
        
        for img in images:
            src = await img.get_attribute("src")
            if src:
                # 상대 경로를 절대 경로로 변환
                if src.startswith("//"):
                    src = "https:" + src
                elif src.startswith("/"):
                    src = page_url.split("/")[0] + "//" + page_url.split("/")[2] + src
                image_urls.append(src)
        
        await browser.close()
        
        # 5. 광고/배너 필터링
        filtered_urls = filter_product_images(image_urls, site=site)
        
        return filtered_urls

# 사용 예시
# urls = await extract_product_images("https://www.coupang.com/vp/products/123456")
```

#### 2-2. OCR 파이프라인과 연동

```python
from ocr_pipeline import process_product_from_urls

async def process_product_page(page_url: str) -> dict:
    """
    상품 페이지 URL을 받아 OCR 처리 후 요약을 반환합니다.
    
    이 함수가 전체 흐름을 관리합니다:
    1. Playwright로 이미지 URL 추출
    2. OCR 파이프라인 실행
    3. 요약 결과 반환
    """
    # 1. 이미지 URL 추출
    image_urls = await extract_product_images(page_url)
    
    if not image_urls:
        return {
            "error": "상품 이미지를 찾을 수 없습니다.",
            "summary": []
        }
    
    # 2. OCR 파이프라인 실행
    result = process_product_from_urls(
        image_urls=image_urls,
        site="auto"
    )
    
    return result

# 사용 예시
# result = await process_product_page("https://www.coupang.com/vp/products/123456")
# print(result["summary"])  # TTS로 읽어줄 내용
```

---

## 3. REST API 인터페이스 (선택)

### FastAPI 예시

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="OCR API")

class OCRRequest(BaseModel):
    urls: List[str] = None
    page_url: str = None
    site: str = "auto"

class OCRResponse(BaseModel):
    product_type: str
    product_name: str
    summary: List[str]
    keywords: dict

@app.post("/api/ocr/process", response_model=OCRResponse)
async def process_ocr(request: OCRRequest):
    """
    OCR 처리 API
    
    - urls: 이미지 URL 리스트 (직접 전달)
    - page_url: 상품 페이지 URL (Playwright로 이미지 추출)
    """
    if request.page_url:
        # Playwright로 이미지 추출 후 처리
        result = await process_product_page(request.page_url)
    elif request.urls:
        # 직접 전달된 URL로 처리
        result = process_product_from_urls(request.urls, site=request.site)
    else:
        raise HTTPException(status_code=400, detail="urls 또는 page_url 필요")
    
    return result

# 실행: uvicorn api:app --reload --port 8000
```

### API 호출 예시

```bash
# 이미지 URL 직접 전달
curl -X POST "http://localhost:8000/api/ocr/process" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://...", "https://..."], "site": "coupang"}'

# 상품 페이지 URL 전달 (Playwright 사용)
curl -X POST "http://localhost:8000/api/ocr/process" \
  -H "Content-Type: application/json" \
  -d '{"page_url": "https://www.coupang.com/vp/products/123456"}'
```

---

## 4. 전체 연동 흐름도

```
[사용자]
    │
    ▼ 상품 페이지 접속 또는 음성 명령
    │
[트리거 감지] ─────────────────────────────┐
    │ (is_product_page 함수)              │
    ▼                                     │
[Playwright] ◄────────────────────────────┘
    │ extract_product_images()
    │ - 페이지 접속
    │ - CSS 셀렉터로 이미지 추출
    │ - 광고/배너 필터링
    ▼
[OCR 파이프라인] ─── process_product_from_urls()
    │
    ├─ 이미지 다운로드
    ├─ PaddleOCR 처리
    ├─ 텍스트 전처리/병합
    ├─ 상품 타입 감지
    └─ LLM 요약 생성
    │
    ▼
[TTS 출력]
    │ result["summary"]를 음성으로 변환
    ▼
[사용자 청취]
```

---

## 📞 질문이 있으시면

OCR 파이프라인 관련 문의는 해당 모듈 담당자에게 연락해주세요.

**핵심 진입점:**
- `ocr_pipeline.process_product_from_urls()` - URL 기반 처리
- `ocr_pipeline.process_product_image()` - 로컬 이미지 처리
- `image_fetcher.get_selector()` - 사이트별 CSS 셀렉터
- `image_fetcher.filter_product_images()` - 이미지 필터링
