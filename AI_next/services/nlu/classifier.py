"""
KoELECTRA 기반 의도 분류기

사이트별 파인튜닝된 모델을 로드하고, 사용자 텍스트의 의도를 분류합니다.
- coupang: 28개 인텐트
- hearbe: 39개 인텐트
"""

import logging
from pathlib import Path
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# Lazy imports — torch/transformers are only available inside Docker
torch = None
ElectraForSequenceClassification = None
AutoTokenizer = None


def _ensure_deps():
    global torch, ElectraForSequenceClassification, AutoTokenizer
    if torch is not None:
        return
    import torch as _torch
    from transformers import (
        ElectraForSequenceClassification as _Electra,
        AutoTokenizer as _Tok,
    )
    torch = _torch
    ElectraForSequenceClassification = _Electra
    AutoTokenizer = _Tok

MAX_LENGTH = 64


class IntentClassifier:
    """KoELECTRA 의도 분류기"""

    def __init__(self, models_dir: Optional[str] = None):
        if models_dir is None:
            models_dir = Path(__file__).parent.parent.parent / "models"
        self._models_dir = Path(models_dir)
        self._models: Dict[str, Tuple] = {}
        self._device = "cpu"  # resolved in initialize()

    async def initialize(self):
        _ensure_deps()
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        model_configs = {
            "coupang": "coupang",
            "hearbe": "hearbe",
        }
        for site_id, subdir in model_configs.items():
            model_path = self._models_dir / subdir
            if not model_path.exists():
                logger.warning("Model not found for %s: %s", site_id, model_path)
                continue
            try:
                tokenizer = AutoTokenizer.from_pretrained(str(model_path))
                model = ElectraForSequenceClassification.from_pretrained(str(model_path))
                model.to(self._device)
                model.eval()
                id2label = model.config.id2label
                self._models[site_id] = (model, tokenizer, id2label)
                logger.info(
                    "Loaded KoELECTRA model for %s (%d labels) on %s",
                    site_id, len(id2label), self._device,
                )
            except Exception as e:
                logger.error("Failed to load model for %s: %s", site_id, e)

    def classify(self, text: str, site_id: str) -> Tuple[str, float]:
        """
        사용자 텍스트의 의도를 분류합니다.

        Returns:
            (intent_name, confidence)  예: ("search_products", 0.95)
        """
        if site_id not in self._models:
            return ("unknown", 0.0)

        model, tokenizer, id2label = self._models[site_id]
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_LENGTH,
            padding=True,
        )
        inputs = {k: v.to(self._device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            confidence, predicted_id = torch.max(probs, dim=-1)

        label_key = str(predicted_id.item())
        intent_name = id2label.get(label_key, "unknown")
        return (intent_name, confidence.item())

    def classify_top_k(self, text: str, site_id: str, k: int = 3) -> list:
        """Top-k 분류 결과 반환 (디버깅용)"""
        if site_id not in self._models:
            return [("unknown", 0.0)]

        model, tokenizer, id2label = self._models[site_id]
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_LENGTH,
            padding=True,
        )
        inputs = {k_: v.to(self._device) for k_, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            top_k = torch.topk(probs, k, dim=-1)

        results = []
        for i in range(k):
            idx = top_k.indices[0][i].item()
            conf = top_k.values[0][i].item()
            label = id2label.get(str(idx), "unknown")
            results.append((label, conf))
        return results

    def is_ready(self, site_id: Optional[str] = None) -> bool:
        if site_id:
            return site_id in self._models
        return len(self._models) > 0

    def available_sites(self) -> list:
        return list(self._models.keys())
