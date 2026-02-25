"""
Risk Mitigation Strategy Engine

Provides actionable recommendations for reducing contract risk exposure
based on clause type, severity, and specific risk triggers.
"""

from typing import Dict, List


def generate_mitigation_strategies(
    label: str,
    severity: str,
    risk_triggers: List[str],
    monetary_value: float = 0.0,
    durations: Dict[str, int] = None
) -> List[Dict[str, str]]:
    """
    Generate tailored mitigation strategies for a risky clause.
    
    Args:
        label: Risk category (Liability Risk, Termination Risk, etc.)
        severity: Risk severity level (High, Medium, Low)
        risk_triggers: List of specific risk factors detected
        monetary_value: Extracted financial amount
        durations: Extracted time durations
    
    Returns:
        List of mitigation strategies with priority and action items
    """
    strategies = []
    
    if durations is None:
        durations = {}
    
    # Skip neutral clauses
    if label == "Neutral" or severity == "None":
        return strategies
    
    # === LIABILITY RISK MITIGATIONS ===
    if label == "Liability Risk":
        if any("uncapped" in trigger.lower() or "unlimited" in trigger.lower() for trigger in risk_triggers):
            strategies.append({
                "priority": "Critical",
                "strategy": "Cap Liability",
                "action": "Negotiate a liability cap (e.g., 1x or 2x annual contract value) to limit maximum exposure.",
                "rationale": "Uncapped liability creates unlimited financial risk. Industry standard is to cap at a multiple of fees paid."
            })
            strategies.append({
                "priority": "Critical",
                "strategy": "Add Exclusions",
                "action": "Exclude liability for consequential, indirect, or punitive damages unless explicitly required.",
                "rationale": "Consequential damages can far exceed direct contract value."
            })
        
        if monetary_value >= 100000:
            strategies.append({
                "priority": "High",
                "strategy": "Obtain Liability Insurance",
                "action": f"Secure professional liability insurance covering at least ${monetary_value:,.0f} to transfer risk.",
                "rationale": "Insurance mitigates financial impact of indemnification claims."
            })
        
        if any("indemnif" in trigger.lower() for trigger in risk_triggers):
            strategies.append({
                "priority": "High",
                "strategy": "Mutual Indemnification",
                "action": "Negotiate mutual indemnification obligations to balance risk between parties.",
                "rationale": "One-sided indemnification creates asymmetric risk exposure."
            })
            strategies.append({
                "priority": "Medium",
                "strategy": "Add Carve-Outs",
                "action": "Exclude indemnification for third-party claims arising from other party's actions or IP.",
                "rationale": "Limits scope of indemnification to your direct actions only."
            })
        
        if severity == "High":
            strategies.append({
                "priority": "High",
                "strategy": "Legal Review Required",
                "action": "Have legal counsel review liability provisions before signing.",
                "rationale": "High-severity liability clauses require expert interpretation and negotiation."
            })
    
    # === TERMINATION RISK MITIGATIONS ===
    elif label == "Termination Risk":
        if any("immediate" in trigger.lower() for trigger in risk_triggers):
            strategies.append({
                "priority": "Critical",
                "strategy": "Add Notice Period",
                "action": "Negotiate minimum 30-60 day notice period before termination becomes effective.",
                "rationale": "Provides time to find replacement services or wind down operations."
            })
        
        if any("convenience" in trigger.lower() or "without cause" in trigger.lower() for trigger in risk_triggers):
            strategies.append({
                "priority": "High",
                "strategy": "Add Termination Fee",
                "action": "Require counterparty to pay termination fee (e.g., 3-6 months of fees) for convenience termination.",
                "rationale": "Compensates for investment and planned revenue loss."
            })
            strategies.append({
                "priority": "High",
                "strategy": "Remove Unilateral Right",
                "action": "Make termination for convenience mutual (both parties have equal rights).",
                "rationale": "Prevents one-sided termination advantage."
            })
        
        if any("no cure" in trigger.lower() for trigger in risk_triggers):
            strategies.append({
                "priority": "Critical",
                "strategy": "Add Cure Period",
                "action": "Negotiate 30-day cure period for non-material breaches before termination.",
                "rationale": "Provides opportunity to fix issues and preserve business relationship."
            })
        
        notice_days = durations.get("notice_period_days", 0)
        if notice_days > 0 and notice_days < 30:
            strategies.append({
                "priority": "Medium",
                "strategy": "Extend Notice Period",
                "action": f"Extend notice period from {notice_days} to 30-60 days.",
                "rationale": "Short notice periods increase operational disruption risk."
            })
    
    # === DATA PRIVACY RISK MITIGATIONS ===
    elif label == "Data Privacy Risk":
        if any("gdpr" in trigger.lower() or "ccpa" in trigger.lower() for trigger in risk_triggers):
            strategies.append({
                "priority": "Critical",
                "strategy": "Implement Compliance Program",
                "action": "Establish GDPR/CCPA compliance program with data mapping, consent management, and breach response.",
                "rationale": "Regulatory fines for non-compliance can reach millions of dollars."
            })
            strategies.append({
                "priority": "High",
                "strategy": "Data Processing Agreement",
                "action": "Execute Data Processing Agreement (DPA) defining roles, responsibilities, and liability allocation.",
                "rationale": "DPA clarifies processor vs. controller obligations and limits liability exposure."
            })
        
        if any("pii" in trigger.lower() or "personal data" in trigger.lower() for trigger in risk_triggers):
            strategies.append({
                "priority": "High",
                "strategy": "Data Minimization",
                "action": "Collect and process only minimum PII necessary for contract performance.",
                "rationale": "Reduces exposure to data breach liability and regulatory scrutiny."
            })
            strategies.append({
                "priority": "High",
                "strategy": "Encryption & Access Controls",
                "action": "Implement encryption at rest/in transit and role-based access controls for PII.",
                "rationale": "Technical safeguards reduce breach risk and demonstrate compliance."
            })
        
        if any("breach" in trigger.lower() for trigger in risk_triggers):
            strategies.append({
                "priority": "Critical",
                "strategy": "Incident Response Plan",
                "action": "Develop and test data breach incident response plan with notification procedures.",
                "rationale": "Rapid breach response limits liability and regulatory penalties."
            })
            strategies.append({
                "priority": "Medium",
                "strategy": "Cyber Insurance",
                "action": "Obtain cyber liability insurance covering breach notification costs and regulatory fines.",
                "rationale": "Transfers financial risk of data breaches and regulatory actions."
            })
    
    # === PAYMENT RISK MITIGATIONS ===
    elif label == "Payment Risk":
        if any("liquidated damages" in trigger.lower() or "penalty" in trigger.lower() for trigger in risk_triggers):
            strategies.append({
                "priority": "High",
                "strategy": "Negotiate Reasonable Damages",
                "action": "Ensure liquidated damages are reasonable estimate of actual harm, not penalties.",
                "rationale": "Excessive penalties may be unenforceable and create budget risk."
            })
            strategies.append({
                "priority": "Medium",
                "strategy": "Add Performance Standards",
                "action": "Define clear performance metrics and SLAs to avoid ambiguity in damages triggers.",
                "rationale": "Clarity reduces disputes and unexpected penalty assessments."
            })
        
        if monetary_value >= 25000:
            strategies.append({
                "priority": "High",
                "strategy": "Payment Terms Negotiation",
                "action": f"Negotiate extended payment terms or milestone-based payments for ${monetary_value:,.0f}+.",
                "rationale": "Reduces cash flow impact and aligns payments with value delivery."
            })
        
        if any("late" in trigger.lower() or "interest" in trigger.lower() for trigger in risk_triggers):
            strategies.append({
                "priority": "Medium",
                "strategy": "Reduce Late Fees",
                "action": "Cap late payment interest at prime rate + 2-3% (avoid excessive penalties).",
                "rationale": "High interest rates compound financial impact of payment delays."
            })
            strategies.append({
                "priority": "Medium",
                "strategy": "Grace Period",
                "action": "Negotiate 10-15 day grace period before late fees apply.",
                "rationale": "Provides buffer for administrative delays without penalty."
            })
    
    # === IP RISK MITIGATIONS ===
    elif label == "IP Risk":
        if any("ownership" in trigger.lower() or "assignment" in trigger.lower() for trigger in risk_triggers):
            strategies.append({
                "priority": "Critical",
                "strategy": "Retain IP Ownership",
                "action": "Negotiate to retain ownership of pre-existing IP and background IP.",
                "rationale": "Prevents loss of core competitive assets and future business flexibility."
            })
            strategies.append({
                "priority": "High",
                "strategy": "Grant Limited License",
                "action": "Instead of assignment, grant limited license to counterparty for contract purposes only.",
                "rationale": "Maintains IP ownership while allowing necessary use."
            })
        
        if any("perpetual" in trigger.lower() or "irrevocable" in trigger.lower() for trigger in risk_triggers):
            strategies.append({
                "priority": "High",
                "strategy": "Limit License Term",
                "action": "Change perpetual license to term license tied to contract duration.",
                "rationale": "Prevents permanent loss of control over IP monetization."
            })
            strategies.append({
                "priority": "Medium",
                "strategy": "Add Reversion Rights",
                "action": "Include IP reversion clause if contract terminates or fees stop.",
                "rationale": "Restores IP control if business relationship ends."
            })
        
        if any("infringement" in trigger.lower() for trigger in risk_triggers):
            strategies.append({
                "priority": "High",
                "strategy": "IP Indemnification",
                "action": "Obtain IP indemnification from counterparty for their provided IP/technology.",
                "rationale": "Transfers risk of third-party IP claims to the IP provider."
            })
            strategies.append({
                "priority": "Medium",
                "strategy": "IP Warranty",
                "action": "Require warranty that counterparty's IP does not infringe third-party rights.",
                "rationale": "Provides contractual recourse for IP infringement claims."
            })
        
        if any("work for hire" in trigger.lower() for trigger in risk_triggers):
            strategies.append({
                "priority": "Critical",
                "strategy": "Exclude Background IP",
                "action": "Clarify that only new work created specifically for this project is work-for-hire.",
                "rationale": "Prevents loss of existing IP assets and reusable components."
            })
    
    # === GENERAL HIGH-SEVERITY MITIGATIONS ===
    if severity == "High" and not strategies:
        strategies.append({
            "priority": "High",
            "strategy": "Legal and Business Review",
            "action": "Escalate to legal counsel and senior management for review and approval.",
            "rationale": f"High-severity {label} requires expert evaluation before contract execution."
        })
        strategies.append({
            "priority": "Medium",
            "strategy": "Document Assumptions",
            "action": "Document business assumptions and risk acceptance in writing for future reference.",
            "rationale": "Creates audit trail for risk decisions and facilitates future negotiations."
        })
    
    return strategies


