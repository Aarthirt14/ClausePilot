from typing import Dict, List

import csv


def collect_error_samples(
	texts: List[str],
	y_true: List[str],
	y_pred: List[str],
	confidences: List[float],
	low_confidence_count: int = 10,
	boundary_low: float = 0.45,
	boundary_high: float = 0.55,
) -> Dict[str, List[Dict[str, object]]]:
	"""Collect misclassifications, low-confidence predictions, and boundary cases."""
	samples = []
	for text, true_label, pred_label, conf in zip(texts, y_true, y_pred, confidences):
		samples.append(
			{
				"clause_text": text,
				"true_label": true_label,
				"pred_label": pred_label,
				"confidence": round(float(conf), 4),
			}
		)

	misclassified = [s for s in samples if s["true_label"] != s["pred_label"]]
	lowest_conf = sorted(samples, key=lambda s: s["confidence"])[:low_confidence_count]
	boundary = [s for s in samples if boundary_low <= s["confidence"] <= boundary_high]

	return {
		"misclassified": misclassified,
		"lowest_confidence": lowest_conf,
		"boundary": boundary,
	}


def save_error_samples_csv(samples: Dict[str, List[Dict[str, object]]], out_path: str) -> None:
	"""Save error samples to CSV for manual inspection."""
	rows = []
	for key, items in samples.items():
		for item in items:
			rows.append({"category": key, **item})

	fieldnames = ["category", "clause_text", "true_label", "pred_label", "confidence"]
	with open(out_path, "w", newline="", encoding="utf-8") as handle:
		writer = csv.DictWriter(handle, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(rows)
