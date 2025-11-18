# Baseline Comparison Experiment Guide

## Overview

This guide explains how to run a valid, correct, IEEE-formatted baseline comparison experiment comparing our system (Gemini 2.5 Pro) against baseline models (Claude, OpenAI).

## Quick Start

### Step 1: Set Up API Keys

```powershell
# Required: Gemini API key
$env:GEMINI_API_KEY = "your-gemini-key"

# Optional: Baseline model keys
$env:ANTHROPIC_API_KEY = "sk-ant-your-claude-key"
$env:OPENAI_API_KEY = "sk-your-openai-key"
```

### Step 2: Run Experiment

```powershell
# Run full experiment with Claude baseline
python scripts/run_baseline_experiment.py --limit 50 --baseline claude

# Or with OpenAI baseline
python scripts/run_baseline_experiment.py --limit 50 --baseline openai

# Or both
python scripts/run_baseline_experiment.py --limit 50 --baseline claude openai
```

### Step 3: Generate IEEE Report

```powershell
# Generate IEEE-formatted report
python scripts/generate_ieee_experiment_report.py reports/baseline_experiment_*.json
```

## What Gets Generated

### 1. Experiment Results (JSON)
- `reports/baseline_experiment_YYYYMMDD_HHMMSS.json`
- Contains:
  - Primary model results (Gemini)
  - Baseline model results (Claude/OpenAI)
  - Detailed per-case results
  - Category-wise accuracy
  - Statistical comparisons

### 2. IEEE Report (Markdown)
- `reports/IEEE_Experiment_Report_YYYYMMDD_HHMMSS.md`
- Contains:
  - Abstract
  - Methodology section
  - Results tables (IEEE format)
  - Statistical analysis
  - Category-wise comparison
  - Conclusion

## Experiment Structure

### Methodology
- **Test Cases:** 50 hard test cases
- **Primary Model:** Gemini 2.5 Pro
- **Baseline Models:** Claude 3.5 Sonnet, OpenAI GPT-4o
- **Evaluation:** Exact match accuracy
- **Categories:** A01, A04, A05, A07 (OWASP Top 10:2025)

### Metrics Collected
1. **Overall Accuracy:** (Correct / Total) × 100%
2. **Category-Wise Accuracy:** Per-category breakdown
3. **Average Confidence:** Model confidence scores
4. **Response Time:** Average time per classification
5. **Error Analysis:** Detailed per-case results

## IEEE Report Sections

### I. Introduction
- Objective
- Hypothesis

### II. Methodology
- Experimental setup
- Test case distribution
- Evaluation protocol

### III. Results
- **Table I:** Overall accuracy comparison
- **Table II:** Category-wise accuracy comparison
- **Table III:** Performance metrics comparison
- Detailed analysis

### IV. Conclusion
- Summary of findings
- Performance comparison
- Implications

## Example Output

### Table I: Overall Accuracy Comparison

| Model | Accuracy (%) | Correct/Total | Avg Confidence | Avg Time (s) |
|-------|--------------|---------------|---------------|--------------|
| **Gemini 2.5 Pro** (Proposed) | **98.00** | 49/50 | 0.923 | 2.145 |
| Claude 3.5 Sonnet (Baseline) | 94.00 | 47/50 | 0.891 | 1.876 |

### Table II: Category-Wise Accuracy Comparison

| Category | Gemini 2.5 Pro | Claude | Difference |
|----------|----------------|--------|------------|
| A01: Broken Access Control | 92.31% | 88.46% | +3.85% |
| A04: Cryptographic Failures | 100.00% | 100.00% | 0.00% |
| A05: Injection | 100.00% | 96.15% | +3.85% |
| A07: Authentication Failures | 100.00% | 100.00% | 0.00% |

## Using Existing Gemini Results

If you already have Gemini test results but no baseline yet:

```powershell
# Convert existing Gemini results to experiment format
python scripts/create_experiment_from_experiment.py reports/accuracy_results_all_50_*.json

# Generate IEEE report (without baseline comparison)
python scripts/generate_ieee_experiment_report.py reports/baseline_experiment_from_gemini_*.json
```

This creates a report showing your Gemini results, ready to add baseline comparisons later.

## Validation & Correctness

### What Makes This Valid:
1. ✅ **Controlled Experiment:** Same test cases for all models
2. ✅ **Normalized Labels:** Consistent label comparison
3. ✅ **Statistical Metrics:** Accuracy, confidence, time
4. ✅ **Category Breakdown:** Per-category analysis
5. ✅ **Error Analysis:** Detailed per-case results

### What Makes This Correct:
1. ✅ **Exact Match:** Predictions compared to ground truth
2. ✅ **Canonical Labels:** Normalized for fair comparison
3. ✅ **Rate Limiting:** Prevents API throttling
4. ✅ **Error Handling:** Graceful failure handling
5. ✅ **Reproducible:** Same inputs = same outputs

### What Makes This IEEE-Compliant:
1. ✅ **Structured Sections:** Abstract, Introduction, Methodology, Results, Conclusion
2. ✅ **Numbered Tables:** Table I, Table II, Table III
3. ✅ **Statistical Analysis:** Quantitative comparisons
4. ✅ **Professional Formatting:** Clear, concise, academic style
5. ✅ **Complete Documentation:** Methodology fully described

## Troubleshooting

### API Key Issues
- Ensure keys are set in environment variables
- Check key validity before running
- Use `scripts/test_api_key.py` to verify

### Rate Limiting
- Scripts include automatic rate limiting
- Gemini: 4.5s between calls
- Claude: 1.0s between calls
- OpenAI: 1.0s between calls

### Missing Baseline Results
- If baseline test fails, report will show only Gemini results
- You can add baseline results later by re-running with valid keys

## Next Steps

1. **Get Baseline API Keys:**
   - Claude: https://console.anthropic.com/ (free $5 credit)
   - OpenAI: https://platform.openai.com/ (requires billing)

2. **Run Full Experiment:**
   ```powershell
   python scripts/run_baseline_experiment.py --limit 50 --baseline claude
   ```

3. **Generate Report:**
   ```powershell
   python scripts/generate_ieee_experiment_report.py reports/baseline_experiment_*.json
   ```

4. **Include in Paper:**
   - Copy tables from IEEE report
   - Reference methodology section
   - Include comparison charts (if generated)

---

**Status:** ✅ Experiment framework ready
**Current:** Gemini results available (98% accuracy)
**Next:** Add baseline model results when API keys available

