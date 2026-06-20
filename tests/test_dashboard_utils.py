from src.dashboard_utils import (
    truncate_clause,
    build_risk_summary,
    build_confidence_histogram_data,
    enrich_results,
    build_executive_summary,
    generate_risk_report_pdf,
)


def test_truncate_clause_short_text_is_unchanged():
    assert truncate_clause("Short clause.", limit=120) == "Short clause."


def test_truncate_clause_long_text_is_truncated_with_ellipsis():
    long_text = "a" * 200
    result = truncate_clause(long_text, limit=10)
    assert result.endswith("...")
    assert len(result) <= 13


def test_build_risk_summary_counts_severities(sample_results):
    summary = build_risk_summary(sample_results)
    assert summary["total_clauses"] == 2
    assert summary["high_risk_count"] == 1
    assert summary["neutral_count"] == 1


def test_build_confidence_histogram_data_bins_sum_to_total(sample_results):
    hist = build_confidence_histogram_data(sample_results, bins=10)
    assert sum(hist["counts"]) == len(sample_results)
    assert len(hist["labels"]) == 10


def test_enrich_results_assigns_sequential_ids(sample_results):
    # Strip the ids the fixture already has, to test enrich_results sets them.
    raw = [{k: v for k, v in r.items() if k != "id"} for r in sample_results]
    enriched = enrich_results(raw)
    assert [item["id"] for item in enriched] == [1, 2]


def test_build_executive_summary_returns_nonempty_list(sample_results):
    summary = build_risk_summary(sample_results)
    exec_summary = build_executive_summary(sample_results, summary, overall_risk_score=55.0)
    assert isinstance(exec_summary, list)
    assert len(exec_summary) > 0
    assert all(isinstance(line, str) for line in exec_summary)


def test_generate_risk_report_pdf_produces_valid_pdf_bytes(sample_results):
    summary = build_risk_summary(sample_results)
    pdf_bytes = generate_risk_report_pdf(
        filename="contract.pdf",
        analyzed_at="2026-06-17 10:00:00",
        summary=summary,
        overall_risk_score=88.5,
        results=sample_results,
    )
    assert pdf_bytes[:4] == b"%PDF"
    assert len(pdf_bytes) > 500
