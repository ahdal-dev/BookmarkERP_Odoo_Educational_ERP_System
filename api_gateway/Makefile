# ============================================================================
# Makefile for API Gateway Management
# ============================================================================
# Usage: make <target>
# ============================================================================

.PHONY: help setup up down restart logs build clean test health ssl

# Default target
.DEFAULT_GOAL := help

# Variables
COMPOSE := docker-compose
SERVICES := nginx fastapi_gateway ocr_microservice odoo postgres redis

# ============================================================================
# Help
# ============================================================================
help: ## Show this help message
	@echo "Educational ERP API Gateway - Available Commands"
	@echo "================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# Setup & Installation
# ============================================================================
setup: ## Initial setup (create dirs, generate SSL, copy env)
	@echo "Setting up API Gateway..."
	@mkdir -p logs/nginx logs/fastapi logs/ocr logs/odoo
	@mkdir -p temp/ocr_uploads
	@mkdir -p prometheus/data grafana/data redis/data
	@mkdir -p nginx/ssl
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo ".env file created - please update with your credentials"; \
	fi
	@if [ ! -f nginx/ssl/cert.pem ]; then \
		$(MAKE) ssl; \
	fi
	@echo "Setup complete!"

ssl: ## Generate self-signed SSL certificates for development
	@echo "Generating SSL certificates..."
	@openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout nginx/ssl/key.pem \
		-out nginx/ssl/cert.pem \
		-subj "/C=EG/ST=Cairo/L=Cairo/O=EduERP/CN=localhost"
	@echo "SSL certificates generated!"

# ============================================================================
# Docker Operations
# ============================================================================
up: ## Start all services
	@echo "Starting services..."
	@$(COMPOSE) up -d
	@echo "Services started! Access: https://localhost"

down: ## Stop all services
	@echo "Stopping services..."
	@$(COMPOSE) down
	@echo "Services stopped!"

restart: down up ## Restart all services

build: ## Build/rebuild all containers
	@echo "Building containers..."
	@$(COMPOSE) build
	@echo "Build complete!"

rebuild: ## Rebuild and restart all services
	@$(COMPOSE) up -d --build

pull: ## Pull latest images
	@$(COMPOSE) pull

# ============================================================================
# Service Management
# ============================================================================
scale-fastapi: ## Scale FastAPI gateway (usage: make scale-fastapi N=3)
	@$(COMPOSE) up -d --scale fastapi_gateway=$(N)
	@echo "FastAPI gateway scaled to $(N) instances"

start-nginx: ## Start only NGINX service
	@$(COMPOSE) up -d nginx

start-fastapi: ## Start only FastAPI gateway
	@$(COMPOSE) up -d fastapi_gateway

start-ocr: ## Start only OCR service
	@$(COMPOSE) up -d ocr_microservice

start-odoo: ## Start only Odoo service
	@$(COMPOSE) up -d odoo postgres

stop-nginx: ## Stop NGINX service
	@$(COMPOSE) stop nginx

stop-fastapi: ## Stop FastAPI gateway
	@$(COMPOSE) stop fastapi_gateway

stop-ocr: ## Stop OCR service
	@$(COMPOSE) stop ocr_microservice

stop-odoo: ## Stop Odoo service
	@$(COMPOSE) stop odoo

restart-nginx: ## Restart NGINX service
	@$(COMPOSE) restart nginx

restart-fastapi: ## Restart FastAPI gateway
	@$(COMPOSE) restart fastapi_gateway

restart-ocr: ## Restart OCR service
	@$(COMPOSE) restart ocr_microservice

restart-odoo: ## Restart Odoo service
	@$(COMPOSE) restart odoo

# ============================================================================
# Logs & Monitoring
# ============================================================================
logs: ## View logs from all services
	@$(COMPOSE) logs -f

logs-nginx: ## View NGINX logs
	@$(COMPOSE) logs -f nginx

logs-fastapi: ## View FastAPI logs
	@$(COMPOSE) logs -f fastapi_gateway

logs-ocr: ## View OCR service logs
	@$(COMPOSE) logs -f ocr_microservice

logs-odoo: ## View Odoo logs
	@$(COMPOSE) logs -f odoo

logs-postgres: ## View PostgreSQL logs
	@$(COMPOSE) logs -f postgres

logs-redis: ## View Redis logs
	@$(COMPOSE) logs -f redis

logs-tail: ## View last 100 lines of all logs
	@$(COMPOSE) logs --tail=100


ps: ## Show running containers (detailed)
	@$(COMPOSE) ps -a

top: ## Display running processes in containers
	@$(COMPOSE) top

stats: ## Show container resource usage statistics
	@docker stats --no-stream $(shell $(COMPOSE) ps -q)

inspect-network: ## Inspect Docker network configuration
	@docker network inspect api_gateway_backend

