#!/usr/bin/env python3
"""
MLflow Tracking for Student Performance Service

Tracks model predictions, performance metrics, and risk assessments
for the Student Performance prediction service.
"""

import mlflow
import os
import json
import numpy as np
from datetime import datetime
import sys

# Add service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'Student Perfromance Service'))

# Configure MLflow
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "file:///tmp/mlflow"))

def generate_test_data():
    """Generate sample test data for student performance prediction."""
    
    test_cases = [
        {
            "cumulative_gpa": 3.5,
            "semester_gpas": [3.2, 3.3, 3.4, 3.5],
            "fail_withdrawal_count": 0,
            "domain_gpas": {"MATH": 3.6, "CS": 3.4},
            "expected_trajectory": "Improving",
            "expected_risk": "Low"
        },
        {
            "cumulative_gpa": 2.8,
            "semester_gpas": [3.5, 3.2, 2.9, 2.8],
            "fail_withdrawal_count": 1,
            "domain_gpas": {"MATH": 2.5, "CS": 3.0},
            "expected_trajectory": "Declining",
            "expected_risk": "Medium"
        },
        {
            "cumulative_gpa": 2.2,
            "semester_gpas": [2.5, 2.3, 2.1, 2.0],
            "fail_withdrawal_count": 2,
            "domain_gpas": {"MATH": 1.8, "CS": 2.1},
            "expected_trajectory": "Declining",
            "expected_risk": "High"
        },
        {
            "cumulative_gpa": 3.0,
            "semester_gpas": [3.0, 3.0, 3.0, 3.0],
            "fail_withdrawal_count": 0,
            "domain_gpas": {"MATH": 3.0, "CS": 3.0},
            "expected_trajectory": "Stable",
            "expected_risk": "Low"
        }
    ]
    
    return test_cases


def track_student_performance():
    """Track student performance model predictions with MLflow."""
    
    print("=" * 70)
    print("📈 Student Performance Service - MLflow Tracking")
    print("=" * 70)
    print()
    
    exp = mlflow.get_experiment_by_name("Student_Performance_Service")

    if exp is None:
        exp_id = mlflow.create_experiment(
            "Student_Performance_Service"
        )
    else:
        exp_id = exp.experiment_id
    


    
    
    exp_id = exp.experiment_id
    
    # Try to import the predictor
    try:
        from app.predictor import predict
        print("✅ Student Performance predictor imported successfully")
    except ImportError as e:
        print(f"⚠️  Could not import predictor: {str(e)}")
        print("   Using mock predictor for demonstration")
        
        def predict(summary_input):
            """Mock predictor for demonstration."""
            sem_gpas = summary_input.get("semester_gpas", [3.0])
            trend = sem_gpas[-1] - sem_gpas[0] if len(sem_gpas) > 1 else 0
            
            return {
                "next_semester_gpa": round(sem_gpas[-1] + np.random.uniform(-0.2, 0.2), 2),
                "predicted_graduation_gpa": round(np.mean(sem_gpas) + 0.1, 2),
                "trajectory": "Improving" if trend > 0.2 else "Declining" if trend < -0.2 else "Stable",
                "risk_level": "Low" if np.mean(sem_gpas) > 3.0 else "Medium" if np.mean(sem_gpas) > 2.5 else "High",
                "risk_score": round(max(0, min(1, (3.0 - np.mean(sem_gpas)) * 0.3)), 2)
            }
    
    test_cases = generate_test_data()
    
    with mlflow.start_run(experiment_id=exp_id, run_name="student_performance_eval") as run:
        
        # Log experiment metadata
        mlflow.log_param("test_cases_count", len(test_cases))
        mlflow.log_param("model_type", "regression_with_risk_assessment")
        mlflow.log_param("prediction_targets", "next_semester_gpa,trajectory,risk_level")
        mlflow.log_param("git_commit", os.getenv("GITHUB_SHA", "N/A"))
        
        # Track predictions
        predictions = []
        trajectory_matches = 0
        risk_matches = 0
        trajectory_accuracy = 0.0
        risk_accuracy = 0.0
        
        for i, test_case in enumerate(test_cases):
            try:
                # Make prediction
                prediction = predict(test_case)
                predictions.append({
                    "test_case": i + 1,
                    "input": test_case,
                    "prediction": prediction
                })
                
                # Calculate accuracy
                if prediction["trajectory"] == test_case["expected_trajectory"]:
                    trajectory_matches += 1
                
                if prediction["risk_level"] == test_case["expected_risk"]:
                    risk_matches += 1
                
                print(f"  ✅ Test case {i+1}:")
                print(f"     GPA Trend: {test_case['cumulative_gpa']}")
                print(f"     Predicted Trajectory: {prediction['trajectory']}")
                print(f"     Predicted Risk Level: {prediction['risk_level']}")
                print(f"     Risk Score: {prediction['risk_score']}")
                print()
                
            except Exception as e:
                print(f"  ❌ Error predicting test case {i+1}: {str(e)}")
        
        # Calculate metrics
        if len(test_cases) > 0:
            trajectory_accuracy = trajectory_matches / len(test_cases)
            risk_accuracy = risk_matches / len(test_cases)
        
        # Log metrics
        mlflow.log_metric("trajectory_accuracy", trajectory_accuracy)
        mlflow.log_metric("risk_assessment_accuracy", risk_accuracy)
        mlflow.log_metric("avg_accuracy", (trajectory_accuracy + risk_accuracy) / 2)
        mlflow.log_metric("test_cases_passed", trajectory_matches + risk_matches)
        mlflow.log_metric("total_tests", len(test_cases) * 2)
        
        # Log metrics by category
        mlflow.log_metric("trajectory_predictions", trajectory_matches)
        mlflow.log_metric("risk_predictions", risk_matches)
        
        # Save predictions to artifact
        os.makedirs("reports/student_performance", exist_ok=True)
        predictions_file = "reports/student_performance/predictions.json"
        
        with open(predictions_file, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "run_id": run.info.run_id,
                "predictions": predictions,
                "metrics": {
                    "trajectory_accuracy": float(trajectory_accuracy),
                    "risk_accuracy": float(risk_accuracy),
                    "avg_accuracy": float((trajectory_accuracy + risk_accuracy) / 2)
                }
            }, f, indent=2)
        
        mlflow.log_artifact(predictions_file, "predictions")
        
        print("=" * 70)
        print("📊 Tracking Summary:")
        print(f"   Run ID: {run.info.run_id}")
        print(f"   Trajectory Accuracy: {trajectory_accuracy:.2%}")
        print(f"   Risk Assessment Accuracy: {risk_accuracy:.2%}")
        print(f"   Overall Accuracy: {(trajectory_accuracy + risk_accuracy) / 2:.2%}")
        print("=" * 70)
        
        return True


def main():
    """Main tracking function."""
    
    try:
        success = track_student_performance()
        if success:
            print("\n✅ Student Performance tracking completed successfully!")
            return 0
        else:
            print("\n⚠️  Student Performance tracking completed with warnings")
            return 0
    except Exception as e:
        print(f"\n❌ Error during tracking: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
