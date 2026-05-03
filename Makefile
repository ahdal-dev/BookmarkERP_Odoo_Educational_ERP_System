.PHONY: config run install update-module clean help ocr-run ocr-install ocr-test ocr-stop test-admission test-all test-module grade-run grade-install gateway-up gateway-down clean-ghosts k8s-install-tools k8s-create-cluster k8s-delete-cluster k8s-minikube-start k8s-minikube-delete k8s-build-images k8s-load-images k8s-minikube-load-images k8s-deploy k8s-status k8s-port-forward k8s-logs k8s-clean

# Configuration
PYTHON = venv/Scripts/python.exe
PIP = venv/Scripts/pip.exe
ODOO_BIN = odoo/odoo-bin
ODOO_CONF = config/odoo.conf
DB_NAME = edu_demo_new
OCR_DIR = services/ocr
GRADE_DIR = services/grade_predector
GATEWAY_DIR = api_gateway
OCR_PORT = 5000
GRADE_PORT = 5001
MINIKUBE_PROFILE = edu-erp
MINIKUBE_BIN = "C:\Program Files\Kubernetes\Minikube\minikube.exe"

# Default target
help:
	@echo ============================================
	@echo Odoo Educational ERP - Available Commands
	@echo ============================================
	@echo.
	@echo ODOO COMMANDS:
	@echo   make config         - Configure database and update base module
	@echo   make run            - Start Odoo server
	@echo   make install        - Install Python dependencies
	@echo   make update-module  - Update specific module (set MODULE=name)
	@echo   make remove-module  - Remove/uninstall module (set MODULE=name)
	@echo   make clean          - Clean Python cache files
	@echo.
	@echo OCR MICROSERVICE COMMANDS:
	@echo   make ocr-install    - Install OCR service dependencies
	@echo   make ocr-run        - Start OCR microservice on port $(OCR_PORT)
	@echo   make ocr-test       - Test OCR service health endpoint
	@echo   make ocr-stop       - Stop OCR microservice
	@echo.
	@echo TESTING COMMANDS:
	@echo   make test-admission - Run all admission_portal module tests
	@echo   make test-all       - Run tests for all installed modules
	@echo   make test-module    - Run tests for specific module (set MODULE=name)
	@echo.
	@echo GRADE PREDICTOR COMMANDS:
	@echo   make grade-install  - Install Grade Predictor dependencies
	@echo   make grade-run      - Start Grade Predictor on port $(GRADE_PORT)
	@echo.
	@echo API GATEWAY COMMANDS:
	@echo   make gateway-up     - Start API gateway services (Docker)
	@echo   make gateway-down   - Stop API gateway services (Docker)
	@echo.
	@echo KUBERNETES LOCAL TESTING COMMANDS:
	@echo   make k8s-install-tools      - Install kubectl and kind
	@echo   make k8s-create-cluster     - Create local Kind cluster
	@echo   make k8s-delete-cluster     - Delete local Kind cluster
	@echo   make k8s-minikube-start     - Start local Minikube cluster
	@echo   make k8s-minikube-delete    - Delete local Minikube cluster
	@echo   make k8s-build-images       - Build Docker images for Kubernetes
	@echo   make k8s-load-images        - Load Docker images into Kind cluster
	@echo   make k8s-minikube-load-images - Load Docker images into Minikube cluster
	@echo   make k8s-deploy             - Deploy all Kubernetes manifests
	@echo   make k8s-status             - Check cluster, pod, service status
	@echo   make k8s-port-forward       - Forward NGINX to localhost:8080
	@echo   make k8s-logs               - View logs from running pods
	@echo   make k8s-clean              - Complete cleanup
	@echo.
	@echo EXAMPLES:
	@echo   make config
	@echo   make run
	@echo   make ocr-run
	@echo   make grade-run
	@echo   make gateway-up
	@echo   make test-admission
	@echo   make update-module MODULE=education_management
	@echo   make test-module MODULE=education_management
	@echo   make remove-module MODULE=my_module
	@echo.
	@echo   make help           - Show this help message
	@echo ============================================

# Configure module or database
# Updates base module and stops after initialization
config:
	@echo Configuring Odoo module/database: $(DB_NAME)
	$(PYTHON) $(ODOO_BIN) -c $(ODOO_CONF) -d $(DB_NAME) -u base --stop-after-init

# Start Odoo server manually
run:
	@echo Starting Odoo server...
	$(PYTHON) $(ODOO_BIN) -c $(ODOO_CONF)

# Install Python dependencies
install:
	@echo Installing Odoo dependencies...
	$(PIP) install -r odoo/requirements.txt

# Update specific module
# Usage: make update-module MODULE=education_management
update-module:
ifndef MODULE
	@echo Error: MODULE variable not set
	@echo Usage: make update-module MODULE=education_management
	@exit 1
endif
	@echo Updating module: $(MODULE)
	$(PYTHON) $(ODOO_BIN) -c $(ODOO_CONF) -d $(DB_NAME) -u $(MODULE) --stop-after-init