inspect-volumes: ## List all volumes
	@$(COMPOSE) config --volumes
	@docker volume ls | grep api_gateway
logs-errors: ## Show only error logs from all services
	@$(COMPOSE) logs | grep -i error

# ============================================================================
# Health & Status
# ============================================================================
status: ## Show status of all services
	@$(COMPOSE) ps

health: ## Check health of all services
	@curl -s http://localhost/health | jq .
	@echo ""


test-health: ## Test health endpoint
	@echo "Testing health endpoint..."
	@curl -s -k https://localhost/health | jq .

test-metrics: ## Test metrics endpoint
	@echo "Testing metrics endpoint..."
	@curl -s -k https://localhost/metrics | jq .

test-rate-limit: ## Test rate limiting (sends 20 requests)
	@echo "Testing rate limiting..."
	@for i in {1..20}; do \
		curl -s -k -o /dev/null -w "Request $$i: %{http_code}\n" https://localhost/health; \
		sleep 0.1; \
	done

test-admission: ## Test admission endpoint with sample data
	@echo "Testing admission application..."
	@TOKEN=$$(curl -s -k -X POST "https://localhost/api/v1/auth/token" \
		-H "Content-Type: application/json" \
		-d '{"username":"test","role":"prospective_student"}' | jq -r .access_token); \
	curl -s -k -X POST "https://localhost/api/v1/admissions/apply" \
		-H "Authorization: Bearer $$TOKEN" \
		-H "Content-Type: application/json" \
		-d '{"full_name":"Test Student","national_id":"12345678901234","email":"test@example.com","phone":"+201234567890","date_of_birth":"2000-01-01T00:00:00","address":"Test Address","city":"Cairo","country":"Egypt","previous_qualification":"High School","graduation_year":2018,"gpa":3.5,"desired_program":"Computer Science","application_type":"regular"}' | jq .
# ============================================================================
# Testing
# ============================================================================
test: ## Run API tests
	@echo "Running API tests..."
	@if command -v pwsh > /dev/null; then \
		pwsh -File test_api.ps1; \
	else \
		echo "PowerShell not found. Please 

clean-docker: ## Remove unused Docker resources
	@echo "Cleaning Docker system..."
	@docker system prune -f
	@echo "Docker cleanup complete!"

clean-volumes: ## Remove all project volumes (WARNING: deletes data!)
	@echo "WARNING: This will delete all data volumes!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@$(COMPOSE) down -v
	@echo "Volumes removed!"

clean-images: ## Remove project Docker images
	@echo "Removing project images..."
	@docker images | grep api_gateway | awk '{print $$3}' | xargs -r docker rmi -f
	@echo "Images removed!"run test_api.ps1 manually"; \
	fi

test-token: ## Generate test JWT token
	@curl -X POST "https://localhost/api/v1/auth/token" \
		-H "Content-Type: application/json" \
		-d '{"username": "test_user", "role": "prospective_student"}' \
		-k | jq .

# ============================================================================
# Cleanup
# ============================================================================
clean: down ## Stop services and remove volumes
	@echo "Removing volumes..."
	@$(COMPOSE) down -v
	@echo "Cleanup complete!"

