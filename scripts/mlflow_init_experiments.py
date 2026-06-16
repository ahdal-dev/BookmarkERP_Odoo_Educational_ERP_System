#!/usr/bin/env python3
"""
MLflow Experiment Initialization Script

Initializes MLflow experiments and runs for all microservices.
Creates organized experiment structure for tracking model performance.
"""

import mlflow
import os
import json
from datetime import datetime

# Configure MLflow
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "file:///tmp/mlflow"))
experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "Odoo_ERP_Services")

def create_experiment_structure():
    """Create MLflow experiment hierarchy for all services."""
    
    experiments = {
        "Student_Performance_Service": {
            "description": "Student performance prediction and risk assessment",
            "tags": ["model_type:regression", "service:student_performance", "domain:education"],
        },
        "Grade_Predictor_Service": {
            "description": "Grade prediction and classification",
            "tags": ["model_type:classification", "service:grade_predictor", "domain:education"],
        },
        "OCR_Service": {
            "description": "Optical Character Recognition and document extraction",
            "tags": ["model_type:ocr", "service:ocr", "domain:document_processing"],
        },
        "System_Integration": {
            "description": "Cross-service integration tests and performance",
            "tags": ["model_type:integration", "service:system", "domain:integration"],
        },
    }
    
    created_experiments = {}
    
    for exp_name, config in experiments.items():
        try:
            # Check if experiment exists
            exp = mlflow.get_experiment_by_name(exp_name)
            
            if exp is None:
                # Create new experiment
                exp_id = mlflow.create_experiment(
                    name=exp_name,
                    tags=config["tags"]
                )
                exp = mlflow.get_experiment(exp_id)
                print(f"✅ Created experiment: {exp_name} (ID: {exp_id})")
            else:
                print(f"📌 Experiment exists: {exp_name} (ID: {exp.experiment_id})")
            
            created_experiments[exp_name] = {
                "id": exp.experiment_id,
                "name": exp.name,
                "description": config["description"],
                "tags": config["tags"]
            }
            
        except Exception as e:
            print(f"❌ Error creating experiment {exp_name}: {str(e)}")
    
    return created_experiments


def initialize_global_run():
    """Create a global run to track overall pipeline execution."""
    
    exp_id = mlflow.get_experiment_by_name("System_Integration").experiment_id
    
    with mlflow.start_run(experiment_id=exp_id, run_name="Pipeline_Initialization") as run:
        mlflow.log_param("pipeline_name", "MLflow Model Tracking")
        mlflow.log_param("git_commit", os.getenv("GITHUB_SHA", "N/A"))
        mlflow.log_param("git_branch", os.getenv("GITHUB_REF", "N/A"))
        mlflow.log_param("run_id", os.getenv("GITHUB_RUN_ID", "N/A"))
        mlflow.log_param("workflow", "mlflow-model-tracking")
        
        mlflow.log_metric("pipeline_start_timestamp", datetime.now().timestamp())
        
        print(f"✅ Global run initialized: {run.info.run_id}")


def create_tags_file(experiments):
    """Create a JSON file with experiment tags for reference."""
    
    os.makedirs("reports", exist_ok=True)
    
    output = {
        "timestamp": datetime.now().isoformat(),
        "experiments": experiments
    }
    
    with open("reports/mlflow_experiments.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Experiment tags saved to reports/mlflow_experiments.json")


def main():
    """Main initialization function."""
    
    print("=" * 70)
    print("🔧 MLflow Experiment Initialization")
    print("=" * 70)
    print()
    
    # Create experiment structure
    experiments = create_experiment_structure()
    print()
    
    # Initialize global tracking run
    initialize_global_run()
    print()
    
    # Save tags reference
    create_tags_file(experiments)
    print()
    
    print("=" * 70)
    print("✅ MLflow initialization complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
