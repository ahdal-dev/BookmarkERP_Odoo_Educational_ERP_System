# ============================================================================
# API Testing Script (PowerShell)
# ============================================================================
# Tests all API endpoints with sample data
# ============================================================================

$ErrorActionPreference = "Stop"

$API_BASE = "https://localhost"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "API Gateway Testing Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Ignore SSL certificate errors for development
add-type @"
    using System.Net;
    using System.Security.Cryptography.X509Certificates;
    public class TrustAllCertsPolicy : ICertificatePolicy {
        public bool CheckValidationResult(
            ServicePoint srvPoint, X509Certificate certificate,
            WebRequest request, int certificateProblem) {
            return true;
        }
    }
"@
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy

# Test 1: Health Check
Write-Host "Test 1: Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$API_BASE/health" -Method Get
    Write-Host "✓ Health check passed" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Health check failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Generate JWT Token
Write-Host "Test 2: Generate JWT Token" -ForegroundColor Yellow
try {
    $tokenBody = @{
        username = "test_student"
        role = "prospective_student"
    } | ConvertTo-Json

    $tokenResponse = Invoke-RestMethod -Uri "$API_BASE/api/v1/auth/token" `
        -Method Post `
        -Body $tokenBody `
        -ContentType "application/json"
    
    $token = $tokenResponse.access_token
    Write-Host "✓ JWT token generated" -ForegroundColor Green
    Write-Host "Token: $($token.Substring(0, 50))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Token generation failed: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Test 3: Submit Admission Application
Write-Host "Test 3: Submit Admission Application" -ForegroundColor Yellow
try {
    $applicationData = @{
        full_name = "Ahmed Mohamed"
        national_id = "12345678901234"
        email = "ahmed.mohamed@example.com"
        phone = "+201234567890"
        date_of_birth = "2000-01-15T00:00:00"
        address = "123 Main Street, Nasr City"
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
        -Body $applicationData
    
    Write-Host "✓ Application submitted successfully" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Application submission failed: $_" -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
}
Write-Host ""

# Test 4: Extract Document (requires image file)
Write-Host "Test 4: Extract Document (OCR)" -ForegroundColor Yellow
if (Test-Path "test_document.jpg") {
    try {
        $headers = @{
            "Authorization" = "Bearer $token"
        }

        # PowerShell doesn't have native multipart/form-data support
        # Using System.Net.Http for proper file upload
        Write-Host "⚠ File upload test requires curl or Invoke-WebRequest with file" -ForegroundColor Yellow
        Write-Host "Example: curl -X POST https://localhost/api/v1/extract-document -H 'Authorization: Bearer $token' -F 'file=@test_document.jpg'" -ForegroundColor Gray
    } catch {
        Write-Host "✗ Document extraction failed: $_" -ForegroundColor Red
    }
} else {
    Write-Host "⚠ Skipping OCR test - test_document.jpg not found" -ForegroundColor Yellow
}
Write-Host ""

# Test 5: Check Rate Limiting
Write-Host "Test 5: Rate Limiting Test" -ForegroundColor Yellow
Write-Host "Sending 15 requests rapidly..." -ForegroundColor Gray
$rateLimitHit = $false
for ($i = 1; $i -le 15; $i++) {
    try {
        Invoke-RestMethod -Uri "$API_BASE/health" -Method Get | Out-Null
        Write-Host "." -NoNewline -ForegroundColor Green
    } catch {
        if ($_.Exception.Response.StatusCode -eq 429) {
            $rateLimitHit = $true
            Write-Host "!" -NoNewline -ForegroundColor Red
        }
    }
    Start-Sleep -Milliseconds 50
}
Write-Host ""
if ($rateLimitHit) {
    Write-Host "✓ Rate limiting is working correctly" -ForegroundColor Green
} else {
    Write-Host "⚠ Rate limit not triggered (may need adjustment)" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Testing Complete!" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "For full API documentation, visit: https://localhost/docs" -ForegroundColor Green
