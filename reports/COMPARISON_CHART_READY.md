# Baseline Comparison Chart - Ready to Generate

## ✅ What's Ready

The IEEE-format comparison chart generator is complete and ready to use once you have baseline comparison results.

## 📊 Chart Features (IEEE Format)

### Visual Design
- ✅ **Serif fonts** (Times New Roman) for professional academic look
- ✅ **Side-by-side bars** showing Gemini vs OpenAI accuracy
- ✅ **High contrast colors** (blue for Gemini, orange for OpenAI)
- ✅ **Value labels** on each bar showing exact percentages
- ✅ **Clean layout** with removed top/right spines
- ✅ **300 DPI** resolution for publication quality
- ✅ **Proper sizing** (10×5 inches) for IEEE paper

### Data Displayed
- Accuracy by OWASP category (A01, A04, A05, A07)
- Direct comparison between models
- Clear visual distinction between models

## 🚀 How to Generate

### Step 1: Run Baseline Comparison Test
```bash
# Set API keys first
$env:GEMINI_API_KEY = "your-key"
$env:OPENAI_API_KEY = "your-key"

# Run comparison (50 test cases)
python scripts/test_baseline_comparison.py --limit 50
```

This creates: `reports/baseline_comparison_TIMESTAMP.json`

### Step 2: Generate Comparison Chart
```bash
python scripts/visualize_accuracy_results.py \
    reports/accuracy_results_all_50_20251118_152137.json \
    --baseline reports/baseline_comparison_*.json
```

This creates: `reports/baseline_comparison_chart_ieee.png`

## 📝 Example Figure Caption (IEEE)

```
Figure 3: Classification accuracy comparison between Gemini 2.5 Pro and 
OpenAI GPT-4o across OWASP Top 10:2025 categories. Both models were tested 
on 50 hard test cases covering A01 (Broken Access Control), A04 
(Cryptographic Failures), A05 (Injection), and A07 (Authentication Failures).
```

## 📄 LaTeX Code

```latex
\begin{figure}[!t]
\centering
\includegraphics[width=0.95\textwidth]{baseline_comparison_chart_ieee.png}
\caption{Classification accuracy comparison between Gemini 2.5 Pro and OpenAI GPT-4o.}
\label{fig:baseline_comparison}
\end{figure}
```

## 🎯 What the Chart Shows

- **Direct comparison** of accuracy per category
- **Visual performance** differences
- **Model strengths** (which categories each model excels at)
- **Overall winner** (if one model consistently outperforms)

## ⚠️ Current Status

- ✅ Chart generator: **Ready**
- ✅ IEEE formatting: **Complete**
- ⏳ Baseline test: **Needs API keys**
- ⏳ Comparison data: **Pending test run**

Once you run the baseline comparison test with valid API keys, the chart will be automatically generated in IEEE format!

