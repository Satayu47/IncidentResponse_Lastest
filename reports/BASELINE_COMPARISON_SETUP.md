# Baseline Comparison Setup Guide

## Current Status

The baseline comparison test script is ready, but API keys need to be configured.

## Setup Instructions

### 1. Set API Keys

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY = "your-gemini-api-key-here"
$env:OPENAI_API_KEY = "your-openai-api-key-here"
```

**Or create `.env` file:**
```
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

### 2. Run Baseline Comparison

```bash
# Test on all 50 cases (takes ~5-10 minutes with rate limiting)
python scripts/test_baseline_comparison.py --limit 50

# Or test on first 10 cases for quick test
python scripts/test_baseline_comparison.py --limit 10
```

### 3. Generate Visualizations

After the comparison test completes:

```bash
# Generate IEEE comparison chart
python scripts/visualize_accuracy_results.py \
    reports/accuracy_results_all_50_*.json \
    --baseline reports/baseline_comparison_*.json
```

### 4. Generate IEEE Report

```bash
python scripts/generate_ieee_baseline_report.py \
    reports/baseline_comparison_*.json
```

## What You'll Get

1. **Comparison JSON Results** - Detailed results for both models
2. **IEEE Comparison Chart** - Side-by-side bar chart (`baseline_comparison_chart_ieee.png`)
3. **IEEE Report** - Full comparison report in IEEE format (`IEEE_Baseline_Comparison.md`)

## Expected Output

The comparison will show:
- **Accuracy by category** for both models
- **Overall accuracy** comparison
- **Response time** comparison
- **Category-wise wins** (which model performs better per category)

## Notes

- **Rate Limiting:** Gemini (4.5s delay), OpenAI (1.0s delay)
- **Cost:** ~50 API calls per model = 100 total calls
- **Time:** ~5-10 minutes for 50 test cases
- **Results:** Saved to `reports/baseline_comparison_TIMESTAMP.json`

## Current Gemini Results (For Reference)

From your latest test:
- **Overall Accuracy:** 98.0% (49/50)
- **A01:** 92.3% (12/13)
- **A04:** 100.0% (12/12)
- **A05:** 100.0% (13/13)
- **A07:** 100.0% (12/12)

Once you run the baseline comparison, you'll be able to see how ChatGPT (GPT-4o) compares to these results!

