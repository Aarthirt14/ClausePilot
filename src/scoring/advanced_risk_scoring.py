"""
Advanced Risk Scoring Module

Implements sophisticated risk scoring with:
- Impact × Likelihood × Financial/Exposure Factor
- Category-specific weight matrices
- Context-aware confidence calibration
- High-risk clause detection rules
"""

from typing import Dict, List, Tuple
import re


# Enhanced risk categories with IP Risk added
RISK_CATEGORIES = {
    "Liability Risk": {
        "base_impact": 1.8,
        "high_risk_keywords": [
            "indemnif", "unlimited liability", "uncapped liability",
            "shall defend", "hold harmless", "breach of warranty",
            "gross negligence", "willful misconduct"
        ],
        "financial_threshold": 100000,  # $100k+ triggers high exposure
        "description": "Obligations to compensate for damages, defend claims, or accept unlimited liability"
    },
    "Termination Risk": {
        "base_impact": 1.7,
        "high_risk_keywords": [
            "termination for convenience", "immediate termination",
            "without cause", "at any time", "upon notice",
            "change of control", "material breach", "cure period"
        ],
        "financial_threshold": 50000,
        "description": "Clauses allowing contract termination with minimal notice or cause"
    },
    "Data Privacy Risk": {
        "base_impact": 1.5,
        "high_risk_keywords": [
            "personal data", "personally identifiable", "pii",
            "gdpr", "ccpa", "data breach", "data protection",
            "privacy policy", "consent", "data subject rights",
            "data processing", "sensitive data", "biometric"
        ],
        "financial_threshold": 500000,  # Regulatory fines can be massive
        "description": "Data privacy compliance obligations and regulatory exposure (GDPR/CCPA)"
    },
    "Payment Risk": {
        "base_impact": 1.3,
        "high_risk_keywords": [
            "late payment", "penalty", "interest", "liquidated damages",
            "payment terms", "overdue", "default", "acceleration",
            "payment upon demand", "upfront payment"
        ],
        "financial_threshold": 25000,
        "description": "Financial obligations including penalties, late fees, and payment terms"
    },
    "IP Risk": {
        "base_impact": 1.6,
        "high_risk_keywords": [
            "intellectual property", "ip ownership", "ip assignment",
            "patent", "trademark", "copyright", "trade secret",
            "license grant", "perpetual license", "irrevocable",
            "ip infringement", "joint ownership", "work for hire",
            "derivative works"
        ],
        "financial_threshold": 100000,
        "description": "Intellectual property ownership, licensing, assignment, and infringement risks"
    },
    "Neutral": {
        "base_impact": 0.0,
        "high_risk_keywords": [],
        "financial_threshold": 0,
        "description": "Standard contractual terms with minimal risk"
    }
}


# Financial exposure multipliers
EXPOSURE_MULTIPLIERS = {
    "critical": 1.5,      # >$500k or uncapped
    "high": 1.3,          # $100k - $500k
    "medium": 1.1,        # $25k - $100k
    "low": 1.0,           # <$25k or no amount
}


def extract_monetary_value(text: str) -> float:
    """
    Extract monetary amounts from clause text using NLP patterns.
    
    Patterns covered:
    - $100,000
    - $1.5 million
    - USD 250,000
    - one hundred thousand dollars
    - 100k
    
    Returns the highest amount found, or 0.0 if none.
    """
    text_lower = text.lower()
    amounts = []
    
    # Pattern 1: $X,XXX,XXX or $X.X million/billion
    currency_patterns = [
        r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',           # $100,000.00
        r'\$\s*(\d+\.?\d*)\s*(million|billion|thousand)',   # $1.5 million
        r'usd\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',         # USD 100,000
        r'(\d{1,3}(?:,\d{3})*)\s*dollars',                  # 100,000 dollars
        r'\$\s*(\d+)k',                                      # $100k
    ]
    
    for pattern in currency_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            try:
                amount_str = match.group(1).replace(',', '')
                amount = float(amount_str)
                
                # Handle million/billion multipliers
                if len(match.groups()) > 1:
                    multiplier = match.group(2).lower()
                    if multiplier == 'thousand':
                        amount *= 1_000
                    elif multiplier == 'million':
                        amount *= 1_000_000
                    elif multiplier == 'billion':
                        amount *= 1_000_000_000
                
                # Handle k suffix
                if 'k' in match.group(0).lower():
                    amount *= 1_000
                
                amounts.append(amount)
            except (ValueError, IndexError):
                continue
    
    # Pattern 2: Text numbers (one hundred thousand)
    text_number_map = {
        'hundred': 100,
        'thousand': 1_000,
        'million': 1_000_000,
        'billion': 1_000_000_000,
    }
    
    for word, multiplier in text_number_map.items():
        if word in text_lower and 'dollar' in text_lower:
            # Simple heuristic: extract digit before the word
            pattern = rf'(\d+)\s+{word}'
            match = re.search(pattern, text_lower)
            if match:
                base = float(match.group(1))
                amounts.append(base * multiplier)
    
    return max(amounts) if amounts else 0.0


