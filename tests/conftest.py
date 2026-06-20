"""
Shared pytest fixtures.

Most fixtures here avoid touching the actual BERT model so the test
suite runs fast and doesn't require a trained checkpoint. Tests that
exercise app.py routes monkeypatch the inference/explainability layer
directly rather than mocking torch/transformers internals.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_clauses():
    return [
        "Either party may terminate this Agreement upon 30 days written notice.",
        "Consultant shall indemnify and hold harmless Client from any and all claims, with no cap.",
        "This Agreement shall remain confidential for a period of five years.",
        "Payment of $50,000 is due within 30 days of invoice.",
    ]


@pytest.fixture
def sample_results():
    """A small set of already-scored clause results, shaped like what
    attach_advanced_risk_scores + enrich_results would produce."""
    return [
        {
            "id": 1,
            "clause": "Uncapped indemnification for any and all damages.",
            "label": "Liability Risk",
            "severity": "High",
            "confidence": 0.91,
            "confidence_pct": 91.0,
        },
        {
            "id": 2,
            "clause": "This is a standard recital clause with no risk implications.",
            "label": "Neutral",
            "severity": "None",
            "confidence": 0.40,
            "confidence_pct": 40.0,
        },
    ]
