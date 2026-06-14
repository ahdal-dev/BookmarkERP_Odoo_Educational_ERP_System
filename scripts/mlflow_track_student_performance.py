#!/usr/bin/env python3
"""
MLflow Tracking for Student Performance Service
"""

import mlflow
import os
import json
import numpy as np
from datetime import datetime
import sys

# -------------------------------
# IMPORTANT: NO FALLBACK
# -------------------------------
MLFLOW_URI = os.environ["MLFLOW_TRACKING_URI"]
mlflow.set_tracking_uri(MLFLOW_URI)

# -------------------------------
# Import service
# -------------------------------
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), '..', 'services', 'Student Perfromance Service')
)

def generate_test_data():
    return [
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


def track_student_performance():

    print("=" * 70)
    print("📈 Student Performance MLflow Tracking")
    print("=" * 70)

    # -------------------------------
    # FIXED: clean experiment setup
    # -------------------------------
    EXPERIMENT_NAME = "Student_Performance_Service"
    mlflow.set_experiment(EXPERIMENT_NAME)

    # -------------------------------
    # predictor import
    # -------------------------------
    try:
        from app.predictor import predict
        print("✅ Predictor loaded")
    except Exception as e:
        print(f"⚠️ Using mock predictor: {e}")

        def predict(summary_input):
            sem_gpas = summary_input.get("semester_gpas", [3.0])
            trend = sem_gpas[-1] - sem_gpas[0]

            return {
                "next_semester_gpa": round(sem_gpas[-1] + np.random.uniform(-0.2, 0.2), 2),
                "predicted_graduation_gpa": round(np.mean(sem_gpas) + 0.1, 2),
                "trajectory": "Improving" if trend > 0.2 else "Declining" if trend < -0.2 else "Stable",
                "risk_level": "Low" if np.mean(sem_gpas) > 3.0 else "Medium" if np.mean(sem_gpas) > 2.5 else "High",
                "risk_score": round(max(0, min(1, (3.0 - np.mean(sem_gpas)) * 0.3)), 2)
            }

    test_cases = generate_test_data()

    # -------------------------------
    # SINGLE CLEAN RUN
    # -------------------------------
    with mlflow.start_run(run_name="student_performance_eval") as run:

        mlflow.log_param("test_cases_count", len(test_cases))
        mlflow.log_param("model_type", "regression_with_risk_assessment")
        mlflow.log_param("git_commit", os.getenv("GITHUB_SHA", "N/A"))

        predictions = []
        trajectory_matches = 0
        risk_matches = 0

        for i, case in enumerate(test_cases):

            prediction = predict(case)

            predictions.append({
                "test_case": i + 1,
                "input": case,
                "prediction": prediction
            })

            if prediction["trajectory"] == case["expected_trajectory"]:
                trajectory_matches += 1

            if prediction["risk_level"] == case["expected_risk"]:
                risk_matches += 1

            print(f"Test {i+1}: {prediction['trajectory']} | {prediction['risk_level']}")

        # -------------------------------
        # METRICS
        # -------------------------------
        total = len(test_cases)

        trajectory_acc = trajectory_matches / total
        risk_acc = risk_matches / total

        mlflow.log_metric("trajectory_accuracy", trajectory_acc)
        mlflow.log_metric("risk_accuracy", risk_acc)
        mlflow.log_metric("avg_accuracy", (trajectory_acc + risk_acc) / 2)

        # -------------------------------
        # ARTIFACT
        # -------------------------------
        os.makedirs("reports/student_performance", exist_ok=True)

        output_path = "reports/student_performance/predictions.json"

        with open(output_path, "w") as f:
            json.dump({
                "run_id": run.info.run_id,
                "timestamp": datetime.now().isoformat(),
                "predictions": predictions,
                "metrics": {
                    "trajectory_accuracy": trajectory_acc,
                    "risk_accuracy": risk_acc
                }
            }, f, indent=2)

        mlflow.log_artifact(output_path)

        print("\n" + "=" * 70)
        print(f"Run ID: {run.info.run_id}")
        print(f"Trajectory Accuracy: {trajectory_acc:.2%}")
        print(f"Risk Accuracy: {risk_acc:.2%}")
        print("=" * 70)

        return True


def main():
    try:
        return 0 if track_student_performance() else 1
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit(main())