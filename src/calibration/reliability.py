from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np


def compute_ece(confidences: List[float], correct: List[int], bins: int = 10) -> float:
	"""Compute Expected Calibration Error (ECE)."""
	confidences = np.array(confidences)
	correct = np.array(correct)
	bin_edges = np.linspace(0.0, 1.0, bins + 1)
	ece = 0.0

	for i in range(bins):
		mask = (confidences >= bin_edges[i]) & (confidences < bin_edges[i + 1])
		if not np.any(mask):
			continue
		bin_acc = correct[mask].mean()
		bin_conf = confidences[mask].mean()
		ece += (mask.mean()) * abs(bin_acc - bin_conf)

	return round(float(ece), 4)


def plot_reliability_diagram(confidences: List[float], correct: List[int], out_path: str, bins: int = 10) -> None:
	"""Plot reliability diagram for calibration diagnostics."""
	confidences = np.array(confidences)
	correct = np.array(correct)
	bin_edges = np.linspace(0.0, 1.0, bins + 1)
	bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
	accs = []

	for i in range(bins):
		mask = (confidences >= bin_edges[i]) & (confidences < bin_edges[i + 1])
		accs.append(correct[mask].mean() if np.any(mask) else 0.0)

	fig, ax = plt.subplots(figsize=(6, 5))
	ax.plot([0, 1], [0, 1], linestyle="--", color="#64748b", label="Perfect Calibration")
	ax.bar(bin_centers, accs, width=1 / bins, color="#334155", alpha=0.8)
	ax.set_xlabel("Confidence")
	ax.set_ylabel("Accuracy")
	ax.set_title("Reliability Diagram")
	ax.set_xlim(0, 1)
	ax.set_ylim(0, 1)
	ax.legend()
	fig.tight_layout()
	fig.savefig(out_path, dpi=200)
	plt.close(fig)
