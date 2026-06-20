"""
Flask route tests.

These mock out analyze_contract / infer_clauses / explain_clause_with_shap
rather than running real BERT inference, so the suite stays fast and
doesn't require a trained model checkpoint. Importing app.py itself
still requires torch/transformers/shap to be installed (see
requirements.txt) since those are real dependencies of the app.
"""
import io
import os

import pytest

import app as app_module


@pytest.fixture
def client(tmp_path, monkeypatch):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    app_module.app.config["TESTING"] = True
    app_module.app.config["UPLOAD_FOLDER"] = str(upload_dir)
    with app_module.app.test_client() as test_client:
        yield test_client


def _write_fake_upload(client, name: str = "contract.pdf") -> str:
    path = os.path.join(app_module.app.config["UPLOAD_FOLDER"], name)
    with open(path, "wb") as handle:
        handle.write(b"%PDF-1.4 fake contract bytes")
    return path


def _fake_analysis(label="Liability Risk", severity="High", confidence=0.91):
    return {
        "results": [
            {
                "id": 1,
                "clause": "Uncapped indemnification for any and all damages.",
                "label": label,
                "severity": severity,
                "confidence": confidence,
                "confidence_pct": confidence * 100,
            }
        ],
        "summary": {
            "total_clauses": 1,
            "high_risk_count": 1 if severity == "High" else 0,
            "medium_risk_count": 1 if severity == "Medium" else 0,
            "low_risk_count": 0,
            "neutral_count": 0,
            "severity_counts": {"High": 1 if severity == "High" else 0, "Medium": 0, "Low": 0, "None": 0},
            "severity_percentages": {"High": 100.0, "Medium": 0, "Low": 0, "None": 0},
            "label_counts": {label: 1},
            "label_percentages": {label: 100.0},
        },
        "overall_risk_score": 91.0,
        "risk_score_breakdown": {
            "scoring_method": "x",
            "total_severity_score": 1,
            "max_possible_score": 1,
            "normalized_score": 91.0,
            "category_weights": {},
            "exposure_multipliers": {},
            "high_risk_count": 1,
            "calibrated_clauses": 0,
        },
        "executive_summary": ["Test summary line."],
        "confidence_histogram": {"labels": ["0.9-1.0"], "counts": [1]},
        "model_comparison": {"available": False, "bert_macro_f1": None, "legal_bert_macro_f1": None, "delta": None},
        "mitigation_summary": {
            "critical_actions": [],
            "high_priority_actions": [],
            "recommended_reviews": [],
            "total_mitigation_items": 0,
            "estimated_effort": "Low",
            "risk_acceptance_threshold": "x",
        },
        "total_clauses": 1,
    }


def test_index_page_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Upload" in resp.data


def test_upload_with_no_file_redirects_to_index(client):
    resp = client.post("/upload", data={})
    assert resp.status_code in (302, 303)


def test_upload_rejects_non_pdf(client):
    resp = client.post(
        "/upload",
        data={"file": (io.BytesIO(b"hello"), "notes.txt")},
        content_type="multipart/form-data",
    )
    assert resp.status_code in (302, 303)
    # Should redirect back to index, not forward to a (nonexistent) result page.
    assert "/result/" not in resp.headers.get("Location", "")


def test_upload_accepts_pdf_and_redirects_to_result(client):
    resp = client.post(
        "/upload",
        data={"file": (io.BytesIO(b"%PDF-1.4 fake"), "contract.pdf")},
        content_type="multipart/form-data",
    )
    assert resp.status_code in (302, 303)
    assert "/result/contract.pdf" in resp.headers["Location"]


def test_result_redirects_when_file_missing(client):
    resp = client.get("/result/does-not-exist.pdf")
    assert resp.status_code in (302, 303)


def test_result_shows_friendly_message_when_model_missing(client, monkeypatch):
    _write_fake_upload(client, "demo.pdf")

    def _raise_missing_model(_path):
        raise FileNotFoundError("Model directory not found: models/bert_model")

    monkeypatch.setattr(app_module, "analyze_contract", _raise_missing_model)
    resp = client.get("/result/demo.pdf")
    assert resp.status_code == 200
    assert b"train" in resp.data.lower() or b"risk model" in resp.data.lower()


def test_result_renders_analysis_and_mitigations(client, monkeypatch):
    _write_fake_upload(client, "demo.pdf")
    analysis = _fake_analysis()
    analysis["results"][0]["mitigation_strategies"] = [
        {
            "priority": "Critical",
            "strategy": "Cap Liability",
            "action": "Negotiate a liability cap.",
            "rationale": "Uncapped liability creates unlimited exposure.",
        }
    ]
    analysis["mitigation_summary"]["critical_actions"] = [analysis["results"][0]["mitigation_strategies"][0]]
    analysis["mitigation_summary"]["total_mitigation_items"] = 1

    monkeypatch.setattr(app_module, "analyze_contract", lambda _path: analysis)
    resp = client.get("/result/demo.pdf")
    assert resp.status_code == 200
    body = resp.data.decode()
    assert "Liability Risk" in body
    assert "Cap Liability" in body
    assert "Recommended Mitigations" in body


def test_explain_requires_clause_text(client):
    resp = client.post("/explain", json={})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_explain_returns_explanation_for_valid_clause(client, monkeypatch):
    monkeypatch.setattr(
        app_module,
        "explain_clause_with_shap",
        lambda clause, model_dir=None: {"label": "Liability Risk", "top_contributing_words": []},
    )
    resp = client.post("/explain", json={"clause": "Uncapped liability for damages."})
    assert resp.status_code == 200
    assert resp.get_json()["label"] == "Liability Risk"


def test_healthz_reports_degraded_when_model_missing(client, monkeypatch):
    monkeypatch.setattr(os.path, "isdir", lambda _path: False)
    resp = client.get("/healthz")
    assert resp.status_code == 503
    assert resp.get_json()["status"] == "degraded"


def test_upload_too_large_file_is_rejected(client, monkeypatch):
    monkeypatch.setitem(app_module.app.config, "MAX_CONTENT_LENGTH", 10)  # 10 bytes
    resp = client.post(
        "/upload",
        data={"file": (io.BytesIO(b"%PDF-1.4 " * 50), "big.pdf")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 413
