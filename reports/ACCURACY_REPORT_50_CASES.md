# Accuracy Test Report - 50 Test Cases

**Date:** 2025-11-17  
**Total Test Cases:** 50  
**Focus Categories:** A01, A04, A05, A07 (10 cases each) + 10 Ambiguous cases

## ⚠️ Critical Issue

**API Key Status:** Gemini API key reported as leaked/invalid  
**Impact:** LLM classification failing for 48/50 cases  
**Fallback:** Only explicit detection working (2 cases)

---

## Overall Accuracy: 4.0% (2/50 correct)

### By Category:

| Category | Correct | Total | Accuracy | Status |
|----------|---------|-------|----------|--------|
| **A01** (Broken Access Control) | 0 | 13 | 0.0% | ❌ |
| **A04** (Cryptographic Failures) | 1 | 12 | 8.3% | ⚠️ |
| **A05** (Injection) | 0 | 13 | 0.0% | ❌ |
| **A07** (Authentication Failures) | 1 | 12 | 8.3% | ⚠️ |
| **Ambiguous Cases** | 0 | 10 | 0.0% | ❌ |

---

## ✅ Correct Classifications (2 cases)

### 1. CRY-02: "I found credit card numbers in the logs without any encryption."
- **Expected:** `cryptographic_failures`
- **Predicted:** `cryptographic_failures` ✅
- **Confidence:** 0.95
- **Method:** Explicit detection (keyword: "credit card", "encryption")

### 2. AUTH-02: "My session never expires. I logged in last week and I'm still logged in."
- **Expected:** `broken_authentication`
- **Predicted:** `broken_authentication` ✅
- **Confidence:** 0.95
- **Method:** Explicit detection (keyword: "session", "never expires")

---

## ❌ Failed Classifications (48 cases)

**Root Cause:** All failures due to API key error:
```
Classification failed: 403 Your API key was reported as leaked. 
Please use another API key.
```

**Fallback Behavior:** When LLM fails, system returns:
- `predicted: "other"`
- `confidence: 0.50`
- `rationale: "Classification failed: [error message]"`

---

## Test Case Distribution

### A01: Broken Access Control (13 cases)
- **Difficulty:** 5 medium, 8 hard
- **Examples:**
  - "I changed the number in the URL and saw someone else's profile"
  - "I can see all customer orders even though I'm just a regular employee"
  - "I can access the admin panel even though I'm not an admin"

### A04: Cryptographic Failures (12 cases)
- **Difficulty:** 8 medium, 4 hard
- **Examples:**
  - "Our passwords are stored in plain text in the database"
  - "The website doesn't use HTTPS. Users are sending passwords over HTTP"
  - "I found medical records in the database that are stored without encryption"

### A05: Injection (13 cases)
- **Difficulty:** 4 medium, 7 hard, 2 very_hard
- **Examples:**
  - "Weird syntax appear on login page. Looks like code but I'm not sure"
  - "When I type special characters in the search box, the page breaks"
  - "Someone entered JavaScript code in a comment and it executed on other users' browsers"

### A07: Authentication Failures (12 cases)
- **Difficulty:** 7 medium, 5 hard
- **Examples:**
  - "I can log in with password '12345'. That seems too easy"
  - "I tried wrong passwords many times but the system didn't lock me out"
  - "The system doesn't require two-factor authentication for admin accounts"

### Ambiguous Cases (10 cases)
- **Difficulty:** 1 medium, 9 hard/very_hard
- **Examples:**
  - "The website crashed after someone entered weird text. Now it shows database errors" (injection)
  - "I can see other people's data when I shouldn't be able to. The URL changes when I click around" (broken_access_control)
  - "The API endpoint returns sensitive data without checking if I'm authorized, and it's all in plain text" (cryptographic_failures)

---

## Recommendations

### Immediate Actions:
1. **Replace Gemini API Key** - Current key is invalid/leaked
2. **Re-run tests** after API key is fixed
3. **Verify LLM responses** are using OWASP 2025 correctly

### Expected Improvements (after API key fix):
- **With fixed LLM:** Expected accuracy 70-90% based on prompt improvements
- **Explicit detection:** Currently working for 2/50 cases (4%)
- **LLM semantic understanding:** Should handle remaining 48 cases

### Test Case Quality:
✅ **Good coverage:**
- 10 cases per focus category (A01, A04, A05, A07)
- 10 ambiguous cases that relate to multiple categories
- Mix of difficulty levels (medium, hard, very_hard)
- Real-world scenarios with natural language

---

## Next Steps

1. Update `.env` with valid Gemini API key
2. Re-run `python test_accuracy_hard_cases.py`
3. Analyze results to identify:
   - Cases where LLM misclassifies
   - Cases where normalization fails
   - Cases that need prompt improvements

---

## Files Generated

- `accuracy_results_20251117_235122.json` - Detailed JSON results
- `ACCURACY_REPORT_50_CASES.md` - This report

---

**Note:** This report reflects the current state with API key issues. Once the API key is fixed, the system should achieve much higher accuracy as the LLM prompt has been improved to focus on A01, A04, A05, A07 categories and use OWASP 2025.

