#!/usr/bin/env python3
"""
MLflow Tracking for Grade Predictor Service (Fixed)
"""

import mlflow
import os
import json
import numpy as np
from datetime import datetime
from pathlib import Path

import sys

# ==================================================
# MUST FAIL FAST if secret is missing
# ==================================================
MLFLOW_URI = os.environ["MLFLOW_TRACKING_URI"]
mlflow.set_tracking_uri(MLFLOW_URI)


def generate_test_data():

    return [
        {
            "course_id": "CS101",
            "coursework": 95.0,
            "quiz_average": 92.0,
            "project_score": 95.0,
            "gpa_current": 3.8,
            "expected_grade": "A"
        },
        {
            "course_id": "MATH201",
            "coursework": 75.0,
            "quiz_average": 72.0,
            "project_score": 78.0,
            "gpa_current": 3.0,
            "expected_grade": "B"
        },
        {
            "course_id": "ENG102",
            "coursework": 85.0,
            "quiz_average": 88.0,
            "project_score": 85.0,
            "gpa_current": 3.5,
            "expected_grade": "A-"
        }
    ]


def mock_predict(x):

    composite = (
        x["coursework"] * 0.3 +
        x["quiz_average"] * 0.2 +
        x["project_score"] * 0.3 +
        x["gpa_current"] * 100 * 0.2
    ) / 100

    if composite >= 90: g = "A"
    elif composite >= 85: g = "A-"
    elif composite >= 80: g = "B"
    elif composite >= 75: g = "B+"
    elif composite >= 70: g = "B-"
    elif composite >= 65: g = "C"
    elif composite >= 60: g = "C+"
    elif composite >= 55: g = "C-"
    else: g = "F"

    return {
        "predicted_grade": g,
        "confidence": min(0.99, abs(composite - 75) / 100 + 0.5)
    }


def track_grade_predictor():

    print("=" * 70)
    print("🎓 Grade Predictor MLflow Tracking (Fixed)")
    print("=" * 70)

    # ==================================================
    # CLEAN EXPERIMENT (NO EXP ID)
    # ==================================================
    mlflow.set_experiment("Grade_Predictor_Service")

    # ==================================================
    # MODEL LOADING (FIXED)
    # ==================================================
    model = None
    use_model = False

    model_path = (
        Path(__file__).resolve().parent /
        "services" /
        "grade_predictor_service" /
        "models" /
        "gpa_predictor.pkl"
    )

    try:
        import joblib
        if model_path.exists():
            model = joblib.load(model_path)
            use_model = True
            print("✅ Real model loaded")
        else:
            print("⚠️ Model not found → using mock")
    except Exception as e:
        print(f"⚠️ Model load failed: {e}")

    test_cases = generate_test_data()

    with mlflow.start_run(run_name="grade_predictor_eval") as run:

        mlflow.log_param("test_cases", len(test_cases))
        mlflow.log_param("model_used", "real" if use_model else "mock")
        mlflow.log_param("git_commit", os.getenv("GITHUB_SHA", "N/A"))

        predictions = []
        correct = 0
        confidence_sum = 0

        for i, tc in enumerate(test_cases):

            if use_model:
                import pandas as pd
                pred_id = model.predict(pd.DataFrame([tc]))[0]

                grade_map = {
                    0: "A", 1: "A-", 2: "B", 3: "B+",
                    4: "B-", 5: "C", 6: "C+",
                    7: "C-", 8: "F"
                }

                result = {
                    "predicted_grade": grade_map.get(pred_id, "Unknown"),
                    "confidence": 0.85
                }
            else:
                result = mock_predict(tc)

            predictions.append({
                "input": tc,
                "prediction": result
            })

            if result["predicted_grade"] == tc["expected_grade"]:
                correct += 1

            confidence_sum += result["confidence"]

            print(f"{tc['course_id']} → {result['predicted_grade']}")

        # ==================================================
        # METRICS
        # ==================================================
        acc = correct / len(test_cases)
        avg_conf = confidence_sum / len(test_cases)

        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("avg_confidence", avg_conf)

        # ==================================================
        # ARTIFACT
        # ==================================================
        os.makedirs("reports/grade_predictor", exist_ok=True)

        out = "reports/grade_predictor/results.json"

        with open(out, "w") as f:
            json.dump({
                "run_id": run.info.run_id,
                "metrics": {
                    "accuracy": acc,
                    "avg_confidence": avg_conf
                },
                "predictions": predictions
            }, f, indent=2)

        mlflow.log_artifact(out)

        print("\n" + "=" * 70)
        print(f"Run ID: {run.info.run_id}")
        print(f"Accuracy: {acc:.2%}")
        print(f"Confidence: {avg_conf:.2%}")
        print("=" * 70)

        return True


def main():
    try:
        return 0 if track_grade_predictor() else 1
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit(main())