# Remove/uninstall specific module
# Usage: make remove-module MODULE=module_name
remove-module:
ifndef MODULE
	@echo Error: MODULE variable not set
	@echo Usage: make remove-module MODULE=module_name
	@exit 1
endif
	@echo Uninstalling module: $(MODULE)
	$(PYTHON) scripts/remove_module.py $(MODULE) $(ODOO_CONF) $(DB_NAME)

# ============================================================================
# OCR Microservice Commands
# ============================================================================

# Install OCR service dependencies
ocr-install:
	@echo Installing OCR microservice dependencies...
	@cd "$(OCR_DIR)" && python -m pip install -r requirements.txt
	@echo OCR dependencies installed!

# Start OCR microservice
ocr-run:
	@echo Starting OCR microservice on port $(OCR_PORT)...
	@echo.
	@echo Press Ctrl+C to stop the service
	@echo ============================================
	@cd "$(OCR_DIR)" && python run.py

# Test OCR service health
ocr-test:
	@echo Testing OCR microservice health endpoint...
	@powershell -Command "try { $$response = Invoke-WebRequest -Uri 'http://localhost:$(OCR_PORT)/health' -UseBasicParsing; Write-Host 'OCR Service Status:' -ForegroundColor Green; Write-Host $$response.Content; exit 0 } catch { Write-Host 'Error: OCR service is not running on port $(OCR_PORT)' -ForegroundColor Red; Write-Host 'Run: make ocr-run' -ForegroundColor Yellow; exit 1 }"

# Stop OCR microservice (kills all python processes on port 5000)
ocr-stop:
	@echo Stopping OCR microservice...

# ============================================================================
# Grade Predictor Microservice Commands
# ============================================================================

# Install Grade Predictor dependencies
grade-install:
	@echo Installing Grade Predictor dependencies...
	@cd "$(GRADE_DIR)" && python -m pip install -r requirements.txt
	@echo Grade Predictor dependencies installed!

# Start Grade Predictor microservice
grade-run:
	@echo Starting Grade Predictor on port $(GRADE_PORT)...
	@echo.
	@echo Press Ctrl+C to stop the service
	@echo ============================================
	@cd "$(GRADE_DIR)" && python run.py

# ============================================================================
# API Gateway Commands
# ============================================================================

# Start API gateway services
gateway-up:
	@echo Starting API Gateway services...
	@cd "$(GATEWAY_DIR)" && docker-compose up -d
	@echo API Gateway started!

# Stop API gateway services
gateway-down:
	@echo Stopping API Gateway services...
	@cd "$(GATEWAY_DIR)" && docker-compose down
	@echo API Gateway stopped!

# ============================================================================
# Database Cleanup Commands
# ============================================================================

# Clean ghost modules and orphaned models from the database
clean-ghosts:
	@echo Cleaning ghost modules and orphaned models from database...
	$(PYTHON) scripts/clean_ghost_modules.py $(ODOO_CONF) $(DB_NAME)

# ============================================================================
# Testing Commands
# ============================================================================

# Run admission_portal module tests
test-admission:
	@echo ============================================
	@echo Running admission_portal module tests
	@echo ============================================
	$(PYTHON) $(ODOO_BIN) -c $(ODOO_CONF) -d $(DB_NAME) -u admission_portal --test-enable --stop-after-init --log-level=test

# Run all tests for all modules
test-all:
	@echo ============================================
	@echo Running all module tests
	@echo ============================================
	$(PYTHON) $(ODOO_BIN) -c $(ODOO_CONF) -d $(DB_NAME) --test-enable --stop-after-init --log-level=test

# Run tests for a specific module
# Usage: make test-module MODULE=education_management
test-module:
ifndef MODULE
	@echo Error: MODULE variable not set
	@echo Usage: make test-module MODULE=education_management
	@exit 1
endif
	@echo ============================================
	@echo Running tests for module: $(MODULE)
	@echo ============================================
	$(PYTHON) $(ODOO_BIN) -c $(ODOO_CONF) -d $(DB_NAME) -u $(MODULE) --test-enable --stop-after-init --log-level=test

# Clean Python cache files
clean:
	@echo Cleaning Python cache files...
	@del /s /q *.pyc 2>nul
	@for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
	@echo Done!

# ============================================================================
# Kubernetes Local Testing Commands
# ============================================================================

# Install Kubernetes tools (kind, kubectl)
k8s-install-tools:
	@echo Installing Kubernetes tools...
	@echo Installing kubectl...
	@choco install kubernetes-cli -y
	@echo Installing kind...
	@choco install kind -y
	@echo Kubernetes tools installed!
	@echo Verify with: kubectl version --client
	@echo Verify with: kind version

# Create local Kind cluster
k8s-create-cluster:
	@echo Creating local Kind cluster (edu-erp)...
	@kind create cluster --name edu-erp --config k8s/kind-config.yaml
	@echo Cluster created!
	@echo Verify with: kubectl cluster-info
	@echo Verify with: kubectl get nodes

