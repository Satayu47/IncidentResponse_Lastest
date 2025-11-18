# Baseline Comparison Testing Guide

This guide explains how to test the chatbot with ChatGPT as a baseline model and generate IEEE-formatted reports.

## Overview

The system now supports both **Gemini** and **OpenAI/ChatGPT** models for incident classification. You can compare their performance using the baseline comparison test script.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `google-generativeai` (for Gemini)
- `openai` (for ChatGPT)

### 2. Configure API Keys

Set environment variables (or use `.env` file):

```bash
# For Gemini
export GEMINI_API_KEY="your-gemini-api-key"

# For OpenAI/ChatGPT
export OPENAI_API_KEY="your-openai-api-key"
```

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY = "your-gemini-api-key"
$env:OPENAI_API_KEY = "your-openai-api-key"
```

## Running Baseline Comparison Tests

### Basic Usage

```bash
python scripts/test_baseline_comparison.py
```

This will:
1. Test Gemini (default: `gemini-2.5-pro`) on all test cases
2. Test OpenAI (default: `gpt-4o`) on all test cases
3. Compare results and save to `reports/baseline_comparison_TIMESTAMP.json`

### Advanced Options

```bash
# Use different models
python scripts/test_baseline_comparison.py \
    --gemini-model "gemini-2.5-pro" \
    --openai-model "gpt-4o-mini"

# Limit to first 10 test cases (for quick testing)
python scripts/test_baseline_comparison.py --limit 10

# Specify API keys directly
python scripts/test_baseline_comparison.py \
    --gemini-key "your-key" \
    --openai-key "your-key"

# Custom output file
python scripts/test_baseline_comparison.py \
    --output "reports/my_comparison.json"
```

### Example Output

```
============================================================
BASELINE COMPARISON TEST
Test Cases: 50
Gemini Model: gemini-2.5-pro
OpenAI Model: gpt-4o
============================================================

Testing GEMINI: gemini-2.5-pro
[1/50] BAC-01: I changed the number in the URL...
  ✅ Expected: broken_access_control, Got: broken_access_control (conf: 0.95, 2.34s)
...

============================================================
COMPARISON SUMMARY
============================================================
Gemini (gemini-2.5-pro):
  Accuracy: 98.00% (49/50)
  Avg Time: 2.45s

OpenAI (gpt-4o):
  Accuracy: 96.00% (48/50)
  Avg Time: 1.89s

Difference:
  Accuracy: +2.00% (Gemini better)
  Speed: +0.56s (OpenAI faster)
============================================================
```

## Generating IEEE-Formatted Reports

After running the comparison test, generate an IEEE-formatted report:

```bash
python scripts/generate_ieee_baseline_report.py reports/baseline_comparison_TIMESTAMP.json
```

This creates `reports/IEEE_Baseline_Comparison.md` with:
- **Table I**: Overall Performance Comparison
- **Table II**: Category-Wise Accuracy Comparison
- **Table III**: Sample Test Case Results
- **Table IV**: Performance Metrics
- Methodology section
- Results analysis
- Conclusion

### Custom Output File

```bash
python scripts/generate_ieee_baseline_report.py \
    reports/baseline_comparison_20251118_120000.json \
    -o reports/IEEE_Baseline_Report.md
```

## Complete Workflow

1. **Run comparison test:**
   ```bash
   python scripts/test_baseline_comparison.py --limit 50
   ```

2. **Generate IEEE report:**
   ```bash
   python scripts/generate_ieee_baseline_report.py \
       reports/baseline_comparison_*.json
   ```

3. **View results:**
   - JSON results: `reports/baseline_comparison_*.json`
   - IEEE report: `reports/IEEE_Baseline_Comparison.md`

## Model Selection

The `LLMAdapter` automatically detects which provider to use based on:

1. **Model name:**
   - `gpt-*`, `o1-*`, `o3-*` → OpenAI
   - `gemini-*` → Gemini

2. **API key format:**
   - `sk-*` → OpenAI
   - `AIza*` → Gemini

### Using in Code

```python
from src.llm_adapter import LLMAdapter

# Use Gemini (default)
adapter = LLMAdapter(model="gemini-2.5-pro")

# Use OpenAI/ChatGPT
adapter = LLMAdapter(model="gpt-4o")

# Auto-detect from API key
adapter = LLMAdapter(model="gpt-4o", api_key="sk-...")
```

## Supported Models

### Gemini Models
- `gemini-2.5-pro` (default)
- `gemini-2.0-flash-exp`
- `gemini-1.5-pro`

### OpenAI Models
- `gpt-4o` (recommended)
- `gpt-4o-mini` (faster, cheaper)
- `gpt-4-turbo`
- `gpt-3.5-turbo`

## Troubleshooting

### "openai package not installed"
```bash
pip install openai>=1.0.0
```

### "API key not valid"
- Check your API keys are set correctly
- Verify keys are valid and have sufficient credits
- For OpenAI: Check API key starts with `sk-`
- For Gemini: Check API key starts with `AIza`

### Rate Limiting
The script includes rate limiting:
- Gemini: 4.5s between requests (15 RPM free tier)
- OpenAI: 1.0s between requests

If you hit rate limits, the script will show errors. Wait and retry.

## Notes

- **No API keys in code**: All API keys are loaded from environment variables or `.env` file
- **Git-safe**: `.env` is in `.gitignore`, so API keys won't be committed
- **Cost awareness**: Each test case makes 1 API call per model. 50 test cases = 100 API calls total
- **Deterministic**: Both models use low temperature (0.1) for consistent results

## Example IEEE Report Structure

The generated IEEE report includes:

1. **Executive Summary** - High-level comparison
2. **Table I** - Overall performance metrics
3. **Table II** - Category-wise accuracy breakdown
4. **Table III** - Sample test case results
5. **Table IV** - Performance metrics (accuracy, speed, category wins)
6. **Methodology** - Test configuration and process
7. **Results Analysis** - Detailed findings
8. **Conclusion** - Recommendations

Perfect for academic papers and technical reports!