def extract_duration(text: str) -> Dict[str, int]:
    """
    Extract time durations from clause text.
    
    Returns:
    {
        "days": 30,
        "months": 12,
        "years": 2,
        "notice_period_days": 60
    }
    """
    text_lower = text.lower()
    durations = {
        "days": 0,
        "months": 0,
        "years": 0,
        "notice_period_days": 0
    }
    
    # Extract days
    day_patterns = [
        r'(\d+)\s*(?:calendar\s+)?days?',
        r'(\d+)\s*(?:-|\s)day',
    ]
    for pattern in day_patterns:
        match = re.search(pattern, text_lower)
        if match:
            durations["days"] = max(durations["days"], int(match.group(1)))
    
    # Extract months
    month_patterns = [
        r'(\d+)\s*months?',
        r'(\d+)\s*(?:-|\s)month',
    ]
    for pattern in month_patterns:
        match = re.search(pattern, text_lower)
        if match:
            durations["months"] = max(durations["months"], int(match.group(1)))
    
    # Extract years
    year_patterns = [
        r'(\d+)\s*years?',
        r'(\d+)\s*(?:-|\s)year',
    ]
    for pattern in year_patterns:
        match = re.search(pattern, text_lower)
        if match:
            durations["years"] = max(durations["years"], int(match.group(1)))
    
    # Extract notice periods
    notice_patterns = [
        r'(?:upon|with|provide|giving?)\s+(\d+)\s*(?:calendar\s+)?days?\s+(?:prior\s+)?notice',
        r'notice\s+of\s+(\d+)\s*days?',
        r'(\d+)\s*(?:-|\s)day\s+notice',
    ]
    for pattern in notice_patterns:
        match = re.search(pattern, text_lower)
        if match:
            durations["notice_period_days"] = max(durations["notice_period_days"], int(match.group(1)))
    
    return durations


def calculate_financial_exposure_factor(text: str, label: str, monetary_value: float = None) -> Tuple[str, float]:
    """
    Determine financial exposure level and multiplier.
    
    Args:
        text: Clause text
        label: Risk category label
        monetary_value: Extracted monetary amount (optional, will extract if not provided)
    
    Returns:
        (exposure_level, multiplier)
        e.g., ("high", 1.3)
    """
    if monetary_value is None:
        monetary_value = extract_monetary_value(text)
    
    text_lower = text.lower()
    
    # Check for uncapped/unlimited liability
    if any(keyword in text_lower for keyword in ['uncapped', 'unlimited', 'no limit', 'without limit']):
        return ("critical", EXPOSURE_MULTIPLIERS["critical"])
    
    # Get category-specific threshold
    category_info = RISK_CATEGORIES.get(label, {})
    threshold = category_info.get("financial_threshold", 100000)
    
    # Classify based on amount
    if monetary_value >= 500000:
        return ("critical", EXPOSURE_MULTIPLIERS["critical"])
    elif monetary_value >= 100000:
        return ("high", EXPOSURE_MULTIPLIERS["high"])
    elif monetary_value >= 25000:
        return ("medium", EXPOSURE_MULTIPLIERS["medium"])
    else:
        return ("low", EXPOSURE_MULTIPLIERS["low"])


