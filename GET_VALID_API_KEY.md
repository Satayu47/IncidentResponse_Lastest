# 🔑 Get Valid API Key for Real Data

## ❌ Current Status

The key you provided (`sk-or-v1-2e18f273...`) is **INVALID**:
- Format: Anthropic (Claude) ✅
- Status: 401 Authentication Error ❌
- Reason: Expired, incorrect, or missing permissions

---

## ✅ Solution: Get a New API Key

You have **two options**:

### Option 1: Get Anthropic (Claude) Key

1. **Go to Anthropic Console:**
   - https://console.anthropic.com/settings/keys
   - Sign in (or create account)

2. **Create API Key:**
   - Click "Create Key"
   - Copy the key (starts with `sk-or-v1-` or `sk-ant-`)
   - ⚠️ Save it immediately!

3. **Set and Test:**
   ```powershell
   $env:ANTHROPIC_API_KEY = "sk-or-v1-your-new-key"
   python scripts/measure_claude_latency.py
   ```

---

### Option 2: Get OpenAI (ChatGPT) Key

1. **Go to OpenAI Platform:**
   - https://platform.openai.com/account/api-keys
   - Sign in (or create account)

2. **Create API Key:**
   - Click "Create new secret key"
   - Copy the key (starts with `sk-` or `sk-proj-`)
   - ⚠️ Save it immediately!

3. **Set and Test:**
   ```powershell
   $env:OPENAI_API_KEY = "sk-your-new-key"
   python scripts/measure_chatgpt_latency.py
   ```

---

## 🚀 Once You Have a Valid Key

### For Claude:
```powershell
# Set key
$env:ANTHROPIC_API_KEY = "sk-or-v1-your-key"

# Measure latency
python scripts/measure_claude_latency.py

# Measure accuracy
python scripts/run_improved_accuracy_comparison.py

# Re-generate graphs (auto-detects Claude)
python scripts/visualization/create_latency_comparison.py
python scripts/visualization/create_accuracy_graphs.py
```

### For ChatGPT:
```powershell
# Set key
$env:OPENAI_API_KEY = "sk-your-key"

# Measure latency
python scripts/measure_chatgpt_latency.py

# Measure accuracy
python scripts/run_improved_accuracy_comparison.py

# Re-generate graphs (auto-detects ChatGPT)
python scripts/visualization/create_latency_comparison.py
python scripts/visualization/create_accuracy_graphs.py
```

---

## 📊 What You'll Get

Once you have a valid key and run the measurements:

- ✅ **Real latency data** (not estimated)
- ✅ **Real accuracy data** (not estimated)
- ✅ **IEEE-compliant graphs** with actual measurements
- ✅ **ChatOps vs Baseline** comparison

---

## ⚠️ Important Notes

- **Anthropic keys** start with `sk-or-v1-` or `sk-ant-`
- **OpenAI keys** start with `sk-` or `sk-proj-` (NOT `sk-or-v1-`)
- You may need to add a payment method (but first $5 is usually free)
- Keys are sensitive - don't share them publicly!

---

**Get a valid key and we can measure real data!** 🎯

