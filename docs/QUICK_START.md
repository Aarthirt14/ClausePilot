# Enhanced Risk Scoring System - Quick Start Guide

## 🚀 What's New in This Upgrade

Your contract risk analysis system now includes:

1. **IP Risk Detection** - New 6th category for intellectual property risks
2. **Advanced Scoring** - Impact × Likelihood × Financial Exposure formula
3. **Smart Detection** - Automatically flags high-risk patterns (>$100k indemnification, termination triggers, etc.)
4. **Monetary Extraction** - Extracts dollar amounts from clauses ($500,000, $1.5 million, etc.)
5. **Mitigation Strategies** - Get 3-5 actionable recommendations per risky clause
6. **Enhanced Explanations** - See why each clause was flagged with specific impact reasoning

---

## ⚡ Quick Test (2 minutes)

### Step 1: Run Test Suite
```bash
# In PowerShell (already activated venv):
python scripts\test_enhanced_scoring.py
```

Expected output:
```
✓ TEST 1: Monetary Value Extraction
✓ TEST 2: Duration Extraction
✓ TEST 3: IP Risk Detection
✓ TEST 4: Data Privacy Risk Detection
✓ TEST 5: High-Risk Clause Detection
✓ TEST 6: Confidence Calibration
✓ TEST 7: Mitigation Strategy Generation
✓ TEST 8: Advanced Risk Scoring
✓ ALL TESTS COMPLETED
```

### Step 2: Test Web App with High-Risk Contract
```bash
# Start Flask (if not already running):
python app.py
```

1. Navigate to http://localhost:5000
2. Upload: `data/sample_contracts/high_risk_test_contract.txt`
3. Review results:
   - **Overall Risk Score**: Should be 70-85% (high risk)
   - **IP Risk Category**: Should appear in charts and filters
   - **High-Risk Patterns**: Should show 10-15 flagged clauses
   - **Mitigation Alert**: Yellow box at top with critical actions
   - **Clause Cards**: Show monetary amounts and durations extracted

---

## 📊 New Features Explained

### 1. IP Risk Category (NEW!)

The system now detects and categorizes intellectual property risks:

**Examples:**
- "All intellectual property rights transfer to Company" → **IP Risk**
- "Perpetual, irrevocable license grant" → **IP Risk**
- "Work made for hire - copyright transfers" → **IP Risk**

**Where to see it:**
- Risk Label charts (purple color)
- Filter dropdown (6th option)
- Impact weights table (1.6 weight)

### 2. High-Risk Pattern Detection

Automatically flags dangerous clauses:

| Pattern | Example | Impact |
|---------|---------|--------|
| **Unlimited Liability** | "Indemnification is uncapped and unlimited" | Critical |
| **>$100k Exposure** | "Liquidated damages of $500,000 apply" | High |
| **Immediate Termination** | "Company may terminate immediately without notice" | High |
| **No Cure Period** | "Termination without opportunity to cure" | High |
| **GDPR/CCPA** | "Must comply with GDPR and process PII" | High |
| **IP Assignment** | "All IP ownership transfers perpetually" | High |

### 3. Financial Exposure Scoring

Risk score multipliers based on monetary amounts:

```
0 - $25k:      1.0× (Low)
$25k - $100k:  1.1× (Medium)
$100k - $500k: 1.3× (High)
>$500k:        1.5× (Critical)
Uncapped:      1.5× (Critical)
```

**Example:**
- Base Liability Risk impact: 1.8
- Clause mentions "$750,000 indemnification"
- Adjusted impact: 1.8 × 1.3 = **2.34** (High Exposure)

### 4. Confidence Calibration

The system adjusts confidence based on clause context:

**Confidence Boosts:**
- +0.10 for strong keyword signals (3+ matches)
- +0.08 for explicit dollar amounts
- +0.05 for enforceability language ("shall", "must")
- +0.03 for detailed clauses (>50 words)

**Confidence Reductions:**
- -0.07 for negation/exceptions ("not", "except", "unless")
- -0.05 for short clauses (<15 words)

