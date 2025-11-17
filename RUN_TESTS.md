# Running the 100-Case Human-Style Test Suite

## Quick Start

```powershell
# 1. Install test dependencies
pip install pytest pytest-json-report

# 2. Ensure your .env has OPENAI_API_KEY
#    (Tests will be skipped if not set)

# 3. Run the full test suite
pytest tests/test_human_multiturn_full.py -v

# 4. Generate accuracy report with JSON output
pytest tests/test_human_multiturn_full.py -v --json-report --json-report-file=tests/results.json
python tests/generate_accuracy_report.py tests/results.json

# 5. View report
cat tests/ACCURACY_REPORT.md
```

---

## What Gets Tested

### A. Single-Incident Classification (72 tests)
Tests Phase-1 classification accuracy with human-style multi-turn conversations.

**Categories tested:**
- Broken Access Control (12 cases) - A01
- Injection (12 cases) - A03
- Broken Authentication (12 cases) - A07
- Security Misconfiguration (12 cases) - A05
- Sensitive Data Exposure (8 cases)
- Cryptographic Failures (8 cases) - A02
- Other/Non-Security (8 cases)

**Example test case:**
```
ID: BAC-01
Expected: broken_access_control
Text: "Normal staff can access /admin dashboard. They don't have 
       admin role but they can still see all reports."
```

### B. Multi-Incident / Merge Tests (28 tests)
Tests Phase-2 playbook mapping and DAG merging with complex scenarios.

**What's validated:**
- Multiple playbooks mapped for multi-category incidents
- DAG merging produces valid execution plans
- Response structure has all required fields
- OPA policy evaluation hooks present (when enabled)

**Example test case:**
```
ID: MIX-01
Expected Labels: ["broken_access_control", "injection"]
Text: "Normal users can access /admin. Also log shows ' OR 1=1 
       payloads on login."
```

---

## Understanding Results

### Test Output Format

**Passing test:**
```
PASSED tests/test_human_multiturn_full.py::test_single_incident_classification[BAC-01-broken_access_control-...]
```

**Failing test:**
```
FAILED tests/test_human_multiturn_full.py::test_single_incident_classification[INJ-03-injection-...]
❌ INJ-03 FAILED
   Expected: injection
   Got:      security_misconfiguration
   Text:     Attacker sent id=1; DROP TABLE users; in the query string.
   Coarse:   A05
   Fine:     security_misconfiguration
```

### Accuracy Metrics

After running with `--json-report`, the generated `ACCURACY_REPORT.md` includes:

1. **Overall accuracy:** `X / 72 * 100%` for single-incident tests
2. **Per-category accuracy:** Breakdown by OWASP category
3. **Failed case IDs:** Which specific tests failed
4. **Key insights:** Strengths, weaknesses, recommendations

---

## Test Options

### Run specific test types

```powershell
# Only single-incident classification tests
pytest tests/test_human_multiturn_full.py::test_single_incident_classification -v

# Only multi-incident merge tests
pytest tests/test_human_multiturn_full.py::test_multi_incident_playbook_mapping -v

# Only DAG merge validation
pytest tests/test_human_multiturn_full.py::test_dag_merge_multiple_incidents -v

# Only OPA policy tests
pytest tests/test_human_multiturn_full.py::test_opa_policy_evaluation -v
```

### Run specific categories

```powershell
# Only Broken Access Control tests
pytest tests/test_human_multiturn_full.py -k "BAC" -v

# Only Injection tests
pytest tests/test_human_multiturn_full.py -k "INJ" -v

# Only Authentication tests
pytest tests/test_human_multiturn_full.py -k "AUTH" -v
```

### Run with different verbosity

```powershell
# Quiet mode (just summary)
pytest tests/test_human_multiturn_full.py -q

# Verbose mode (show each test)
pytest tests/test_human_multiturn_full.py -v

# Very verbose (show full output)
pytest tests/test_human_multiturn_full.py -vv

# Stop on first failure
pytest tests/test_human_multiturn_full.py -x
```

---

## Interpreting Accuracy

### What's "Good" Accuracy?

- **≥ 85%:** Excellent - production-ready for that category
- **70-84%:** Good - minor tuning needed
- **60-69%:** Fair - needs prompt engineering or more keywords
- **< 60%:** Poor - requires significant improvement

### Common Failure Patterns

1. **Vague language without keywords**
   - "Something feels wrong" → hard to classify
   - Solution: Add more contextual keywords to prompts