clean-logs: ## Remove all log files
	@rm -rf logs/*
	@mkdir -p logs/nginx logs/fastapi logs/ocr logs/odoo
	@echo "Logs cleared!"


shell-postgres: ## Open PostgreSQL shell
	@$(COMPOSE) exec postgres psql -U odoo edu_demo_new


db-shell: ## Open PostgreSQL interactive shell
	@$(COMPOSE) exec postgres psql -U odoo edu_demo_new

db-list: ## List all databases
	@$(COMPOSE) exec postgres psql -U odoo -c '\l'

db-size: ## Show database size

redoc: ## Open ReDoc API documentation
	@xdg-open https://localhost/redoc 2>/dev/null || open https://localhost/redoc 2>/dev/null || start https://localhost/redoc

nginx-reload: ## Reload NGINX configuration without downtime
	@$(COMPOSE) exec nginx nginx -s reload
	@echo "NGINX configuration reloaded!"

nginx-test: ## Test NGINX configuration

update: ## Update Docker images to latest versions
	@echo "Updating Docker images..."
	@$(COMPOSE) pull
	@echo "Update complete! Run 'make rebuild' to apply changes"

upgrade: pull rebuild ## Pull latest images and rebuild services

security-scan: ## Scan Docker images for vulnerabilities
	@echo "Scanning images for security vulnerabilities..."
	@docker images --format "{{.Repository}}:{{.Tag}}" | grep -v "<none>" | xargs -I {} sh -c 'echo "Scanning {}..." && docker scan {} || true'
	@$(COMPOSE) exec nginx nginx -t
	@$(COMPOSE) exec postgres psql -U odoo -c "SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) AS size FROM pg_database;"

db-vacuum: ## Vacuum and analyze database
	@echo "Running database maintenance..."
	@$(COMPOSE) exec postgres psql -U odoo edu_demo_new -c "VACUUM ANALYZE;"
	@echo "Database maintenance complete!"
shell-redis: ## Open Redis CLI
	@$(COMPOSE) exec redis redis-cli

shell-odoo: ## Open shell in Odoo container
	@$(COMPOSE) exec odoo /bin/bash

exec: ## Execute command in container (usage: make exec SERVICE=nginx CMD="ls -la")
	@$(COMPOSE) exec $(SERVICE) $(CMD)
clean-all: clean clean-logs ## Complete cleanup (services, volumes, logs)
	@rm -rf temp/*
	@mkdir -p temp/ocr_uploads
validate-env: ## Validate environment configuration
	@echo "Validating environment configuration..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found!"; \
		exit 1; \
	fi
	@echo "✓ .env file exists"
	@if [ ! -f nginx/ssl/cert.pem ]; then \
		echo "❌ SSL certificates not found!"; \
		exit 1; \
	fi
	@echo "✓ SSL certificates exist"
	@echo "✓ Environment validation passed!"

config: ## Show Docker Compose configuration
	@$(COMPOSE) config

ports: ## Show all exposed ports
	@echo "Exposed Ports:"
	@$(COMPOSE) ps --format json | jq -r '.[] | select(.Publishers != null) | .Publishers[] | "\(.PublishedPort) -> \(.TargetPort) (\(.Protocol))"' 2>/dev/null || $(COMPOSE) ps

version: ## Show version information
	@echo "Docker version:"
	@docker --version
	@echo "\nDocker Compose version:"
	@docker-compose --version
	@echo "\nProject version: 1.0.0"

	@echo "All temporary files removed!"

# =======

watch: ## Watch container logs in real-time (all services)
	@$(COMPOSE) logs -f --tail=50

monitor: ## Monitor resource usage continuously
	@watch -n 2 'docker stats --no-stream $(shell $(COMPOSE) ps -q 2>/dev/null)'

benchmark: ## Run simple performance benchmark
	@echo "Running benchmark (100 requests to health endpoint)..."
	@time for i in {1..100}; do curl -s -k https://localhost/health > /dev/null; done
	@echo "Benchmark complete!"

quick-start: setup ssl up ## Quick start from scratch (setup + SSL + start)
	@echo ""
	@echo "Quick start complete! Services are running."
	@$(MAKE) info

prune: ## Clean up ALL unused Docker resources (containers, networks, images)
	@echo "WARNING: This will remove all unused Docker resources!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@docker system prune -a --volumes -f
	@echo "Docker system pruned!"=====================================================================
# Development
# ============================================================================
dev: ## Start in development mode (with code reloading)
	@$(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up

shell-fastapi: ## Open shell in FastAPI container
	@$(COMPOSE) exec fastapi_gateway /bin/bash

shell-nginx: ## Open shell in NGINX container
	@$(COMPOSE) exec nginx /bin/sh

# ============================================================================
# Database Operations
# ============================================================================
db-backup: ## Backup PostgreSQL database
	@echo "Creating database backup..."
	@$(COMPOSE) exec -T postgres pg_dump -U odoo edu_demo_new > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup created!"

db-restore: ## Restore database (usage: make db-restore FILE=backup.sql)
	@echo "Restoring database from $(FILE)..."
	@$(COMPOSE) exec -T postgres psql -U odoo edu_demo_new < $(FILE)
	@echo "Database restored!"

# ============================================================================
# Monitoring
# ============================================================================
metrics: ## Open Prometheus metrics
	@xdg-open http://localhost:9090 2>/dev/null || open http://localhost:9090 2>/dev/null || start http://localhost:9090

grafana: ## Open Grafana dashboard
	@xdg-open http://localhost:3000 2>/dev/null || open http://localhost:3000 2>/dev/null || start http://localhost:3000

docs: ## Open API documentation
	@xdg-open https://localhost/docs 2>/dev/null || open https://localhost/docs 2>/dev/null || start https://localhost/docs

# ============================================================================
# Production
# ============================================================================
prod-up: ## Start in production mode
	@$(COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-down: ## Stop production services
	@$(COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml down

# ============================================================================
# Information
# ============================================================================
info: ## Display service URLs and information
	@echo "========================================="
	@echo "Educational ERP API Gateway"
	@echo "========================================="
	@echo ""
	@echo "Service URLs:"
	@echo "  • API Gateway:     https://localhost"
	@echo "  • API Docs:        https://localhost/docs"
	@echo "  • Prometheus:      http://localhost:9090"
	@echo "  • Grafana:         http://localhost:3000"
	@echo ""
	@echo "Useful Commands:"
	@echo "  • View logs:       make logs"
	@echo "  • Check status:    make status"
	@echo "  • Run tests:       make test"
	@echo "  • Get help:        make help"
	@echo ""
