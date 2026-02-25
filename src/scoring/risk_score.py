from typing import Dict, List, Tuple


IMPACT_WEIGHTS = {
	"Liability Risk": 1.6,
	"Termination Risk": 1.5,
	"Data Privacy Risk": 1.3,
	"Payment Risk": 1.1,
	"Neutral": 0.0,
}


def compute_severity_score(label: str, confidence: float) -> float:
	"""
	Compute severity as impact x likelihood.
	Impact is higher for Termination and Liability.
	Likelihood is the model confidence.
	"""
	impact = IMPACT_WEIGHTS.get(label, 1.0)
	likelihood = max(min(confidence, 1.0), 0.0)
	return round(float(impact * likelihood), 4)


def attach_risk_scores(results: List[Dict[str, object]]) -> Tuple[List[Dict[str, object]], Dict[str, object]]:
	"""Attach impact/likelihood severity scores and compute overall normalized score."""
	updated = []
	total_score = 0.0
	max_possible = 0.0

	for item in results:
		label = str(item.get("label", "Neutral"))
		confidence = float(item.get("confidence", 0.0))
		impact = float(IMPACT_WEIGHTS.get(label, 1.0))
		severity_score = compute_severity_score(label, confidence)

		total_score += severity_score
		max_possible += impact

		updated.append(
			{
				**item,
				"impact": impact,
				"likelihood": round(confidence, 4),
				"severity_score": severity_score,
			}
		)

	normalized = round((total_score / max_possible) * 100, 2) if max_possible else 0.0

	breakdown = {
		"impact_weights": IMPACT_WEIGHTS,
		"total_severity_score": round(total_score, 4),
		"max_possible": round(max_possible, 4),
		"normalized_score": normalized,
		"formula": "score = (sum(impact(label) * confidence) / sum(impact(label))) * 100",
	}

	return updated, breakdown
