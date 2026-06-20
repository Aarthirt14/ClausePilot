from src.segmentation import segment_clauses, normalize_contract_text


def test_segment_clauses_splits_numbered_sections():
    text = (
        "1. Termination. Either party may terminate this Agreement immediately "
        "upon written notice.\n\n"
        "2. Liability. Consultant shall indemnify and hold harmless Client "
        "from any and all claims, uncapped."
    )
    clauses = segment_clauses(text)
    assert len(clauses) == 2
    assert "terminate" in clauses[0].lower()
    assert "indemnify" in clauses[1].lower()


def test_segment_clauses_handles_empty_text():
    assert segment_clauses("") == []
    assert segment_clauses(None) == []


def test_segment_clauses_strips_section_numbering():
    text = "1.1 The fee is due within 30 days."
    clauses = segment_clauses(text)
    assert len(clauses) == 1
    assert not clauses[0].startswith("1.1")


def test_normalize_contract_text_collapses_whitespace():
    raw = "Some   text......  with\r\n\r\nextra   spaces"
    normalized = normalize_contract_text(raw)
    assert "......" not in normalized
    assert "  " not in normalized
    assert "\r" not in normalized


def test_normalize_contract_text_removes_form_feed():
    raw = "Page one\x0cPage two"
    normalized = normalize_contract_text(raw)
    assert "\x0c" not in normalized
