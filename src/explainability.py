from typing import Dict, List

import numpy as np
import shap
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from transformers import pipeline

from src.category_mapper import get_category_description
from src.scoring.advanced_risk_scoring import (
    extract_monetary_value,
    extract_duration,
    detect_high_risk_clause,
    RISK_CATEGORIES
)


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

    # Generate risk explanation with impact reasoning
    risk_explanation = generate_risk_explanation(
        clause=clause_text,
        label=predicted_label,
        positive_words=top_positive,
        negative_words=top_negative
    )

    return {
        "label": predicted_label,
        "top_contributing_words": top_tokens,
        "top_positive_words": top_positive,
        "top_negative_words": top_negative,
        "shap_threshold": shap_threshold,
        "risk_explanation": risk_explanation,
    }


def generate_risk_explanation(
    clause: str,
    label: str,
    positive_words: List[str],
    negative_words: List[str]
) -> Dict[str, object]:
    """
    Generate comprehensive risk explanation with impact reasoning.
    
    Returns:
    {
        "category_description": "...",
        "why_flagged": "...",
        "potential_impact": [...],
        "risk_factors": [...],
        "extracted_values": {...}
    }
    """
    # Get category description
    category_desc = get_category_description(label)
    
    # Extract metadata
    monetary_value = extract_monetary_value(clause)
    durations = extract_duration(clause)
    
    # Detect high-risk patterns
    high_risk_detection = detect_high_risk_clause(clause, label)
    risk_triggers = high_risk_detection.get("risk_triggers", [])
    
    # Generate why_flagged explanation
    why_flagged_parts = []
    
    if positive_words:
        why_flagged_parts.append(
            f"Key risk indicators detected: {', '.join(positive_words[:3])}"
        )
    
    if risk_triggers:
        why_flagged_parts.append(
            f"High-risk patterns: {'; '.join(risk_triggers[:2])}"
        )
    
    if monetary_value > 0:
        why_flagged_parts.append(
            f"Financial exposure identified: ${monetary_value:,.0f}"
        )
    
    why_flagged = ". ".join(why_flagged_parts) if why_flagged_parts else "Pattern matching indicates potential risk."
    
    # Generate potential_impact based on category
    potential_impacts = {
        "Liability Risk": [
            "Financial liability for damages or losses",
            "Legal defense costs and settlements",
            "Reputational harm from breach claims"
        ],
        "Termination Risk": [
            "Unexpected contract termination",
            "Loss of revenue stream",
            "Operational disruption and transition costs"
        ],
        "Data Privacy Risk": [
            "Regulatory fines (GDPR: up to €20M or 4% revenue)",
            "Data breach notification and remediation costs",
            "Loss of customer trust and business"
        ],
        "Payment Risk": [
            "Cash flow impact from penalties or fees",
            "Budget overruns beyond planned costs",
            "Dispute and collection costs"
        ],
        "IP Risk": [
            "Loss of intellectual property ownership",
            "Inability to monetize or license IP",
            "Third-party IP infringement claims"
        ],
        "Neutral": ["Minimal impact expected"]
    }
    
    impact_list = potential_impacts.get(label, ["Potential business impact"])
    
    # Add monetary impact if applicable
    if monetary_value >= 100000:
        impact_list.insert(0, f"Direct financial exposure: ${monetary_value:,.0f}")
    
    # Combine risk factors
    risk_factors = []
    
    if risk_triggers:
        risk_factors.extend(risk_triggers[:3])
    
    # Add duration risks
    if durations.get("notice_period_days", 0) > 0:
        days = durations["notice_period_days"]
        if days < 30:
            risk_factors.append(f"Short notice period: only {days} days")
    
    # Add severity flags from category keywords
    category_info = RISK_CATEGORIES.get(label, {})
    high_risk_kws = category_info.get("high_risk_keywords", [])
    clause_lower = clause.lower()
    matched_kws = [kw for kw in high_risk_kws if kw in clause_lower]
    
    if matched_kws:
        risk_factors.append(f"Contains high-risk terms: {', '.join(matched_kws[:3])}")
    
    return {
        "category_description": category_desc,
        "why_flagged": why_flagged,
        "potential_impact": impact_list,
        "risk_factors": risk_factors if risk_factors else ["Standard contractual language"],
        "extracted_values": {
            "monetary_amount": f"${monetary_value:,.0f}" if monetary_value > 0 else "None detected",
            "durations": durations,
        }
    }