def generate_executive_mitigation_summary(enriched_results: List[Dict[str, object]]) -> Dict[str, object]:
    """
    Generate executive summary of top mitigation priorities across all clauses.
    
    Returns:
    {
        "critical_actions": [...],
        "high_priority_actions": [...],
        "recommended_reviews": [...],
        "estimated_effort": "..."
    }
    """
    critical_actions = []
    high_priority_actions = []
    recommended_reviews = []
    
    # Collect mitigation strategies from all high/medium risk clauses
    for item in enriched_results:
        severity = item.get("severity", "None")
        if severity in ["High", "Medium"]:
            label = item.get("label", "")
            risk_triggers = item.get("high_risk_detection", {}).get("risk_triggers", [])
            monetary_value = item.get("extracted_metadata", {}).get("monetary_value", 0.0)
            durations = item.get("extracted_metadata", {}).get("durations", {})
            
            strategies = generate_mitigation_strategies(
                label, severity, risk_triggers, monetary_value, durations
            )
            
            for strategy in strategies:
                if strategy["priority"] == "Critical":
                    critical_actions.append(strategy)
                elif strategy["priority"] == "High":
                    high_priority_actions.append(strategy)
    
    # Deduplicate strategies by key
    def deduplicate_strategies(strategies_list):
        seen = set()
        unique = []
        for s in strategies_list:
            key = (s["strategy"], s["action"][:50])  # Use first 50 chars of action as key
            if key not in seen:
                seen.add(key)
                unique.append(s)
        return unique
    
    critical_actions = deduplicate_strategies(critical_actions)
    high_priority_actions = deduplicate_strategies(high_priority_actions)
    
    # Generate recommended reviews
    high_risk_count = sum(1 for item in enriched_results if item.get("severity") == "High")
    if high_risk_count > 0:
        recommended_reviews.append(f"Legal review required for {high_risk_count} high-severity clauses")
    
    liability_risk_count = sum(1 for item in enriched_results if item.get("label") == "Liability Risk" and item.get("severity") in ["High", "Medium"])
    if liability_risk_count > 0:
        recommended_reviews.append(f"Risk management review for {liability_risk_count} liability clauses")
    
    ip_risk_count = sum(1 for item in enriched_results if item.get("label") == "IP Risk" and item.get("severity") in ["High", "Medium"])
    if ip_risk_count > 0:
        recommended_reviews.append(f"IP counsel review for {ip_risk_count} intellectual property clauses")
    
    # Estimate effort
    total_mitigations = len(critical_actions) + len(high_priority_actions)
    if total_mitigations == 0:
        effort_estimate = "Low - Minimal negotiation required"
    elif total_mitigations <= 3:
        effort_estimate = "Medium - 2-3 weeks for negotiation and legal review"
    elif total_mitigations <= 7:
        effort_estimate = "High - 4-6 weeks for comprehensive risk mitigation"
    else:
        effort_estimate = "Very High - 6+ weeks; consider walking away if risks cannot be mitigated"
    
    return {
        "critical_actions": critical_actions[:5],  # Top 5
        "high_priority_actions": high_priority_actions[:10],  # Top 10
        "recommended_reviews": recommended_reviews,
        "total_mitigation_items": total_mitigations,
        "estimated_effort": effort_estimate,
        "risk_acceptance_threshold": "Critical and High priority mitigations should be addressed before contract execution."
    }
