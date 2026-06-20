from src.category_mapper import (
    map_cuad_to_risk_category,
    detect_ip_risk_from_text,
    enhance_label_with_text_detection,
)


def test_map_cuad_to_risk_category_known_mappings():
    assert map_cuad_to_risk_category("Uncapped Liability") == "Liability Risk"
    assert map_cuad_to_risk_category("Termination For Convenience") == "Termination Risk"


def test_map_cuad_to_risk_category_unknown_falls_back_to_ip_risk():
    # CUAD has many IP/license-related label variants that aren't
    # individually enumerated; unknown categories default to IP Risk
    # as the safer assumption for a legal-clause classifier.
    assert map_cuad_to_risk_category("Some Unrecognized License Category") == "IP Risk"


def test_detect_ip_risk_from_text_finds_ip_language():
    text = "All intellectual property rights, including patents and trademarks, shall be assigned to Client."
    assert detect_ip_risk_from_text(text) is True


def test_detect_ip_risk_from_text_negative_case():
    text = "Either party may terminate this Agreement upon 30 days notice."
    assert detect_ip_risk_from_text(text) is False


def test_enhance_label_with_text_detection_returns_tuple():
    label, confidence, method = enhance_label_with_text_detection(
        "Neutral", "This is a routine recital clause.", 0.5
    )
    assert isinstance(label, str)
    assert isinstance(confidence, float)
    assert isinstance(method, str)
