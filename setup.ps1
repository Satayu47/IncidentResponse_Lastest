# Quick Setup Script for Incident Response Platform
# Run this to set up your environment quickly

Write-Host "🛡️ Incident Response Platform - Quick Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "1️⃣ Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   ❌ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Install dependencies
Write-Host "2️⃣ Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "   ❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Set up .env file
Write-Host "3️⃣ Setting up environment file..." -ForegroundColor Yellow
if (Test-Path .env) {
    Write-Host "   ⚠️  .env file already exists (skipping)" -ForegroundColor Yellow
} else {
    Copy-Item .env.example .env
    Write-Host "   ✅ Created .env file from template" -ForegroundColor Green
    Write-Host "   ⚠️  Don't forget to add your OPENAI_API_KEY in .env!" -ForegroundColor Yellow
}

Write-Host ""

# Check file structure
Write-Host "4️⃣ Verifying file structure..." -ForegroundColor Yellow

$requiredFiles = @(
    "app.py",
    "requirements.txt",
    "src\__init__.py",
    "phase2_engine\__init__.py",
    "phase2_engine\core\runner_bridge.py",
    "phase2_engine\playbooks\A03_injection.yaml"
)

$allPresent = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Missing: $file" -ForegroundColor Red
        $allPresent = $false
    }
}

Write-Host ""

# Count playbooks
$playbookCount = (Get-ChildItem "phase2_engine\playbooks\*.yaml").Count
Write-Host "   📚 Found $playbookCount playbook(s)" -ForegroundColor Cyan

Write-Host ""

# Final status
if ($allPresent) {
    Write-Host "✅ Setup Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Edit .env and add your OPENAI_API_KEY" -ForegroundColor White
    Write-Host "   2. Run: streamlit run app.py" -ForegroundColor White
    Write-Host "   3. Open: http://localhost:8501" -ForegroundColor White
    Write-Host ""
    Write-Host "📖 Documentation:" -ForegroundColor Cyan
    Write-Host "   - README.md (main docs)" -ForegroundColor White
    Write-Host "   - QUICKSTART.md (quick start)" -ForegroundColor White
    Write-Host "   - ARCHITECTURE.md (system design)" -ForegroundColor White
    Write-Host ""
    
    # Offer to start the app
    Write-Host "Would you like to start the application now? (y/n): " -NoNewline -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host ""
        Write-Host "🚀 Starting Incident Response Platform..." -ForegroundColor Green
        Write-Host ""
        streamlit run app.py
    } else {
        Write-Host ""
        Write-Host "👍 Run 'streamlit run app.py' when you're ready!" -ForegroundColor Cyan
    }
} else {
    Write-Host "❌ Setup incomplete - some files are missing" -ForegroundColor Red
    Write-Host "   Please check the file structure and try again." -ForegroundColor Red
    exit 1
}
