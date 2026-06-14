#!/usr/bin/env python3
"""
MLflow Tracking for OCR Service (Fixed Version)
"""

import mlflow
import os
import json
import numpy as np
from datetime import datetime

# ==================================================
# IMPORTANT: NO FALLBACK (prevents silent local logs)
# ==================================================
MLFLOW_URI = os.environ["MLFLOW_TRACKING_URI"]
mlflow.set_tracking_uri(MLFLOW_URI)

def generate_test_scenarios():
    return [
        {
            "name": "Egyptian National ID - Clear",
            "document_type": "national_id",
            "quality": "high",
            "language": "arabic",
            "expected_fields": ["full_name", "national_id", "dob"],
            "simulated_accuracy": 0.95,
            "simulated_extraction_time": 0.5
        },
        {
            "name": "Thanawiya Amma",
            "document_type": "thanawiya_amma",
            "quality": "medium",
            "language": "arabic",
            "expected_fields": ["student_name", "subjects", "total_score"],
            "simulated_accuracy": 0.87,
            "simulated_extraction_time": 1.2
        },
        {
            "name": "IGCSE Transcript",
            "document_type": "ig_transcript",
            "quality": "high",
            "language": "english",
            "expected_fields": ["student_name", "subjects", "grades"],
            "simulated_accuracy": 0.92,
            "simulated_extraction_time": 0.7
        },
        {
            "name": "American Transcript",
            "document_type": "american_transcript",
            "quality": "medium",
            "language": "english",
            "expected_fields": ["student_name", "gpa", "courses"],
            "simulated_accuracy": 0.85,
            "simulated_extraction_time": 0.9
        },
        {
            "name": "Passport",
            "document_type": "passport",
            "quality": "high",
            "language": "english",
            "expected_fields": ["full_name", "passport_number", "expiry"],
            "simulated_accuracy": 0.98,
            "simulated_extraction_time": 0.4
        }
    ]


def simulate_ocr_extraction(scenario):
    acc = scenario["simulated_accuracy"]
    acc = max(0, min(1, acc + np.random.normal(0, 0.02)))

    time_ms = max(100, (scenario["simulated_extraction_time"] + np.random.normal(0, 0.1)) * 1000)

    fields_extracted = int(len(scenario["expected_fields"]) * acc)

    return {
        "accuracy": round(acc, 3),
        "time_ms": round(time_ms, 2),
        "fields_extracted": fields_extracted,
        "total_fields": len(scenario["expected_fields"]),
        "field_accuracy": round(fields_extracted / len(scenario["expected_fields"]), 3)
    }


def track_ocr_service():

    print("=" * 70)
    print("🔍 OCR Service MLflow Tracking (Fixed)")
    print("=" * 70)

    # ==================================================
    # CLEAN EXPERIMENT HANDLING (NO EXP ID LOGIC)
    # ==================================================
    mlflow.set_experiment("OCR_Service")

    scenarios = generate_test_scenarios()

    with mlflow.start_run(run_name="ocr_service_eval") as run:

        mlflow.log_param("scenarios_count", len(scenarios))
        mlflow.log_param("model_stack", "ocr_detection+extraction")
        mlflow.log_param("languages", "arabic,english")
        mlflow.log_param("git_commit", os.getenv("GITHUB_SHA", "N/A"))

        results = []
        total_acc = 0
        total_time = 0
        success = 0

        by_type = {}
        by_lang = {}

        for i, s in enumerate(scenarios):

            r = simulate_ocr_extraction(s)

            results.append({
                "scenario": s["name"],
                "document_type": s["document_type"],
                "language": s["language"],
                "result": r
            })

            total_acc += r["accuracy"]
            total_time += r["time_ms"]

            if r["accuracy"] > 0.8:
                success += 1

            # group by type
            by_type.setdefault(s["document_type"], []).append(r["accuracy"])
            by_lang.setdefault(s["language"], []).append(r["accuracy"])

            print(f"{s['name']} → acc={r['accuracy']:.2%} time={r['time_ms']:.0f}ms")

        n = len(scenarios)

        avg_acc = total_acc / n
        avg_time = total_time / n
        success_rate = success / n

        # ==================================================
        # METRICS (CLEAN + CONSISTENT)
        # ==================================================
        mlflow.log_metric("ocr_accuracy", avg_acc)
        mlflow.log_metric("ocr_latency_ms", avg_time)
        mlflow.log_metric("success_rate", success_rate)

        # per-type metrics
        for k, v in by_type.items():
            mlflow.log_metric(f"acc_{k}", float(np.mean(v)))

        # per-language metrics
        for k, v in by_lang.items():
            mlflow.log_metric(f"acc_{k}", float(np.mean(v)))

        # ==================================================
        # ARTIFACT
        # ==================================================
        os.makedirs("reports/ocr_service", exist_ok=True)

        path = "reports/ocr_service/results.json"

        with open(path, "w") as f:
            json.dump({
                "run_id": run.info.run_id,
                "timestamp": datetime.now().isoformat(),
                "results": results,
                "metrics": {
                    "accuracy": avg_acc,
                    "latency_ms": avg_time,
                    "success_rate": success_rate
                }
            }, f, indent=2)

        mlflow.log_artifact(path)

        print("\n" + "=" * 70)
        print(f"Run ID: {run.info.run_id}")
        print(f"Accuracy: {avg_acc:.2%}")
        print(f"Latency: {avg_time:.1f} ms")
        print(f"Success Rate: {success_rate:.2%}")
        print("=" * 70)

        return True


def main():
    try:
        return 0 if track_ocr_service() else 1
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit(main())