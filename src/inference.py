import os
from typing import Dict, List

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


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
    Load the fine-tuned BERT model and tokenizer from disk.

    Returns:
        tokenizer, model, device
    """
    if not os.path.isdir(model_dir):
        raise FileNotFoundError(f"Model directory not found: {model_dir}")

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    return tokenizer, model, device


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
            label = str(label_map.get(pred_id, pred_id))
            severity = assign_severity(label, confidence)

            results.append(
                {
                    "clause": clause_text,
                    "label": label,
                    "confidence": round(confidence, 4),
                    "severity": severity,
                }
            )

    return results
