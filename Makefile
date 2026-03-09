.PHONY: config run install update-module clean help ocr-run ocr-install ocr-test ocr-stop test-admission test-all test-module

# Configuration
PYTHON = venv/Scripts/python.exe
PIP = venv/Scripts/pip.exe
ODOO_BIN = odoo/odoo-bin
ODOO_CONF = odoo.conf
DB_NAME = edu_demo_new
OCR_DIR = AI Models/OCR As Micro Service
OCR_PORT = 5000

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
	@echo EXAMPLES:
	@echo   make config
	@echo   make run
	@echo   make ocr-run
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
	@echo Removing module: $(MODULE)
	@echo Note: This command requires Odoo shell access
	@echo Run manually: python odoo-bin shell -c odoo.conf -d $(DB_NAME)

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
