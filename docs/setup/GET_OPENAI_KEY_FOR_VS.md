# 🚀 Get OpenAI Key for VS Comparison (TONIGHT!)

## ⚡ Quick Steps

1. **Go to OpenAI Platform:**
   - https://platform.openai.com/account/api-keys
   - Sign in (or create account)

2. **Create API Key:**
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)
   - ⚠️ **Save it immediately** - you won't see it again!

3. **Set the Key:**
   ```powershell
   $env:OPENAI_API_KEY = "sk-your-key-here"
   ```

4. **Run Fast Comparison:**
   ```powershell
   .\RUN_VS_CHATGPT_FAST.ps1
   python scripts/run_improved_accuracy_comparison.py
   ```

## ⚡ Fast Mode Settings

- **30 test cases** (instead of 72)
- **1 run per case** (instead of 3)
- **Reduced rate limits** (faster API calls)
- **Expected time: 5-10 minutes**

## 📊 What You'll Get

- ChatOps accuracy (Gemini + explicit detection)
- ChatGPT accuracy (GPT-4o)
- Precision, Recall, F1-score
- Comparison summary
- Results saved to JSON file

## ⚠️ Important

- OpenAI keys start with `sk-` (NOT `sk-or-v1-` or `sk-ant-`)
- You may need to add payment method (but first $5 is free)
- Key format: `sk-proj-...` or `sk-...`

## 🎯 Alternative: Use Existing Results

If you can't get OpenAI key tonight, you already have:
- ✅ ChatOps: 95.37% accuracy (206/216)
- ✅ Latency: 52ms mean, 7.8ms median

These are ready for your paper!

