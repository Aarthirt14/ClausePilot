import pytest

from src.scoring.risk_score import attach_risk_scores, compute_severity_score


@pytest.mark.parametrize(
    "label,confidence",
    [
        ("Liability Risk", 0.9),
        ("Termination Risk", 0.7),
        ("Payment Risk", 0.5),
        ("Neutral", 0.99),
    ],
)
def test_compute_severity_score_is_impact_times_confidence(label, confidence):
    from src.scoring.risk_score import IMPACT_WEIGHTS

    expected = round(IMPACT_WEIGHTS.get(label, 0.0) * confidence, 4)
    assert compute_severity_score(label, confidence) == expected


def test_attach_risk_scores_returns_breakdown_with_normalized_score():
    results = [
        {"label": "Liability Risk", "confidence": 0.9},
        {"label": "Neutral", "confidence": 0.99},
    ]
    scored, breakdown = attach_risk_scores(results)
    assert len(scored) == 2
    assert 0 <= breakdown["normalized_score"] <= 100
    assert "total_severity_score" in breakdown


def test_attach_risk_scores_handles_empty_input():
    scored, breakdown = attach_risk_scores([])
    assert scored == []
    assert breakdown["normalized_score"] == 0.0
