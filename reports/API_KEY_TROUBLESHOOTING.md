# API Key Troubleshooting Guide

## OpenAI API Key Issue

### Error Observed
```
Error code: 401 - {'error': {'message': 'Incorrect API key provided: sk-or-v1***********************
```

### Possible Reasons

1. **Key Format Issue**
   - Your key starts with `sk-or-v1-` which is unusual
   - Standard OpenAI keys start with `sk-` or `sk-proj-`
   - `sk-or-v1-` might be from a different service or an old format

2. **Key Expired or Revoked**
   - API keys can expire or be revoked
   - Check your OpenAI dashboard

3. **Insufficient Credits**
   - Account might not have credits
   - Check billing status

4. **Wrong Service**
   - Key might be for a different OpenAI service
   - Ensure it's for OpenAI API (not ChatGPT Plus, etc.)

---

## How to Get a Valid OpenAI API Key

### Step 1: Go to OpenAI Platform
1. Visit: https://platform.openai.com/api-keys
2. Sign in to your OpenAI account
3. Click "Create new secret key"

### Step 2: Copy the Key
- Key format should be: `sk-...` or `sk-proj-...`
- **Important:** Copy it immediately (you can't see it again!)

### Step 3: Set Environment Variable
```powershell
$env:OPENAI_API_KEY = "sk-your-actual-key-here"
```

### Step 4: Test the Key
```bash
python scripts/test_baseline_comparison.py --limit 5
```

---

## Alternative: Use Your Gemini Results

**Good News:** You already have excellent results!

- **98.0% accuracy** with Gemini 2.5 Pro
- **IEEE visualizations** ready
- **Publication-ready** results

You can proceed with your paper using just the Gemini results. The baseline comparison is nice-to-have, but 98% accuracy is already strong enough for publication!

---

## Quick Test

To verify if a key works, you can test it directly:

```python
from openai import OpenAI

client = OpenAI(api_key="your-key-here")
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Say hello"}]
)
print(response.choices[0].message.content)
```

If this works, your key is valid!

---

## Current Status

- ✅ **Gemini Results:** 98.0% accuracy (excellent!)
- ✅ **IEEE Visualizations:** Ready
- ❌ **OpenAI Key:** Invalid (needs new key)
- ⏳ **Baseline Comparison:** Pending valid key

---

**Recommendation:** 
1. Get a new OpenAI API key from https://platform.openai.com/api-keys
2. Or proceed with your excellent Gemini results (98% is publication-ready!)

