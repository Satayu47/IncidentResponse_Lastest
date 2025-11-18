# OPA Server Setup Script for Windows
# This script sets up and starts the OPA server with policies

Write-Host "=== OPA Server Setup ===" -ForegroundColor Cyan

# Check if Docker is running
Write-Host "`n[1/4] Checking Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Stop existing OPA container if running
Write-Host "`n[2/4] Stopping existing OPA container (if any)..." -ForegroundColor Yellow
docker stop opa-server 2>$null
docker rm opa-server 2>$null

# Start OPA server
Write-Host "`n[3/4] Starting OPA server..." -ForegroundColor Yellow
$opaContainer = docker run -d `
    --name opa-server `
    -p 8181:8181 `
    openpolicyagent/opa run --server --log-level=info

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ OPA server started (container: $opaContainer)" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to start OPA server" -ForegroundColor Red
    exit 1
}

# Wait for server to be ready
Write-Host "`nWaiting for OPA server to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Load policies
Write-Host "`n[4/4] Loading policies..." -ForegroundColor Yellow

$policiesDir = Join-Path $PSScriptRoot ".." "phase2_engine" "policies"
if (-not (Test-Path $policiesDir)) {
    Write-Host "✗ Policies directory not found: $policiesDir" -ForegroundColor Red
    exit 1
}

# Load playbook policy
$playbookPolicy = Join-Path $policiesDir "playbook.rego"
if (Test-Path $playbookPolicy) {
    Write-Host "  Loading playbook.rego..." -ForegroundColor Gray
    $content = Get-Content $playbookPolicy -Raw
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
    $base64 = [Convert]::ToBase64String($bytes)
    
    $body = @{
        policy = $base64
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8181/v1/policies/playbook" `
            -Method Put `
            -Body $body `
            -ContentType "application/json"
        Write-Host "  ✓ playbook.rego loaded" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠ Could not load playbook.rego (server may need more time)" -ForegroundColor Yellow
    }
}

# Load incident policy
$incidentPolicy = Join-Path $policiesDir "incident.rego"
if (Test-Path $incidentPolicy) {
    Write-Host "  Loading incident.rego..." -ForegroundColor Gray
    $content = Get-Content $incidentPolicy -Raw
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
    $base64 = [Convert]::ToBase64String($bytes)
    
    $body = @{
        policy = $base64
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8181/v1/policies/incident" `
            -Method Put `
            -Body $body `
            -ContentType "application/json"
        Write-Host "  ✓ incident.rego loaded" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠ Could not load incident.rego (server may need more time)" -ForegroundColor Yellow
    }
}

# Test OPA server
Write-Host "`n[5/5] Testing OPA server..." -ForegroundColor Yellow
try {
    $testResponse = Invoke-RestMethod -Uri "http://localhost:8181/health" -Method Get
    Write-Host "✓ OPA server is healthy" -ForegroundColor Green
} catch {
    Write-Host "⚠ OPA server may not be fully ready yet" -ForegroundColor Yellow
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Cyan
Write-Host "OPA Server URL: http://localhost:8181" -ForegroundColor White
Write-Host "Playbook Policy: http://localhost:8181/v1/data/playbook/allow" -ForegroundColor White
Write-Host "Incident Policy: http://localhost:8181/v1/data/incident/result" -ForegroundColor White
Write-Host "`nTo stop OPA: docker stop opa-server" -ForegroundColor Gray
Write-Host "To view logs: docker logs opa-server" -ForegroundColor Gray

