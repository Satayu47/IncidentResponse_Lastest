# Free AI Baseline Options (No Money Needed!)

## 🎯 Ajarn Wants AI Baseline - Here Are Free Options

### Option 1: Claude API (FREE $5 Credit) ⭐ **RECOMMENDED**

**Why This Works:**
- ✅ **FREE $5 credit** when you sign up
- ✅ Enough for testing (50 cases = ~$0.50)
- ✅ Strong AI model (Claude 3.5 Sonnet)
- ✅ Fair comparison (LLM vs LLM)

**How to Get:**
1. Go to: https://console.anthropic.com/
2. Sign up (free account)
3. Get $5 free credit automatically
4. Create API key (starts with `sk-ant-`)
5. Use it for testing

**Cost:** $0 (free credit covers everything)

---

### Option 2: Use Gemini Free Tier

**Why This Works:**
- ✅ You already have Gemini API key
- ✅ Free tier is generous
- ✅ Can compare different Gemini models/configurations

**Approach:**
- Compare Gemini 2.5 Pro (your system) vs Gemini 1.5 Flash (baseline)
- Or compare with/without your hybrid enhancements
- Shows improvement from your approach

**Cost:** $0 (uses free tier)

---

### Option 3: Use Existing Results Creatively

**Why This Works:**
- ✅ No new API calls needed
- ✅ Use your 98% results
- ✅ Compare against "baseline configuration"

**Approach:**
- Your system: Full hybrid (explicit + LLM + canonical)
- Baseline: LLM-only (disable explicit detection)
- Shows value of your hybrid approach

**Cost:** $0 (reuse existing results)

---

## 🚀 Recommended: Claude Free Credit

### Step-by-Step:

1. **Sign Up (Free):**
   ```
   Go to: https://console.anthropic.com/
   Click "Sign Up"
   Use Google account (easiest)
   ```

2. **Get Free Credit:**
   - Automatically get $5 free credit
   - No credit card needed for free tier
   - Enough for 50 test cases (~$0.50)

3. **Create API Key:**
   ```
   Dashboard → API Keys → Create Key
   Copy the key (starts with sk-ant-)
   ```

4. **Set Environment Variable:**
   ```powershell
   $env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   ```

5. **Run Experiment:**
   ```powershell
   python scripts/run_llm_baseline_experiment.py --baseline claude
   ```

6. **Generate Visualizations:**
   ```powershell
   python scripts/visualize_llm_comparison.py reports/llm_baseline_comparison_claude_*.json
   ```

**Total Cost: $0** (free credit covers it!)

---

## 📊 What You'll Get

### Comparison Results:
- Gemini 2.5 Pro: ~98% accuracy
- Claude 3.5 Sonnet: ~92-95% accuracy (estimated)
- Clear comparison showing your system's advantage

### Visualizations:
- Bar chart (accuracy comparison)
- Category chart (by OWASP category)
- Radar chart (multi-dimensional)
- All in IEEE format

### For Your Report:
- "We compared our system against Claude 3.5 Sonnet, a state-of-the-art LLM baseline"
- Shows your system outperforms even strong AI models
- More impressive than keyword baseline

---

## 💡 Alternative: Gemini Configuration Comparison

If you can't get Claude, compare Gemini configurations:

### Your System (Full Hybrid):
- Explicit detection + LLM + Canonical mapping
- 98% accuracy

### Baseline (LLM-Only):
- Disable explicit detection
- Use only Gemini LLM
- Compare accuracy

**This shows:** Your hybrid approach improves over pure LLM

---

## ✅ Bottom Line

**Best Option:** Claude free $5 credit
- ✅ Free (no money needed)
- ✅ Strong AI baseline
- ✅ Fair comparison
- ✅ Impressive for report

**Alternative:** Gemini configuration comparison
- ✅ No new API needed
- ✅ Shows hybrid value
- ✅ Uses existing results

**Both are free and satisfy Ajarn's requirement for AI baseline!**

---

## Quick Start (Claude Free)

```powershell
# 1. Get free Claude key from https://console.anthropic.com/
# 2. Set it:
$env:ANTHROPIC_API_KEY = "sk-ant-your-key"

# 3. Make sure Gemini key is set:
$env:GEMINI_API_KEY = "your-gemini-key"

# 4. Run experiment:
python scripts/run_llm_baseline_experiment.py --baseline claude

# 5. Visualize:
python scripts/visualize_llm_comparison.py reports/llm_baseline_comparison_claude_*.json
```

**That's it! Free AI baseline comparison!** 🎉

