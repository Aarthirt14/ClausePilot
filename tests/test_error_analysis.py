from src.evaluation.error_analysis import collect_error_samples


def test_collect_error_samples_finds_misclassifications():
    texts = ["clause one", "clause two", "clause three"]
    y_true = ["A", "B", "A"]
    y_pred = ["A", "B", "B"]
    confidences = [0.9, 0.8, 0.55]

    result = collect_error_samples(texts, y_true, y_pred, confidences)
    assert len(result["misclassified"]) == 1
    assert result["misclassified"][0]["clause_text"] == "clause three"


def test_collect_error_samples_no_errors():
    result = collect_error_samples(["a", "b"], ["A", "B"], ["A", "B"], [0.9, 0.9])
    assert result["misclassified"] == []