2. **Multi-category overlap**
   - "Admin uses default password" → authentication + misconfiguration
   - Solution: Accept that some cases are ambiguous

3. **"Other" category confusion**
   - Non-security issues misclassified as security
   - Solution: Strengthen "other" detection in explicit rules

4. **Emotional/human phrasing**
   - "Boss shouted 'we are hacked'" → needs better context extraction
   - Solution: LLM prompt engineering for emotional language

---

## Improving Accuracy

### 1. Update Explicit Keywords
Edit `src/explicit_detector.py`:
```python
KEYWORD_PATTERNS = {
    "injection": [
        r"sql injection",
        r"union select",
        r"\' OR 1=1",
        # Add more patterns based on failed cases
    ],
}
```

### 2. Enhance LLM Prompts
Edit `src/llm_adapter.py`:
```python
CLASSIFICATION_PROMPT = """
You are a security analyst. Given a user's incident description,
classify it into one of these OWASP 2021 categories...

Pay special attention to:
- Emotional or vague language
- Implicit security issues
- Multi-turn conversation context
...
"""
```

### 3. Adjust Confidence Thresholds
Edit `src/classification_rules.py`:
```python
def refine_label(coarse, fine, explicit, iocs):
    # If explicit detection is strong, boost confidence
    if explicit.get("confidence", 0) > 0.8:
        return explicit.get("fine", fine)
    ...
```

### 4. Add More Test Cases
Edit `tests/test_human_multiturn_full.py`:
```python
CASES_SINGLE = [
    # Add your own edge cases
    ("BAC-13", "broken_access_control",
     "Your custom test case here..."),
]
```

---

## Automated Report Generation

The report includes:
- Date/time of test run
- Overall accuracy percentage
- Per-category breakdown table
- Failed case IDs
- Key insights and recommendations
- Detailed methodology

**Sample report structure:**
```markdown
# Human-Style OWASP Test Suite Report

**Date:** 2025-11-17 14:30:00

## Test Summary
- Total single-incident cases tested: 72
- Passed: 65
- Failed: 7
- Overall accuracy: 90.3%

## Per-Category Accuracy
| Category                  | Correct | Total | Accuracy |
|---------------------------|---------|-------|----------|
| Broken Access Control     | 11      | 12    | 91.7%    |
| Injection                 | 10      | 12    | 83.3%    |
...
```

---

## Troubleshooting

### Tests are skipped
```
SKIPPED [1] OPENAI_API_KEY not set - skipping LLM tests
```
**Solution:** Create `.env` file with `OPENAI_API_KEY=sk-...`

### Import errors
```
ModuleNotFoundError: No module named 'pytest'
```
**Solution:** `pip install pytest pytest-json-report`

### API rate limits
```
openai.error.RateLimitError: Rate limit exceeded
```
**Solution:** Add delays or use different API key tier

### Low accuracy on specific category
**Solution:** 
1. Check failed case IDs in report
2. Review those test cases
3. Update prompts/keywords for that pattern
4. Re-run tests

---

## Next Steps After Testing

1. **Review ACCURACY_REPORT.md** - Identify weak categories
2. **Update prompts/keywords** - Improve low-accuracy areas
3. **Add edge cases** - Create tests for your specific use cases
4. **Iterate** - Re-run tests after each improvement
5. **Track progress** - Compare reports over time

---

## Example Full Workflow

```powershell
# Fresh start
cd c:\Users\legen\Downloads\incidentResponse_Combine

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-json-report

# Verify .env exists
cat .env  # Should show OPENAI_API_KEY=...

# Run all tests with report generation
pytest tests/test_human_multiturn_full.py -v --json-report --json-report-file=tests/results.json

# Generate accuracy report
python tests/generate_accuracy_report.py tests/results.json

# View results
cat tests/ACCURACY_REPORT.md

# Check specific failures
pytest tests/test_human_multiturn_full.py -k "BAC" -vv
```

**Expected output:**
```
============== test session starts ==============
tests/test_human_multiturn_full.py::test_single_incident_classification[BAC-01-...] PASSED [ 1%]
tests/test_human_multiturn_full.py::test_single_incident_classification[BAC-02-...] PASSED [ 2%]
...
============== 100 passed in 45.23s ==============

✅ Report generated: tests/ACCURACY_REPORT.md

📊 Summary:
   Total tests: 100
   Passed: 93
   Failed: 7
```

---

**You now have a production-ready test suite to measure and improve your incident response platform!** 🚀
