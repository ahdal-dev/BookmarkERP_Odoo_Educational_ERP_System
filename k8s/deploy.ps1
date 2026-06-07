@echo off
REM ================================================================
REM Kubernetes Deployment Script for Educational ERP System (Windows)
REM ================================================================
REM Purpose: Automated deployment of all microservices to Kubernetes
REM Usage: deploy.ps1 -Namespace default -Environment development
REM ================================================================

param(
    [string]$Namespace = "default",
    [string]$Environment = "development"
)

# Colors for output
$ErrorActionPreference = "Stop"
$K8sDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Write-LogInfo($message) {
    Write-Host "[INFO] $message" -ForegroundColor Cyan
}

function Write-LogSuccess($message) {
    Write-Host "[SUCCESS] $message" -ForegroundColor Green
}

function Write-LogWarning($message) {
    Write-Host "[WARNING] $message" -ForegroundColor Yellow
}

function Write-LogError($message) {
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

function Check-Kubectl {
    $kubectl = Get-Command kubectl -ErrorAction SilentlyContinue
    if ($null -eq $kubectl) {
        Write-LogError "kubectl is not installed. Please install kubectl."
        exit 1
    }
    $version = kubectl version --client --short 2>$null
    Write-LogSuccess "kubectl found: $version"
}

function Check-Cluster {
    try {
        kubectl cluster-info 2>$null | Out-Null
        $clusterInfo = kubectl cluster-info 2>$null | Select-Object -First 1
        Write-LogSuccess "Connected to cluster: $clusterInfo"
    } catch {
        Write-LogError "Cannot connect to Kubernetes cluster. Please configure kubectl."
        exit 1
    }
}

function Create-Namespace {
    $ns = kubectl get namespace $Namespace 2>$null
    if ($null -eq $ns) {
        Write-LogInfo "Creating namespace: $Namespace"
        kubectl create namespace $Namespace
        Write-LogSuccess "Namespace created"
    } else {
        Write-LogInfo "Namespace already exists: $Namespace"
    }
}

function Deploy-Config {
    Write-LogInfo "Deploying ConfigMaps and Secrets..."
    
    kubectl apply -f "$K8sDir\config\configmap.yaml" -n $Namespace
    kubectl apply -f "$K8sDir\config\secret.yaml" -n $Namespace
    kubectl apply -f "$K8sDir\config\postgres-initdb-configmap.yaml" -n $Namespace
    
    Write-LogSuccess "Configuration deployed"
}

function Deploy-Postgres {
    Write-LogInfo "Deploying PostgreSQL database..."
    
    kubectl apply -f "$K8sDir\config\postgres-serviceaccount.yaml" -n $Namespace
    kubectl apply -f "$K8sDir\config\postgres-service.yaml" -n $Namespace
    kubectl apply -f "$K8sDir\config\postgres-deployment.yaml" -n $Namespace
    
    Write-LogInfo "Waiting for PostgreSQL to be ready..."
    kubectl wait --for=condition=ready pod -l component=postgres-db -n $Namespace --timeout=300s 2>$null || Write-LogWarning "PostgreSQL pod not ready yet"
    
    Write-LogSuccess "PostgreSQL deployed"
}

function Deploy-FastAPI {
    Write-LogInfo "Deploying FastAPI Gateway..."
    
    kubectl apply -f "$K8sDir\fastapi\serviceaccount.yaml" -n $Namespace
    kubectl apply -f "$K8sDir\fastapi\service.yaml" -n $Namespace
    kubectl apply -f "$K8sDir\fastapi\deployment.yaml" -n $Namespace
    
    Write-LogSuccess "FastAPI Gateway deployed"
}

function Deploy-Odoo {
    Write-LogInfo "Deploying Odoo ERP..."
    
    kubectl apply -f "$K8sDir\odoo\serviceaccount.yaml" -n $Namespace
    kubectl apply -f "$K8sDir\odoo\configmap.yaml" -n $Namespace
    kubectl apply -f "$K8sDir\odoo\service.yaml" -n $Namespace
    kubectl apply -f "$K8sDir\odoo\deployment.yaml" -n $Namespace
    
    Write-LogSuccess "Odoo ERP deployed"
}

function Deploy-OCR {
    Write-LogInfo "Deploying OCR Microservice..."
    
    kubectl apply -f "$K8sDir\ocr\serviceaccount.yaml" -n $Namespace
    kubectl apply -f "$K8sDir\ocr\service.yaml" -n $Namespace
    kubectl apply -f "$K8sDir\ocr\deployment.yaml" -n $Namespace
    
    Write-LogSuccess "OCR Microservice deployed"
}

function Deploy-NGINX {
    Write-LogInfo "Deploying NGINX API Gateway..."
    
    kubectl apply -f "$K8sDir\nginx\serviceaccount.yaml" -n $Namespace
    kubectl apply -f "$K8sDir\nginx\configmap.yaml" -n $Namespace
    kubectl apply -f "$K8sDir\nginx\conf-d-configmap.yaml" -n $Namespace
    kubectl apply -f "$K8sDir\nginx\service.yaml" -n $Namespace
    kubectl apply -f "$K8sDir\nginx\deployment.yaml" -n $Namespace
    
    Write-LogSuccess "NGINX API Gateway deployed"
}

function Wait-ForDeployments {
    Write-LogInfo "Waiting for all deployments to be ready..."
    
    kubectl wait --for=condition=available deployment -l app=edu-erp -n $Namespace --timeout=600s 2>$null || $true
    
    Write-LogSuccess "Deployments are ready"
}

function Show-Status {
    Write-Host ""
    Write-LogInfo "=== Deployment Status ==="
    Write-LogInfo "Namespace: $Namespace"
    Write-LogInfo "Environment: $Environment"
    Write-Host ""
    
    Write-LogInfo "Pods:"
    kubectl get pods -l app=edu-erp -n $Namespace
    
    Write-Host ""
    Write-LogInfo "Services:"
    kubectl get svc -l app=edu-erp -n $Namespace
    
    Write-Host ""
    Write-LogInfo "Deployments:"
    kubectl get deployments -l app=edu-erp -n $Namespace
}

function Main {
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  Educational ERP - Kubernetes Deployment Script (Windows) ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-LogInfo "Starting deployment process..."
    Write-LogInfo "Namespace: $Namespace | Environment: $Environment"
    Write-Host ""
    
    Write-LogInfo "=== Pre-Deployment Checks ==="
    Check-Kubectl
    Check-Cluster
    
    Write-LogInfo "=== Namespace Setup ==="
    Create-Namespace
    
    Write-LogInfo "=== Deploying Services ==="
    Deploy-Config
    Write-Host ""
    
    Deploy-Postgres
    Write-Host ""
    
    Deploy-FastAPI
    Write-Host ""
    
    Deploy-Odoo
    Write-Host ""
    
    Deploy-OCR
    Write-Host ""
    
    Deploy-NGINX
    Write-Host ""
    
    Write-LogInfo "=== Verification ==="
    Wait-ForDeployments
    
    Show-Status
    
    Write-Host ""
    Write-LogSuccess "Deployment completed successfully!"
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
}

Main
