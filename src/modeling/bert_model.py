from typing import List, Tuple

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


def load_transformer(model_dir: str):
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    return tokenizer, model, device


def predict_with_transformer(
    model_dir: str,
    texts: List[str],
    max_length: int = 256,
    batch_size: int = 8,
) -> Tuple[List[str], List[float], List[List[float]]]:
    """Predict labels, confidences, and probabilities from transformer model."""
    tokenizer, model, device = load_transformer(model_dir)
    id2label = model.config.id2label or {}

    y_pred: List[str] = []
    confidences: List[float] = []
    all_probs: List[List[float]] = []

    with torch.no_grad():
        for start in range(0, len(texts), batch_size):
            batch = texts[start:start + batch_size]
            encoded = tokenizer(batch, truncation=True, padding=True, max_length=max_length, return_tensors="pt")
            encoded = {k: v.to(device) for k, v in encoded.items()}
            logits = model(**encoded).logits
            probs = torch.softmax(logits, dim=-1).cpu().numpy()
            pred_ids = probs.argmax(axis=-1)

            for row_idx, pred_id in enumerate(pred_ids):
                y_pred.append(str(id2label.get(int(pred_id), int(pred_id))))
                confidences.append(float(probs[row_idx, pred_id]))
                all_probs.append(probs[row_idx].tolist())

    return y_pred, confidences, all_probs


def predict_logits(
    model_dir: str,
    texts: List[str],
    true_labels: List[str],
    max_length: int = 256,
    batch_size: int = 8,
) -> Tuple[List[str], List[int], torch.Tensor, dict]:
    """Return logits and true label ids for calibration and temperature scaling."""
    tokenizer, model, device = load_transformer(model_dir)
    label2id = model.config.label2id or {}

    y_pred: List[str] = []
    logits_out: List[torch.Tensor] = []

    with torch.no_grad():
        for start in range(0, len(texts), batch_size):
            batch = texts[start:start + batch_size]
            encoded = tokenizer(batch, truncation=True, padding=True, max_length=max_length, return_tensors="pt")
            encoded = {k: v.to(device) for k, v in encoded.items()}
            logits = model(**encoded).logits
            probs = torch.softmax(logits, dim=-1)
            pred_batch = torch.argmax(probs, dim=-1)

            for pred_id in pred_batch.tolist():
                y_pred.append(str(model.config.id2label.get(int(pred_id), int(pred_id))))
            logits_out.append(logits.cpu())

    stacked_logits = torch.cat(logits_out, dim=0)
    label_ids = [label2id.get(label, -1) for label in true_labels]
    return y_pred, label_ids, stacked_logits, label2id
