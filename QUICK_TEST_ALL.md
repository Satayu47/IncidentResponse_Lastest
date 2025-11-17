# 🚀 Quick Test Commands

## Run All Tests

```powershell
# Classification accuracy tests (100 cases)
pytest tests/test_human_multiturn_full.py -v

# DAG merge validation (22 tests)
pytest tests/test_multilabel_merge.py -v

# Run everything
pytest tests/ -v
```

---

## Generate Reports

```powershell
# Classification accuracy report
pytest tests/test_human_multiturn_full.py --json-report --json-report-file=tests/results.json
python tests/generate_accuracy_report.py tests/results.json
cat tests/ACCURACY_REPORT.md

# Merge test results (already generated)
cat MERGE_TEST_RESULTS.md
```

---

## Expected Results

### Classification Tests (100 total)
- **Target:** ≥85% accuracy overall
- **Time:** ~45-60 seconds (OpenAI API calls)
- **Requires:** OPENAI_API_KEY in .env

### Merge Tests (22 total)
- **Status:** ✅ 22/22 PASSED (100%)
- **Time:** <1 second
- **No API required**

---

## Quick Validation

```powershell
# Just show summary
pytest tests/ -v --tb=line | Select-String -Pattern "passed|failed|======"

# Show merge stats
pytest tests/test_multilabel_merge.py -v -s | Select-String -Pattern "Critical|All 8"
```

**Expected output:**
```
✅ Critical four playbooks merged successfully!
   Merged DAG size: 62 nodes
   
✅ All 8 playbooks merged successfully!
   Merged DAG size: 130 nodes
```

---

## Show Instructor/Ajarn

1. **Classification accuracy:**
   ```powershell
   cat tests/ACCURACY_REPORT.md
   ```

2. **Merge validation:**
   ```powershell
   cat MERGE_TEST_RESULTS.md
   ```

3. **Critical four categories (A01, A04, A05, A07):**
   ```powershell
   pytest tests/test_multilabel_merge.py::test_merge_critical_four_labels -v -s
   ```

---

## Files to Show

📊 **For grading/review:**
- `MERGE_TEST_RESULTS.md` - All merge tests passed (22/22)
- `tests/ACCURACY_REPORT.md` - Classification accuracy metrics
- `tests/test_multilabel_merge.py` - Test source code
- `tests/test_human_multiturn_full.py` - 100-case test suite

📄 **Documentation:**
- `README.md` - Main overview with test sections
- `RUN_TESTS.md` - Complete testing guide
- `QUICK_TEST.md` - Quick reference (this file)

---

## Troubleshooting

**Tests skip with "OPENAI_API_KEY not set":**
```powershell
# Create .env file
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-...
```

**Import errors:**
```powershell
pip install -r requirements.txt
pip install pytest pytest-json-report
```

**Just want to validate DAG merging (no LLM):**
```powershell
pytest tests/test_multilabel_merge.py -v
# ✅ 22/22 passed in <1 second
```

---

## Test Summary

| Test Suite                | Tests | Status | Time   | Requires API? |
|---------------------------|-------|--------|--------|---------------|
| Multilabel DAG Merge      | 22    | ✅ 100% | <1s    | No            |
| Classification Accuracy   | 100   | TBD    | ~60s   | Yes (OpenAI)  |
| **TOTAL**                 | 122   | -      | ~60s   | -             |

---

**Ready to test? Just run:**

```powershell
pytest tests/test_multilabel_merge.py -v
```

✅ **Expected: 22 passed in 0.59s**
