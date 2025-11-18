# API Key Guide for Experiments

## What Needs API Keys?

### ✅ Baseline Keyword Classifier
- **API Key Needed:** ❌ NO
- **Why:** It's just simple keyword matching (no LLM)
- **Can run:** ✅ RIGHT NOW

### ⚠️ Proposed System (Gemini 2.5 Pro)
- **API Key Needed:** ✅ YES (Gemini API key)
- **Why:** Uses Gemini LLM for classification
- **Get it:** https://aistudio.google.com/apikey (free)

## Options

### Option 1: Run Baseline Only (No API Key)
```powershell
python scripts/run_experiment_baseline_only.py
```
- ✅ Works immediately
- ✅ Shows baseline performance
- ❌ Doesn't test your system

### Option 2: Use Existing Gemini Results
You already have 98% accuracy results!
- **File:** `reports/accuracy_results_all_50_20251118_152137.json`
- **Accuracy:** 98.0% (49/50)
- **Can use:** ✅ For comparison table

### Option 3: Get Gemini API Key and Run Full
1. **Get key:** https://aistudio.google.com/apikey
2. **Set key:**
   ```powershell
   $env:GEMINI_API_KEY = "your-key-here"
   ```
3. **Run:**
   ```powershell
   python scripts/run_full_experiment.py
   ```

## Recommended Approach

Since you already have 98% accuracy results, you can:

1. **Run baseline now** (no API key):
   ```powershell
   python scripts/run_experiment_baseline_only.py
   ```

2. **Use your existing Gemini results** for comparison:
   - Baseline: ~52% (from baseline run)
   - Your System: 98% (from existing results)

3. **Generate comparison table** manually or use existing IEEE report

## Quick Setup

### Get Gemini API Key (Free):
1. Go to: https://aistudio.google.com/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy the key

### Set in PowerShell:
```powershell
$env:GEMINI_API_KEY = "AIzaSy..."
```

### Verify:
```powershell
python -c "import os; print('Set' if os.getenv('GEMINI_API_KEY') else 'Not set')"
```

---

**Bottom Line:** 
- Baseline: ✅ No API key needed
- Your System: Use existing 98% results OR get Gemini key

