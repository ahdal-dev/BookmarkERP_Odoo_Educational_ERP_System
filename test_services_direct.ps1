# ============================================================================
# Direct Services Testing Script
# Tests OCR and Odoo services without API Gateway
# ============================================================================

$ErrorActionPreference = "Continue"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Direct Services Testing Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# Test 1: OCR Service Health Check
# ============================================================================
Write-Host "Test 1: OCR Service Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get
    Write-Host "✓ OCR service is running" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "✗ OCR service not available: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Run: make ocr-run" -ForegroundColor Yellow
}
Write-Host ""

# ============================================================================
# Test 2: Odoo Service Health Check
# ============================================================================
Write-Host "Test 2: Odoo Service Health Check" -ForegroundColor Yellow
try {
    # Try port 8081 (your current port)
    $response = Invoke-WebRequest -Uri "http://localhost:8081/web/database/selector" -Method Get -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Odoo service is running on port 8081" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ Odoo not responding on port 8081" -ForegroundColor Yellow
    
    # Try port 8069 (default port)
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8069/web/database/selector" -Method Get -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Odoo service is running on port 8069" -ForegroundColor Green
        }
    } catch {
        Write-Host "✗ Odoo service not available on 8069 or 8081" -ForegroundColor Red
        Write-Host "  Run: make run (in Odoo directory)" -ForegroundColor Yellow
    }
}
Write-Host ""

# ============================================================================
# Test 3: OCR Document Processing
# ============================================================================
Write-Host "Test 3: OCR Document Processing (if test image available)" -ForegroundColor Yellow

# Check for test images
$testImages = @(
    "test_document.jpg",
    "test_image.jpg",
    "test_id.jpg",
    "..\test_document.jpg"
)

$imageFound = $false
$testImagePath = $null

foreach ($img in $testImages) {
    if (Test-Path $img) {
        $imageFound = $true
        $testImagePath = $img
        break
    }
}

if ($imageFound) {
    try {
        Write-Host "Found test image: $testImagePath" -ForegroundColor Gray
        
        # Create multipart form data
        $filePath = Resolve-Path $testImagePath
        $fileName = Split-Path $filePath -Leaf
        
        # Using .NET HttpClient for proper multipart upload
        Add-Type -AssemblyName System.Net.Http
        
        $httpClient = New-Object System.Net.Http.HttpClient
        $multipartContent = New-Object System.Net.Http.MultipartFormDataContent
        
        $fileStream = [System.IO.File]::OpenRead($filePath)
        $fileContent = New-Object System.Net.Http.StreamContent($fileStream)
        $multipartContent.Add($fileContent, "file", $fileName)
        
        $response = $httpClient.PostAsync("http://localhost:5000/ocr", $multipartContent).Result
        $result = $response.Content.ReadAsStringAsync().Result
        
        $fileStream.Close()
        $httpClient.Dispose()
        
        if ($response.IsSuccessStatusCode) {
            Write-Host "✓ OCR processing successful" -ForegroundColor Green
            $result | ConvertFrom-Json | ConvertTo-Json -Depth 3
        } else {
            Write-Host "✗ OCR processing failed" -ForegroundColor Red
            Write-Host $result -ForegroundColor Red
        }
        
    } catch {
        Write-Host "✗ OCR test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "⚠ No test image found - skipping OCR test" -ForegroundColor Yellow
    Write-Host "  Place a test image (JPG) in the current directory to test OCR" -ForegroundColor Gray
}
Write-Host ""

# ============================================================================
# Test 4: Admission Portal Availability
# ============================================================================
Write-Host "Test 4: Admission Portal Availability" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8081/admission/apply" -Method Get -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Admission portal is accessible" -ForegroundColor Green
        Write-Host "  URL: http://localhost:8081/admission/apply" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠ Admission portal not accessible" -ForegroundColor Yellow
    Write-Host "  Make sure admission_portal module is installed and Odoo is running" -ForegroundColor Gray
}
Write-Host ""

# ============================================================================
# Service Status Summary
# ============================================================================
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Service Status Summary" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check ports in use
Write-Host "`nPorts in use:" -ForegroundColor Gray
$ports = @(5000, 8069, 8081)
foreach ($port in $ports) {
    $connections = netstat -ano | Select-String ":$port " | Select-String "LISTENING"
    if ($connections) {
        Write-Host "  Port $port : ACTIVE" -ForegroundColor Green
    } else {
        Write-Host "  Port $port : NOT IN USE" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Testing Complete!" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Quick Start Commands:" -ForegroundColor Yellow
Write-Host "  Start OCR    : make ocr-run (in C:\Odoo)" -ForegroundColor Gray
Write-Host "  Start Odoo   : make run (in C:\Odoo)" -ForegroundColor Gray
Write-Host "  Test Admission: http://localhost:8081/admission/apply" -ForegroundColor Gray
Write-Host ""
