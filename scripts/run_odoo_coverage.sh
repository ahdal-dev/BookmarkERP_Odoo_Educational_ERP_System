#!/usr/bin/env bash
# ============================================================================
# run_odoo_coverage.sh — Coverage for Custom Odoo ERP Modules
# ============================================================================
# Runs odoo-bin under coverage.py, scoped to addons/edu_mangment/* via
# the .coveragerc config file. Produces terminal, HTML, and XML reports
# and fails the build if coverage drops below the configured threshold (80%).
#
# Usage:
#   chmod +x scripts/run_odoo_coverage.sh
#   ./scripts/run_odoo_coverage.sh                 # default: test all custom modules
#   ./scripts/run_odoo_coverage.sh custom_registration  # test a single module
# ============================================================================

set -euo pipefail

# ── Configuration ───────────────────────────────────────────────────────
PYTHON="${PYTHON:-venv/Scripts/python.exe}"       # Python interpreter
ODOO_BIN="${ODOO_BIN:-odoo/odoo-bin}"             # Odoo binary
ODOO_CONF="${ODOO_CONF:-config/odoo.conf}"        # Odoo configuration file
DB_NAME="${DB_NAME:-edu_demo_new}"                # Target database
COVERAGERC="${COVERAGERC:-.coveragerc}"           # Coverage config file

# Modules to test — override via CLI argument or MODULES env var
# Default: all custom modules under edu_mangment
DEFAULT_MODULES="custom_registration,edu_mang_admission,edu_mang_auth,edu_mang_petition,edu_mang_website,edu_portal_gateway"
MODULES="${1:-${MODULES:-$DEFAULT_MODULES}}"

# Report outputs (must match .coveragerc [html] / [xml] sections)
HTML_DIR="htmlcov_odoo"
XML_REPORT="coverage_odoo.xml"
COV_THRESHOLD=80

# ── Preflight checks ───────────────────────────────────────────────────
echo "============================================"
echo " Odoo Custom Module Coverage Runner"
echo "============================================"
echo ""

# Verify critical files exist
for f in "$PYTHON" "$ODOO_BIN" "$ODOO_CONF" "$COVERAGERC"; do
    if [[ ! -f "$f" ]]; then
        echo "ERROR: Required file not found: $f"
        exit 1
    fi
done

# Ensure coverage.py is installed
if ! "$PYTHON" -m coverage --version > /dev/null 2>&1; then
    echo "Installing coverage.py..."
    "$PYTHON" -m pip install coverage
fi

echo "Database : $DB_NAME"
echo "Modules  : $MODULES"
echo "Config   : $ODOO_CONF"
echo "Threshold: ${COV_THRESHOLD}%"
echo ""

# ── Step 1: Clean previous data ────────────────────────────────────────
echo "[1/4] Cleaning previous coverage data..."
"$PYTHON" -m coverage erase
rm -rf "$HTML_DIR" "$XML_REPORT"

# ── Step 2: Run Odoo under coverage ────────────────────────────────────
echo "[2/4] Running odoo-bin under coverage instrumentation..."
echo "      Updating modules: $MODULES"
echo ""

"$PYTHON" -m coverage run \
    --rcfile="$COVERAGERC" \
    "$ODOO_BIN" \
    -c "$ODOO_CONF" \
    -d "$DB_NAME" \
    -u "$MODULES" \
    --test-enable \
    --stop-after-init \
    --log-level=test

echo ""
echo "[2/4] Odoo test run complete."

# ── Step 3: Generate reports ───────────────────────────────────────────
echo "[3/4] Generating coverage reports..."

# Terminal report with missing lines
"$PYTHON" -m coverage report --rcfile="$COVERAGERC"

# HTML report (interactive browsing)
"$PYTHON" -m coverage html --rcfile="$COVERAGERC"
echo "       HTML report → $HTML_DIR/index.html"

# XML report (CI / Codecov / SonarQube)
"$PYTHON" -m coverage xml --rcfile="$COVERAGERC"
echo "       XML  report → $XML_REPORT"

# ── Step 4: Enforce threshold ──────────────────────────────────────────
echo "[4/4] Enforcing minimum coverage threshold (${COV_THRESHOLD}%)..."

# coverage report --fail-under exits with code 2 if below threshold
if "$PYTHON" -m coverage report --rcfile="$COVERAGERC" --fail-under="$COV_THRESHOLD" > /dev/null 2>&1; then
    echo ""
    echo "============================================"
    echo " ✅  PASSED — Coverage >= ${COV_THRESHOLD}%"
    echo "============================================"
    exit 0
else
    echo ""
    echo "============================================"
    echo " ❌  FAILED — Coverage < ${COV_THRESHOLD}%"
    echo "    Minimum required: ${COV_THRESHOLD}%"
    echo "    Review: $HTML_DIR/index.html"
    echo "============================================"
    exit 1
fi
