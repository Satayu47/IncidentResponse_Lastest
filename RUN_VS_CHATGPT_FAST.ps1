# Fast VS Comparison: ChatOps vs ChatGPT
# This script runs a faster version with fewer test cases

Write-Host "Setting up for FAST VS comparison..." -ForegroundColor Cyan

# ChatOps - Gemini API Key
$env:GEMINI_API_KEY = "AIzaSyD2kilCSTMXuvcipwSCUwo_XleNYVUV_xs"
Write-Host "✅ Gemini API Key set" -ForegroundColor Green

# ChatGPT - OpenAI API Key (REQUIRED)
# You need a valid OpenAI key that starts with "sk-" (not "sk-or-v1-")
Write-Host "`n⚠️  IMPORTANT: You need a valid OpenAI API key!" -ForegroundColor Yellow
Write-Host "   Get one from: https://platform.openai.com/account/api-keys" -ForegroundColor Cyan
Write-Host "   Format: sk-..." -ForegroundColor White

# Set your OpenAI key here:
# $env:OPENAI_API_KEY = "sk-your-openai-key-here"

# Force ChatGPT (don't use Claude even if Anthropic key detected)
$env:FORCE_CHATGPT = "true"

# Fast mode (fewer test cases, faster)
$env:FAST_MODE = "true"

Write-Host "`nConfiguration:" -ForegroundColor Cyan
Write-Host "  Model: ChatGPT (GPT-4o) - FORCED" -ForegroundColor White
Write-Host "  Fast Mode: ENABLED (30 test cases, 1 run each)" -ForegroundColor White
Write-Host "  Expected time: ~5-10 minutes" -ForegroundColor White

if (-not $env:OPENAI_API_KEY) {
    Write-Host "`n❌ ERROR: OPENAI_API_KEY not set!" -ForegroundColor Red
    Write-Host "   Set it with: `$env:OPENAI_API_KEY = 'sk-your-key'" -ForegroundColor Yellow
    Write-Host "   Then run: python scripts/run_improved_accuracy_comparison.py" -ForegroundColor Yellow
} else {
    Write-Host "`n✅ Ready to run!" -ForegroundColor Green
    Write-Host "   Run: python scripts/run_improved_accuracy_comparison.py" -ForegroundColor Yellow
}

