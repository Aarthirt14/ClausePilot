"""
Test Suite for Enhanced Risk Scoring System

Run tests to validate:
- IP Risk detection
- High-risk clause pattern matching
- Financial exposure calculation
- Confidence calibration
- Mitigation strategy generation
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.scoring.advanced_risk_scoring import (
    extract_monetary_value,
    extract_duration,
    detect_high_risk_clause,
    compute_advanced_risk_score,
    calibrate_confidence,
    attach_advanced_risk_scores
)
from src.scoring.mitigation_strategies import (
    generate_mitigation_strategies,
    generate_executive_mitigation_summary
)
from src.category_mapper import (
    detect_ip_risk_from_text,
    detect_data_privacy_risk_from_text,
    map_cuad_to_risk_category
)


def test_monetary_extraction():
    """Test monetary value extraction from various formats."""
    print("=" * 60)
    print("TEST 1: Monetary Value Extraction")
    print("=" * 60)
    
    test_cases = [
        ("The indemnification cap is $500,000 per claim.", 500000),
        ("Liquidated damages of $1.5 million apply.", 1500000),
        ("Payment of USD 250,000 required within 30 days.", 250000),
        ("Penalty: one hundred thousand dollars ($100,000).", 100000),
        ("The fee is $50k per month.", 50000),
        ("No monetary amount specified.", 0.0),
        ("Uncapped liability with no limit on damages.", 0.0),
    ]
    
    for text, expected in test_cases:
        result = extract_monetary_value(text)
        status = "✓" if abs(result - expected) < 1 else "✗"
        print(f"{status} Text: {text[:60]}...")
        print(f"  Expected: ${expected:,.0f} | Got: ${result:,.0f}\n")


def test_duration_extraction():
    """Test duration extraction."""
    print("=" * 60)
    print("TEST 2: Duration Extraction")
    print("=" * 60)
    
    test_cases = [
        "Termination requires 30 days prior notice.",
        "The contract term is 24 months from the effective date.",
        "Cure period of 15 days after breach notification.",
        "Non-compete for 2 years after termination.",
    ]
    
    for text in test_cases:
        result = extract_duration(text)
        print(f"Text: {text}")
        print(f"  Durations: {result}\n")


def test_ip_risk_detection():
    """Test IP risk detection from text."""
    print("=" * 60)
    print("TEST 3: IP Risk Detection")
    print("=" * 60)
    
    test_cases = [
        ("All intellectual property and patents created shall be owned by Company.", True),
        ("License grant is perpetual and irrevocable.", True),
        ("Work made for hire - all copyright transfers to Company.", True),
        ("Confidential information shall be kept private.", False),
        ("Payment terms are net 30 days.", False),
    ]
    
    for text, expected in test_cases:
        result = detect_ip_risk_from_text(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} Text: {text[:60]}...")
        print(f"  Expected: {expected} | Got: {result}\n")


def test_data_privacy_detection():
    """Test data privacy risk detection."""
    print("=" * 60)
    print("TEST 4: Data Privacy Risk Detection")
    print("=" * 60)
    
    test_cases = [
        ("Contractor shall process personal data in accordance with GDPR.", True),
        ("PII and personally identifiable information must be encrypted.", True),
        ("Data breach notification within 72 hours per CCPA requirements.", True),
        ("Payment processing shall be PCI compliant.", False),
        ("Insurance coverage required.", False),
    ]
    
    for text, expected in test_cases:
        result = detect_data_privacy_risk_from_text(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} Text: {text[:60]}...")
        print(f"  Expected: {expected} | Got: {result}\n")


def test_high_risk_detection():
    """Test high-risk clause pattern detection."""
    print("=" * 60)
    print("TEST 5: High-Risk Clause Detection")
    print("=" * 60)
    
    test_clauses = [
        ("Company may terminate immediately without notice for convenience.", "Termination Risk"),
        ("Indemnification obligation is uncapped and unlimited.", "Liability Risk"),
        ("Contractor must comply with GDPR and process personal data securely.", "Data Privacy Risk"),
        ("All intellectual property rights transfer perpetually to Company.", "IP Risk"),
        ("Late payment penalty of $50,000 per day applies.", "Payment Risk"),
    ]
    
    for text, label in test_clauses:
        result = detect_high_risk_clause(text, label)
        print(f"Clause: {text}")
        print(f"  Label: {label}")
        print(f"  High Risk: {result['is_high_risk']}")
        print(f"  Triggers: {result['risk_triggers']}\n")


def test_confidence_calibration():
    """Test confidence calibration based on contextual signals."""
    print("=" * 60)
    print("TEST 6: Confidence Calibration")
    print("=" * 60)
    
    test_cases = [
        (0.70, "Liability Risk", "Party shall indemnify and defend Company for all claims exceeding $500,000."),
        (0.65, "Termination Risk", "Contract may terminate immediately."),
        (0.80, "IP Risk", "Perpetual assignment of all intellectual property rights."),
    ]
    
    for base_conf, label, text in test_cases:
        calibrated, details = calibrate_confidence(base_conf, label, text)
        print(f"Clause: {text[:60]}...")
        print(f"  Base Confidence: {base_conf:.2f}")
        print(f"  Calibrated: {calibrated:.2f}")
        print(f"  Adjustments: {len(details['adjustments'])}")
        for adj in details['adjustments']:
            print(f"    - {adj['factor']}: {adj['adjustment']:+.2f}")
        print()


def test_mitigation_strategies():
    """Test mitigation strategy generation."""
    print("=" * 60)
    print("TEST 7: Mitigation Strategy Generation")
    print("=" * 60)
    
    test_cases = [
        ("Liability Risk", "High", ["Uncapped indemnification liability", "Indemnification obligation >$500,000"]),
        ("Termination Risk", "High", ["Immediate termination allowed", "No cure period provided"]),
        ("IP Risk", "High", ["IP ownership transfer or assignment", "Perpetual or irrevocable license grant"]),
    ]
    
    for label, severity, triggers in test_cases:
        strategies = generate_mitigation_strategies(label, severity, triggers, monetary_value=500000)
        print(f"Risk: {label} ({severity})")
        print(f"Triggers: {triggers}")
        print(f"Mitigation Strategies ({len(strategies)}):")
        for strat in strategies[:3]:
            print(f"  [{strat['priority']}] {strat['strategy']}: {strat['action'][:80]}...")
        print()


def test_advanced_scoring():
    """Test complete advanced risk scoring."""
    print("=" * 60)
    print("TEST 8: Advanced Risk Scoring")
    print("=" * 60)
    
    test_clause = "Contractor shall indemnify Company for all claims without limit or cap. Payment of $750,000 required for liquidated damages upon breach."
    
    assessment = compute_advanced_risk_score(
        label="Liability Risk",
        base_confidence=0.85,
        text=test_clause,
        calibrate=True
    )
    
    print(f"Clause: {test_clause}")
    print(f"\nRisk Assessment:")
    print(f"  Label: {assessment['label']}")
    print(f"  Confidence: {assessment['confidence']:.2f} → {assessment['calibrated_confidence']:.2f}")
    print(f"  Impact: {assessment['impact']:.2f} → {assessment['adjusted_impact']:.2f}")
    print(f"  Severity Score: {assessment['severity_score']:.4f}")
    print(f"  Severity: {assessment['severity']}")
    print(f"  Financial Exposure: {assessment['financial_exposure']['level']} (${assessment['financial_exposure']['monetary_value']:,.0f})")
    print(f"  High Risk: {assessment['high_risk_detection']['is_high_risk']}")
    print(f"  Risk Triggers: {assessment['high_risk_detection']['risk_triggers']}")
    print()


def run_all_tests():
    """Run all test suites."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "ENHANCED RISK SCORING SYSTEM - TEST SUITE" + " " * 16 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    try:
        test_monetary_extraction()
        test_duration_extraction()
        test_ip_risk_detection()
        test_data_privacy_detection()
        test_high_risk_detection()
        test_confidence_calibration()
        test_mitigation_strategies()
        test_advanced_scoring()
        
        print("=" * 60)
        print("✓ ALL TESTS COMPLETED")
        print("=" * 60)
        print("\nTo test with a real contract:")
        print("  1. Upload data/sample_contracts/high_risk_test_contract.txt to the web app")
        print("  2. Review the risk scores and mitigation strategies")
        print("  3. Check that IP Risk category appears in results")
        print()
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
