# MLflow Model Tracking Integration

## Overview

This GitHub Actions workflow provides comprehensive model performance tracking for all Odoo Educational ERP System microservices using MLflow. It automatically:

- ✅ Initializes MLflow experiment structure
- ✅ Tracks Student Performance predictions and risk assessments
- ✅ Tracks Grade Predictor classification accuracy
- ✅ Tracks OCR Service extraction performance
- ✅ Generates comprehensive HTML reports and dashboards
- ✅ Archives historical results for trend analysis

## 🚀 Quick Start

### Local Development

1. **Install MLflow locally:**
   ```bash
   pip install mlflow==2.10.2
   ```

2. **Start MLflow UI (optional):**
   ```bash
   mlflow ui --backend-store-uri file:///tmp/mlflow
   ```

3. **Run initialization script:**
   ```bash
   python scripts/mlflow_init_experiments.py
   ```

4. **Track individual services:**
   ```bash
   # Student Performance
   python scripts/mlflow_track_student_performance.py
   
   # Grade Predictor
   python scripts/mlflow_track_grade_predictor.py
   
   # OCR Service
   python scripts/mlflow_track_ocr_service.py
   ```

5. **Generate report:**
   ```bash
   python scripts/mlflow_generate_report.py
   ```

### GitHub Actions Workflow

The workflow is automatically triggered on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Weekly schedule (Sundays at 2 AM UTC)
- Manual trigger via `workflow_dispatch`

## 📊 Experiment Structure

```
Odoo_ERP_Services (Main Experiment)
├── Student_Performance_Service
│   ├── Model Type: Regression with Risk Assessment
│   ├── Tracks: GPA predictions, trajectory, risk scores
│   └── Metrics: trajectory_accuracy, risk_accuracy
│
├── Grade_Predictor_Service
│   ├── Model Type: Logistic Regression Classification
│   ├── Tracks: Grade predictions, confidence scores
│   └── Metrics: prediction_accuracy, avg_confidence
│
├── OCR_Service
│   ├── Model Type: Document Detection & Text Extraction
│   ├── Tracks: Extraction accuracy, detection time
│   └── Metrics: extraction_accuracy, extraction_time_ms
│
└── System_Integration
    ├── Cross-service integration tests
    └── Pipeline health metrics
```

## 📋 Key Metrics Tracked

### Student Performance Service
- **trajectory_accuracy**: Accuracy of trend prediction (Improving/Stable/Declining)
- **risk_assessment_accuracy**: Accuracy of risk level prediction
- **avg_accuracy**: Combined accuracy metric
- Test cases: 4 scenarios with varying GPA trends

### Grade Predictor Service
- **prediction_accuracy**: Accuracy of grade classification
- **avg_confidence**: Average confidence in predictions
- **correct_predictions**: Number of correct predictions
- Test cases: 3 scenarios with different course metrics

### OCR Service
- **overall_extraction_accuracy**: Average text extraction accuracy
- **avg_extraction_time_ms**: Average extraction time
- **success_rate**: Percentage of high-accuracy extractions (>80%)
- **metrics_by_type**: Accuracy per document type
- **metrics_by_language**: Accuracy per language (Arabic, English)
- Test scenarios: 5 document types across 2 languages

## 📁 Generated Artifacts

### GitHub Actions Artifacts

1. **mlflow-tracking-db**
   - SQLite database with all tracked experiments
   - Retained for 90 days

2. **mlflow-report**
   - `mlflow_report.html`: Interactive HTML dashboard
   - `mlflow_metrics_summary.json`: Machine-readable metrics

3. **Service Results**
   - `student-perf-results`: Student performance service metrics
   - `grade-predictor-results`: Grade predictor metrics
   - `ocr-service-results`: OCR service metrics

4. **model-results-archive**
   - Compressed archive of all run results
   - Retained for 365 days for historical analysis

### Local Artifacts

When running locally, artifacts are saved in:
- `reports/student_performance/predictions.json`
- `reports/grade_predictor/predictions.json`
- `reports/ocr_service/extraction_results.json`
- `mlflow_report.html`
- `mlflow_metrics_summary.json`

## 🔧 Configuration

### Environment Variables

```bash
# MLflow tracking URI (default: file:///tmp/mlflow)
MLFLOW_TRACKING_URI=file:///tmp/mlflow

# Experiment name (default: Odoo_ERP_Services)
MLFLOW_EXPERIMENT_NAME=Odoo_ERP_Services

# GitHub Actions specific
GITHUB_SHA=<commit-hash>
GITHUB_REF=<branch-name>
GITHUB_RUN_ID=<workflow-run-id>
GITHUB_RUN_NUMBER=<run-number>
```

### Remote MLflow Server (Optional)

To use a remote MLflow server (e.g., Databricks, custom server):

1. Add GitHub secrets:
   - `MLFLOW_TRACKING_URI`: Remote server URI
   - `MLFLOW_TRACKING_TOKEN`: Authentication token (if needed)

