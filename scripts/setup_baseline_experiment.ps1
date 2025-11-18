# Baseline Experiment Setup Script
# =================================
# This script helps you set up and run the baseline comparison experiment

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Baseline Comparison Experiment Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check current API keys
Write-Host "Checking API keys..." -ForegroundColor Yellow
$geminiKey = $env:GEMINI_API_KEY
$claudeKey = $env:ANTHROPIC_API_KEY
$openaiKey = $env:OPENAI_API_KEY

Write-Host "`nCurrent Status:" -ForegroundColor Green
Write-Host "  Gemini API Key: $(if ($geminiKey -and $geminiKey.Length -gt 10) { 'Set ✓' } else { 'Not set ✗' })"
Write-Host "  Claude API Key: $(if ($claudeKey -and $claudeKey.Length -gt 10) { 'Set ✓' } else { 'Not set ✗' })"
Write-Host "  OpenAI API Key: $(if ($openaiKey -and $openaiKey.Length -gt 10) { 'Set ✓' } else { 'Not set ✗' })"

# Guide for getting keys
if (-not $claudeKey -or $claudeKey.Length -le 10) {
    Write-Host "`n📝 To get Claude API Key (Recommended - Free $5 credit):" -ForegroundColor Yellow
    Write-Host "   1. Go to: https://console.anthropic.com/" -ForegroundColor White
    Write-Host "   2. Sign up (free account)" -ForegroundColor White
    Write-Host "   3. Go to API Keys section" -ForegroundColor White
    Write-Host "   4. Create new key (starts with 'sk-ant-')" -ForegroundColor White
    Write-Host "   5. Run: `$env:ANTHROPIC_API_KEY = 'sk-ant-your-key-here'" -ForegroundColor Cyan
}

if (-not $openaiKey -or $openaiKey.Length -le 10) {
    Write-Host "`n📝 To get OpenAI API Key:" -ForegroundColor Yellow
    Write-Host "   1. Go to: https://platform.openai.com/api-keys" -ForegroundColor White
    Write-Host "   2. Sign up and add billing" -ForegroundColor White
    Write-Host "   3. Create new key (starts with 'sk-' or 'sk-proj-')" -ForegroundColor White
    Write-Host "   4. Run: `$env:OPENAI_API_KEY = 'sk-your-key-here'" -ForegroundColor Cyan
}

# Test keys if available
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Testing API Keys" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

if ($geminiKey -and $geminiKey.Length -gt 10) {
    Write-Host "Testing Gemini API key..." -ForegroundColor Yellow
    python scripts/test_api_key.py --provider gemini --key $geminiKey
}

if ($claudeKey -and $claudeKey.Length -gt 10) {
    Write-Host "`nTesting Claude API key..." -ForegroundColor Yellow
    python scripts/test_api_key.py --provider anthropic --key $claudeKey
}

if ($openaiKey -and $openaiKey.Length -gt 10) {
    Write-Host "`nTesting OpenAI API key..." -ForegroundColor Yellow
    python scripts/test_api_key.py --provider openai --key $openaiKey
}

# Ready to run?
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Ready to Run Experiment?" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$canRun = $false
$baselineModels = @()

if ($geminiKey -and $geminiKey.Length -gt 10) {
    Write-Host "✓ Gemini key ready (Primary model)" -ForegroundColor Green
    $canRun = $true
    
    if ($claudeKey -and $claudeKey.Length -gt 10) {
        Write-Host "✓ Claude key ready (Baseline)" -ForegroundColor Green
        $baselineModels += "claude"
    }
    
    if ($openaiKey -and $openaiKey.Length -gt 10) {
        Write-Host "✓ OpenAI key ready (Baseline)" -ForegroundColor Green
        $baselineModels += "openai"
    }
}

if ($canRun) {
    if ($baselineModels.Count -gt 0) {
        Write-Host "`n🚀 Ready to run experiment!" -ForegroundColor Green
        Write-Host "`nRun this command:" -ForegroundColor Yellow
        $baselineStr = $baselineModels -join " "
        Write-Host "  python scripts/run_baseline_experiment.py --limit 50 --baseline $baselineStr" -ForegroundColor Cyan
    } else {
        Write-Host "`n⚠️  Gemini key ready, but no baseline keys found." -ForegroundColor Yellow
        Write-Host "   You can still generate IEEE report with Gemini results only." -ForegroundColor White
        Write-Host "`n   Run: python scripts/generate_ieee_experiment_report.py reports/baseline_experiment_from_gemini_*.json" -ForegroundColor Cyan
    }
} else {
    Write-Host "`n⚠️  Need at least Gemini API key to run experiment." -ForegroundColor Yellow
    Write-Host "   Get your key from: https://aistudio.google.com/apikey" -ForegroundColor White
}

Write-Host "`n"

