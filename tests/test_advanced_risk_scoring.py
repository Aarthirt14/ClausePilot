import pytest

from src.scoring.advanced_risk_scoring import (
    extract_monetary_value,
    extract_duration,
    compute_advanced_risk_score,
    attach_advanced_risk_scores,
)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("The cap is $1.5 million for damages.", 1_500_000),
        ("Liability shall not exceed $250,000.", 250_000),
        ("This clause mentions no money at all.", 0.0),
    ],
)
def test_extract_monetary_value(text, expected):
    assert extract_monetary_value(text) == expected


def test_extract_duration_finds_notice_period():
    duration = extract_duration("Either party may terminate upon 30 days notice.")
    assert duration["notice_period_days"] == 30
    assert duration["days"] == 30


def test_extract_duration_handles_no_duration_language():
    duration = extract_duration("This clause has no time-based language.")
    assert duration["notice_period_days"] == 0


def test_compute_advanced_risk_score_flags_high_risk_liability_language():
    risk = compute_advanced_risk_score(
        "Liability Risk", 0.92, "Uncapped indemnification for any and all damages."
    )
    assert risk["severity"] == "High"
    assert risk["high_risk_detection"]["is_high_risk"] is True


def test_compute_advanced_risk_score_neutral_clause_has_no_severity():
    risk = compute_advanced_risk_score("Neutral", 0.99, "This is a routine recital.")
    assert risk["severity"] == "None"


def test_attach_advanced_risk_scores_produces_bounded_normalized_score():
    results = [
        {"clause": "Uncapped liability for any damages.", "label": "Liability Risk", "confidence": 0.91}
    ]
    enriched, breakdown = attach_advanced_risk_scores(results)
    assert len(enriched) == 1
    assert 0 <= breakdown["normalized_score"] <= 100
    assert "high_risk_count" in breakdown


def test_attach_advanced_risk_scores_handles_empty_input():
    enriched, breakdown = attach_advanced_risk_scores([])
    assert enriched == []
    assert breakdown["normalized_score"] == 0
