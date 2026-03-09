#!/bin/bash

# ============================================================================
# Quick Setup Script for API Gateway
# ============================================================================
# Usage: ./setup.sh
# ============================================================================

set -e  # Exit on error

echo "========================================="
echo "Educational ERP API Gateway Setup"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    
    # Generate random JWT secret
    JWT_SECRET=$(openssl rand -hex 32)
    sed -i "s/your-very-secure-secret-key-min-32-characters-long/$JWT_SECRET/" .env
    
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Please review and update credentials in .env file${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

echo ""

# Create SSL certificates directory
echo -e "${YELLOW}Generating SSL certificates for development...${NC}"
mkdir -p nginx/ssl

if [ ! -f nginx/ssl/cert.pem ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=EG/ST=Cairo/L=Cairo/O=EduERP/CN=localhost" \
        2>/dev/null
    
    echo -e "${GREEN}✓ SSL certificates generated${NC}"
else
    echo -e "${GREEN}✓ SSL certificates already exist${NC}"
fi

echo ""

# Create necessary directories
echo -e "${YELLOW}Creating required directories...${NC}"
mkdir -p logs/nginx logs/fastapi logs/ocr logs/odoo
mkdir -p temp/ocr_uploads
mkdir -p prometheus/data grafana/data redis/data
chmod -R 777 logs temp prometheus/data grafana/data redis/data

echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Pull Docker images
echo -e "${YELLOW}Pulling Docker images (this may take a while)...${NC}"
docker-compose pull

echo ""

# Build custom images
echo -e "${YELLOW}Building custom images...${NC}"
docker-compose build

echo ""

# Start services
echo -e "${YELLOW}Starting services...${NC}"
docker-compose up -d

echo ""

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Check service status
echo ""
echo "========================================="
echo "Service Status"
echo "========================================="
docker-compose ps

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo -e "${GREEN}Access points:${NC}"
echo "  • API Gateway (HTTPS): https://localhost"
echo "  • API Documentation:   https://localhost/docs"
echo "  • Prometheus:          http://localhost:9090"
echo "  • Grafana:             http://localhost:3000"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review and update credentials in .env file"
echo "  2. Generate a test JWT token: ./scripts/generate_token.sh"
echo "  3. Test API endpoints: ./scripts/test_endpoints.sh"
echo "  4. View logs: docker-compose logs -f"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
