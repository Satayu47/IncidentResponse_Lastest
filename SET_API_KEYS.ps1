# Set API Keys for Improved Experiments
# Run this script before running experiments

# Gemini API Key (Free)
$env:GEMINI_API_KEY = "AIzaSyD2kilCSTMXuvcipwSCUwo_XleNYVUV_xs"

# OpenAI API Key (should already be set, but check)
if (-not $env:OPENAI_API_KEY) {
    Write-Host "[WARNING] OPENAI_API_KEY not set. Accuracy comparison will fail." -ForegroundColor Yellow
    Write-Host "Set it with: `$env:OPENAI_API_KEY = 'your_key'" -ForegroundColor Yellow
}

Write-Host "API Keys Configured:" -ForegroundColor Green
Write-Host "  Gemini: $($env:GEMINI_API_KEY.Substring(0, 20))..." -ForegroundColor Cyan
Write-Host "  OpenAI: $(if ($env:OPENAI_API_KEY) { 'Set' } else { 'Not set' })" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now run:" -ForegroundColor Green
Write-Host "  python scripts/run_improved_accuracy_comparison.py" -ForegroundColor Yellow

