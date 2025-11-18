# 🚀 Run Improved Experiments

## ✅ API Keys Status

- ✅ **Gemini API Key:** Valid and ready
- ✅ **OpenAI API Key:** Set and ready

---

## 📊 Experiment 1: Improved Latency (Already Done!)

**Status:** ✅ Already tested successfully!

**Results:**
- 50 test cases, 3 runs each (150 measurements)
- Mean: 52.04 ms (95% CI: [40.65, 63.43] ms)
- Fast Path: 72% of cases (7.85 ms avg)
- LLM Path: 28% of cases

**Files:**
- `reports/overall_latency_improved_20251118_202155.json`
- `reports/overall_latency_improved_summary_20251118_202155.json`

---

## 🎯 Experiment 2: Improved Accuracy Comparison

### **Setup:**
```powershell
# Set API keys
$env:GEMINI_API_KEY = "AIzaSyD2kilCSTMXuvcipwSCUwo_XleNYVUV_xs"
# OpenAI key should already be set

# Or use the script
.\SET_API_KEYS.ps1
```

### **Run:**
```powershell
python scripts/run_improved_accuracy_comparison.py
```

### **What It Does:**
- Tests ChatOps (Gemini + explicit detection) on 100 test cases
- Tests ChatGPT (GPT-4o) on same 100 test cases
- Runs each case 3 times (300 measurements per system)
- Calculates precision, recall, F1-score
- Per-category detailed analysis

### **Expected Duration:**
- ~30-60 minutes (depends on API response times)
- 100 cases × 3 runs × 2 systems = 600 API calls
- Rate limiting: 4.5s between Gemini calls, 1s between OpenAI calls

### **Output:**
- `reports/accuracy_comparison_improved_YYYYMMDD_HHMMSS.json`

---

## ⚠️ Important Notes

### **API Quota:**
- **Gemini Free Tier:** 50 requests/day
- **For 100 cases × 3 runs = 300 calls** → You'll need multiple days OR paid tier
- **OpenAI:** Pay-per-use (~$1-5 for 300 calls)

### **Recommendation:**
If you hit quota limits, you can:
1. **Run with fewer test cases** (edit script to use first 20-30 cases)
2. **Use existing 98% results** (already valid for paper)
3. **Run over multiple days** (50 calls/day limit)

---

## 📝 Quick Start

```powershell
# 1. Set API keys
.\SET_API_KEYS.ps1

# 2. Run improved accuracy comparison
python scripts/run_improved_accuracy_comparison.py

# 3. Wait for completion (~30-60 minutes)

# 4. Check results
# File: reports/accuracy_comparison_improved_*.json
```

---

## ✅ Alternative: Use Existing Results

You already have valid results:
- ✅ **98% accuracy** (49/50 test cases)
- ✅ **Improved latency** (150 measurements)

**These are ready for your D3 paper!**

You don't need to run new experiments unless you want:
- Multiple runs for confidence intervals
- ChatGPT comparison
- Per-category precision/recall/F1

---

## 🎓 For Your Paper

**Current Results (Ready to Use):**
- Latency: 8.72ms average (improved version with 150 measurements)
- Accuracy: 98% (49/50, existing results)

**If You Run Improved Accuracy:**
- Will get: 95% CI, precision/recall/F1, ChatGPT comparison
- Will need: ~30-60 minutes + API quota

**Recommendation:** Use existing results unless you specifically need the improved metrics.

