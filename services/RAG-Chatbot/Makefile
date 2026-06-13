# Cross-platform Makefile for Multi-Organization RAG Chatbot Platform
# Detects OS and adapts Python paths and binary executions accordingly.

export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

ifeq ($(OS),Windows_NT)
    # Windows configurations
    VENV_BIN = venv\Scripts
    PYTHON = ..\venv\Scripts\python.exe
    PIP = ..\venv\Scripts\python.exe -m pip
    ROOT_PYTHON = venv\Scripts\python.exe
    ROOT_PIP = venv\Scripts\python.exe -m pip
else
    # Unix/macOS configurations
    VENV_BIN = venv/bin
    PYTHON = ../venv/bin/python
    PIP = ../venv/bin/pip
    ROOT_PYTHON = venv/bin/python
    ROOT_PIP = venv/bin/pip
endif

.PHONY: help venv install db-init superadmin run test clean

# Default target: show help instructions
help:
	@echo "======================================================================"
	@echo " Multi-Organization RAG Chatbot Platform Automation Menu"
	@echo "======================================================================"
	@echo "Setup Commands:"
	@echo "  make venv                 Create a virtual environment (venv)"
	@echo "  make install              Install dependencies inside the virtual environment"
	@echo "  make db-init              Initialize the database tables and schemas"
	@echo "  make superadmin           Create a super-admin user"
	@echo "                            Usage: make superadmin USERNAME=admin PASSWORD=pass"
	@echo ""
	@echo "Run & Test Commands:"
	@echo "  make run                  Start the FastAPI web server with Uvicorn reload"
	@echo "  make test                 Run database connection and models validation tests"
	@echo "  make clean                Clean all Python cache (__pycache__) and .pyc files"
	@echo "======================================================================"

# Create python virtual environment
venv:
	python -m venv venv
	@echo "Virtual environment created. Active it using:"
	@echo "  Windows: venv\\Scripts\\activate"
	@echo "  Unix/macOS: source venv/bin/activate"

# Install backend dependencies
install: venv
	$(ROOT_PIP) install --upgrade pip
	$(ROOT_PIP) install -r Backend/requirements.txt

# Initialize database schemas and tables
db-init:
	cd Backend && $(PYTHON) -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine); print('✅ Database tables created successfully.')"

# Create a super-admin user in the database
superadmin:
	cd Backend && $(PYTHON) setup_super_admin.py $(USERNAME) $(PASSWORD)

# Run uvicorn server in development mode
run:
	cd Backend && $(PYTHON) -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
test:
	cd Backend && $(PYTHON) test.py
	cd Backend && $(PYTHON) test_models.py

# Clean python cache files
clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]; [p.unlink() for p in pathlib.Path('.').rglob('*.pyc')]; print('🧹 Cleaned python cache files.')"
