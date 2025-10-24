.PHONY: config run install update-module clean help

# Configuration
PYTHON = venv/Scripts/python.exe
PIP = venv/Scripts/pip.exe
ODOO_BIN = odoo/odoo-bin
ODOO_CONF = odoo.conf
DB_NAME = edu_demo_new

# Default target
help:
	@echo ============================================
	@echo Odoo Educational ERP - Available Commands
	@echo ============================================
	@echo.
	@echo   make config         - Configure database and update base module
	@echo   make run            - Start Odoo server
	@echo   make install        - Install Python dependencies
	@echo   make update-module  - Update specific module (set MODULE=name)
	@echo   make clean          - Clean Python cache files
	@echo   make help           - Show this help message
	@echo.
	@echo Examples:
	@echo   make config
	@echo   make run
	@echo   make update-module MODULE=education_management
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

# Clean Python cache files
clean:
	@echo Cleaning Python cache files...
	@del /s /q *.pyc 2>nul
	@for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
	@echo Done!
