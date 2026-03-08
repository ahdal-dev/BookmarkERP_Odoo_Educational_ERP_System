# ============================================================================
# Direct Services Testing Script (Without Docker API Gateway)
# Tests OCR, Odoo, and Admission Portal
# ============================================================================

$ErrorActionPreference = "Continue"

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "Educational ERP Services Test" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# Test 1: OCR Microservice
# ============================================================================
Write-Host "[1/5] Testing OCR Microservice (port 5000)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get -TimeoutSec 5
    Write-Host "  ✓ OCR Service: RUNNING" -ForegroundColor Green
    Write-Host "    Status: $($response.status)" -ForegroundColor Gray
    Write-Host "    Service: $($response.service)" -ForegroundColor Gray
    $ocrRunning = $true
} catch {
    Write-Host "  ✗ OCR Service: NOT RUNNING" -ForegroundColor Red
    Write-Host "    Start with: make ocr-run" -ForegroundColor Yellow
    $ocrRunning = $false
}
Write-Host ""

# ============================================================================
# Test 2: Odoo Service (check both ports)
# ============================================================================
Write-Host "[2/5] Testing Odoo Service..." -ForegroundColor Yellow
$odooPort = $null
$odooPorts = @(8069, 8081)

foreach ($port in $odooPorts) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$port/web/database/selector" -Method Get -TimeoutSec 3 -UseBasicParsing
        Write-Host "  ✓ Odoo: RUNNING on port $port" -ForegroundColor Green
        $odooPort = $port
        break
    } catch {
        # Continue checking next port
    }
}

if (-not $odooPort) {
    Write-Host "  ✗ Odoo: NOT RUNNING (checked ports 8069, 8081)" -ForegroundColor Red
    Write-Host "    Start with: make run" -ForegroundColor Yellow
} else {
    Write-Host "    URL: http://localhost:$odooPort" -ForegroundColor Gray
}
Write-Host ""

# ============================================================================
# Test 3: Admission Portal Module
# ============================================================================
Write-Host "[3/5] Testing Admission Portal..." -ForegroundColor Yellow
if ($odooPort) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$odooPort/admission/apply" -Method Get -TimeoutSec 5 -UseBasicParsing
        Write-Host "  ✓ Admission Portal: ACCESSIBLE" -ForegroundColor Green
        Write-Host "    URL: http://localhost:$odooPort/admission/apply" -ForegroundColor Gray
        $portalRunning = $true
    } catch {
        Write-Host "  ✗ Admission Portal: NOT ACCESSIBLE" -ForegroundColor Red
        Write-Host "    The module may not be installed or database not selected" -ForegroundColor Yellow
        Write-Host "    Try: http://localhost:$odooPort/web?db=edu_demo_new" -ForegroundColor Yellow
        $portalRunning = $false
    }
} else {
    Write-Host "  ⊗ SKIPPED (Odoo not running)" -ForegroundColor Gray
    $portalRunning = $false
}
Write-Host ""

# ============================================================================
# Test 4: OCR Processing (if image available)
# ============================================================================
Write-Host "[4/5] Testing OCR Document Processing..." -ForegroundColor Yellow
if ($ocrRunning) {
    $testImages = @("test_image.jpg", "test_document.jpg", "..\test_image.jpg", "C:\Odoo\test_image.jpg")
    $imageFound = $null
    
    foreach ($img in $testImages) {
        if (Test-Path $img) {
            $imageFound = $img
            break
        }
    }
    
    if ($imageFound) {
        try {
            Add-Type -AssemblyName System.Net.Http
            $httpClient = New-Object System.Net.Http.HttpClient
            $httpClient.Timeout = [TimeSpan]::FromSeconds(30)
            $multipartContent = New-Object System.Net.Http.MultipartFormDataContent
            
            $filePath = Resolve-Path $imageFound
            $fileStream = [System.IO.File]::OpenRead($filePath)
            $fileContent = New-Object System.Net.Http.StreamContent($fileStream)
            $multipartContent.Add($fileContent, "file", (Split-Path $filePath -Leaf))
            
            $response = $httpClient.PostAsync("http://localhost:5000/ocr", $multipartContent).Result
            $result = $response.Content.ReadAsStringAsync().Result
            
            $fileStream.Close()
            $httpClient.Dispose()
            
            if ($response.IsSuccessStatusCode) {
                $data = $result | ConvertFrom-Json
                Write-Host "  ✓ OCR Processing: SUCCESS" -ForegroundColor Green
                $nid = if ($data.result.nid) { $data.result.nid } else { $data.result.back_nid }
                if ($nid) {
                    Write-Host "    Extracted NID: $nid" -ForegroundColor Gray
                }
                if ($data.result.name) {
                    Write-Host "    Extracted Name: $($data.result.name)" -ForegroundColor Gray
                }
            } else {
                Write-Host "  ✗ OCR Processing: FAILED" -ForegroundColor Red
            }
        } catch {
            Write-Host "  ✗ OCR Processing: ERROR - $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "  ⊗ SKIPPED (No test image found)" -ForegroundColor Gray
        Write-Host "    Place a test image in: $PWD\test_image.jpg" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⊗ SKIPPED (OCR service not running)" -ForegroundColor Gray
}
Write-Host ""

# ============================================================================
# Test 5: Docker API Gateway
# ============================================================================
Write-Host "[5/5] Testing Docker API Gateway..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    $dockerRunning = $true
    
    $containers = docker ps --format "{{.Names}}" | Where-Object { $_ -like "*nginx*" -or $_ -like "*fastapi*" }
    if ($containers) {
        Write-Host "  ✓ API Gateway: RUNNING" -ForegroundColor Green
        Write-Host "    Containers: $($containers -join ', ')" -ForegroundColor Gray
        
        try {
            $response = Invoke-RestMethod -Uri "http://localhost/health" -Method Get -TimeoutSec 3
            Write-Host "    Gateway Health: OK" -ForegroundColor Gray
        } catch {
            Write-Host "    Gateway Health: Not responding" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ⊗ API Gateway: NOT RUNNING" -ForegroundColor Gray
        Write-Host "    Start with: docker-compose up -d" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⊗ Docker: NOT AVAILABLE" -ForegroundColor Gray
    Write-Host "    Start Docker Desktop to use API Gateway" -ForegroundColor Yellow
}
Write-Host ""

# ============================================================================
# Summary
# ============================================================================
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Active Services:" -ForegroundColor White
if ($ocrRunning) {
    Write-Host "  ✓ OCR Microservice (localhost:5000)" -ForegroundColor Green
}
if ($odooPort) {
    Write-Host "  ✓ Odoo ERP (localhost:$odooPort)" -ForegroundColor Green
}
if ($portalRunning) {
    Write-Host "  ✓ Admission Portal" -ForegroundColor Green
}

Write-Host "`nQuick Access URLs:" -ForegroundColor White
if ($ocrRunning) {
    Write-Host "  OCR Health: http://localhost:5000/health" -ForegroundColor Gray
}
if ($odooPort) {
    Write-Host "  Odoo Login: http://localhost:$odooPort/web?db=edu_demo_new" -ForegroundColor Gray
}
if ($portalRunning) {
    Write-Host "  Admission: http://localhost:$odooPort/admission/apply" -ForegroundColor Gray
}

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "Testing Complete!" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
