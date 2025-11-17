# Quick Test Reference

## Run Tests Immediately

```powershell
# 1. Install dependencies (one time)
pip install pytest pytest-json-report

# 2. Run all 100 tests
pytest tests/test_human_multiturn_full.py -v

# 3. Generate accuracy report
pytest tests/test_human_multiturn_full.py --json-report --json-report-file=tests/results.json
python tests/generate_accuracy_report.py tests/results.json
```

## What You Get

**Instant accuracy metrics:**
- Overall accuracy percentage
- Per-category breakdown (Broken Access Control, Injection, etc.)
- List of failed test IDs
- Insights and recommendations

**Example output:**
```
============== test session starts ==============
tests/test_human_multiturn_full.py::test_single_incident_classification[BAC-01-...] PASSED [ 1%]
tests/test_human_multiturn_full.py::test_single_incident_classification[BAC-02-...] PASSED [ 2%]
...
============== 93 passed, 7 failed in 45.23s ==============
```

**Generated files:**
- `tests/results.json` - Raw test results
- `tests/ACCURACY_REPORT.md` - Formatted accuracy report

## Sample Test Cases

### Single Incident (BAC-01)
```
Expected: broken_access_control
Text: "Normal staff can access /admin dashboard. They don't have 
       admin role but they can still see all reports."
```

### Multi-Incident (MIX-01)
```
Expected: ["broken_access_control", "injection"]
Text: "Normal users can access /admin. Also log shows ' OR 1=1 
       payloads on login."
```

## Common Commands

```powershell
# Run only access control tests
pytest tests/test_human_multiturn_full.py -k "BAC" -v

# Run only injection tests
pytest tests/test_human_multiturn_full.py -k "INJ" -v

# Stop on first failure
pytest tests/test_human_multiturn_full.py -x

# Quiet mode (summary only)
pytest tests/test_human_multiturn_full.py -q
```

## Expected Results

**Good accuracy targets:**
- ≥85% = Production-ready
- 70-84% = Good, minor tuning needed
- 60-69% = Fair, needs improvement
- <60% = Requires significant work

## Full Documentation

See **[RUN_TESTS.md](RUN_TESTS.md)** for complete guide.
