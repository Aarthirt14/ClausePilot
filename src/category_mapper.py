"""
Category Mapping Module

Maps fine-grained CUAD contract categories to high-level risk categories
including the new IP Risk category.
"""

from typing import Dict


# Mapping from CUAD dataset categories to risk categories
CUAD_TO_RISK_CATEGORY = {
    # Liability Risk
    "Uncapped Liability": "Liability Risk",
    "Cap On Liability": "Liability Risk",
    "Covenant Not To Sue": "Liability Risk",
    "Insurance": "Liability Risk",
    "Warranty Duration": "Liability Risk",
    
    # Termination Risk
    "Termination For Convenience": "Termination Risk",
    "Change Of Control": "Termination Risk",
    "Post-Termination Services": "Termination Risk",
    "Notice Period To Terminate Renewal": "Termination Risk",
    "Expiration Date": "Termination Risk",
    "Renewal Term": "Termination Risk",
    
    # Data Privacy Risk
    # (CUAD doesn't have explicit privacy categories, but we can infer from context)
    
    # Payment Risk
    "Liquidated Damages": "Payment Risk",
    "Minimum Commitment": "Payment Risk",
    "Price Restrictions": "Payment Risk",
    "Revenue/Profit Sharing": "Payment Risk",
    "Volume Restriction": "Payment Risk",
    "Most Favored Nation": "Payment Risk",
    
    # IP Risk (NEW)
    "Ip Ownership Assignment": "IP Risk",
    "Joint Ip Ownership": "IP Risk",
    "Irrevocable Or Perpetual License": "IP Risk",
    "License Grant": "IP Risk",
    "Non-Transferable License": "IP Risk",
    "Affiliate License-Licensee": "IP Risk",
    "Affiliate License-Licensor": "IP Risk",
    "Unlimited/All-You-Can-Eat-License": "IP Risk",
    "Source Code Escrow": "IP Risk",
    
    # Neutral (administrative/low-risk)
    "Document Name": "Neutral",
    "Parties": "Neutral",
    "Agreement Date": "Neutral",
    "Effective Date": "Neutral",
    "Governing Law": "Neutral",
    "Exclusivity": "Neutral",
    "No-Solicit Of Customers": "Neutral",
    "No-Solicit Of Employees": "Neutral",
    "Rofr/Rofo/Rofn": "Neutral",
    "Anti-Assignment": "Neutral",
    "Audit Rights": "Neutral",
    "Non-Compete": "Neutral",
    "Competitive Restriction Exception": "Neutral",
    "Third Party Beneficiary": "Neutral",
    "Non-Disparagement": "Neutral",
}


def map_cuad_to_risk_category(cuad_label: str) -> str:
    """
    Map a CUAD fine-grained label to a high-level risk category.
    
    Args:
        cuad_label: Original CUAD category label
    
    Returns:
        Risk category: "Liability Risk", "Termination Risk", "Data Privacy Risk", 
                       "Payment Risk", "IP Risk", or "Neutral"
    """
    # Direct mapping
    if cuad_label in CUAD_TO_RISK_CATEGORY:
        return CUAD_TO_RISK_CATEGORY[cuad_label]
    
    # Keyword-based fallback for unlisted categories
    label_lower = cuad_label.lower()
    
    # Check for IP-related keywords
    if any(kw in label_lower for kw in ['ip', 'intellectual property', 'patent', 'trademark', 
                                          'copyright', 'license', 'ownership']):
        return "IP Risk"
    
    # Check for liability keywords
    if any(kw in label_lower for kw in ['liability', 'indemnif', 'warranty', 'insurance']):
        return "Liability Risk"
    
    # Check for termination keywords
    if any(kw in label_lower for kw in ['termination', 'expir', 'renewal', 'end']):
        return "Termination Risk"
    
    # Check for payment keywords
    if any(kw in label_lower for kw in ['payment', 'fee', 'price', 'cost', 'revenue', 'damage']):
        return "Payment Risk"
    
    # Check for data privacy keywords
    if any(kw in label_lower for kw in ['data', 'privacy', 'personal', 'pii', 'gdpr', 'ccpa']):
        return "Data Privacy Risk"
    
    # Default to neutral
    return "Neutral"


