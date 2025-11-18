# Set API Keys for VS Comparison Test
# This will set up both ChatOps (Gemini) and Baseline (OpenAI/Claude)

# ChatOps - Gemini API Key (Required)
$env:GEMINI_API_KEY = "AIzaSyD2kilCSTMXuvcipwSCUwo_XleNYVUV_xs"
Write-Host "✅ Gemini API Key set (for ChatOps)" -ForegroundColor Green

# Baseline - Choose ONE:
# Option 1: OpenAI (ChatGPT)
# $env:OPENAI_API_KEY = "sk-your-openai-key-here"

# Option 2: Anthropic (Claude) - Try the new key
$env:OPENAI_API_KEY = "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"
Write-Host "✅ Anthropic API Key set (for Claude baseline)" -ForegroundColor Green
Write-Host "   Note: Script will auto-detect and use Claude 3.5 Sonnet" -ForegroundColor Yellow

Write-Host "`nReady to run VS comparison!" -ForegroundColor Cyan
Write-Host "Run: python scripts/run_improved_accuracy_comparison.py" -ForegroundColor Yellow