def calibrate_confidence(
    base_confidence: float,
    label: str,
    text: str,
    monetary_value: float = None,
    context_signals: Dict[str, bool] = None
) -> Tuple[float, Dict[str, object]]:
    """
    Calibrate model confidence based on contextual signals.
    
    Factors considered:
    1. Keyword signal strength (presence of high-risk terms)
    2. Financial amount clarity (explicit $ amounts boost confidence)
    3. Clause context (enforceability, specificity)
    4. Text length and structure
    
    Returns:
        (calibrated_confidence, calibration_details)
    """
    if context_signals is None:
        context_signals = {}
    
    calibrated = base_confidence
    adjustments = []
    
    text_lower = text.lower()
    category_info = RISK_CATEGORIES.get(label, {})
    keywords = category_info.get("high_risk_keywords", [])
    
    # 1. Keyword signal strength
    keyword_matches = sum(1 for kw in keywords if kw in text_lower)
    if keyword_matches >= 3:
        calibrated = min(calibrated + 0.10, 1.0)
        adjustments.append({"factor": "Strong keyword signals", "adjustment": +0.10})
    elif keyword_matches >= 1:
        calibrated = min(calibrated + 0.05, 1.0)
        adjustments.append({"factor": "Moderate keyword signals", "adjustment": +0.05})
    
    # 2. Financial clarity
    if monetary_value is None:
        monetary_value = extract_monetary_value(text)
    
    if monetary_value > 0:
        calibrated = min(calibrated + 0.08, 1.0)
        adjustments.append({"factor": "Explicit financial amount", "adjustment": +0.08})
    
    # 3. Enforceability signals (legal language strength)
    enforceability_terms = ['shall', 'must', 'will', 'obligated', 'required', 'agrees to']
    if any(term in text_lower for term in enforceability_terms):
        calibrated = min(calibrated + 0.05, 1.0)
        adjustments.append({"factor": "Strong enforceability language", "adjustment": +0.05})
    
    # 4. Specificity check (longer, more detailed clauses)
    if len(text.split()) > 50:
        calibrated = min(calibrated + 0.03, 1.0)
        adjustments.append({"factor": "Detailed clause (high specificity)", "adjustment": +0.03})
    elif len(text.split()) < 15:
        calibrated = max(calibrated - 0.05, 0.0)
        adjustments.append({"factor": "Short clause (low specificity)", "adjustment": -0.05})
    
    # 5. Negation check (reduces confidence)
    negation_terms = ['not', 'except', 'unless', 'excluding', 'notwithstanding']
    if any(term in text_lower for term in negation_terms):
        calibrated = max(calibrated - 0.07, 0.0)
        adjustments.append({"factor": "Negation/exception language", "adjustment": -0.07})
    
    calibration_details = {
        "original_confidence": round(base_confidence, 4),
        "calibrated_confidence": round(calibrated, 4),
        "adjustments": adjustments,
        "keyword_matches": keyword_matches,
        "monetary_value": monetary_value,
    }
    
    return round(calibrated, 4), calibration_details


def detect_high_risk_clause(text: str, label: str) -> Dict[str, object]:
    """
    Apply high-risk detection rules for specific clause types.
    
    Returns:
    {
        "is_high_risk": True/False,
        "risk_triggers": ["Unlimited indemnification", "No cure period"],
        "severity_override": "High"  # or None
    }
    """
    text_lower = text.lower()
    risk_triggers = []
    is_high_risk = False
    
    # Rule 1: Termination triggers (immediate or convenience)
    if label == "Termination Risk":
        if any(term in text_lower for term in ['immediate', 'immediately', 'without notice']):
            risk_triggers.append("Immediate termination allowed")
            is_high_risk = True
        if any(term in text_lower for term in ['for convenience', 'without cause', 'at any time']):
            risk_triggers.append("Termination for convenience")
            is_high_risk = True
        if 'no cure' in text_lower or 'without opportunity to cure' in text_lower:
            risk_triggers.append("No cure period provided")
            is_high_risk = True
    
    # Rule 2: Liquidated damages, penalties, late payments
    if label in ["Payment Risk", "Liability Risk"]:
        if any(term in text_lower for term in ['liquidated damages', 'penalty', 'late fee']):
            risk_triggers.append("Liquidated damages or penalties")
            is_high_risk = True
        
        monetary_value = extract_monetary_value(text)
        if monetary_value >= 100000:
            risk_triggers.append(f"High financial exposure (${monetary_value:,.0f})")
            is_high_risk = True
    
    # Rule 3: Indemnification >$100k or uncapped
    if label == "Liability Risk":
        if any(term in text_lower for term in ['indemnif', 'hold harmless', 'defend']):
            monetary_value = extract_monetary_value(text)
            if monetary_value >= 100000:
                risk_triggers.append(f"Indemnification obligation >${monetary_value:,.0f}")
                is_high_risk = True
            if any(term in text_lower for term in ['uncapped', 'unlimited', 'no limit']):
                risk_triggers.append("Uncapped indemnification liability")
                is_high_risk = True
    
    # Rule 4: Data privacy & regulatory (PII, GDPR/CCPA)
    if label == "Data Privacy Risk":
        if any(term in text_lower for term in ['pii', 'personal data', 'personally identifiable']):
            risk_triggers.append("PII/personal data handling required")
            is_high_risk = True
        if any(term in text_lower for term in ['gdpr', 'ccpa', 'data protection regulation']):
            risk_triggers.append("GDPR/CCPA compliance obligations")
            is_high_risk = True
        if 'data breach' in text_lower:
            risk_triggers.append("Data breach liability")
            is_high_risk = True
    
    # Rule 5: IP ownership, licensing, infringement
    if label == "IP Risk":
        if any(term in text_lower for term in ['ownership', 'assign', 'transfer']):
            risk_triggers.append("IP ownership transfer or assignment")
            is_high_risk = True
        if any(term in text_lower for term in ['perpetual', 'irrevocable']):
            risk_triggers.append("Perpetual or irrevocable license grant")
            is_high_risk = True
        if 'infringement' in text_lower:
            risk_triggers.append("IP infringement liability")
            is_high_risk = True
        if 'work for hire' in text_lower or 'work made for hire' in text_lower:
            risk_triggers.append("Work-for-hire IP assignment")
            is_high_risk = True
    
    return {
        "is_high_risk": is_high_risk,
        "risk_triggers": risk_triggers,
        "severity_override": "High" if is_high_risk else None
    }


