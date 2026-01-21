# OCR 서비스 설치 및 실행 가이드

## �️ 가상환경 설정

프로젝트 의존성을 격리하기 위해 가상환경을 생성합니다:

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (Linux/Mac)
source venv/bin/activate
```

---

## 🔐 환경변수 (.env) 설정

프로젝트 루트에 `.env` 파일을 생성하고 아래 내용을 설정합니다:

```env
(LLM 요약에 필요)
GMS_KEY=your_google_gemini_api_key_here



## �📦 PaddlePaddle 설치

pip를 사용하여 PaddlePaddle을 설치하려면 아래 명령어를 참고하세요:

```bash
# CUDA 11.8 버전
python -m pip install paddlepaddle-gpu==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/

# CUDA 12.6 버전
python -m pip install paddlepaddle-gpu==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/

# CPU 버전
python -m pip install paddlepaddle==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
```

PaddlePaddle 설치에 대한 자세한 내용은 [PaddlePaddle 공식 웹사이트](https://www.paddlepaddle.org.cn/)를 참조하세요.

---

## 📦 PaddleOCR 설치

PyPI에서 PaddleOCR 최신 버전을 설치합니다:

```bash
python -m pip install paddleocr
```

---

## 📦 기타 의존성 설치

```bash
pip install requests python-dotenv
```

---

## 🚀 실행 방법

### Step 1. OCR 실행 (이미지 → 텍스트)

이미지 파일에서 텍스트를 추출합니다.

```bash
python paddleocr_korean_test.py
```

### Step 2. LLM 요약 실행 (텍스트 → 정보 요약)

OCR 결과 파일을 바탕으로 상품 정보를 분석합니다.

```bash
python ocr_llm_summarizer.py --input output/<파일명>_res_texts.json
```
