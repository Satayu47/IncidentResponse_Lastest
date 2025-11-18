# 🔑 API Keys Required for Improved Experiments

## 📊 Experiment 1: Improved Latency Measurement

### **API Key Needed:** ⚠️ **Optional (Gemini)**

**Why:**
- Most test cases use **fast path** (explicit detection) - **NO API call needed**
- Some cases may need LLM fallback - **API call needed**

**Current Status:**
- ✅ **Can run without API key** (will use fast path only)
- ⚠️ **Better with API key** (tests both fast path and LLM path)

**To Run:**
```bash
# Without API key (fast path only)
python scripts/measure_overall_latency_improved.py

# With API key (full test)
$env:GEMINI_API_KEY = "your_gemini_key"
python scripts/measure_overall_latency_improved.py
```

**Result from test run:**
- Fast Path: 72% of cases (no API needed)
- LLM Path: 28% of cases (API needed)

---

## 🎯 Experiment 2: Improved Accuracy Comparison

### **API Keys Needed:** ✅ **REQUIRED (Both)**

**Required:**
1. **GEMINI_API_KEY** - For ChatOps system (Gemini 2.5 Pro)
2. **OPENAI_API_KEY** - For ChatGPT baseline (GPT-4o)

**Why:**
- ChatOps uses Gemini API for classification
- ChatGPT baseline uses OpenAI API for comparison
- Both are required for fair comparison

**To Run:**
```powershell
# Set both API keys
$env:GEMINI_API_KEY = "your_gemini_key"
$env:OPENAI_API_KEY = "your_openai_key"

# Run comparison
python scripts/run_improved_accuracy_comparison.py
```

---

## 🔑 How to Get API Keys

### **1. Gemini API Key (Free)** ⭐ EASIEST

**Get it here:** https://aistudio.google.com/apikey

**Steps:**
1. Go to https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)

**Free Tier Limits:**
- 50 requests/day
- 15 requests/minute
- 1 million tokens/minute

**Cost:** ✅ **FREE**

---

### **2. OpenAI API Key (Paid)** ⚠️ REQUIRES CREDIT

**Get it here:** https://platform.openai.com/api-keys

**Steps:**
1. Go to https://platform.openai.com/api-keys
2. Sign in or create account
3. Add payment method (required)
4. Click "Create new secret key"
5. Copy the key (starts with `sk-...`)

**Pricing:**
- GPT-4o: ~$2.50 per 1M input tokens, ~$10 per 1M output tokens
- For 100 test cases × 3 runs = 300 API calls
- Estimated cost: **$1-5** (depends on prompt length)

**Cost:** ⚠️ **PAID** (but cheap for testing)

---

## 💡 Alternative Options

### **Option 1: Run Latency Only** ✅ NO API KEY NEEDED

The latency experiment works mostly without API keys (72% fast path):
```bash
python scripts/measure_overall_latency_improved.py
```

**Result:** You get latency measurements for fast path cases.

---

### **Option 2: Use Existing Accuracy Results** ✅ NO NEW API CALLS

You already have accuracy results from previous runs:
- **File:** `reports/accuracy_results_all_50_20251118_152137.json`
- **Accuracy:** 98% (49/50)

**Can use these for:**
- Comparison with baseline
- Paper results
- Graphs

**Note:** These are from single run, not the improved version with multiple runs.

---

### **Option 3: Run ChatOps Only (No ChatGPT)** ✅ GEMINI KEY ONLY

If you only have Gemini key, you can:
1. Run ChatOps accuracy evaluation
2. Compare against your existing baseline results
3. Skip ChatGPT comparison

**To run:**
```powershell
$env:GEMINI_API_KEY = "your_gemini_key"
python scripts/eval_accuracy.py
```

---

## 📋 Summary Table

| Experiment | API Key Needed | Can Run Without? | Cost |
|------------|---------------|------------------|------|
| **Latency (Improved)** | Gemini (optional) | ✅ Yes (72% fast path) | Free |
| **Accuracy (Improved)** | Gemini + OpenAI | ❌ No (both required) | Gemini: Free<br>OpenAI: ~$1-5 |

---

## 🚀 Recommended Approach

### **For Your D3 Paper:**

1. **Latency Experiment:** ✅ **Run now** (works without API key)
   ```bash
   python scripts/measure_overall_latency_improved.py
   ```

2. **Accuracy Experiment:** 
   - **Option A:** Use existing 98% results (already have)
   - **Option B:** Get both API keys and run improved version
   - **Option C:** Get Gemini key only, run ChatOps, compare with baseline

### **Minimum Required:**
- ✅ **Latency:** No API key needed (already tested!)
- ⚠️ **Accuracy:** 
  - Use existing results (no new API calls)
  - OR get Gemini key (free) for ChatOps only
  - OR get both keys for full comparison

---

## ✅ Quick Check

**Check if you have API keys set:**
```powershell
# Check Gemini
python -c "import os; print('Gemini: ' + ('Set' if os.getenv('GEMINI_API_KEY') else 'Not set'))"

# Check OpenAI
python -c "import os; print('OpenAI: ' + ('Set' if os.getenv('OPENAI_API_KEY') else 'Not set'))"
```

---

## 🎯 Bottom Line

**For Improved Experiments:**
- **Latency:** ✅ Can run now (no API key needed for most cases)
- **Accuracy:** ⚠️ Needs both API keys OR use existing results

**Easiest Path:**
1. Run latency experiment now (no API key)
2. Use existing 98% accuracy results for paper
3. Get Gemini key if you want to re-run ChatOps
4. Get OpenAI key only if you want ChatGPT comparison

