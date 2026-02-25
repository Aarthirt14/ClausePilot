import os
import json
from io import BytesIO

from flask import Flask, jsonify, redirect, render_template, request, send_file, send_from_directory, url_for
from werkzeug.utils import secure_filename

from src.api.evaluation_api import load_error_samples, load_metrics
from src.dashboard_utils import (
    build_confidence_histogram_data,
    build_executive_summary,
    build_risk_summary,
    current_analysis_timestamp,
    enrich_results,
    generate_risk_report_pdf,
    load_model_comparison_metrics,
)
from src.scoring.risk_score import attach_risk_scores
from src.scoring.advanced_risk_scoring import attach_advanced_risk_scores
from src.scoring.mitigation_strategies import (
    generate_mitigation_strategies,
    generate_executive_mitigation_summary
)
from src.explainability import explain_clause_with_shap
from src.inference import infer_clauses
from src.pdf_extractor import extract_text_from_pdf
from src.segmentation import segment_clauses


UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs("evaluation", exist_ok=True)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def analyze_contract(file_path: str) -> dict:
    """Run extraction, segmentation, inference, and summary preparation."""
    raw_text = extract_text_from_pdf(file_path)
    clauses = segment_clauses(raw_text)
    predictions = infer_clauses(clauses)
    
    # Use advanced risk scoring (includes IP Risk, financial exposure, confidence calibration)
    scored_results, risk_score_breakdown = attach_advanced_risk_scores(predictions)
    
    # Enrich with mitigation strategies
    for item in scored_results:
        label = item.get("label", "Neutral")
        severity = item.get("severity", "None")
        risk_triggers = item.get("high_risk_detection", {}).get("risk_triggers", [])
        monetary_value = item.get("extracted_metadata", {}).get("monetary_value", 0.0)
        durations = item.get("extracted_metadata", {}).get("durations", {})
        
        mitigations = generate_mitigation_strategies(
            label, severity, risk_triggers, monetary_value, durations
        )
        item["mitigation_strategies"] = mitigations
    
    enriched_results = enrich_results(scored_results)
    summary = build_risk_summary(enriched_results)
    overall_risk_score = float(risk_score_breakdown.get("normalized_score", 0.0))
    executive_summary = build_executive_summary(enriched_results, summary, overall_risk_score)
    confidence_histogram = build_confidence_histogram_data(enriched_results, bins=10)
    model_comparison = load_model_comparison_metrics("evaluation/evaluation_report.json")
    
    # Generate mitigation summary
    mitigation_summary = generate_executive_mitigation_summary(enriched_results)

    return {
        "results": enriched_results,
        "summary": summary,
        "overall_risk_score": overall_risk_score,
        "risk_score_breakdown": risk_score_breakdown,
        "executive_summary": executive_summary,
        "confidence_histogram": confidence_histogram,
        "model_comparison": model_comparison,
        "mitigation_summary": mitigation_summary,
        "total_clauses": len(enriched_results),
    }


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    return redirect(url_for("result", filename=filename))


