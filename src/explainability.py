from typing import Dict, List

import numpy as np
import shap
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from transformers import pipeline


def _normalize_prediction_scores(raw_output) -> List[Dict[str, float]]:
    """Normalize pipeline outputs into a list of {label, score} dicts."""
    if isinstance(raw_output, dict):
        return [raw_output]

    if not isinstance(raw_output, list) or not raw_output:
        return []

    # Case 1: [ {label, score}, ... ]
    if isinstance(raw_output[0], dict):
        return raw_output

    # Case 2: [ [ {label, score}, ... ] ]
    if isinstance(raw_output[0], list) and raw_output[0] and isinstance(raw_output[0][0], dict):
        return raw_output[0]

    return []


def explain_clause_with_shap(
    clause: str,
    model_dir: str = "models/bert_model",
    top_k: int = 5,
    shap_threshold: float = 0.01,
) -> Dict[str, object]:
    """
    Explain BERT prediction for a single clause using SHAP.

    Returns:
    {
      "label": "Liability Risk",
      "top_contributing_words": ["liability", "indemnify", ...]
    }
    """
    clause_text = (clause or "").strip()
    if not clause_text:
        return {
            "label": "",
            "top_contributing_words": [],
        }

    clf = pipeline(
        "text-classification",
        model=model_dir,
        tokenizer=model_dir,
        top_k=None,
    )

    prediction_scores = _normalize_prediction_scores(clf(clause_text))
    if not prediction_scores:
        return {
            "label": "",
            "top_contributing_words": [],
        }

    best = max(prediction_scores, key=lambda item: item["score"])
    predicted_label = best["label"]

    explainer = shap.Explainer(clf)
    shap_values = explainer([clause_text])

    output_names = getattr(shap_values, "output_names", [])
    class_names = list(output_names) if isinstance(output_names, (list, tuple, np.ndarray)) else []
    try:
        target_class_idx = class_names.index(predicted_label)
    except ValueError:
        target_class_idx = int(np.argmax([item["score"] for item in prediction_scores]))

    raw_values = np.array(shap_values.values[0])
    if raw_values.ndim == 1:
        token_values = raw_values
    else:
        max_class_idx = raw_values.shape[-1] - 1
        target_class_idx = min(max(target_class_idx, 0), max_class_idx)
        token_values = raw_values[:, target_class_idx]

    token_data = shap_values.data[0]

    positive_scores = []
    negative_scores = []

    def _normalize_token(token: str) -> str:
        cleaned = token.replace("##", "").strip().lower()
        cleaned = cleaned.strip(".,;:!?()[]{}\"'`-_/\\")
        return cleaned

    for token, score in zip(token_data, token_values):
        raw_token = str(token).strip()
        t = _normalize_token(raw_token)
        if not t:
            continue
        if t in ENGLISH_STOP_WORDS:
            continue
        score_value = float(score)
        if abs(score_value) < shap_threshold:
            continue
        if score_value > 0:
            positive_scores.append((t, score_value))
        else:
            negative_scores.append((t, score_value))

    positive_scores.sort(key=lambda x: x[1], reverse=True)
    negative_scores.sort(key=lambda x: x[1])

    def _top_unique(items: List[tuple], limit: int) -> List[str]:
        seen = set()
        output: List[str] = []
        for token, _ in items:
            if token in seen:
                continue
            seen.add(token)
            output.append(token)
            if len(output) >= limit:
                break
        return output

    top_positive = _top_unique(positive_scores, top_k)
    top_negative = _top_unique(negative_scores, top_k)

    top_tokens: List[str] = []
    for token in top_positive + top_negative:
        if token not in top_tokens:
            top_tokens.append(token)
        if len(top_tokens) >= top_k:
            break

    return {
        "label": predicted_label,
        "top_contributing_words": top_tokens,
        "top_positive_words": top_positive,
        "top_negative_words": top_negative,
        "shap_threshold": shap_threshold,
    }
