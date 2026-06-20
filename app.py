import logging
import json
import os
import time
from io import BytesIO

from flask import Flask, jsonify, redirect, render_template, request, send_file, send_from_directory, url_for
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from src.config import config
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
from src.scoring.advanced_risk_scoring import attach_advanced_risk_scores
from src.scoring.mitigation_strategies import (
    generate_mitigation_strategies,
    generate_executive_mitigation_summary
)
from src.explainability import explain_clause_with_shap
from src.inference import infer_clauses, load_bert_model
from src.pdf_extractor import extract_text_from_pdf
from src.segmentation import segment_clauses


logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(config.EVALUATION_DIR, exist_ok=True)


def _cleanup_old_uploads(retention_hours: int) -> None:
    """Delete uploaded contract files older than retention_hours.

    Uploaded contracts can be sensitive documents, so we don't keep
    them around indefinitely. This runs once at startup; for a
    long-running deployment, pair it with a periodic scheduled job
    instead of relying solely on process restarts.
    """
    if retention_hours <= 0:
        return
    cutoff = time.time() - (retention_hours * 3600)
    folder = app.config["UPLOAD_FOLDER"]
    if not os.path.isdir(folder):
        return
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        try:
            if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
                os.remove(path)
                logger.info("Removed expired upload: %s", name)
        except OSError as exc:
            logger.warning("Could not clean up upload %s: %s", name, exc)


_cleanup_old_uploads(config.UPLOAD_RETENTION_HOURS)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in config.ALLOWED_EXTENSIONS


def analyze_contract(file_path: str) -> dict:
    """Run extraction, segmentation, inference, and summary preparation."""
    raw_text = extract_text_from_pdf(file_path)
    clauses = segment_clauses(raw_text)
    predictions = infer_clauses(clauses, model_dir=config.MODEL_DIR, max_length=config.MAX_TOKEN_LENGTH)

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
    model_comparison = load_model_comparison_metrics(
        os.path.join(config.EVALUATION_DIR, "evaluation_report.json")
    )

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


def _empty_results_context(filename: str, error_message: str) -> dict:
    """Shared fallback render context for the results page on failure."""
    return dict(
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
            "category_weights": {
                "Liability Risk": 1.8,
                "Termination Risk": 1.7,
                "Data Privacy Risk": 1.5,
                "Payment Risk": 1.3,
                "IP Risk": 1.6,
                "Neutral": 0.0,
            },
            "total_severity_score": 0,
            "max_possible_score": 1,
            "normalized_score": 0,
            "high_risk_count": 0,
            "calibrated_clauses": 0,
            "scoring_method": "Advanced: Impact x Likelihood x Financial Exposure Factor",
        },
        executive_summary=[],
        mitigation_summary={
            "critical_actions": [],
            "high_priority_actions": [],
            "recommended_reviews": [],
            "total_mitigation_items": 0,
            "estimated_effort": "N/A",
            "risk_acceptance_threshold": "",
        },
        model_comparison={"available": False, "bert_macro_f1": None, "legal_bert_macro_f1": None, "delta": None},
        pie_labels=[],
        pie_values=[],
        bar_labels=["High", "Medium", "Low", "None"],
        bar_values=[0, 0, 0, 0],
        confidence_hist_labels=["0.0-0.1", "0.1-0.2", "0.2-0.3", "0.3-0.4", "0.4-0.5", "0.5-0.6", "0.6-0.7", "0.7-0.8", "0.8-0.9", "0.9-1.0"],
        confidence_hist_counts=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        high_conf_threshold=0.85,
        error=error_message,
    )


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(_exc):
    max_mb = app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
    return render_template(
        "index.html",
        max_upload_mb=max_mb,
        error=f"That file is too large. The upload limit is {max_mb} MB.",
    ), 413


@app.route("/", methods=["GET"])
def index():
    max_mb = app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
    return render_template("index.html", max_upload_mb=max_mb, error=None)


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
            mitigation_summary=analysis["mitigation_summary"],
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
    except FileNotFoundError as exc:
        # Most commonly: the BERT model hasn't been trained/placed yet.
        logger.error("Model or asset not found while analyzing %s: %s", filename, exc)
        return render_template(
            "results.html",
            **_empty_results_context(
                filename,
                "The risk model isn't available yet. Train it with "
                "`python src/train_bert.py` or place a checkpoint at "
                f"{config.MODEL_DIR}, then try again.",
            ),
        )
    except Exception as exc:  # noqa: BLE001 - surfaced to the user, logged for us
        logger.exception("Failed to analyze contract %s", filename)
        return render_template("results.html", **_empty_results_context(filename, str(exc)))


@app.route("/explain", methods=["POST"])
def explain_clause():
    payload = request.get_json(silent=True) or {}
    clause = (payload.get("clause") or "").strip()

    if not clause:
        return jsonify({"error": "Missing clause text."}), 400

    try:
        explanation = explain_clause_with_shap(clause, model_dir=config.MODEL_DIR)
        return jsonify(explanation)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to generate SHAP explanation")
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
        logger.exception("Failed to generate PDF report for %s", filename)
        return redirect(url_for("result", filename=filename))


@app.route("/evaluation", methods=["GET"])
def evaluation_dashboard():
    """Render advanced model evaluation metrics and plots."""
    report_path = os.path.join(config.EVALUATION_DIR, "metrics.json")
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
        logger.exception("Failed to load evaluation report")
        return render_template(
            "evaluation.html",
            report=None,
            metrics={},
            comparison={},
            error=f"Failed to load evaluation report: {exc}",
        )

    metrics = {key: value for key, value in report.items() if key in {"bert", "baseline"}}
    comparison_path = os.path.join(config.EVALUATION_DIR, "baseline_comparison.json")
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
    return send_from_directory(config.EVALUATION_DIR, safe_name)


@app.route("/api/metrics", methods=["GET"])
def api_metrics():
    metrics = load_metrics(os.path.join(config.EVALUATION_DIR, "metrics.json"))
    return jsonify(metrics)


@app.route("/api/error-samples", methods=["GET"])
def api_error_samples():
    samples = load_error_samples(os.path.join(config.EVALUATION_DIR, "error_samples.csv"))
    return jsonify(samples)


@app.route("/healthz", methods=["GET"])
def healthz():
    """Lightweight liveness/readiness probe for container orchestrators."""
    model_available = os.path.isdir(config.MODEL_DIR)
    status = "ok" if model_available else "degraded"
    return jsonify({"status": status, "model_available": model_available}), 200 if model_available else 503


if __name__ == "__main__":
    # Warm the model cache at startup (rather than on the first request)
    # so the first user doesn't eat the multi-second load time. This is
    # best-effort: if the model hasn't been trained yet, the app still
    # boots and routes will report a clear error instead of crashing.
    try:
        load_bert_model(model_dir=config.MODEL_DIR)
        logger.info("BERT model loaded and cached at startup.")
    except FileNotFoundError:
        logger.warning(
            "No model found at %s. The app will run, but analysis routes "
            "will fail until a model is trained or placed there.",
            config.MODEL_DIR,
        )

    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
