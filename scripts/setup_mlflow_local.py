#!/usr/bin/env python3
"""
MLflow Local Setup & Testing Guide

This script demonstrates how to set up and test MLflow locally
before running the GitHub Actions workflow.
"""

import os
import sys
import subprocess

def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def check_python_version():
    """Check Python version."""
    print_header("1️⃣  Checking Python Version")
    
    python_version = sys.version_info
    print(f"Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major >= 3 and python_version.minor >= 9:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python 3.9+ required")
        return False


def install_mlflow():
    """Install MLflow."""
    print_header("2️⃣  Installing MLflow")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mlflow==2.10.2", "pandas", "plotly"])
        print("✅ MLflow installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install MLflow: {e}")
        return False


def setup_mlflow_directories():
    """Setup MLflow directories."""
    print_header("3️⃣  Setting Up Directories")
    
    directories = [
        "/tmp/mlflow",
        "reports",
        "reports/student_performance",
        "reports/grade_predictor",
        "reports/ocr_service",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}")


def initialize_experiments():
    """Initialize MLflow experiments."""
    print_header("4️⃣  Initializing Experiments")
    
    try:
        subprocess.check_call([
            sys.executable,
            "scripts/mlflow_init_experiments.py"
        ], cwd=os.path.dirname(__file__) or ".")
        print("✅ Experiments initialized")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize experiments: {e}")
        return False


def track_student_performance():
    """Track student performance model."""
    print_header("5️⃣  Tracking Student Performance Model")
    
    try:
        subprocess.check_call([
            sys.executable,
            "scripts/mlflow_track_student_performance.py"
        ], cwd=os.path.dirname(__file__) or ".")
        print("✅ Student Performance tracking complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to track Student Performance: {e}")
        return False


def track_grade_predictor():
    """Track grade predictor model."""
    print_header("6️⃣  Tracking Grade Predictor Model")
    
    try:
        subprocess.check_call([
            sys.executable,
            "scripts/mlflow_track_grade_predictor.py"
        ], cwd=os.path.dirname(__file__) or ".")
        print("✅ Grade Predictor tracking complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to track Grade Predictor: {e}")
        return False


def track_ocr_service():
    """Track OCR service."""
    print_header("7️⃣  Tracking OCR Service")
    
    try:
        subprocess.check_call([
            sys.executable,
            "scripts/mlflow_track_ocr_service.py"
        ], cwd=os.path.dirname(__file__) or ".")
        print("✅ OCR Service tracking complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to track OCR Service: {e}")
        return False


def generate_report():
    """Generate MLflow report."""
    print_header("8️⃣  Generating MLflow Report")
    
    try:
        subprocess.check_call([
            sys.executable,
            "scripts/mlflow_generate_report.py"
        ], cwd=os.path.dirname(__file__) or ".")
        print("✅ Report generated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate report: {e}")
        return False


def launch_mlflow_ui():
    """Launch MLflow UI."""
    print_header("9️⃣  Launching MLflow UI")
    
    print("🔗 MLflow UI is available at: http://localhost:5000")
    print()
    print("📊 Run the following command to start MLflow UI:")
    print()
    print("   mlflow ui --backend-store-uri file:///tmp/mlflow")
    print()
    print("Then open: http://localhost:5000")
    print()


def print_results_summary():
    """Print summary of generated files."""
    print_header("📊 Generated Files Summary")
    
    files = [
        ("mlflow_report.html", "Interactive MLflow dashboard"),
        ("mlflow_metrics_summary.json", "Structured metrics data"),
        ("reports/mlflow_experiments.json", "Experiment configuration"),
        ("reports/student_performance/predictions.json", "Student performance predictions"),
        ("reports/grade_predictor/predictions.json", "Grade predictor results"),
        ("reports/ocr_service/extraction_results.json", "OCR service results"),
    ]
    
    print("Generated artifacts:")
    print()
    for filename, description in files:
        if os.path.exists(filename):
            print(f"  ✅ {filename}")
            print(f"     └─ {description}")
        else:
            print(f"  ⚠️  {filename} (not found)")
    
    print()


def main():
    """Main setup and testing function."""
    
    print("""
    ╔════════════════════════════════════════════════════════════════════════╗
    ║                                                                        ║
    ║         MLflow Local Setup & Testing for Odoo ERP System              ║
    ║                                                                        ║
    ║    This guide will help you set up MLflow locally and test the       ║
    ║    model tracking pipeline before running GitHub Actions             ║
    ║                                                                        ║
    ╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing MLflow", install_mlflow),
        ("Setting up directories", setup_mlflow_directories),
        ("Initializing experiments", initialize_experiments),
        ("Tracking Student Performance model", track_student_performance),
        ("Tracking Grade Predictor model", track_grade_predictor),
        ("Tracking OCR Service", track_ocr_service),
        ("Generating MLflow report", generate_report),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            failed_steps.append(step_name)
    
    print_results_summary()
    
    if not failed_steps:
        print_header("✅ All Steps Completed Successfully!")
        launch_mlflow_ui()
        print("📚 Next Steps:")
        print("   1. Start MLflow UI")
        print("   2. View experiments and runs")
        print("   3. Review generated HTML report")
        print("   4. Check metrics in mlflow_metrics_summary.json")
        print()
        return 0
    else:
        print_header("❌ Some Steps Failed")
        print(f"Failed steps: {', '.join(failed_steps)}")
        print()
        print("Troubleshooting tips:")
        print("  1. Check Python version (3.9+)")
        print("  2. Verify all dependencies are installed")
        print("  3. Check file permissions on /tmp/mlflow")
        print("  4. Review error messages above")
        print()
        return 1


if __name__ == "__main__":
    exit(main())