def compute_advanced_risk_score(
    label: str,
    base_confidence: float,
    text: str,
    calibrate: bool = True
) -> Dict[str, object]:
    """
    Advanced risk scoring: Impact × Likelihood × Financial Exposure Factor
    
    Returns comprehensive risk assessment including:
    - Weighted severity score
    - Calibrated confidence
    - Financial exposure analysis
    - High-risk detection results
    - Extracted metadata (monetary values, durations)
    """
    # Extract financial metadata
    monetary_value = extract_monetary_value(text)
    durations = extract_duration(text)
    
    # Calibrate confidence based on context
    if calibrate:
        calibrated_confidence, calibration_details = calibrate_confidence(
            base_confidence, label, text, monetary_value
        )
    else:
        calibrated_confidence = base_confidence
        calibration_details = {"original_confidence": base_confidence}
    
    # Get category-specific impact weight
    category_info = RISK_CATEGORIES.get(label, RISK_CATEGORIES["Neutral"])
    base_impact = category_info["base_impact"]
    
    # Calculate financial exposure factor
    exposure_level, exposure_multiplier = calculate_financial_exposure_factor(
        text, label, monetary_value
    )
    
    # Final impact with exposure adjustment
    adjusted_impact = base_impact * exposure_multiplier
    
    # Likelihood is the calibrated confidence
    likelihood = calibrated_confidence
    
    # Advanced severity score: Impact × Likelihood
    severity_score = round(adjusted_impact * likelihood, 4)
    
    # Detect high-risk patterns
    high_risk_detection = detect_high_risk_clause(text, label)
    
    # Determine final severity category
    if high_risk_detection["severity_override"]:
        severity_category = high_risk_detection["severity_override"]
    elif label == "Neutral":
        severity_category = "None"
    elif calibrated_confidence >= 0.85:
        severity_category = "High"
    elif calibrated_confidence >= 0.65:
        severity_category = "Medium"
    else:
        severity_category = "Low"
    
    return {
        "label": label,
        "confidence": base_confidence,
        "calibrated_confidence": calibrated_confidence,
        "impact": base_impact,
        "adjusted_impact": round(adjusted_impact, 4),
        "likelihood": likelihood,
        "severity_score": severity_score,
        "severity": severity_category,
        "financial_exposure": {
            "level": exposure_level,
            "multiplier": exposure_multiplier,
            "monetary_value": monetary_value,
        },
        "extracted_metadata": {
            "monetary_value": monetary_value,
            "durations": durations,
        },
        "high_risk_detection": high_risk_detection,
        "calibration_details": calibration_details,
    }


def attach_advanced_risk_scores(results: List[Dict[str, object]]) -> Tuple[List[Dict[str, object]], Dict[str, object]]:
    """
    Apply advanced risk scoring to all clauses and compute overall contract risk score.
    
    Args:
        results: List of clause predictions with basic label/confidence
    
    Returns:
        (enriched_results, risk_score_breakdown)
    """
    enriched = []
    total_score = 0.0
    max_possible = 0.0
    
    for item in results:
        clause = str(item.get("clause", "")).strip()
        label = str(item.get("label", "Neutral"))
        base_confidence = float(item.get("confidence", 0.0))
        
        # Compute advanced risk assessment
        risk_assessment = compute_advanced_risk_score(
            label=label,
            base_confidence=base_confidence,
            text=clause,
            calibrate=True
        )
        
        # Merge with original item
        enriched_item = {
            **item,
            **risk_assessment
        }
        
        enriched.append(enriched_item)
        
        # Accumulate for overall score
        total_score += risk_assessment["severity_score"]
        max_possible += risk_assessment["adjusted_impact"]
    
    # Normalize overall score to 0-100
    normalized_score = round((total_score / max_possible) * 100, 2) if max_possible > 0 else 0.0
    
    breakdown = {
        "scoring_method": "Advanced: Impact × Likelihood × Financial Exposure Factor",
        "total_severity_score": round(total_score, 4),
        "max_possible_score": round(max_possible, 4),
        "normalized_score": normalized_score,
        "category_weights": {k: v["base_impact"] for k, v in RISK_CATEGORIES.items()},
        "exposure_multipliers": EXPOSURE_MULTIPLIERS,
        "high_risk_count": sum(1 for item in enriched if item.get("high_risk_detection", {}).get("is_high_risk")),
        "calibrated_clauses": sum(1 for item in enriched if item.get("calibration_details", {}).get("adjustments")),
    }
    
    return enriched, breakdown
