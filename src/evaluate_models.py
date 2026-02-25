"""Evaluation pipeline for contract risk classification."""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Tuple
import hashlib

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split

from src.calibration.reliability import compute_ece, plot_reliability_diagram
from src.calibration.temperature_scaling import apply_temperature, fit_temperature
from src.data_processing.cleaning import normalize_text
from src.evaluation.error_analysis import collect_error_samples, save_error_samples_csv
from src.evaluation.metrics import compute_metrics, plot_class_distribution, plot_confusion_matrix
from src.modeling.baseline import baseline_predict, baseline_predict_proba, train_baseline
from src.modeling.bert_model import predict_logits, predict_with_transformer


logger = logging.getLogger(__name__)


def load_and_clean_dataset(data_path: str) -> Tuple[List[str], List[str], List[str], int]:
    """Load dataset, normalize text, and remove duplicates using hashing."""
    df = pd.read_csv(data_path).dropna(subset=["clause_text", "risk_label"])
    seen_hashes = set()
    cleaned_texts: List[str] = []
    raw_texts: List[str] = []
    labels: List[str] = []
    removed_duplicates = 0

    for clause_text, label in zip(df["clause_text"], df["risk_label"]):
        normalized = normalize_text(str(clause_text))
        if not normalized:
            continue
        hashed = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        if hashed in seen_hashes:
            removed_duplicates += 1
            continue
        seen_hashes.add(hashed)
        cleaned_texts.append(normalized)
        raw_texts.append(str(clause_text))
        labels.append(str(label))

    return cleaned_texts, raw_texts, labels, removed_duplicates


def split_dataset(
    texts: List[str],
    raw_texts: List[str],
    labels: List[str],
    test_size: float = 0.2,
    seed: int = 42,
) -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
    """Split dataset while preserving raw and cleaned text alignment."""
    x_train, x_val, y_train, y_val, raw_train, raw_val = train_test_split(
        texts,
        labels,
        raw_texts,
        test_size=test_size,
        random_state=seed,
        stratify=labels,
    )
    return x_train, x_val, y_train, y_val, raw_val


def main() -> None:
    os.makedirs("evaluation", exist_ok=True)

    cleaned_texts, raw_texts, labels, removed_count = load_and_clean_dataset("data/cuad_with_risk.csv")
    if removed_count:
        logger.info("Removed %s duplicate clauses during evaluation cleaning", removed_count)
    x_train, x_val, y_train, y_val, raw_val = split_dataset(cleaned_texts, raw_texts, labels)

    unique_labels = sorted(set(y_val))

    baseline_model, baseline_vectorizer = train_baseline(x_train, y_train)
    baseline_preds, baseline_conf = baseline_predict(baseline_model, baseline_vectorizer, x_val)
    baseline_probs = baseline_predict_proba(baseline_model, baseline_vectorizer, x_val)

    bert_preds, bert_conf, bert_probs = predict_with_transformer("models/bert_model", x_val)

    baseline_metrics = compute_metrics(y_val, baseline_preds, unique_labels)
    bert_metrics = compute_metrics(y_val, bert_preds, unique_labels)

    plot_confusion_matrix(y_val, bert_preds, unique_labels, "evaluation/confusion_matrix.png", "BERT Confusion Matrix")
    plot_class_distribution(y_val, "evaluation/class_distribution.png", "Validation Class Distribution")

    error_samples = collect_error_samples(raw_val, y_val, bert_preds, bert_conf)
    save_error_samples_csv(error_samples, "evaluation/error_samples.csv")

    correct_flags = [1 if true == pred else 0 for true, pred in zip(y_val, bert_preds)]
    ece_before = compute_ece(bert_conf, correct_flags)

    _, label_ids, logits, label2id = predict_logits("models/bert_model", x_val, y_val)
    label_tensor = torch.tensor(label_ids)
    valid_mask = label_tensor >= 0
    if valid_mask.sum().item() == 0:
        raise ValueError("No valid labels found for calibration.")

    logits = logits[valid_mask]
    label_tensor = label_tensor[valid_mask]
    scaler, _ = fit_temperature(logits, label_tensor)
    calibrated_probs = apply_temperature(logits, scaler).numpy()
    calibrated_conf = calibrated_probs.max(axis=1).tolist()
    id2label = {v: k for k, v in label2id.items()}
    calibrated_preds = [id2label.get(int(idx), bert_preds[i]) for i, idx in enumerate(calibrated_probs.argmax(axis=1))]
    filtered_y_val = [label for label, valid in zip(y_val, valid_mask.tolist()) if valid]
    calibrated_correct = [1 if true == pred else 0 for true, pred in zip(filtered_y_val, calibrated_preds)]
    ece_after = compute_ece(calibrated_conf, calibrated_correct)

    plot_reliability_diagram(bert_conf, correct_flags, "evaluation/reliability_diagram.png")

    metrics_payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "bert": bert_metrics,
        "baseline": baseline_metrics,
        "artifacts": {
            "confusion_matrix": "evaluation/confusion_matrix.png",
            "class_distribution": "evaluation/class_distribution.png",
            "reliability_diagram": "evaluation/reliability_diagram.png",
        },
    }

    comparison_payload = {
        "bert_macro_f1": bert_metrics["macro_f1"],
        "baseline_macro_f1": baseline_metrics["macro_f1"],
        "delta_bert_minus_baseline": round(bert_metrics["macro_f1"] - baseline_metrics["macro_f1"], 4),
    }

    calibration_payload = {
        "ece_before": ece_before,
        "ece_after": ece_after,
        "temperature": round(float(scaler.temperature.item()), 4),
    }

    with open("evaluation/metrics.json", "w", encoding="utf-8") as handle:
        json.dump(metrics_payload, handle, indent=2)
    with open("evaluation/baseline_comparison.json", "w", encoding="utf-8") as handle:
        json.dump(comparison_payload, handle, indent=2)
    with open("evaluation/calibration.json", "w", encoding="utf-8") as handle:
        json.dump(calibration_payload, handle, indent=2)

    print("✅ Evaluation outputs saved to evaluation/")


if __name__ == "__main__":
    main()
