from src.scoring.mitigation_strategies import (
    generate_mitigation_strategies,
    generate_executive_mitigation_summary,
)


def test_generate_mitigation_strategies_for_uncapped_liability():
    strategies = generate_mitigation_strategies(
        "Liability Risk", "High", ["uncapped liability"], 0, {}
    )
    strategy_names = [s["strategy"] for s in strategies]
    assert "Cap Liability" in strategy_names
    assert all("priority" in s and "action" in s and "rationale" in s for s in strategies)


def test_generate_mitigation_strategies_neutral_clause_has_no_strategies():
    strategies = generate_mitigation_strategies("Neutral", "None", [], 0, {})
    assert strategies == []


def test_generate_executive_mitigation_summary_aggregates_by_priority():
    enriched_results = [
        {
            "label": "Liability Risk",
            "severity": "High",
            "high_risk_detection": {"risk_triggers": ["uncapped liability"]},
            "extracted_metadata": {"monetary_value": 0.0, "durations": {}},
        },
        {
            "label": "Neutral",
            "severity": "None",
            "high_risk_detection": {"risk_triggers": []},
            "extracted_metadata": {"monetary_value": 0.0, "durations": {}},
        },
    ]
    summary = generate_executive_mitigation_summary(enriched_results)
    assert summary["total_mitigation_items"] > 0
    assert any(a["strategy"] == "Cap Liability" for a in summary["critical_actions"])


def test_generate_executive_mitigation_summary_handles_no_risk():
    summary = generate_executive_mitigation_summary(
        [{"label": "Neutral", "severity": "None", "high_risk_detection": {}, "extracted_metadata": {}}]
    )
    assert summary["total_mitigation_items"] == 0
    assert summary["critical_actions"] == []


def test_generate_executive_mitigation_summary_deduplicates_repeated_strategies():
    # Two clauses that each trigger the same "Cap Liability" strategy should
    # only appear once in the executive summary, not twice.
    enriched_results = [
        {
            "label": "Liability Risk",
            "severity": "High",
            "high_risk_detection": {"risk_triggers": ["uncapped liability"]},
            "extracted_metadata": {"monetary_value": 0.0, "durations": {}},
        }
    ] * 2
    summary = generate_executive_mitigation_summary(enriched_results)
    cap_liability_count = sum(1 for a in summary["critical_actions"] if a["strategy"] == "Cap Liability")
    assert cap_liability_count == 1
