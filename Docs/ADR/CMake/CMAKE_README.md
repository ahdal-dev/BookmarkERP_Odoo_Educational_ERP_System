# CMake Setup and Usage Guide

## Table of Contents
- [What is CMake?](#what-is-cmake)
- [Why CMake for Odoo?](#why-cmake-for-odoo)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Available Targets](#available-targets)
- [Detailed Usage](#detailed-usage)
- [Troubleshooting](#troubleshooting)

---

## What is CMake?

**CMake** is a cross-platform build system generator and task orchestrator. While traditionally used for C/C++ projects, we're using it as a **task runner** to standardize common Odoo development workflows.

### Key Benefits
- ✅ **Cross-platform** - Works on Windows, Linux, and macOS
- ✅ **IDE Integration** - Supported by VS Code, CLion, Visual Studio
- ✅ **Standardized Commands** - Same commands for all developers
- ✅ **Self-Documenting** - Commands are defined in `CMakeLists.txt`
- ✅ **Error Prevention** - Centralized command definitions

---

## Why CMake for Odoo?

Instead of remembering and typing long Python commands like:
```bash
python odoo/odoo-bin -c odoo.conf -d edu_demo_new -u base --stop-after-init
```

You can use simple, memorable commands:
```bash
cmake --build build --target config_module
```

This ensures:
- **Consistency** across the development team
- **Fewer errors** from typos or wrong parameters
- **Easier onboarding** for new developers
- **Better documentation** of available tasks

---

## Installation

### Prerequisites
- Python 3.x (already installed in your project)
- Windows, Linux, or macOS

### Windows Installation

#### Option 1: Using winget (How i installed it)
Open PowerShell or Command Prompt and run:
```bash
winget install Kitware.CMake
```

#### Option 2: Using Chocolatey
If you have Chocolatey installed:
```bash
choco install cmake
```


### macOS Installation

#### Using Homebrew
```bash
brew install cmake
```

### Verify Installation

After installation, **restart your terminal** and verify:
```bash
cmake --version
```

You should see output like:
```
cmake version 3.x.x
```

---

## Quick Start

### 1. Install Ninja Build Tool

CMake needs a build tool. Install Ninja (recommended):
```bash
winget install Ninja-build.Ninja
```

**Restart your terminal** after installation.

### 2. Install Python Dependencies

Activate your virtual environment and install Odoo requirements:
```bash
cd C:\Odoo
venv\Scripts\activate
pip install -r odoo\requirements.txt
```

### 3. Configure the Project (First Time Only)

```bash
# Delete old build directory if it exists
rmdir /s /q build

# Configure with Ninja generator
cmake -B build -G Ninja
```

This creates a `build` directory with the CMake configuration.

### 4. Run Tasks

Now you can use the available targets:

```bash
# Configure database and update base module
cmake --build build --target config_module

# Start Odoo server
cmake --build build --target run
```

---

## Available Targets

### `config_module`
**Purpose:** Configure the database and update the base module  
**Command:** `cmake --build build --target config_module`  
**What it does:**
```bash
python odoo/odoo-bin -c odoo.conf -d edu_demo_new -u base --stop-after-init
```
- Initializes or updates the database `edu_demo_new`
- Updates the `base` module
- Stops after initialization (doesn't start the server)

**When to use:**
- First time setting up the project
- After pulling database schema changes
- When you need to reinitialize the database

---

### `run`
**Purpose:** Start the Odoo server manually  
**Command:** `cmake --build build --target run`  
**What it does:**
```bash
python odoo/odoo-bin -c odoo.conf
```
- Starts the Odoo development server
- Uses configuration from `odoo.conf`
- Server runs until you stop it (Ctrl+C)

**When to use:**
- Daily development work
- Testing your changes in the browser
- Running the application locally

---

### `update_module`
**Purpose:** Update a specific custom module  
**Command:** `cmake --build build --target update_module`  
**What it does:**
```bash
python odoo/odoo-bin -c odoo.conf -d edu_demo_new -u ${MODULE_NAME} --stop-after-init
```

**When to use:**
- After making changes to a specific module
- To reload module changes without full restart

---

## Detailed Usage

### First-Time Setup Workflow

```bash
# 1. Navigate to project directory
cd C:\Odoo

# 2. Activate virtual environment (if not already active)
venv\Scripts\activate

# 3. Configure CMake (creates build directory)
cmake -B build

# 4. Initialize database and base module
cmake --build build --target config_module

# 5. Start Odoo server
cmake --build build --target run
```

### Daily Development Workflow

```bash
# Activate virtual environment
venv\Scripts\activate

# Start Odoo server
cmake --build build --target run

# Access Odoo in browser at http://localhost:8081
```

### After Making Module Changes

```bash
# Stop the server (Ctrl+C if running)

# Reconfigure the module/database
cmake --build build --target config_module

# Restart the server
cmake --build build --target run
```

---

## Troubleshooting

### Issue: `'cmake' is not recognized`

**Problem:** CMake is not installed or not in PATH

**Solution:**
1. Install CMake using one of the methods above
2. **Restart your terminal** after installation
3. Verify with `cmake --version`
4. If still not working, manually add CMake to PATH:
   - Default location: `C:\Program Files\CMake\bin`
   - Add to System Environment Variables → PATH


## Alternative: Direct Python Commands (That got replaced by CMake)

If you prefer not to use CMake, you can still run commands directly:

```bash
# Configure module/database
python odoo/odoo-bin -c odoo.conf -d edu_demo_new -u base --stop-after-init

# Run Odoo server
python odoo/odoo-bin -c odoo.conf
```