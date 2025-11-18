# Test Results Summary - Hard Classification Cases

**Date:** 2025-11-17  
**Total Test Cases:** 27  
**Focus Categories:** A01, A04, A05, A07

## Overall Accuracy: 3.7% (1/27 correct)

### By Category:

| Category | Correct | Total | Accuracy |
|----------|---------|-------|----------|
| **A01** (Broken Access Control) | 0 | 6 | 0.0% |
| **A04** (Cryptographic Failures) | 0 | 6 | 0.0% |
| **A05** (Injection) | 0 | 8 | 0.0% |
| **A07** (Authentication Failures) | 1 | 7 | 14.3% |

## Key Findings:

### ✅ Correct Classification (1 case):
- **AUTH-HARD-02**: "My session never expires. I logged in last week and I'm still logged in."
  - Predicted: `broken_authentication` ✅
  - Confidence: 0.95
  - Method: Explicit detection

### ❌ Main Issue:
**LLM is classifying most cases as "A06:2025 - Insecure Design" instead of the correct categories.**

The rationales show the LLM **understands** the issues correctly:
- Recognizes IDOR vulnerabilities
- Identifies cryptographic failures
- Detects injection attacks
- Understands authentication problems

But the **classification output** is wrong - everything becomes "Insecure Design" (A06).

### Examples of Misclassification:

1. **BAC-HARD-01**: "I changed the number in the URL and saw someone else's profile"
   - Expected: `broken_access_control`
   - Predicted: `other` (from A06 - Insecure Design)
   - Rationale correctly identifies: "IDOR vulnerability, a form of Broken Access Control"

2. **CRY-HARD-01**: "Our passwords are stored in plain text in the database"
   - Expected: `cryptographic_failures`
   - Predicted: `other` (from A06 - Insecure Design)
   - Rationale correctly identifies: "critical cryptographic failure"

3. **INJ-HARD-05**: "Someone entered JavaScript code in a comment and it executed"
   - Expected: `injection`
   - Predicted: `other` (from A06 - Insecure Design)
   - Rationale correctly identifies: "stored Cross-Site Scripting (XSS) attack"

## Root Cause Analysis:

The LLM is returning `"incident_type": "A06:2025 - Insecure Design"` for almost all cases, which then gets normalized to `"other"` because:
1. The LLM prompt may be too focused on "design flaws"
2. The normalization step doesn't properly handle "insecure_design" → correct category mapping
3. The LLM might be defaulting to A06 when uncertain

## Recommendations:

1. **Update LLM prompt** to emphasize A01, A04, A05, A07 categories
2. **Fix normalization** to map "insecure_design" to more specific categories when context suggests it
3. **Add examples** in prompt showing correct classification for these hard cases
4. **Improve canonical mapping** to handle edge cases better

## Detailed Results:

See `accuracy_results_20251117_233421.json` for complete results with rationales.