# Delete local Kind cluster
k8s-delete-cluster:
	@echo Deleting local Kind cluster (edu-erp)...
	@kind delete cluster --name edu-erp
	@echo Cluster deleted!

# Start local Minikube cluster
k8s-minikube-start:
	@echo Starting local Minikube cluster ($(MINIKUBE_PROFILE))...
	@$(MINIKUBE_BIN) start -p $(MINIKUBE_PROFILE) --driver=docker
	@echo Cluster started!
	@echo Verify with: minikube status -p $(MINIKUBE_PROFILE)
	@echo Verify with: kubectl get nodes

# Delete local Minikube cluster
k8s-minikube-delete:
	@echo Deleting local Minikube cluster ($(MINIKUBE_PROFILE))...
	@$(MINIKUBE_BIN) delete -p $(MINIKUBE_PROFILE)
	@echo Cluster deleted!

# Build Docker images for Kubernetes
k8s-build-images:
	@echo Building Docker images...
	@echo Building FastAPI Gateway image...
	@docker build -t fastapi-gateway:latest -f api_gateway/fastapi_app/Dockerfile api_gateway/fastapi_app
	@echo Building OCR Service image...
	@docker build -t ocr-service:latest -f services/ocr/Dockerfile services/ocr
	@echo Docker images built!
	@echo Verify with: docker images | findstr "fastapi-gateway ocr-service"

# Load Docker images into Kind cluster
k8s-load-images:
	@echo Loading Docker images into Kind cluster...
	@kind load docker-image fastapi-gateway:latest --name edu-erp
	@kind load docker-image ocr-service:latest --name edu-erp
	@echo Docker images loaded into cluster!

# Load Docker images into Minikube cluster
k8s-minikube-load-images:
	@echo Loading Docker images into Minikube cluster ($(MINIKUBE_PROFILE))...
	@$(MINIKUBE_BIN) image load -p $(MINIKUBE_PROFILE) fastapi-gateway:latest
	@$(MINIKUBE_BIN) image load -p $(MINIKUBE_PROFILE) ocr-service:latest
	@echo Docker images loaded into Minikube cluster!

# Deploy all Kubernetes manifests
k8s-deploy:
	@echo Deploying Kubernetes manifests...
	@echo Applying configuration...
	@kubectl apply -f k8s/config/configmap.yaml
	@kubectl apply -f k8s/config/secret.yaml
	@kubectl apply -f k8s/config/postgres-initdb-configmap.yaml
	@echo Applying PostgreSQL...
	@kubectl apply -f k8s/config/postgres-serviceaccount.yaml
	@kubectl apply -f k8s/config/postgres-service.yaml
	@kubectl apply -f k8s/config/postgres-deployment.yaml
	@echo Applying FastAPI Gateway...
	@kubectl apply -f k8s/fastapi/
	@echo Applying Odoo ERP...
	@kubectl apply -f k8s/odoo/
	@echo Applying OCR Service...
	@kubectl apply -f k8s/ocr/
	@echo Applying NGINX Gateway...
	@kubectl apply -f k8s/nginx/
	@echo Deployment complete!
	@echo Check status with: make k8s-status

# Check Kubernetes cluster status
k8s-status:
	@echo ============================================
	@echo Kubernetes Cluster Status
	@echo ============================================
	@kubectl cluster-info
	@echo.
	@echo Nodes:
	@kubectl get nodes
	@echo.
	@echo Pods (edu-erp):
	@kubectl get pods -l app=edu-erp -o wide
	@echo.
	@echo Services (edu-erp):
	@kubectl get svc -l app=edu-erp -o wide
	@echo.
	@echo Deployments (edu-erp):
	@kubectl get deployments -l app=edu-erp

# Port forward NGINX service for local access
k8s-port-forward:
	@echo Starting port forwarding for NGINX...
	@echo Forwarding http://localhost:8080 to nginx-service:80
	@echo Open browser: http://localhost:8080/health
	@echo Press Ctrl+C to stop forwarding
	@kubectl port-forward svc/nginx-service 8080:80

# View pod logs
k8s-logs:
	@echo ============================================
	@echo Kubernetes Pod Logs
	@echo ============================================
	@echo FastAPI Logs:
	@kubectl logs -l component=fastapi-gateway --tail=50
	@echo.
	@echo NGINX Logs:
	@kubectl logs -l component=nginx-gateway --tail=50
	@echo.
	@echo Odoo Logs:
	@kubectl logs -l component=odoo-erp --tail=50

# Clean up Kubernetes cluster and images
k8s-clean:
	@echo Cleaning up Kubernetes...
	@echo Deleting deployments...
	@kubectl delete all -l app=edu-erp
	@echo Deleting cluster...
	@kind delete cluster --name edu-erp
	@echo Cleanup complete!
