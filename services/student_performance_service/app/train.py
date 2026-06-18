#!/usr/bin/env python3
"""
MLflow Training for Student Performance Service
"""

import json
import os
import sys
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import shutil
import subprocess
try:
    import dvc.api
    DVC_AVAILABLE = True
except Exception:
    DVC_AVAILABLE = False
DVC_CLI_AVAILABLE = shutil.which("dvc") is not None
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parent

def find_repo_root(start_dir: Path) -> Path:
    candidates = []
    for parent in [start_dir, *start_dir.parents]:
        candidates.append(parent)

    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if parent not in candidates:
            candidates.append(parent)

    for parent in candidates:
        if (parent / "data" / "transcripts.json").exists() or (parent / "data" / "transcripts.json.dvc").exists():
            return parent

    return cwd if (cwd / "data").exists() else start_dir.parents[2]

REPO_ROOT = find_repo_root(BASE_DIR)
TRANSCRIPTS_PATH = REPO_ROOT / "data" / "transcripts.json"

MLFLOW_URI = os.environ.get("MLFLOW_TRACKING_URI")
mlflow.set_tracking_uri(MLFLOW_URI)

EXPERIMENT_NAME = "Student_Performance_Service"
mlflow.set_experiment(EXPERIMENT_NAME)

ESTIMATORS = 200
MAX_DEPTH = 6
TEST_SIZE = 0.2
RANDOM_STATE = 42

GRADE_POINTS = {
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "C-": 1.7,

    "F": 0.0,
    "W": 0.0,
}

MODEL_DIR = BASE_DIR.parent / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_FILE = MODEL_DIR / "student_performance.pkl"


def grade_to_points(grade):
    return GRADE_POINTS.get(grade.upper(), 0.0)


def summarize_terms(terms):
    term_gpas = [term["term_statistics"]["term_gpa"] for term in terms]
    cumulative_gpa = terms[-1]["running_totals"]["cumulative_gpa"]
    total_credits_completed = sum(term["term_statistics"].get("earned_credits", 0) for term in terms)
    total_credits_attempted = sum(term["term_statistics"].get("attempted_credits", 0) for term in terms)

    fail_withdrawal_count = 0
    domain_points = {"MATH": [], "CS": []}

    for term in terms:
        for course in term.get("courses", []):
            grade = course.get("grade", "")
            grade_point = grade_to_points(grade)
            if grade.upper() in {"F", "W"}:
                fail_withdrawal_count += 1

            course_id = course.get("course_id", "").upper()
            if course_id.startswith("MATH"):
                domain_points["MATH"].append(grade_point)
            elif course_id.startswith("CS"):
                domain_points["CS"].append(grade_point)

    domain_gpas = {}
    for domain, points in domain_points.items():
        domain_gpas[domain] = float(np.mean(points)) if points else 3.0

    return {
        "semester_gpas": term_gpas,
        "cumulative_gpa": float(cumulative_gpa),
        "total_credits_completed": int(total_credits_completed),
        "total_credits_attempted": int(total_credits_attempted),
        "fail_withdrawal_count": int(fail_withdrawal_count),
        "domain_gpas": domain_gpas,
    }


def extract_summary_features(summary):
    sem_gpas = summary["semester_gpas"]

    avg_gpa = np.mean(sem_gpas)
    gpa_slope = sem_gpas[-1] - sem_gpas[0] if len(sem_gpas) > 1 else 0.0
    last_gpa = sem_gpas[-1]
    volatility = np.std(sem_gpas)
    credit_eff = summary["total_credits_completed"] / max(summary["total_credits_attempted"], 1)
    weakest_domain = min(summary["domain_gpas"].values())

    return np.array([
        avg_gpa,
        gpa_slope,
        last_gpa,
        volatility,
        credit_eff,
        summary["fail_withdrawal_count"],
        weakest_domain,
    ])


