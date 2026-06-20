from src.data_processing.cleaning import normalize_text, deduplicate_clauses


def test_normalize_text_lowercases_and_collapses_whitespace():
    assert normalize_text("HELLO   World......") == "hello world."


def test_normalize_text_handles_empty_string():
    assert normalize_text("") == ""
    assert normalize_text(None) == ""


def test_deduplicate_clauses_removes_near_duplicates():
    clauses = ["Hello world.", "Hello   world.", "Different clause."]
    deduped, removed_count = deduplicate_clauses(clauses)
    assert deduped == ["Hello world.", "Different clause."]
    assert removed_count == 1


def test_deduplicate_clauses_preserves_order_and_first_occurrence():
    clauses = ["A.", "B.", "A.", "C.", "B."]
    deduped, removed_count = deduplicate_clauses(clauses)
    assert deduped == ["A.", "B.", "C."]
    assert removed_count == 2
