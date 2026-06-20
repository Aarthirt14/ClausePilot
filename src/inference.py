import logging
import os
import threading
from typing import Dict, List, Tuple

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from src.category_mapper import enhance_label_with_text_detection

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# Model cache
#
# Loading a BERT checkpoint from disk (reading weights, building the
# tokenizer, moving to device) takes anywhere from 1-10+ seconds. The
# original implementation called load_bert_model() inside every
# infer_clauses() call, which meant every PDF upload paid that cost
# again. This cache loads each (model_dir) combination exactly once
# per process and reuses it for the lifetime of the app.
#
# A lock guards first-load so two concurrent requests in a threaded
# Flask dev server don't both try to load the model at once.
# ----------------------------------------------------------------------
_MODEL_CACHE: Dict[str, Tuple[object, object, torch.device]] = {}
_CACHE_LOCK = threading.Lock()


def assign_severity(label: str, confidence: float) -> str:
    """
    Map model output to risk severity.

    Rules:
    - Neutral => None
    - confidence >= 0.85 => High
    - 0.65 <= confidence < 0.85 => Medium
    - confidence < 0.65 => Low
    """
    if label == "Neutral":
        return "None"
    if confidence >= 0.85:
        return "High"
    if confidence >= 0.65:
        return "Medium"
    return "Low"


def load_bert_model(model_dir: str = "models/bert_model"):
    """
    Load the fine-tuned BERT model and tokenizer from disk, caching the
    result so repeated calls (e.g. one per uploaded contract) are free
    after the first.

    Returns:
        tokenizer, model, device
    """
    cached = _MODEL_CACHE.get(model_dir)
    if cached is not None:
        return cached

    with _CACHE_LOCK:
        # Another thread may have populated the cache while we waited.
        cached = _MODEL_CACHE.get(model_dir)
        if cached is not None:
            return cached

        if not os.path.isdir(model_dir):
            raise FileNotFoundError(f"Model directory not found: {model_dir}")

        logger.info("Loading BERT model from %s (first use, will be cached)", model_dir)
        tokenizer = AutoTokenizer.from_pretrained(model_dir)
        model = AutoModelForSequenceClassification.from_pretrained(model_dir)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        model.eval()

        _MODEL_CACHE[model_dir] = (tokenizer, model, device)
        return _MODEL_CACHE[model_dir]


def clear_model_cache() -> None:
    """Drop all cached models. Mainly useful for tests and hot-reloading."""
    with _CACHE_LOCK:
        _MODEL_CACHE.clear()


def infer_clauses(
    clauses: List[str],
    model_dir: str = "models/bert_model",
    max_length: int = 256,
) -> List[Dict[str, object]]:
    """
    Run BERT inference on a list of contract clauses.

    Args:
        clauses: List of clause texts.
        model_dir: Path to saved BERT model directory.
        max_length: Maximum token length for truncation.

    Returns:
        List of dictionaries in format:
        [
          {
            "clause": "...",
            "label": "Liability Risk",
            "confidence": 0.91
          }
        ]
    """
    if not clauses:
        return []

    tokenizer, model, device = load_bert_model(model_dir=model_dir)

    results: List[Dict[str, object]] = []
    with torch.no_grad():
        for clause in clauses:
            clause_text = (clause or "").strip()
            if not clause_text:
                continue

            encoded = tokenizer(
                clause_text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
                padding=False,
            )
            encoded = {key: value.to(device) for key, value in encoded.items()}

            outputs = model(**encoded)
            probs = torch.softmax(outputs.logits, dim=-1).squeeze(0)

            pred_id = int(torch.argmax(probs).item())
            confidence = float(probs[pred_id].item())

            label_map = model.config.id2label or {}
            raw_label = str(label_map.get(pred_id, pred_id))

            # Enhance label with category mapping and text-based detection (includes IP Risk)
            enhanced_label, adjusted_confidence, detection_method = enhance_label_with_text_detection(
                raw_label, clause_text, confidence
            )

            severity = assign_severity(enhanced_label, adjusted_confidence)

            results.append(
                {
                    "clause": clause_text,
                    "label": enhanced_label,
                    "raw_label": raw_label,
                    "confidence": round(adjusted_confidence, 4),
                    "original_confidence": round(confidence, 4),
                    "severity": severity,
                    "detection_method": detection_method,
                }
            )

    return results