def build_training_dataset(transcripts):
    X = []
    y = []

    for record in transcripts:
        semesters = record.get("semesters", [])
        if len(semesters) < 2:
            continue

        for split_index in range(1, len(semesters)):
            summary_terms = semesters[:split_index]
            target_term = semesters[split_index]
            try:
                summary = summarize_terms(summary_terms)
                y.append(float(target_term["term_statistics"]["term_gpa"]))
                X.append(extract_summary_features(summary))
                
                # print(len(X), len(y))
            except Exception as e:
                continue

    if not X:
        raise RuntimeError("No training examples were generated from transcripts data.")

    return np.vstack(X), np.array(y, dtype=float)


def main():
    print(f"Using MLflow tracking URI: {MLFLOW_URI}")
    print(f"Loading transcripts from {TRANSCRIPTS_PATH}")

    transcripts_path = TRANSCRIPTS_PATH
    if transcripts_path.exists():
        with open(transcripts_path, "r", encoding="utf-8") as f:
            transcripts = json.load(f)
    else:
        dvc_file = transcripts_path.with_name(f"{transcripts_path.name}.dvc")
        if dvc_file.exists():
            if DVC_AVAILABLE:
                print(f"Transcript file missing, attempting DVC load from {dvc_file}")
                try:
                    with dvc.api.open(str(transcripts_path.relative_to(REPO_ROOT)), repo=str(REPO_ROOT)) as f:
                        transcripts = json.load(f)
                except Exception as e:
                    raise FileNotFoundError(
                        f"Transcript data not found at {transcripts_path}. DVC file exists but could not load it: {e}"
                    ) from e
            elif DVC_CLI_AVAILABLE:
                print(f"Transcript file missing, attempting DVC CLI pull for {dvc_file}")
                try:
                    subprocess.run(
                        ["dvc", "pull", str(dvc_file)],
                        cwd=str(REPO_ROOT),
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                except subprocess.CalledProcessError as e:
                    raise FileNotFoundError(
                        f"Transcript data not found at {transcripts_path}. DVC CLI failed: {e.stderr or e.stdout}"
                    ) from e

                if transcripts_path.exists():
                    with open(transcripts_path, "r", encoding="utf-8") as f:
                        transcripts = json.load(f)
                else:
                    raise FileNotFoundError(
                        f"Transcript data still missing at {transcripts_path} after DVC pull."
                    )
            else:
                raise FileNotFoundError(
                    f"Transcript data not found at {transcripts_path}. DVC metadata exists at {dvc_file}, "
                    f"but neither dvc.api nor dvc CLI is available in the environment."
                )
        else:
            raise FileNotFoundError(
                f"Transcript data not found at {transcripts_path}."
                f" Ensure data/transcripts.json is present or run `dvc pull {dvc_file}` if using DVC."
            )

    X, y = build_training_dataset(transcripts)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    model = RandomForestRegressor(n_estimators=ESTIMATORS, max_depth=MAX_DEPTH, random_state=RANDOM_STATE)

    with mlflow.start_run(run_name="student_performance_eval") as run:
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        mlflow.log_param("n_estimators", ESTIMATORS)
        mlflow.log_param("max_depth", MAX_DEPTH)
        mlflow.log_param("test_size", TEST_SIZE)
        mlflow.log_param("train_samples", int(X_train.shape[0]))
        mlflow.log_param("test_samples", int(X_test.shape[0]))
        mlflow.log_param("data_source", str(TRANSCRIPTS_PATH))

        mlflow.log_metric("MAE", float(mae))
        mlflow.log_metric("RMSE", float(rmse))

        mlflow.sklearn.log_model(model, "student_performance_model")

        print("Training completed")
        print(f"Train samples: {X_train.shape[0]}")
        print(f"Test samples: {X_test.shape[0]}")
        print(f"MAE: {mae:.4f}")
        print(f"RMSE: {rmse:.4f}")

        joblib.dump(model, MODEL_FILE)
        mlflow.log_artifact(str(MODEL_FILE), artifact_path="model")

        print(f"Saved model to {MODEL_FILE}")
        print(f"MLflow run id: {run.info.run_id}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
