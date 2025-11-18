# Accuracy Test Suite

## Test File: `test_accuracy_50_cases.py`

This test suite evaluates classification accuracy on **50 test cases** covering:
- **A01** (Broken Access Control): 10 cases
- **A04** (Cryptographic Failures): 10 cases  
- **A05** (Injection): 10 cases
- **A07** (Authentication Failures): 10 cases
- **Ambiguous Cases**: 10 cases (relate to multiple categories)

### Test Case Distribution

- **Total**: 50 cases
- **Hard/Very Hard**: 27 cases (24 hard + 3 very_hard)
- **Medium**: 23 cases

## Usage

### Test All 50 Cases (Default)
```bash
python tests/accuracy/test_accuracy_50_cases.py
```

### Test Only Hard Cases (27 cases)
```bash
python tests/accuracy/test_accuracy_50_cases.py --hard
```

## Output

- **Console**: Real-time test results with accuracy summary
- **JSON Report**: Saved to `reports/accuracy_results_*.json`
  - `accuracy_results_all_50_*.json` - All 50 cases
  - `accuracy_results_hard_only_*.json` - Hard cases only

## Test Case Source

All test cases are defined in `test_cases.py` in the project root.

## Expected Accuracy

- **Target**: 70%+ overall accuracy
- **Excellent**: 90%+ overall accuracy
- **Good**: 70-89% overall accuracy

