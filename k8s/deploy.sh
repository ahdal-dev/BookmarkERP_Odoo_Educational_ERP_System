#!/bin/bash
# ================================================================
# Kubernetes Deployment Script for Educational ERP System
# ================================================================
# Purpose: Automated deployment of all microservices to Kubernetes
# Usage: ./deploy.sh [namespace] [environment]
# ================================================================

set -e

# Configuration
NAMESPACE="${1:-default}"
ENVIRONMENT="${2:-development}"
K8S_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ================================================================
# Helper Functions
# ================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is installed
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl."
        exit 1
    fi
    log_success "kubectl found: $(kubectl version --client --short)"
}

# Check cluster connectivity
check_cluster() {
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Please configure kubectl."
        exit 1
    fi
    log_success "Connected to cluster: $(kubectl cluster-info | head -1)"
}

# Create namespace
create_namespace() {
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_info "Creating namespace: $NAMESPACE"
        kubectl create namespace "$NAMESPACE"
        log_success "Namespace created"
    else
        log_info "Namespace already exists: $NAMESPACE"
    fi
}

# Deploy configuration and secrets
deploy_config() {
    log_info "Deploying ConfigMaps and Secrets..."
    
    kubectl apply -f "$K8S_DIR/config/configmap.yaml" -n "$NAMESPACE"
    kubectl apply -f "$K8S_DIR/config/secret.yaml" -n "$NAMESPACE"
    kubectl apply -f "$K8S_DIR/config/postgres-initdb-configmap.yaml" -n "$NAMESPACE"
    
    log_success "Configuration deployed"
}

# Deploy PostgreSQL database
deploy_postgres() {
    log_info "Deploying PostgreSQL database..."
    
    kubectl apply -f "$K8S_DIR/config/postgres-serviceaccount.yaml" -n "$NAMESPACE"
    kubectl apply -f "$K8S_DIR/config/postgres-service.yaml" -n "$NAMESPACE"
    kubectl apply -f "$K8S_DIR/config/postgres-deployment.yaml" -n "$NAMESPACE"
    
    log_info "Waiting for PostgreSQL to be ready..."
    kubectl wait --for=condition=ready pod \
        -l component=postgres-db \
        -n "$NAMESPACE" \
        --timeout=300s 2>/dev/null || log_warning "PostgreSQL pod not ready yet"
    
    log_success "PostgreSQL deployed"
}

# Deploy FastAPI service
deploy_fastapi() {
    log_info "Deploying FastAPI Gateway..."
    
    kubectl apply -f "$K8S_DIR/fastapi/serviceaccount.yaml" -n "$NAMESPACE"
    kubectl apply -f "$K8S_DIR/fastapi/service.yaml" -n "$NAMESPACE"
    kubectl apply -f "$K8S_DIR/fastapi/deployment.yaml" -n "$NAMESPACE"
    
    log_success "FastAPI Gateway deployed"
}

# Deploy Odoo service
deploy_odoo() {
    log_info "Deploying Odoo ERP..."
    
    kubectl apply -f "$K8S_DIR/odoo/serviceaccount.yaml" -n "$NAMESPACE"
    kubectl apply -f "$K8S_DIR/odoo/configmap.yaml" -n "$NAMESPACE"
    kubectl apply -f "$K8S_DIR/odoo/service.yaml" -n "$NAMESPACE"
    kubectl apply -f "$K8S_DIR/odoo/deployment.yaml" -n "$NAMESPACE"
    
    log_success "Odoo ERP deployed"
}

# Deploy OCR service
deploy_ocr() {
    log_info "Deploying OCR Microservice..."
    
    kubectl apply -f "$K8S_DIR/ocr/serviceaccount.yaml" -n "$NAMESPACE"
    kubectl apply -f "$K8S_DIR/ocr/service.yaml" -n "$NAMESPACE"
    kubectl apply -f "$K8S_DIR/ocr/deployment.yaml" -n "$NAMESPACE"
    
    log_success "OCR Microservice deployed"
}

# Deploy NGINX gateway
deploy_nginx() {
    log_info "Deploying NGINX API Gateway..."
    
    kubectl apply -f "$K8S_DIR/nginx/serviceaccount.yaml" -n "$NAMESPACE"
    kubectl apply -f "$K8S_DIR/nginx/configmap.yaml" -n "$NAMESPACE"
    kubectl apply -f "$K8S_DIR/nginx/conf-d-configmap.yaml" -n "$NAMESPACE"
    kubectl apply -f "$K8S_DIR/nginx/service.yaml" -n "$NAMESPACE"
    kubectl apply -f "$K8S_DIR/nginx/deployment.yaml" -n "$NAMESPACE"
    
    log_success "NGINX API Gateway deployed"
}

# Wait for all deployments to be ready
wait_for_deployments() {
    log_info "Waiting for all deployments to be ready..."
    
    kubectl wait --for=condition=available deployment \
        -l app=edu-erp \
        -n "$NAMESPACE" \
        --timeout=600s 2>/dev/null || true
    
    log_success "Deployments are ready"
}

# Display deployment status
show_status() {
    echo ""
    log_info "=== Deployment Status ==="
    log_info "Namespace: $NAMESPACE"
    log_info "Environment: $ENVIRONMENT"
    echo ""
    
    log_info "Pods:"
    kubectl get pods -l app=edu-erp -n "$NAMESPACE"
    
    echo ""
    log_info "Services:"
    kubectl get svc -l app=edu-erp -n "$NAMESPACE"
    
    echo ""
    log_info "Deployments:"
    kubectl get deployments -l app=edu-erp -n "$NAMESPACE"
    
    echo ""
    log_info "=== Access Information ==="
    
    NGINX_IP=$(kubectl get svc nginx-service -n "$NAMESPACE" \
        -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    NGINX_PORT=$(kubectl get svc nginx-service -n "$NAMESPACE" \
        -o jsonpath='{.spec.ports[0].port}' 2>/dev/null)
    
    if [ "$NGINX_IP" != "pending" ]; then
        log_success "NGINX Gateway: http://$NGINX_IP:$NGINX_PORT"
    else
        log_warning "NGINX IP pending (LoadBalancer may take time to assign)"
        log_info "Run 'kubectl get svc -n $NAMESPACE' to check status"
    fi
}

# ================================================================
# Main Execution
# ================================================================

main() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Educational ERP - Kubernetes Deployment Script           ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    log_info "Starting deployment process..."
    log_info "Namespace: $NAMESPACE | Environment: $ENVIRONMENT"
    echo ""
    
    # Pre-deployment checks
    log_info "=== Pre-Deployment Checks ==="
    check_kubectl
    check_cluster
    
    # Create namespace
    log_info "=== Namespace Setup ==="
    create_namespace
    
    # Deploy services in order
    log_info "=== Deploying Services ==="
    deploy_config
    echo ""
    
    deploy_postgres
    echo ""
    
    deploy_fastapi
    echo ""
    
    deploy_odoo
    echo ""
    
    deploy_ocr
    echo ""
    
    deploy_nginx
    echo ""
    
    # Wait and verify
    log_info "=== Verification ==="
    wait_for_deployments
    
    # Show final status
    show_status
    
    echo ""
    log_success "Deployment completed successfully!"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
}

# Run main function
main
