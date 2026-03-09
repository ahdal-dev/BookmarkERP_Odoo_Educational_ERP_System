# ============================================================================
# API Gateway Testing Script - Working Version
# ============================================================================

$ErrorActionPreference = "Continue"

# SSL certificate handling for HTTPS
if (-not ([System.Management.Automation.PSTypeName]'ServerCertificateValidationCallback').Type) {
    Add-Type @"
        using System;
        using System.Net;
        using System.Net.Security;
        using System.Security.Cryptography.X509Certificates;
        public class ServerCertificateValidationCallback {
            public static void Ignore() {
                ServicePointManager.ServerCertificateValidationCallback += 
                    delegate { return true; };
            }
        }
"@
}
[ServerCertificateValidationCallback]::Ignore()

$API_BASE = "http://localhost"  # Using HTTP instead of HTTPS for local testing

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "API Gateway Testing Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "[1/5] Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$API_BASE/health" -Method Get -TimeoutSec 5
    Write-Host "  Status: $($response.status)" -ForegroundColor Green
    Write-Host "  Gateway: WORKING" -ForegroundColor Green
} catch {
    Write-Host "  Status: FAILED" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Generate JWT Token
Write-Host "[2/5] JWT Token Generation..." -ForegroundColor Yellow
try {
    $tokenBody = @{
        username = "test_student"
        role = "prospective_student"
    } | ConvertTo-Json

    $tokenResponse = Invoke-RestMethod -Uri "$API_BASE/api/v1/auth/token" `
        -Method Post `
        -Body $tokenBody `
        -ContentType "application/json" `
        -TimeoutSec 5
    
    $token = $tokenResponse.access_token
    Write-Host "  Token: Generated" -ForegroundColor Green
    Write-Host "  Preview: $($token.Substring(0, [Math]::Min(50, $token.Length)))..." -ForegroundColor Gray
} catch {
    Write-Host "  Status: FAILED" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    $token = $null
}
Write-Host ""

# Test 3: Submit Admission Application
Write-Host "[3/5] Admission Application Submission..." -ForegroundColor Yellow
if ($token) {
    try {
        $applicationData = @{
            full_name = "Ahmed Mohamed Test"
            national_id = "12345678901234"
            email = "ahmed.test@example.com"
            phone = "+201234567890"
            date_of_birth = "2000-01-15T00:00:00"
            address = "123 Main Street, Cairo"
            city = "Cairo"
            country = "Egypt"
            previous_qualification = "High School Diploma"
            graduation_year = 2018
            gpa = 3.5
            desired_program = "Computer Science"
            application_type = "regular"
        } | ConvertTo-Json

        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }

        $response = Invoke-RestMethod -Uri "$API_BASE/api/v1/admissions/apply" `
            -Method Post `
            -Headers $headers `
            -Body $applicationData `
            -TimeoutSec 10
        
        Write-Host "  Status: SUCCESS" -ForegroundColor Green
        Write-Host "  Response: Application submitted" -ForegroundColor Gray
    } catch {
        Write-Host "  Status: FAILED" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.ErrorDetails) {
            Write-Host "  Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "  Status: SKIPPED (no token)" -ForegroundColor Gray
}
Write-Host ""

# Test 4: Check OCR Service
Write-Host "[4/5] OCR Service Availability..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get -TimeoutSec 3
    Write-Host "  Status: AVAILABLE" -ForegroundColor Green
} catch {
    Write-Host "  Status: NOT AVAILABLE" -ForegroundColor Yellow
    Write-Host "  Note: Start with 'make ocr-run'" -ForegroundColor Gray
}
Write-Host ""

# Test 5: Rate Limiting
Write-Host "[5/5] Rate Limiting Test..." -ForegroundColor Yellow
Write-Host "  Sending 10 rapid requests..." -ForegroundColor Gray
$rateLimitHit = $false
for ($i = 1; $i -le 10; $i++) {
    try {
        Invoke-RestMethod -Uri "$API_BASE/health" -Method Get -TimeoutSec 2 | Out-Null
        Write-Host "." -NoNewline -ForegroundColor Green
    } catch {
        if ($_.Exception.Response.StatusCode -eq 429) {
            $rateLimitHit = $true
            Write-Host "!" -NoNewline -ForegroundColor Red
        }
    }
    Start-Sleep -Milliseconds 100
}
Write-Host ""
if ($rateLimitHit) {
    Write-Host "  Rate limiting: WORKING" -ForegroundColor Green
} else {
    Write-Host "  Rate limiting: Not triggered (OK)" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Testing Complete!" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "API Documentation:" -ForegroundColor White
Write-Host "  Swagger UI: http://localhost/docs" -ForegroundColor Gray
Write-Host "  ReDoc:      http://localhost/redoc" -ForegroundColor Gray
Write-Host ""
