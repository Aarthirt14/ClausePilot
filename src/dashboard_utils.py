from __future__ import annotations

import io
import importlib
import json
import os
from datetime import datetime
from typing import Dict, List

import numpy as np

from src.scoring.risk_score import attach_risk_scores


def truncate_clause(text: str, limit: int = 120) -> str:
    """Return a short preview for collapsed clause cards."""
    cleaned = (text or "").strip()
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[:limit].rstrip()}..."


def calculate_overall_risk_score(results: List[Dict[str, object]]) -> float:
    """Compute normalized risk score using impact x likelihood."""
    if not results:
        return 0.0

    _, breakdown = attach_risk_scores(results)
    return float(breakdown.get("normalized_score", 0.0))


def build_risk_score_breakdown(results: List[Dict[str, object]]) -> Dict[str, object]:
    """Provide transparent formula inputs for contract risk score."""
    _, breakdown = attach_risk_scores(results)
    return breakdown


def build_risk_summary(results: List[Dict[str, object]]) -> Dict[str, object]:
    """Create dashboard counts, percentages, and chart-ready distributions."""
    total = len(results)

    severity_counts = {
        "High": 0,
        "Medium": 0,
        "Low": 0,
        "None": 0,
    }

    label_counts: Dict[str, int] = {}
    for item in results:
        severity = str(item.get("severity", "None"))
        label = str(item.get("label", "Neutral"))
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        label_counts[label] = label_counts.get(label, 0) + 1

    def pct(value: int) -> float:
        return round((value / total) * 100, 1) if total else 0.0

    severity_percentages = {key: pct(val) for key, val in severity_counts.items()}
    label_percentages = {key: pct(val) for key, val in label_counts.items()}

    summary = {
        "total_clauses": total,
        "high_risk_count": severity_counts.get("High", 0),
        "medium_risk_count": severity_counts.get("Medium", 0),
        "low_risk_count": severity_counts.get("Low", 0),
        "neutral_count": label_counts.get("Neutral", 0),
        "severity_counts": severity_counts,
        "severity_percentages": severity_percentages,
        "label_counts": label_counts,
        "label_percentages": label_percentages,
    }

    return summary


def build_confidence_histogram_data(results: List[Dict[str, object]], bins: int = 10) -> Dict[str, List[float]]:
    """Create histogram bin labels/counts for prediction confidence calibration view."""
    confidences = [float(item.get("confidence", 0.0)) for item in results]
    if not confidences:
        return {
            "labels": [f"{round(i / bins, 1)}-{round((i + 1) / bins, 1)}" for i in range(bins)],
            "counts": [0 for _ in range(bins)],
        }

    hist, edges = np.histogram(confidences, bins=bins, range=(0.0, 1.0))
    labels = [f"{edges[i]:.1f}-{edges[i + 1]:.1f}" for i in range(len(edges) - 1)]

    return {
        "labels": labels,
        "counts": hist.astype(int).tolist(),
    }


def build_executive_summary(results: List[Dict[str, object]], summary: Dict[str, object], overall_risk_score: float) -> List[str]:
    """Generate a concise executive summary in 5–7 sentences."""
    total = int(summary.get("total_clauses", 0))
    high_count = int(summary.get("high_risk_count", 0))
    medium_count = int(summary.get("medium_risk_count", 0))
    low_count = int(summary.get("low_risk_count", 0))
    neutral_count = int(summary.get("neutral_count", 0))

    label_counts = summary.get("label_counts", {})
    if label_counts:
        most_frequent_label = max(label_counts, key=lambda key: label_counts[key])
        most_frequent_count = int(label_counts[most_frequent_label])
    else:
        most_frequent_label = "Neutral"
        most_frequent_count = 0

    termination_count = int(label_counts.get("Termination Risk", 0))
    termination_pct = round((termination_count / total) * 100, 1) if total else 0

    high_examples = [item for item in results if str(item.get("severity", "")) == "High"]
    high_example_text = high_examples[0]["clause"] if high_examples else "No high-severity clauses were identified."
    high_example_text = truncate_clause(high_example_text, 180)

    summary_lines = [
        f"This contract analysis reviewed {total} clauses and produced an overall risk score of {overall_risk_score} out of 100.",
        f"The most frequent risk category is {most_frequent_label} with {most_frequent_count} clauses.",
        f"Severity mix shows {high_count} high, {medium_count} medium, {low_count} low, and {neutral_count} neutral clauses.",
        f"Termination exposure appears in {termination_count} clauses ({termination_pct}% of all clauses).",
        f"High-severity review highlight: {high_example_text}",
        "The score is normalized using impact (risk type) x likelihood (confidence) weights for transparency.",
    ]

    if high_count == 0:
        summary_lines.append("No high-severity terms were detected, which lowers immediate legal risk concentration.")
    else:
        summary_lines.append("High-severity clauses should be prioritized for legal review before execution.")

    return summary_lines


