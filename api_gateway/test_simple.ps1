# Educational ERP Services Test Script
# Tests OCR, Odoo, and Admission Portal without Docker

$ErrorActionPreference = "Continue"

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "Educational ERP Services Test" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: OCR Service
Write-Host "[1/4] OCR Microservice (port 5000)..." -ForegroundColor Yellow
try {
    $ocr = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get -TimeoutSec 5
    Write-Host "  Status: RUNNING" -ForegroundColor Green
    Write-Host "  Health: $($ocr.status)" -ForegroundColor Gray
} catch {
    Write-Host "  Status: NOT RUNNING" -ForegroundColor Red
}
Write-Host ""

# Test 2: Odoo Service
Write-Host "[2/4] Odoo ERP Service..." -ForegroundColor Yellow
$odooFound = $false
$odooPort = 0

# Check port 8069
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8081" -Method Get -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    Write-Host "  Status: RUNNING on port 8081" -ForegroundColor Green
    $odooPort = 8081
    $odooFound = $true
} catch {
    # Try port 8081
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8081" -Method Get -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        Write-Host "  Status: RUNNING on port 8081" -ForegroundColor Green
        $odooPort = 8081
        $odooFound = $true
    } catch {
        # Check if ports are listening even if web request failed
        $listening = netstat -ano | Select-String ":8069|:8081" | Select-String "LISTENING"
        if ($listening) {
            # Port is open but web server might be slow/loading
            if ($listening -match ":8069") {
                $odooPort = 8069
            } elseif ($listening -match ":8081") {
                $odooPort = 8081
            }
            Write-Host "  Status: PORT $odooPort OPEN (web server may be loading)" -ForegroundColor Yellow
            $odooFound = $true
        } else {
            Write-Host "  Status: NOT RUNNING" -ForegroundColor Red
        }
    }
}
Write-Host ""

# Test 3: Admission Portal
Write-Host "[3/4] Admission Portal..." -ForegroundColor Yellow
if ($odooFound) {
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:$odooPort/admission/apply" -Method Get -TimeoutSec 5 -UseBasicParsing
        Write-Host "  Status: ACCESSIBLE" -ForegroundColor Green
        Write-Host "  URL: http://localhost:$odooPort/admission/apply" -ForegroundColor Gray
    } catch {
        Write-Host "  Status: NOT ACCESSIBLE" -ForegroundColor Yellow
        Write-Host "  Try: http://localhost:$odooPort/web?db=edu_demo_new" -ForegroundColor Gray
    }
} else {
    Write-Host "  Status: SKIPPED (Odoo not running)" -ForegroundColor Gray
}
Write-Host ""

# Test 4: Docker Status
Write-Host "[4/4] Docker API Gateway..." -ForegroundColor Yellow
try {
    $null = docker ps 2>$null
    $containers = docker ps --format "{{.Names}}" 2>$null | Select-String -Pattern "(nginx|fastapi)"
    if ($containers) {
        Write-Host "  Status: RUNNING" -ForegroundColor Green
    } else {
        Write-Host "  Status: NOT RUNNING" -ForegroundColor Gray
        Write-Host "  Start: docker-compose up -d" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Status: Docker not available" -ForegroundColor Gray
}
Write-Host ""

# Summary
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Summary & Quick Links" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services:" -ForegroundColor White
Write-Host "  OCR:    http://localhost:5000/health" -ForegroundColor Gray
if ($odooFound) {
    Write-Host "  Odoo:   http://localhost:$odooPort/web?db=edu_demo_new" -ForegroundColor Gray
    Write-Host "  Portal: http://localhost:$odooPort/admission/apply" -ForegroundColor Gray
}
Write-Host ""
Write-Host "Commands:" -ForegroundColor White
Write-Host "  Start OCR:   cd C:\Odoo; make ocr-run" -ForegroundColor Gray
Write-Host "  Start Odoo:  cd C:\Odoo; make run" -ForegroundColor Gray
Write-Host "  Start Gateway: docker-compose up -d" -ForegroundColor Gray
Write-Host ""