def detect_ip_risk_from_text(text: str) -> bool:
    """
    Detect if clause text contains IP risk indicators even if not labeled as such.
    
    This is useful when the model wasn't explicitly trained on "IP Risk" as a category.
    """
    text_lower = text.lower()
    
    ip_keywords = [
        'intellectual property', 'ip rights', 'patent', 'trademark', 'copyright',
        'trade secret', 'proprietary', 'source code', 'license grant',
        'ownership', 'assignment', 'work for hire', 'work made for hire',
        'derivative works', 'joint ownership', 'irrevocable', 'perpetual',
        'infringement', 'license', 'licensor', 'licensee'
    ]
    
    # Count keyword matches
    matches = sum(1 for kw in ip_keywords if kw in text_lower)
    
    # If 2+ IP keywords present, likely IP risk
    return matches >= 2


def detect_data_privacy_risk_from_text(text: str) -> bool:
    """
    Detect if clause text contains data privacy risk indicators.
    
    Since CUAD doesn't have explicit privacy categories, we detect from text.
    """
    text_lower = text.lower()
    
    privacy_keywords = [
        'personal data', 'personally identifiable', 'pii',
        'gdpr', 'ccpa', 'data protection', 'data privacy',
        'data breach', 'data subject', 'data processing',
        'consent', 'opt-in', 'opt-out', 'privacy policy',
        'sensitive data', 'biometric', 'health information',
        'financial information', 'data security'
    ]
    
    matches = sum(1 for kw in privacy_keywords if kw in text_lower)
    
    return matches >= 2


def enhance_label_with_text_detection(
    original_label: str,
    clause_text: str,
    confidence: float
) -> tuple[str, float, str]:
    """
    Enhance predicted label using text-based detection for IP and Privacy risks.
    
    Args:
        original_label: Label from BERT model
        clause_text: Full clause text
        confidence: Model confidence
    
    Returns:
        (enhanced_label, adjusted_confidence, detection_reason)
    """
    # Check if IP risk detected in text
    if detect_ip_risk_from_text(clause_text):
        # If model wasn't confident, override with IP Risk
        if original_label == "Neutral" and confidence < 0.70:
            return "IP Risk", 0.75, "Text-based IP keyword detection"
        # If model suggested something else, boost confidence if it's IP-related
        elif "license" in original_label.lower() or "ownership" in original_label.lower():
            mapped = map_cuad_to_risk_category(original_label)
            if mapped == "IP Risk":
                return mapped, min(confidence + 0.10, 1.0), "CUAD label mapped to IP Risk"
    
    # Check if data privacy risk detected in text
    if detect_data_privacy_risk_from_text(clause_text):
        if original_label == "Neutral" and confidence < 0.70:
            return "Data Privacy Risk", 0.75, "Text-based privacy keyword detection"
    
    # No enhancement needed, use CUAD mapping
    mapped_label = map_cuad_to_risk_category(original_label)
    return mapped_label, confidence, "CUAD category mapping"


def get_category_description(category: str) -> str:
    """Get human-readable description of risk category."""
    descriptions = {
        "Liability Risk": "Obligations to compensate for damages, defend claims, or accept unlimited liability",
        "Termination Risk": "Clauses allowing contract termination with minimal notice or cause",
        "Data Privacy Risk": "Data privacy compliance obligations and regulatory exposure (GDPR/CCPA)",
        "Payment Risk": "Financial obligations including penalties, late fees, and payment terms",
        "IP Risk": "Intellectual property ownership, licensing, assignment, and infringement risks",
        "Neutral": "Standard contractual terms with minimal risk"
    }
    return descriptions.get(category, "Unknown risk category")