def load_model_comparison_metrics(report_path: str = "evaluation/evaluation_report.json") -> Dict[str, object]:
    """Load BERT vs Legal-BERT comparison metrics for dashboard display."""
    if not report_path or not isinstance(report_path, str):
        return {
            "available": False,
            "bert_macro_f1": None,
            "legal_bert_macro_f1": None,
            "delta": None,
        }

    if not os.path.exists(report_path):
        return {
            "available": False,
            "bert_macro_f1": None,
            "legal_bert_macro_f1": None,
            "delta": None,
        }

    with open(report_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    comparison = payload.get("comparison", {})
    bert_macro_f1 = comparison.get("bert_macro_f1")
    legal_macro_f1 = comparison.get("legal_bert_macro_f1")
    delta = comparison.get("f1_delta_legal_minus_bert")

    return {
        "available": bert_macro_f1 is not None or legal_macro_f1 is not None,
        "bert_macro_f1": bert_macro_f1,
        "legal_bert_macro_f1": legal_macro_f1,
        "delta": delta,
    }


def enrich_results(results: List[Dict[str, object]]) -> List[Dict[str, object]]:
    """Attach presentation metadata to each clause result."""
    risk_badge_map = {
        "Liability Risk": "badge-risk-liability",
        "Termination Risk": "badge-risk-termination",
        "Payment Risk": "badge-risk-payment",
        "Data Privacy Risk": "badge-risk-privacy",
        "Neutral": "badge-risk-neutral",
    }
    severity_badge_map = {
        "High": "badge-sev-high",
        "Medium": "badge-sev-medium",
        "Low": "badge-sev-low",
        "None": "badge-sev-none",
    }

    enriched: List[Dict[str, object]] = []
    for idx, item in enumerate(results, start=1):
        clause = str(item.get("clause", "")).strip()
        label = str(item.get("label", "Neutral"))
        severity = str(item.get("severity", "None"))
        confidence = float(item.get("confidence", 0.0))

        enriched.append(
            {
                **item,
                "id": idx,
                "clause": clause,
                "clause_preview": truncate_clause(clause, 120),
                "confidence_pct": round(confidence * 100, 2),
                "risk_badge_class": risk_badge_map.get(label, "badge-risk-neutral"),
                "severity_badge_class": severity_badge_map.get(severity, "badge-sev-none"),
            }
        )

    return enriched


def current_analysis_timestamp() -> str:
    """Return display-friendly analysis date/time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def generate_risk_report_pdf(
    filename: str,
    analyzed_at: str,
    summary: Dict[str, object],
    overall_risk_score: float,
    results: List[Dict[str, object]],
) -> bytes:
    """Build a downloadable PDF risk report using reportlab."""
    colors = importlib.import_module("reportlab.lib.colors")
    pagesizes = importlib.import_module("reportlab.lib.pagesizes")
    styles_module = importlib.import_module("reportlab.lib.styles")
    platypus = importlib.import_module("reportlab.platypus")

    A4 = pagesizes.A4
    getSampleStyleSheet = styles_module.getSampleStyleSheet
    Paragraph = platypus.Paragraph
    SimpleDocTemplate = platypus.SimpleDocTemplate
    Spacer = platypus.Spacer
    Table = platypus.Table
    TableStyle = platypus.TableStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph("Contract Risk Analysis Report", styles["Title"]))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"Contract: {filename}", styles["Normal"]))
    elements.append(Paragraph(f"Date analyzed: {analyzed_at}", styles["Normal"]))
    elements.append(Paragraph(f"Overall risk score: {overall_risk_score}", styles["Normal"]))
    elements.append(Spacer(1, 14))

    summary_data = [
        ["Metric", "Value"],
        ["Total Clauses", str(summary.get("total_clauses", 0))],
        ["High Risk", str(summary.get("high_risk_count", 0))],
        ["Medium Risk", str(summary.get("medium_risk_count", 0))],
        ["Low Risk", str(summary.get("low_risk_count", 0))],
        ["Neutral", str(summary.get("neutral_count", 0))],
    ]

    summary_table = Table(summary_data, colWidths=[200, 120])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    elements.append(summary_table)
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("High Severity Clauses", styles["Heading2"]))

    high_items = [item for item in results if str(item.get("severity", "")) == "High"]
    if not high_items:
        elements.append(Paragraph("No high severity clauses found.", styles["Normal"]))
    else:
        for item in high_items:
            clause = str(item.get("clause", "")).replace("\n", " ")
            label = str(item.get("label", ""))
            confidence_pct = round(float(item.get("confidence", 0.0)) * 100, 2)

            elements.append(Paragraph(f"Risk Type: {label}", styles["Heading4"]))
            elements.append(Paragraph(f"Confidence: {confidence_pct}%", styles["Normal"]))
            elements.append(Paragraph(f"Clause: {clause}", styles["Normal"]))
            elements.append(Spacer(1, 10))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
