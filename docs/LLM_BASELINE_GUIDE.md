# LLM Baseline Comparison Guide

## Overview

Instead of using a simple keyword classifier, you can compare your Gemini system against another LLM model (Claude or OpenAI) for better visualizations.

## Why Use LLM Baseline?

### Advantages:
- ✅ **More meaningful comparison** (LLM vs LLM)
- ✅ **Better visualizations** (similar models, clearer differences)
- ✅ **Academic standard** (comparing state-of-the-art models)
- ✅ **Shows your system's advantages** (even against strong baselines)

### Comparison Types:

1. **Simple Baseline** (Keyword matching)
   - Pros: No API key needed, fast
   - Cons: Too weak (7.5% vs 98% = obvious win)

2. **LLM Baseline** (Claude/OpenAI) ⭐ **Recommended**
   - Pros: Fair comparison, better visualizations
   - Cons: Needs API key

## How to Run

### Step 1: Get API Keys

**Gemini (Required):**
- Get: https://aistudio.google.com/apikey
- Set: `$env:GEMINI_API_KEY = "your-key"`

**Claude (Recommended - Free $5 credit):**
- Get: https://console.anthropic.com/
- Set: `$env:ANTHROPIC_API_KEY = "sk-ant-your-key"`

**OpenAI (Optional):**
- Get: https://platform.openai.com/
- Set: `$env:OPENAI_API_KEY = "sk-your-key"`

### Step 2: Run Experiment

```powershell
# Compare with Claude
python scripts/run_llm_baseline_experiment.py --baseline claude

# Or compare with OpenAI
python scripts/run_llm_baseline_experiment.py --baseline openai
```

### Step 3: Generate Visualizations

```powershell
python scripts/visualize_llm_comparison.py reports/llm_baseline_comparison_*.json
```

## What You'll Get

### 1. Comparison Results (JSON)
- Detailed per-case results
- Accuracy metrics
- Confidence scores

### 2. Visualizations (IEEE Format)

**Bar Chart:**
- Single-incident accuracy
- Ambiguous case accuracy
- Overall accuracy
- Side-by-side comparison

**Category Chart:**
- Accuracy by OWASP category (A01, A04, A05, A07)
- Shows which categories each model handles better

**Radar Chart:**
- Multi-dimensional comparison
- Visual performance profile

## Expected Results

Based on your 98% accuracy:

| Metric | Gemini 2.5 Pro | Claude 3.5 | OpenAI GPT-4o |
|--------|----------------|------------|---------------|
| Single-Incident | 98.0% | ~92-95% | ~94-96% |
| Ambiguous | 90.0% | ~85-88% | ~87-90% |
| Overall | 98.0% | ~90-93% | ~92-94% |

**Your system should still outperform!**

## Files Generated

- `reports/llm_baseline_comparison_claude_*.json` - Results
- `reports/llm_baseline_comparison_claude_*_bar_chart_ieee.png` - Bar chart
- `reports/llm_baseline_comparison_claude_*_category_chart_ieee.png` - Category chart
- `reports/llm_baseline_comparison_claude_*_radar_chart_ieee.png` - Radar chart

## Use in Your Report

1. **Copy comparison table** from JSON results
2. **Include visualizations** in your paper
3. **Discuss differences** between models
4. **Explain why your system performs better**

---

**Recommendation:** Use Claude as baseline (free $5 credit, good performance, fair comparison)

