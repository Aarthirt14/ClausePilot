import pytest

from src.evaluation.metrics import compute_metrics


def test_compute_metrics_perfect_predictions():
    metrics = compute_metrics(["A", "B", "A"], ["A", "B", "A"], labels=["A", "B"])
    assert metrics["macro_f1"] == 1.0
    assert metrics["accuracy"] == 1.0


def test_compute_metrics_partial_accuracy():
    metrics = compute_metrics(["A", "B", "A"], ["A", "B", "B"], labels=["A", "B"])
    assert 0 < metrics["macro_f1"] < 1
    assert metrics["accuracy"] == pytest.approx(2 / 3, abs=1e-3)