@app.route("/result/<filename>", methods=["GET"])
def result(filename: str):
    filename = secure_filename(filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(file_path):
        return redirect(url_for("index"))

    try:
        analysis = analyze_contract(file_path)
        analyzed_at = current_analysis_timestamp()

        label_distribution = analysis["summary"]["label_counts"]
        severity_distribution = analysis["summary"]["severity_counts"]

        pie_labels = list(label_distribution.keys())
        pie_values = list(label_distribution.values())

        bar_labels = ["High", "Medium", "Low", "None"]
        bar_values = [severity_distribution.get(level, 0) for level in bar_labels]

        return render_template(
            "results.html",
            filename=filename,
            analyzed_at=analyzed_at,
            results=analysis["results"],
            summary=analysis["summary"],
            overall_risk_score=analysis["overall_risk_score"],
            risk_score_breakdown=analysis["risk_score_breakdown"],
            executive_summary=analysis["executive_summary"],
            model_comparison=analysis["model_comparison"],
            pie_labels=pie_labels,
            pie_values=pie_values,
            bar_labels=bar_labels,
            bar_values=bar_values,
            confidence_hist_labels=analysis["confidence_histogram"]["labels"],
            confidence_hist_counts=analysis["confidence_histogram"]["counts"],
            high_conf_threshold=0.85,
            error=None,
        )
    except Exception as exc:
        return render_template(
            "results.html",
            filename=filename,
            analyzed_at=current_analysis_timestamp(),
            results=[],
            summary={
                "total_clauses": 0,
                "high_risk_count": 0,
                "medium_risk_count": 0,
                "low_risk_count": 0,
                "neutral_count": 0,
                "severity_counts": {"High": 0, "Medium": 0, "Low": 0, "None": 0},
                "severity_percentages": {"High": 0, "Medium": 0, "Low": 0, "None": 0},
                "label_counts": {},
                "label_percentages": {},
            },
            overall_risk_score=0,
            risk_score_breakdown={
                "impact_weights": {
                    "Liability Risk": 1.6,
                    "Termination Risk": 1.5,
                    "Data Privacy Risk": 1.3,
                    "Payment Risk": 1.1,
                    "Neutral": 0.0,
                },
                "total_severity_score": 0,
                "max_possible": 1,
                "normalized_score": 0,
                "formula": "score = (sum(impact(label) * confidence) / sum(impact(label))) * 100",
            },
            executive_summary=[],
            model_comparison={"available": False, "bert_macro_f1": None, "legal_bert_macro_f1": None, "delta": None},
            pie_labels=[],
            pie_values=[],
            bar_labels=["High", "Medium", "Low", "None"],
            bar_values=[0, 0, 0, 0],
            confidence_hist_labels=["0.0-0.1", "0.1-0.2", "0.2-0.3", "0.3-0.4", "0.4-0.5", "0.5-0.6", "0.6-0.7", "0.7-0.8", "0.8-0.9", "0.9-1.0"],
            confidence_hist_counts=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            high_conf_threshold=0.85,
            error=str(exc),
        )

@app.route("/explain", methods=["POST"])
def explain_clause():
    payload = request.get_json(silent=True) or {}
    clause = (payload.get("clause") or "").strip()

    if not clause:
        return jsonify({"error": "Missing clause text."}), 400

    try:
        explanation = explain_clause_with_shap(clause)
        return jsonify(explanation)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/download-report/<filename>", methods=["GET"])
def download_report(filename: str):
    """Generate and download a PDF report for the analyzed contract."""
    filename = secure_filename(filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(file_path):
        return redirect(url_for("index"))

    try:
        analysis = analyze_contract(file_path)
        analyzed_at = current_analysis_timestamp()
        pdf_data = generate_risk_report_pdf(
            filename=filename,
            analyzed_at=analyzed_at,
            summary=analysis["summary"],
            overall_risk_score=analysis["overall_risk_score"],
            results=analysis["results"],
        )
        return send_file(
            BytesIO(pdf_data),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"risk_report_{filename.rsplit('.', 1)[0]}.pdf",
        )
    except Exception:
        return redirect(url_for("result", filename=filename))


@app.route("/evaluation", methods=["GET"])
def evaluation_dashboard():
    """Render advanced model evaluation metrics and plots."""
    report_path = os.path.join("evaluation", "metrics.json")
    if not os.path.exists(report_path):
        return render_template(
            "evaluation.html",
            report=None,
            metrics={},
            comparison={},
            error="evaluation/metrics.json not found. Run: python src/evaluate_models.py",
        )

    try:
        with open(report_path, "r", encoding="utf-8") as handle:
            report = json.load(handle)
    except Exception as exc:
        return render_template(
            "evaluation.html",
            report=None,
            metrics={},
            comparison={},
            error=f"Failed to load evaluation report: {exc}",
        )

    metrics = {key: value for key, value in report.items() if key in {"bert", "baseline"}}
    comparison_path = os.path.join("evaluation", "baseline_comparison.json")
    if os.path.exists(comparison_path):
        with open(comparison_path, "r", encoding="utf-8") as handle:
            comparison = json.load(handle)
    else:
        comparison = {}
    artifacts = report.get("artifacts", {})

    def to_artifact_url(path_value: str) -> str:
        if not path_value:
            return ""
        name = os.path.basename(path_value)
        return url_for("evaluation_artifact", filename=name)

    artifact_urls = {
        "confusion_matrix": to_artifact_url(artifacts.get("confusion_matrix", "")),
        "class_distribution": to_artifact_url(artifacts.get("class_distribution", "")),
        "reliability_diagram": to_artifact_url(artifacts.get("reliability_diagram", "")),
    }

    return render_template(
        "evaluation.html",
        report=report,
        metrics=metrics,
        comparison=comparison,
        artifact_urls=artifact_urls,
        error=None,
    )


@app.route("/evaluation/artifact/<filename>", methods=["GET"])
def evaluation_artifact(filename: str):
    """Serve generated evaluation plots from evaluation/ directory."""
    safe_name = secure_filename(filename)
    return send_from_directory("evaluation", safe_name)


@app.route("/api/metrics", methods=["GET"])
def api_metrics():
    metrics = load_metrics("evaluation/metrics.json")
    return jsonify(metrics)


@app.route("/api/error-samples", methods=["GET"])
def api_error_samples():
    samples = load_error_samples("evaluation/error_samples.csv")
    return jsonify(samples)


if __name__ == "__main__":
    app.run(debug=True)
