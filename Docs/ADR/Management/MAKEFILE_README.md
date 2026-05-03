# Makefile Setup and Usage Guide

## Table of Contents
- [What is Make?](#what-is-make)
- [Why Make for Odoo?](#why-make-for-odoo)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Available Targets](#available-targets)
- [Detailed Usage](#detailed-usage)
- [Troubleshooting](#troubleshooting)

---

## What is Make?

**GNU Make** is a build automation tool that automatically builds executable programs and libraries from source code by reading files called Makefiles. While traditionally used for compiling code, we're using it as a **task runner** to standardize common Odoo development workflows.

### Key Benefits
- ✅ **Simple** - Easy to read and write
- ✅ **Standard** - Widely known and used across the industry
- ✅ **No setup** - Just run `make <target>` directly
- ✅ **Self-documenting** - `make help` shows available commands
- ✅ **Lightweight** - No build directories or configuration steps

---

## Why Make for Odoo?

Instead of remembering and typing long Python commands like:
```bash
python odoo/odoo-bin -c odoo.conf -d edu_demo_new -u base --stop-after-init
```

You can use simple, memorable commands:
```bash
make config
```

This ensures:
- **Consistency** across the development team
- **Fewer errors** from typos or wrong parameters
- **Easier onboarding** for new developers
- **Better documentation** of available tasks

---

## Installation

### Windows

#### Option 1: Using Chocolatey (What i used)
```bash
choco install make
```

#### Option 2: Using winget
```bash
winget install GnuWin32.Make
```

#### Option 3: Manual Installation
1. Download from [GnuWin32](http://gnuwin32.sourceforge.net/packages/make.htm)
2. Install and add to PATH

### Linux

Make is usually pre-installed. 

### macOS

Make is pre-installed with Xcode Command Line Tools:
```bash
xcode-select --install
```

### Verify Installation

After installation, verify:
```bash
make --version
```

You should see output like:
```
GNU Make 4.x
```

---

## Quick Start

### 1. Install Python Dependencies

Activate your virtual environment and install Odoo requirements:
```bash
cd C:\Odoo
venv\Scripts\activate
make install
```

### 2. Configure the Database

```bash
make config
```

### 3. Start Odoo Server

```bash
make run
```

### 4. See All Available Commands

```bash
make help
```

---

## Available Targets

### `help`
**Purpose:** Show all available commands  
**Command:** `make help` or just `make`  
**What it does:**
- Displays a list of all available targets
- Shows usage examples

**When to use:**
- When you forget available commands
- For onboarding new developers

---

### `config`
**Purpose:** Configure the database and update the base module  
**Command:** `make config`  
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
**Purpose:** Start the Odoo server  
**Command:** `make run`  
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

**Access:** http://localhost:8081

---

### `install`
**Purpose:** Install Python dependencies  
**Command:** `make install`  
**What it does:**
```bash
pip install -r odoo/requirements.txt
```
- Installs all Odoo Python dependencies
- Uses the virtual environment pip

**When to use:**
- First time setup
- After pulling new dependencies
- When dependencies are missing

---

### `update-module`
**Purpose:** Update a specific custom module  
**Command:** `make update-module MODULE=education_management`  
**What it does:**
```bash
python odoo/odoo-bin -c odoo.conf -d edu_demo_new -u MODULE_NAME --stop-after-init
```

**When to use:**
- After making changes to a specific module
- To reload module changes without full restart

**Example:**
```bash
make update-module MODULE=education_management
```

---

### `clean`
**Purpose:** Clean Python cache files  
**Command:** `make clean`  
**What it does:**
- Removes all `.pyc` files
- Removes all `__pycache__` directories

**When to use:**
- When you have import issues
- Before committing code
- To free up disk space

---

## Detailed Usage

### First-Time Setup Workflow

```bash
# 1. Navigate to project directory
cd C:\Odoo

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Install dependencies
make install

# 4. Initialize database and base module
make config

# 5. Start Odoo server
make run
```

### Daily Development Workflow

```bash
# Activate virtual environment
venv\Scripts\activate

# Start Odoo server
make run

# Access Odoo in browser at http://localhost:8081
```

### After Making Module Changes

```bash
# Stop the server (Ctrl+C if running)

# Update the specific module
make update-module MODULE=education_management

# Or reconfigure everything
make config

# Restart the server
make run
```

### Clean Development Environment

```bash
# Clean Python cache
make clean

# Reconfigure database
make config

# Start fresh
make run
```

---