2. Update workflow to use secrets:
   ```yaml
   env:
     MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
     MLFLOW_TRACKING_TOKEN: ${{ secrets.MLFLOW_TRACKING_TOKEN }}
   ```

## 📈 Monitoring & Analysis

### Local MLflow UI

```bash
mlflow ui --backend-store-uri file:///tmp/mlflow
```

Open `http://localhost:5000` to view:
- Experiment comparison
- Run details and metrics
- Artifact history
- Performance trends

### GitHub Artifacts

1. Download `mlflow-report` artifact
2. Open `mlflow_report.html` in browser
3. View service metrics and performance summaries

### Metrics Analysis

```python
import json

with open("mlflow_metrics_summary.json") as f:
    metrics = json.load(f)

# Analyze student performance
student_perf = metrics["services"]["Student_Performance_Service"]
print(f"Trajectory Accuracy: {student_perf['metrics']['trajectory_accuracy']:.2%}")
print(f"Risk Assessment Accuracy: {student_perf['metrics']['risk_assessment_accuracy']:.2%}")
```

## 🔄 CI/CD Integration

### Trigger Conditions

```yaml
on:
  push:
    branches: [main, develop]
    paths:
      - "services/**"
      - "tests/**"
      - ".github/workflows/mlflow-model-tracking.yml"
      - "scripts/mlflow_*.py"
  
  pull_request:
    branches: [main, develop]
  
  schedule:
    - cron: "0 2 * * 0"  # Weekly
  
  workflow_dispatch:  # Manual trigger
```

### Status Checks

The workflow reports:
- ✅ MLflow initialization
- ✅ Student Performance tracking
- ✅ Grade Predictor tracking
- ✅ OCR Service tracking
- ✅ Report generation
- ✅ Results archival

## 📝 Scripts Reference

### `mlflow_init_experiments.py`
Initializes MLflow experiment structure and creates experiment runs.

**Usage:**
```bash
python scripts/mlflow_init_experiments.py
```

**Output:**
- Creates 4 experiments (Student Performance, Grade Predictor, OCR, System Integration)
- Initializes global tracking run
- Saves experiment metadata to `reports/mlflow_experiments.json`

### `mlflow_track_student_performance.py`
Tracks student performance model predictions and metrics.

**Usage:**
```bash
python scripts/mlflow_track_student_performance.py
```

**Test Cases:**
- High GPA trend (Improving trajectory, Low risk)
- Declining GPA trend (Declining trajectory, Medium risk)
- Critical GPA trend (Declining trajectory, High risk)
- Stable GPA trend (Stable trajectory, Low risk)

### `mlflow_track_grade_predictor.py`
Tracks grade prediction accuracy and confidence.

**Usage:**
```bash
python scripts/mlflow_track_grade_predictor.py
```

**Test Cases:**
- High performance student (CS101, expecting A)
- Struggling student (MATH201, expecting B)
- Good performer (ENG102, expecting A-)

### `mlflow_track_ocr_service.py`
Tracks OCR extraction accuracy and performance.

**Usage:**
```bash
python scripts/mlflow_track_ocr_service.py
```

**Scenarios:**
- Egyptian National ID (Arabic, high quality)
- Thanawiya Amma transcript (Arabic, medium quality)
- IGCSE Transcript (English, high quality)
- American Transcript (English, medium quality)
- Passport document (English, high quality)

### `mlflow_generate_report.py`
Generates comprehensive HTML report and JSON metrics summary.

**Usage:**
```bash
python scripts/mlflow_generate_report.py
```

**Output:**
- `mlflow_report.html`: Interactive dashboard
- `mlflow_metrics_summary.json`: Structured metrics data

## 🐛 Troubleshooting

### MLflow experiments not found
```bash
# Check if tracking server is accessible
python -c "import mlflow; print(mlflow.get_tracking_uri())"

# List experiments
mlflow experiments list
```

### Permission denied on tracking database
```bash
# Fix permissions
chmod -R 755 /tmp/mlflow
```

### Artifacts not uploading
```bash
# Verify artifacts directory exists
mkdir -p reports/{student_performance,grade_predictor,ocr_service}

# Check MLflow artifacts path
mlflow experiments describe --experiment-name Student_Performance_Service
```

### Workflow timeouts
- Increase timeout in workflow (currently set to 20 minutes per job)
- Check system resources on GitHub Actions runner
- Optimize test data generation

## 📚 Additional Resources

- [MLflow Documentation](https://mlflow.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Odoo Educational ERP System Docs](../Docs/)

## 🤝 Contributing

When adding new services or models:

1. Create corresponding tracking script in `scripts/mlflow_track_<service_name>.py`
2. Add new experiment to `mlflow_init_experiments.py`
3. Add job to `mlflow-model-tracking.yml` workflow
4. Update this documentation

## 📄 License

Copyright © 2026 Odoo Educational ERP System. All Rights Reserved.
