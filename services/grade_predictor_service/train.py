#!/usr/bin/env python3
"""
MLflow Tracking for Grade Predictor Service
"""

import json
import os
import sys
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

MLFLOW_URI = os.environ["MLFLOW_TRACKING_URI"]
mlflow.set_tracking_uri(MLFLOW_URI)

EXPERIMENT_NAME = "Grade_Predictor_Service"
mlflow.set_experiment(EXPERIMENT_NAME)


def get_model_bundle():
    model_path = Path(__file__).resolve().parent / "models" / "gpa_predictor.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    bundle = joblib.load(model_path)
    if not isinstance(bundle, dict) or "model" not in bundle or "features" not in bundle:
        raise ValueError(f"Invalid model bundle loaded from {model_path}")

    return bundle, model_path


def generate_test_data():
    return [
        {
            "gender": "Male",
            "persona": "solid_b",
            "program": "Software Development",
            "entry_year": 2023,
            "is_transfer": 0,
            "semester_number": 3,
            "cumgpa_before": 2.9,
            "last_term_gpa": 2.7,
            "avg_gpa_so_far": 2.85,
            "min_gpa": 2.5,
            "max_gpa": 3.2,
            "gpa_std": 0.25,
            "gpa_trend": -0.1,
            "recent_trend": 0.1,
            "terms_below_2": 0,
            "terms_below_25": 1,
            "is_recovering": 1,
            "credits_so_far": 51,
            "withdrawals_so_far": 0,
            "failures_so_far": 0,
            "pct_A_grades": 0.15,
            "pct_B_plus_grades": 0.55,
            "pct_below_C_grades": 0.0,
            "pct_retakes": 0.0,
            "pct_lab_courses": 0.2,
            "avg_grade_pts": 2.9,
            "quality_pts_total": 420.0,
            "summer_taken": 0,
            "next_season": 1,
            "expected_gpa": 2.95,
        },
        {
            "gender": "Female",
            "persona": "adult_learners",
            "program": "Business",
            "entry_year": 2021,
            "is_transfer": 1,
            "semester_number": 5,
            "cumgpa_before": 3.3,
            "last_term_gpa": 3.4,
            "avg_gpa_so_far": 3.35,
            "min_gpa": 2.8,
            "max_gpa": 3.8,
            "gpa_std": 0.22,
            "gpa_trend": 0.05,
            "recent_trend": 0.1,
            "terms_below_2": 0,
            "terms_below_25": 0,
            "is_recovering": 0,
            "credits_so_far": 90,
            "withdrawals_so_far": 0,
            "failures_so_far": 0,
            "pct_A_grades": 0.45,
            "pct_B_plus_grades": 0.35,
            "pct_below_C_grades": 0.05,
            "pct_retakes": 0.02,
            "pct_lab_courses": 0.15,
            "avg_grade_pts": 3.3,
            "quality_pts_total": 297.0,
            "summer_taken": 1,
            "next_season": 2,
            "expected_gpa": 3.4,
        },
        {
            "gender": "Female",
            "persona": "traditional",
            "program": "CS",
            "entry_year": 2022,
            "is_transfer": 0,
            "semester_number": 4,
            "cumgpa_before": 3.6,
            "last_term_gpa": 3.8,
            "avg_gpa_so_far": 3.65,
            "min_gpa": 3.2,
            "max_gpa": 4.0,
            "gpa_std": 0.18,
            "gpa_trend": 0.12,
            "recent_trend": 0.15,
            "terms_below_2": 0,
            "terms_below_25": 0,
            "is_recovering": 0,
            "credits_so_far": 72,
            "withdrawals_so_far": 0,
            "failures_so_far": 0,
            "pct_A_grades": 0.55,
            "pct_B_plus_grades": 0.30,
            "pct_below_C_grades": 0.0,
            "pct_retakes": 0.01,
            "pct_lab_courses": 0.4,
            "avg_grade_pts": 3.7,
            "quality_pts_total": 266.4,
            "summer_taken": 0,
            "next_season": 1,
            "expected_gpa": 3.75,
        },
    ]


def safe_transform_label(encoder, label, fallback=0):
    try:
        return encoder.transform([label])[0]
    except ValueError:
        return fallback


def prepare_features(bundle, sample):
    encoders = bundle["encoders"]
    sample["gender_enc"] = safe_transform_label(encoders["gender"], sample["gender"], fallback=0)
    sample["persona_enc"] = safe_transform_label(encoders["persona"], sample["persona"], fallback=0)
    sample["program_target_enc"] = encoders["program_mean_gpa"].get(sample["program"], 2.887)
    sample["persona_target_enc"] = encoders["persona_mean_gpa"].get(sample["persona"], 2.887)

    features = {key: sample[key] for key in bundle["features"] if key in sample}
    return pd.DataFrame([features])


def track_grade_predictor():
    print("=" * 70)
    print("🎓 Grade Predictor MLflow Tracking")
    print("=" * 70)

    bundle, model_path = get_model_bundle()
    model = bundle["model"]

    test_cases = generate_test_data()
    y_true = []
    y_pred = []
    predictions = []

    with mlflow.start_run(run_name="grade_predictor_eval") as run:
        mlflow.log_param("test_cases", len(test_cases))
        mlflow.log_param("model_name", bundle.get("name", "gpa_predictor"))
        mlflow.log_param("model_saved_at", bundle.get("saved_at", "N/A"))
        mlflow.log_param("model_path", str(model_path))
        mlflow.log_param("git_commit", os.getenv("GITHUB_SHA", "N/A"))

        for sample in test_cases:
            expected_gpa = float(sample["expected_gpa"])
            row = prepare_features(bundle, sample.copy())
            predicted_gpa = float(np.clip(model.predict(row)[0], 0.0, 4.0))

            y_true.append(expected_gpa)
            y_pred.append(predicted_gpa)

            status = "AT RISK" if predicted_gpa < 2.0 else "Safe"
            predictions.append({
                "input": sample,
                "predicted_gpa": predicted_gpa,
                "status": status,
            })

            print(f"{sample['program']} / {sample['persona']} → {predicted_gpa:.3f} ({status})")

        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))

        mlflow.log_param("feature_count", len(bundle["features"]))
        mlflow.log_metric("MAE", float(mae))
        mlflow.log_metric("RMSE", float(rmse))

        mlflow.sklearn.log_model(model, "gpa_predictor_model")
        mlflow.log_artifact(str(model_path), artifact_path="model")

        os.makedirs("reports/grade_predictor", exist_ok=True)
        out = Path("reports/grade_predictor") / "results.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump({
                "run_id": run.info.run_id,
                "metrics": {
                    "MAE": mae,
                    "RMSE": rmse,
                },
                "predictions": predictions,
            }, f, indent=2)

        mlflow.log_artifact(str(out))

        print("\n" + "=" * 70)
        print(f"Run ID: {run.info.run_id}")
        print(f"MAE: {mae:.4f}")
        print(f"RMSE: {rmse:.4f}")
        print("=" * 70)

        return True


def main():
    try:
        return 0 if track_grade_predictor() else 1
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())