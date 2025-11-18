# Claude Baseline Setup Guide

## Quick Setup

### 1. Get Claude API Key (Free Tier Available!)

1. Go to: https://console.anthropic.com/
2. Sign up (free $5 credit to start)
3. Go to API Keys: https://console.anthropic.com/settings/keys
4. Click "Create Key"
5. Copy your key (starts with `sk-ant-`)

### 2. Set Environment Variable

**Windows PowerShell:**
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

**Or create `.env` file:**
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Install Package

```bash
pip install anthropic
```

### 4. Run Baseline Comparison

```bash
# Compare Gemini vs Claude (default)
python scripts/test_baseline_comparison.py --limit 50

# Or specify Claude model
python scripts/test_baseline_comparison.py --limit 50 --claude-model "claude-3-5-sonnet-20241022"
```

## Available Claude Models

- `claude-3-5-sonnet-20241022` (recommended - best performance)
- `claude-3-opus-20240229` (most capable, slower)
- `claude-3-sonnet-20240229` (balanced)
- `claude-3-haiku-20240307` (fastest, cheapest)

## Free Tier

- **$5 free credit** when you sign up
- Enough for ~50-100 test cases
- No credit card required initially

## Usage in Code

```python
from src.llm_adapter import LLMAdapter

# Use Claude
adapter = LLMAdapter(model="claude-3-5-sonnet-20241022")
```

## Comparison Test

The baseline comparison script now supports Claude by default:

```bash
python scripts/test_baseline_comparison.py --limit 50 --baseline claude
```

This will:
1. Test Gemini 2.5 Pro on 50 cases
2. Test Claude on the same 50 cases
3. Generate comparison results
4. Create IEEE comparison chart

---

**Ready to use!** Just get your Claude API key and run the comparison test! 🚀