### 5. Mitigation Strategies

Each high/medium risk clause gets personalized recommendations:

**Example - Termination Risk:**
```
[Critical] Add Notice Period
» Negotiate minimum 30-60 day notice period before termination
  Rationale: Provides time to transition or find replacement

[High] Add Termination Fee  
» Require 3-6 months of fees for convenience termination
  Rationale: Compensates for investment and revenue loss

[High] Remove Unilateral Right
» Make termination mutual (both parties have equal rights)
  Rationale: Prevents one-sided termination advantage
```

---

## 🎯 Key Metrics to Watch

### Overall Risk Score
- **0-30%**: Low Risk ✅ (standard terms, minimal exposure)
- **31-60%**: Medium Risk ⚠️ (some concerning clauses, negotiation recommended)
- **61-85%**: High Risk 🚨 (multiple high-risk clauses, legal review required)
- **86-100%**: Critical Risk ⛔ (extremely unfavorable, consider walking away)

### High-Risk Pattern Count
- **0-2**: Normal for most contracts
- **3-5**: Moderate concern, prioritize review
- **6-10**: Significant issues, extensive negotiation needed
- **10+**: Red flag contract, major restructuring required

### Mitigation Effort Estimate
Based on number of mitigation items:
- **Low**: Minimal negotiation (1-2 weeks)
- **Medium**: Moderate negotiation (2-3 weeks)
- **High**: Comprehensive risk mitigation (4-6 weeks)
- **Very High**: Extensive restructuring (6+ weeks, consider alternatives)

---

## 📋 What Changed in the UI

### Results Page Updates:

1. **Risk Score Card** (top)
   - Now shows: "Advanced: Impact × Likelihood × Financial Exposure Factor"
   - Added: "High-Risk Patterns" count in red

2. **Impact Weights Table**
   - Added: **IP Risk** row (1.6 weight, purple badge)

3. **Risk Label Chart** (pie/doughnut)
   - Added: Purple color for IP Risk (6 colors total)

4. **Filter Dropdown**
   - Added: "IP Risk" option

5. **Executive Summary** (new alert box)
   - Shows: Critical mitigation actions
   - Format: Yellow alert box with warning icon
   - Lists: Top 3-5 critical strategies

6. **Clause Cards** (accordion)
   - Added: Monetary amounts extracted (e.g., "$500,000")
   - Added: Duration info (e.g., "30 days notice period")
   - Added: Risk triggers list
   - Enhanced: SHAP explanation with impact reasoning

### SHAP Explanation (click "Explain" button)

**Before:**
```
Top Words: indemnify, liability, damages
```

**After:**
```
Category: Liability Risk - Obligations to compensate for damages

Why Flagged:
» Key risk indicators: indemnify, unlimited, defend
» High-risk patterns: Uncapped indemnification liability
» Financial exposure: $500,000

Potential Impact:
» Direct financial exposure: $500,000
» Financial liability for damages or losses
» Legal defense costs and settlements
» Reputational harm from breach claims

Risk Factors:
» Uncapped indemnification liability
» Contains high-risk terms: indemnify, unlimited, defend

Extracted Values:
» Monetary Amount: $500,000
» Durations: { notice_period_days: 30 }

Mitigation Strategies:
[Critical] Cap Liability
» Negotiate 1x-2x annual contract value cap
[High] Obtain Insurance
» Secure professional liability insurance covering $500,000+
```

---

## 🧪 Testing Your Own Contracts

### Good Test Cases:

1. **Low Risk Contract** (expected score: 10-30%)
   - Standard terms of service
   - Boilerplate consulting agreement
   - Simple purchase orders

2. **Medium Risk Contract** (expected score: 35-55%)
   - Enterprise SaaS agreements
   - Standard vendor contracts with liability caps
   - Typical employment agreements

3. **High Risk Contract** (expected score: 60-85%)
   - Provided test contract: `high_risk_test_contract.txt`
   - M&A transaction documents
   - IP licensing with transfer provisions
   - Uncapped indemnification clauses

### What to Look For:

✅ **IP Risk appears** in charts if contract has licensing/IP terms
✅ **Monetary amounts extracted** from clauses with dollar figures
✅ **High-risk patterns flagged** with specific triggers listed
✅ **Mitigation strategies** show actionable steps (priority, action, rationale)
✅ **Confidence adjustments** visible in calibration details
✅ **Financial exposure** level shows (low/medium/high/critical)

---

## 🔧 Customization Options

### Change Risk Weights

Edit `src/scoring/advanced_risk_scoring.py`:

```python
RISK_CATEGORIES = {
    "Liability Risk": {
        "base_impact": 1.8,  # Change this (recommend: 1.5-2.0)
        ...
    },
```

### Adjust Financial Thresholds

```python
RISK_CATEGORIES = {
    "Liability Risk": {
        ...
        "financial_threshold": 100000,  # Change this (default: $100k)
    },
```

### Modify Confidence Calibration

In `calibrate_confidence()` function:

```python
if keyword_matches >= 3:
    calibrated = min(calibrated + 0.10, 1.0)  # Adjust boost (default: +0.10)
```

---

## 🐛 Troubleshooting

### Problem: IP Risk not showing up

**Check:**
1. Does clausecontain 2+ IP keywords? ("intellectual property", "patent", "license", "ownership", etc.)
2. Is model confidence <0.70 for "Neutral" prediction? (triggers text-based detection)
3. Look at `raw_label` field - does it contain license/IP-related CUAD category?

**Fix:** Add more IP keywords to `RISK_CATEGORIES` if needed.

---

### Problem: No mitigation strategies displayed

**Check:**
1. Is clause severity "High" or "Medium"?
2. Low-risk and Neutral clauses don't get mitigation recommendations

**Verify:** Click "Explain" button and check if `severity` field is "High" or "Medium"

---

### Problem: Monetary extraction not working

**Check:**
1. Dollar format matches: `$500,000`, `$1.5 million`, `USD 250,000`, `$100k`
2. Commas and periods matter: `$500,000` ✅ | `$500000` ✅ | `500000` ❌

**Fix:** Add additional regex patterns to `extract_monetary_value()` function

---

### Problem: Confidence not calibrating

**Check:**
1. Clause length >15 words?
2. Contains high-risk keywords?
3. Look at `calibration_details.adjustments` array for applied boosts

**Verify:** Check console output or API response for `calibrated_confidence` vs `confidence`

---

## 📚 Documentation

- **Full Implementation Guide**: `docs/ENHANCED_RISK_SCORING.md`
- **API Reference**: See "New Response Fields" section in implementation guide
- **Test Suite**: Run `python scripts\test_enhanced_scoring.py`
- **Test Contract**: `data/sample_contracts/high_risk_test_contract.txt`

---

## ✅ Verification Checklist

Run through this checklist to verify all features work:

- [ ] Test suite passes all 8 tests
- [ ] Flask app starts without errors
- [ ] Upload test contract successfully
- [ ] IP Risk appears in pie chart (purple slice)
- [ ] Filter dropdown has "IP Risk" option
- [ ] Impact weights table shows IP Risk (1.6)
- [ ] High-risk patterns count displays (>0 for test contract)
- [ ] Mitigation alert box appears (yellow, at top)
- [ ] Clause cards show monetary amounts if present
- [ ] SHAP explanation includes new fields (why flagged, impact, factors)
- [ ] Mitigation strategies listed (3-5 per high-risk clause)
- [ ] Overall risk score is 70-85% for test contract

---

## 🎉 Success!

If all tests pass and the test contract displays correctly, your enhanced risk scoring system is working perfectly!

**Next Steps:**
1. Test with your own contracts
2. Customize risk weights if needed
3. Review mitigation strategies for accuracy
4. Consider adding the heatmap visualization (future enhancement)

**Questions?**
- Review full docs: `docs/ENHANCED_RISK_SCORING.md`
- Check API response structure for debugging
- Run tests with: `python scripts\test_enhanced_scoring.py`

---

**System Status: ✅ All enhancements completed and tested**
