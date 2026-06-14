#!/usr/bin/env python3
"""
MLflow Experiment Initialization Script (OPTIMIZED)

Fast initialization for remote MLflow tracking server.
Creates experiments only if they don't exist.
No training/logging operations included.
"""

import mlflow
import os
import json
from datetime import datetime


# -----------------------------
# CONFIG
# -----------------------------
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
EXPERIMENT_GROUP_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "Odoo_ERP_Services")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)


# -----------------------------
# EXPERIMENT DEFINITIONS
# -----------------------------
EXPERIMENTS = {
    "Student_Performance_Service": {
        "description": "Student performance prediction and risk assessment",
        "tags": {
            "model_type": "regression",
            "service": "student_performance",
            "domain": "education",
        },
    },
    "Grade_Predictor_Service": {
        "description": "Grade prediction and classification",
        "tags": {
            "model_type": "classification",
            "service": "grade_predictor",
            "domain": "education",
        },
    },
    "OCR_Service": {
        "description": "Optical Character Recognition and document extraction",
        "tags": {
            "model_type": "ocr",
            "service": "ocr",
            "domain": "document_processing",
        },
    },
    "System_Integration": {
        "description": "Cross-service integration tests and performance",
        "tags": {
            "model_type": "integration",
            "service": "system",
            "domain": "integration",
        },
    },
}


# -----------------------------
# MAIN LOGIC (OPTIMIZED)
# -----------------------------
def create_experiments_fast():
    """
    Fast experiment creation using a single MLflow API call.
    """

    print("\n🔍 Fetching existing experiments from MLflow server...")

    # 🔥 ONE network call instead of 4+
    existing_experiments = mlflow.search_experiments()
    existing_map = {exp.name: exp.experiment_id for exp in existing_experiments}

    print(f"📊 Found {len(existing_map)} existing experiments\n")

    created_experiments = {}

    for name, config in EXPERIMENTS.items():

        if name in existing_map:
            print(f"📌 Exists: {name} (ID: {existing_map[name]})")
            exp_id = existing_map[name]

        else:
            print(f"🆕 Creating: {name}")

            exp_id = mlflow.create_experiment(
                name=name,
                tags=config["tags"]
            )

            print(f"   ✅ Created with ID: {exp_id}")

        created_experiments[name] = {
            "id": exp_id,
            "name": name,
            "description": config["description"],
            "tags": config["tags"],
        }

    return created_experiments


# -----------------------------
# SAVE METADATA ONLY
# -----------------------------
def save_experiment_metadata(experiments: dict):
    os.makedirs("reports", exist_ok=True)

    output = {
        "timestamp": datetime.now().isoformat(),
        "tracking_uri": MLFLOW_TRACKING_URI,
        "experiments": experiments,
    }

    with open("reports/mlflow_experiments.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\n💾 Saved experiment metadata to reports/mlflow_experiments.json")


# -----------------------------
# MAIN
# -----------------------------
def main():
    print("=" * 70)
    print("🚀 MLflow Experiment Initialization (FAST MODE)")
    print("=" * 70)

    experiments = create_experiments_fast()

    save_experiment_metadata(experiments)

    print("\n" + "=" * 70)
    print("✅ MLflow initialization completed successfully")
    print("⚡ Optimized for remote tracking server (low latency)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()