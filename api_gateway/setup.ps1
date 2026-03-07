# ============================================================================
# Quick Setup Script for API Gateway (PowerShell/Windows)
# ============================================================================
# Usage: .\setup.ps1
# ============================================================================

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Educational ERP API Gateway Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✓ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "Error: Docker is not installed" -ForegroundColor Red
    Write-Host "Please install Docker Desktop: https://docs.docker.com/desktop/windows/install/" -ForegroundColor Yellow
    exit 1
}

# Check if Docker Compose is installed
try {
    docker-compose --version | Out-Null
    Write-Host "✓ Docker Compose is installed" -ForegroundColor Green
} catch {
    Write-Host "Error: Docker Compose is not installed" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Create .env file if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    
    # Generate random JWT secret
    $bytes = New-Object byte[] 32
    $random = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $random.GetBytes($bytes)
    $jwt_secret = [System.BitConverter]::ToString($bytes).Replace("-", "").ToLower()
    
    (Get-Content .env) -replace 'your-very-secure-secret-key-min-32-characters-long', $jwt_secret | Set-Content .env
    
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host "⚠ Please review and update credentials in .env file" -ForegroundColor Yellow
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

Write-Host ""

# Create SSL certificates directory
Write-Host "Generating SSL certificates for development..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "nginx\ssl" | Out-Null

if (-not (Test-Path "nginx\ssl\cert.pem")) {
    # Check if OpenSSL is available
    try {
        openssl version | Out-Null
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
            -keyout "nginx\ssl\key.pem" `
            -out "nginx\ssl\cert.pem" `
            -subj "/C=EG/ST=Cairo/L=Cairo/O=EduERP/CN=localhost" 2>$null
        
        Write-Host "✓ SSL certificates generated" -ForegroundColor Green
    } catch {
        Write-Host "⚠ OpenSSL not found. Please install OpenSSL or generate certificates manually" -ForegroundColor Yellow
        Write-Host "You can use: choco install openssl" -ForegroundColor Yellow
    }
} else {
    Write-Host "✓ SSL certificates already exist" -ForegroundColor Green
}

Write-Host ""

# Create necessary directories
Write-Host "Creating required directories..." -ForegroundColor Yellow
$directories = @(
    "logs\nginx",
    "logs\fastapi",
    "logs\ocr",
    "logs\odoo",
    "temp\ocr_uploads",
    "prometheus\data",
    "grafana\data",
    "redis\data"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

Write-Host "✓ Directories created" -ForegroundColor Green
Write-Host ""

# Pull Docker images
Write-Host "Pulling Docker images (this may take a while)..." -ForegroundColor Yellow
docker-compose pull

Write-Host ""

# Build custom images
Write-Host "Building custom images..." -ForegroundColor Yellow
docker-compose build

Write-Host ""

# Start services
Write-Host "Starting services..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""

# Wait for services to be ready
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service status
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Service Status" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access points:" -ForegroundColor Green
Write-Host "  • API Gateway (HTTPS): https://localhost"
Write-Host "  • API Documentation:   https://localhost/docs"
Write-Host "  • Prometheus:          http://localhost:9090"
Write-Host "  • Grafana:             http://localhost:3000"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review and update credentials in .env file"
Write-Host "  2. Test API endpoints using PowerShell or Postman"
Write-Host "  3. View logs: docker-compose logs -f"
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Green
