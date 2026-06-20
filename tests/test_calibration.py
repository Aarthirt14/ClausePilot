from src.calibration.reliability import compute_ece


def test_compute_ece_perfect_calibration_is_near_zero():
    # Confidence exactly matches correctness rate within each bin.
    confidences = [1.0, 1.0, 1.0, 1.0]
    correctness = [1, 1, 1, 1]
    ece = compute_ece(confidences, correctness)
    assert ece == 0.0


def test_compute_ece_overconfident_predictions_yield_positive_error():
    confidences = [0.9, 0.9, 0.9]
    correctness = [0, 0, 1]
    ece = compute_ece(confidences, correctness)
    assert ece > 0
