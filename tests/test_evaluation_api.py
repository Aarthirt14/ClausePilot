import json

from src.api.evaluation_api import load_metrics, load_error_samples


def test_load_metrics_missing_file_returns_empty_dict():
    assert load_metrics("does/not/exist.json") == {}


def test_load_error_samples_missing_file_returns_empty_list():
    assert load_error_samples("does/not/exist.csv") == []


def test_load_metrics_reads_existing_json(tmp_path):
    metrics_path = tmp_path / "metrics.json"
    metrics_path.write_text(json.dumps({"macro_f1": 0.85}))
    assert load_metrics(str(metrics_path)) == {"macro_f1": 0.85}


def test_load_error_samples_reads_existing_csv(tmp_path):
    csv_path = tmp_path / "error_samples.csv"
    csv_path.write_text("clause_text,true_label,pred_label,confidence\nfoo,A,B,0.6\n")
    samples = load_error_samples(str(csv_path))
    assert len(samples) == 1
    assert samples[0]["clause_text"] == "foo"
