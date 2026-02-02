# OCR 공통 유틸과 캐시 처리
import hashlib
import json
import logging
import os
import tempfile
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple, List

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# ==================== 이미지 유틸 ====================


def save_json(data: Dict[str, Any], output_path: str, indent: int = 2) -> None:
    """JSON 파일 저장 (원자적 쓰기: 임시파일에 쓴 뒤 교체하여 동시성 안전)"""
    dir_name = os.path.dirname(output_path) or "."
    os.makedirs(dir_name, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        os.replace(tmp_path, output_path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def load_json(input_path: str) -> Dict[str, Any]:
    """JSON 파일 로드 (공통 함수)"""
    with open(input_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_image_size(image_path: str) -> Tuple[int, int]:
    """이미지 크기 반환 (width, height)"""
    with Image.open(image_path) as img:
        return img.size


def prepare_image_for_ocr(img: Image.Image) -> np.ndarray:
    """PIL Image를 OCR용 BGR numpy 배열로 변환 (RGBA/기타 모드 → RGB → BGR)"""
    if img.mode != 'RGB':
        img = img.convert('RGB')
    arr = np.array(img)
    return arr[:, :, ::-1]  # RGB → BGR


# ==================== 캐싱 함수 ====================

# 캐시 디렉토리를 모듈 위치 기준 절대 경로로 설정 (실행 디렉토리에 무관)
_MODULE_DIR = Path(__file__).resolve().parent
CACHE_DIR = str(_MODULE_DIR / "cache")
CACHE_SUMMARIES_DIR = os.path.join(CACHE_DIR, "summaries")
CACHE_LLM_SUMMARIES_DIR = os.path.join(CACHE_DIR, "llm_summaries")
CACHE_PIPELINE_RESULTS_DIR = os.path.join(CACHE_DIR, "pipeline_results")
CACHE_METADATA_PATH = os.path.join(CACHE_DIR, "metadata.json")
CACHE_VERSION = "1.0"
DEFAULT_CACHE_TTL_DAYS = 30

# 캐시 메타데이터 동시 쓰기 보호
_metadata_lock = threading.Lock()


def compute_image_hash(image_path: str) -> str:
    """이미지 파일의 SHA256 해시 계산 (파일 전체를 읽어 정확한 캐시 키 생성)"""
    hash_sha256 = hashlib.sha256()
    chunk_size = 1024 * 1024  # 1MB 단위로 읽기

    with open(image_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hash_sha256.update(chunk)

    return hash_sha256.hexdigest()


def compute_url_hash(url: str) -> str:
    """URL의 SHA256 해시 계산"""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def get_cache_path(image_hash: str) -> str:
    """캐시 파일 경로 반환"""
    return os.path.join(CACHE_SUMMARIES_DIR, f"{image_hash[:16]}.json")


def is_cache_valid(cache_data: Dict[str, Any], ttl_days: int = DEFAULT_CACHE_TTL_DAYS) -> bool:
    """캐시 유효성 검사 (버전 + TTL)"""
    # 버전 체크
    if cache_data.get("cache_version") != CACHE_VERSION:
        return False

    # TTL 체크
    cached_at_str = cache_data.get("cached_at")
    if not cached_at_str:
        return False

    try:
        cached_at = datetime.fromisoformat(cached_at_str)
        now = datetime.now()
        if now - cached_at > timedelta(days=ttl_days):
            return False
    except (ValueError, TypeError):
        return False

    return True


def load_cache(image_hash: str, ttl_days: int = DEFAULT_CACHE_TTL_DAYS) -> Optional[Dict[str, Any]]:
    """캐시 로드 (유효하지 않으면 None 반환)"""
    cache_path = get_cache_path(image_hash)

    if not os.path.exists(cache_path):
        return None

    try:
        cache_data = load_json(cache_path)
        if is_cache_valid(cache_data, ttl_days):
            return cache_data.get("summary")
        else:
            # 만료된 캐시 삭제
            os.remove(cache_path)
            return None
    except Exception:
        return None


def save_cache(image_hash: str, summary: Dict[str, Any]) -> None:
    """캐시 저장"""
    os.makedirs(CACHE_SUMMARIES_DIR, exist_ok=True)

    cache_data = {
        "cache_version": CACHE_VERSION,
        "image_hash": image_hash,
        "cached_at": datetime.now().isoformat(),
        "summary": summary
    }

    cache_path = get_cache_path(image_hash)
    save_json(cache_data, cache_path)


def compute_summary_hash(
    texts: List[str],
    product_type: str,
    model: str,
    prompt_version: str,
) -> str:
    """LLM summary cache key"""
    normalized = "\n".join(t.strip() for t in texts if isinstance(t, str))
    raw = f"{prompt_version}|{model}|{product_type}|{normalized}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_summary_cache_path(summary_hash: str) -> str:
    """LLM summary cache path"""
    return os.path.join(CACHE_LLM_SUMMARIES_DIR, f"{summary_hash[:16]}.json")


def load_summary_cache(summary_hash: str, ttl_days: int = DEFAULT_CACHE_TTL_DAYS) -> Optional[Dict[str, Any]]:
    """Load cached LLM summary if valid"""
    cache_path = get_summary_cache_path(summary_hash)
    if not os.path.exists(cache_path):
        return None
    try:
        cache_data = load_json(cache_path)
        if is_cache_valid(cache_data, ttl_days):
            return cache_data.get("summary")
        os.remove(cache_path)
        return None
    except Exception:
        return None


def save_summary_cache(summary_hash: str, summary: Dict[str, Any]) -> None:
    """Save LLM summary cache"""
    os.makedirs(CACHE_LLM_SUMMARIES_DIR, exist_ok=True)
    cache_data = {
        "cache_version": CACHE_VERSION,
        "summary_hash": summary_hash,
        "cached_at": datetime.now().isoformat(),
        "summary": summary,
    }
    cache_path = get_summary_cache_path(summary_hash)
    save_json(cache_data, cache_path)


def compute_imageset_hash(image_paths: List[str]) -> str:
    """파일 메타데이터(경로, 크기, 수정시간) 기반 빠른 해시 계산"""
    parts: List[str] = []
    for path in image_paths:
        stat = os.stat(path)
        parts.append(f"{os.path.abspath(path)}:{stat.st_size}:{stat.st_mtime}")
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def compute_urllist_hash(urls: List[str], site: str) -> str:
    """Compute a stable hash for a list of URLs"""
    normalized = [u.strip() for u in urls if isinstance(u, str)]
    joined = "\n".join(normalized)
    raw = f"{site}|{joined}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_pipeline_cache_path(pipeline_hash: str) -> str:
    """Pipeline result cache path"""
    return os.path.join(CACHE_PIPELINE_RESULTS_DIR, f"{pipeline_hash[:16]}.json")


def load_pipeline_cache(pipeline_hash: str, ttl_days: int = DEFAULT_CACHE_TTL_DAYS) -> Optional[Dict[str, Any]]:
    """Load cached pipeline result if valid"""
    cache_path = get_pipeline_cache_path(pipeline_hash)
    if not os.path.exists(cache_path):
        return None
    try:
        cache_data = load_json(cache_path)
        if is_cache_valid(cache_data, ttl_days):
            return cache_data.get("result")
        os.remove(cache_path)
        return None
    except Exception:
        return None


def save_pipeline_cache(pipeline_hash: str, result: Dict[str, Any]) -> None:
    """Save pipeline result cache"""
    os.makedirs(CACHE_PIPELINE_RESULTS_DIR, exist_ok=True)
    cache_data = {
        "cache_version": CACHE_VERSION,
        "pipeline_hash": pipeline_hash,
        "cached_at": datetime.now().isoformat(),
        "result": result,
    }
    cache_path = get_pipeline_cache_path(pipeline_hash)
    save_json(cache_data, cache_path)


def update_cache_metadata(hit: bool = False) -> None:
    """캐시 메타데이터 업데이트 (히트율 추적, 스레드 안전)"""
    with _metadata_lock:
        os.makedirs(CACHE_DIR, exist_ok=True)

        if os.path.exists(CACHE_METADATA_PATH):
            try:
                metadata = load_json(CACHE_METADATA_PATH)
            except Exception:
                metadata = {
                    "total_requests": 0,
                    "cache_hits": 0,
                    "cache_misses": 0,
                    "hit_rate": 0.0
                }
        else:
            metadata = {
                "total_requests": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "hit_rate": 0.0
            }

        metadata["total_requests"] += 1
        if hit:
            metadata["cache_hits"] += 1
        else:
            metadata["cache_misses"] += 1

        total = metadata["total_requests"]
        metadata["hit_rate"] = metadata["cache_hits"] / total if total > 0 else 0.0

        save_json(metadata, CACHE_METADATA_PATH)


def get_cache_stats() -> Dict[str, Any]:
    """캐시 통계 조회"""
    if not os.path.exists(CACHE_METADATA_PATH):
        return {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "hit_rate": 0.0
        }
    return load_json(CACHE_METADATA_PATH)


def cleanup_expired_caches(ttl_days: int = DEFAULT_CACHE_TTL_DAYS) -> int:
    """만료된 캐시 파일을 일괄 삭제하고 삭제된 파일 수를 반환"""
    removed = 0
    for cache_dir in [CACHE_SUMMARIES_DIR, CACHE_LLM_SUMMARIES_DIR, CACHE_PIPELINE_RESULTS_DIR]:
        if not os.path.exists(cache_dir):
            continue
        for fname in os.listdir(cache_dir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(cache_dir, fname)
            try:
                data = load_json(fpath)
                if not is_cache_valid(data, ttl_days):
                    os.remove(fpath)
                    removed += 1
            except Exception:
                pass
    return removed
