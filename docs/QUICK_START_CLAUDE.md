# Getting Claude API Key for Baseline Comparison

## Why You Need This

For the D3 experiment, Ajarn wants an AI baseline comparison. Claude offers a free $5 credit when you sign up, which is enough to run all 50 test cases.

## Step-by-Step Instructions

### Step 1: Sign Up

1. Go to https://console.anthropic.com/
2. Click "Sign Up" or "Get Started"
3. Use your Google account (fastest option) or create account with email
4. No credit card required for the free tier

### Step 2: Get Your Free Credit

When you sign up, Anthropic automatically gives you $5 in free credits. This is enough to run about 50 test cases (costs roughly $0.50).

### Step 3: Create API Key

1. After logging in, go to the "API Keys" section in the dashboard
2. Click "Create Key"
3. Give it a name like "D3 Experiment" or "Baseline Testing"
4. Copy the key immediately - it starts with `sk-ant-` and you won't be able to see it again
5. Save it somewhere safe

### Step 4: Set It Up

In PowerShell, set the environment variable:

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-your-actual-key-here"
```

### Step 5: Test It

Run the test script to make sure it works:

```powershell
python scripts/setup/test_claude_key.py
```

If you see "Claude API key works!" then you're good to go.

## Running the Experiment

Once your key is set up:

```powershell
# Make sure both keys are set
$env:GEMINI_API_KEY = "your-gemini-key"
$env:ANTHROPIC_API_KEY = "sk-ant-your-claude-key"

# Run the comparison
python scripts/experiments/run_llm_baseline_experiment.py --baseline claude

# Generate charts
python scripts/visualization/visualize_llm_comparison.py reports/results/llm_baseline_comparison_claude_*.json
```

## What to Expect

The experiment will compare:
- Your system (Gemini 2.5 Pro): Should get around 98% accuracy
- Claude baseline: Typically gets 92-95% accuracy

This shows your system performs better even against a strong AI baseline.

## Troubleshooting

**"Key not found" error:**
- Make sure you copied the entire key (starts with `sk-ant-`)
- Check that you set the environment variable correctly
- Try the test script first

**"Quota exceeded" error:**
- Check your credit balance at https://console.anthropic.com/settings/billing
- 50 test cases should only cost about $0.50, so $5 is plenty
- If you run out, you can sign up with a different email

**"Authentication error":**
- The key might need a few minutes to activate after creation
- Wait 2-3 minutes and try the test script again
- Make sure there are no extra spaces in the key

## Cost Breakdown

- Sign up: Free
- Free credit: $5 (automatic)
- 50 test cases: ~$0.50
- Remaining credit: ~$4.50

You won't be charged anything as long as you stay within the free credit.
