#!/usr/bin/env python3
"""
MLflow Report Generation

Generates comprehensive HTML report and summary from MLflow tracking results.
Creates historical analysis dashboard and model performance trends.
"""

import mlflow
import os
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
MLFLOW_URI = os.environ["MLFLOW_TRACKING_URI"]
# Configure MLflow
mlflow.set_tracking_uri(MLFLOW_URI)

def get_all_experiments():
    """Retrieve all tracked experiments."""
    
    experiments = mlflow.search_experiments()
    return {exp.name: exp for exp in experiments}


def get_experiment_runs(experiment_name):
    """Get all runs for an experiment."""
    
    exp = mlflow.get_experiment_by_name(experiment_name)
    if exp is None:
        return []
    
    runs = mlflow.search_runs(experiment_ids=[exp.experiment_id])
    return runs


def extract_metrics_summary():
    """Extract summary metrics from all experiments."""
    
    experiments = get_all_experiments()
    summary = {}
    
    for exp_name in ["Student_Performance_Service", "Grade_Predictor_Service", "OCR_Service"]:
        if exp_name not in experiments:
            continue
        
        runs = get_experiment_runs(exp_name)
        
        if len(runs) == 0:
            continue
        
        # Get latest run
        latest_run = runs.iloc[-1]
        
        metrics = {}
        if latest_run.data.metrics:
            metrics = latest_run.data.metrics
        
        summary[exp_name] = {
            "run_id": latest_run.run_id,
            "status": latest_run.status,
            "start_time": datetime.fromtimestamp(latest_run.start_time / 1000).isoformat(),
            "metrics": metrics,
            "total_runs": len(runs)
        }
    
    return summary


def generate_html_report(summary):
    """Generate comprehensive HTML report."""
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MLflow Model Tracking Report</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                padding: 20px;
                min-height: 100vh;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                overflow: hidden;
            }
            
            header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }
            
            header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            header p {
                font-size: 1.1em;
                opacity: 0.9;
            }
            
            .content {
                padding: 40px;
            }
            
            .timestamp {
                color: #666;
                font-size: 0.9em;
                margin-bottom: 30px;
                text-align: center;
                border-bottom: 1px solid #eee;
                padding-bottom: 20px;
            }
            
            .section {
                margin-bottom: 40px;
            }
            
            .section h2 {
                color: #667eea;
                font-size: 1.8em;
                margin-bottom: 20px;
                border-left: 4px solid #667eea;
                padding-left: 15px;
            }
            
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
            }
            
            .metric-card h3 {
                font-size: 0.9em;
                opacity: 0.9;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .metric-value {
                font-size: 2em;
                font-weight: bold;
            }
            
            .metric-subtitle {
                font-size: 0.85em;
                opacity: 0.8;
                margin-top: 5px;
            }
            
            .service-section {
                background: #f8f9fa;
                padding: 25px;
                border-radius: 8px;
                margin-bottom: 25px;
                border-left: 4px solid #667eea;
            }
            
            .service-section h3 {
                color: #333;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            
            .service-meta {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 15px;
            }
            
            .meta-item {
                background: white;
                padding: 12px;
                border-radius: 5px;
                font-size: 0.9em;
            }
            
            .meta-label {
                color: #666;
                font-weight: bold;
                margin-bottom: 3px;
            }
            
            .meta-value {
                color: #333;
            }
            
            .metrics-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }
            
            .metrics-table th {
                background: white;
                color: #667eea;
                padding: 12px;
                text-align: left;
                border-bottom: 2px solid #667eea;
                font-weight: 600;
            }
            
            .metrics-table td {
                padding: 12px;
                border-bottom: 1px solid #eee;
            }
            
            .metrics-table tr:hover {
                background: white;
            }
            
            .status-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: bold;
            }
            
            .status-success {
                background: #d4edda;
                color: #155724;
            }
            
            .status-warning {
                background: #fff3cd;
                color: #856404;
            }
            
            .status-error {
                background: #f8d7da;
                color: #721c24;
            }
            
            .footer {
                background: #f8f9fa;
                padding: 20px 40px;
                text-align: center;
                color: #666;
                font-size: 0.9em;
                border-top: 1px solid #eee;
            }
            
            .icon {
                font-size: 1.5em;
                margin-right: 8px;
            }
            
            .summary-box {
                background: #e7f3ff;
                border-left: 4px solid #2196F3;
                padding: 15px;
                border-radius: 4px;
                margin-bottom: 20px;
            }
            
            .summary-box strong {
                color: #1976D2;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>📊 MLflow Model Tracking Report</h1>
                <p>Odoo Educational ERP System - Comprehensive Model Performance Dashboard</p>
            </header>
            
            <div class="content">
                <div class="timestamp">
                    <strong>Report Generated:</strong> """ + datetime.now().isoformat() + """
                </div>
                
                <div class="summary-box">
                    <strong>📋 Summary:</strong> This report contains comprehensive tracking metrics from all MLflow experiments 
                    for the Odoo Educational ERP System microservices. Each service's model performance is tracked and archived 
                    for historical analysis and continuous improvement.
                </div>
    """
    
    # Add service sections
    for service_name, service_data in summary.items():
        service_display_name = service_name.replace("_", " ")
        icon = "📈" if "Performance" in service_name else "🎓" if "Grade" in service_name else "🔍"
        
        html_content += f"""
                <div class="section">
                    <h2>{icon} {service_display_name}</h2>
                    
                    <div class="service-section">
                        <h3>Model Information</h3>
                        <div class="service-meta">
                            <div class="meta-item">
                                <div class="meta-label">Latest Run ID</div>
                                <div class="meta-value"><code>{service_data['run_id']}</code></div>
                            </div>
                            <div class="meta-item">
                                <div class="meta-label">Status</div>
                                <div class="meta-value">
                                    <span class="status-badge status-success">{service_data['status'].upper()}</span>
                                </div>
                            </div>
                            <div class="meta-item">
                                <div class="meta-label">Start Time</div>
                                <div class="meta-value">{service_data['start_time']}</div>
                            </div>
                            <div class="meta-item">
                                <div class="meta-label">Total Runs</div>
                                <div class="meta-value">{service_data['total_runs']}</div>
                            </div>
                        </div>
                        
                        <h4 style="margin-top: 20px; margin-bottom: 10px; color: #333;">Performance Metrics</h4>
                        <table class="metrics-table">
                            <thead>
                                <tr>
                                    <th>Metric</th>
                                    <th>Value</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for metric_name, metric_value in service_data['metrics'].items():
            # Format value
            if isinstance(metric_value, float):
                # Check if it looks like a percentage
                if metric_value <= 1.0 and metric_value >= 0.0:
                    formatted_value = f"{metric_value:.2%}"
                else:
                    formatted_value = f"{metric_value:.3f}"
            else:
                formatted_value = str(metric_value)
            
            html_content += f"""
                                <tr>
                                    <td><strong>{metric_name}</strong></td>
                                    <td>{formatted_value}</td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
        """
    
    # Add footer
    html_content += """
                <div class="section">
                    <h2>📚 Documentation</h2>
                    <div class="service-section">
                        <p>For more information about MLflow and model tracking, visit the official documentation:</p>
                        <ul style="margin-left: 20px; margin-top: 10px;">
                            <li><a href="https://mlflow.org/" target="_blank">MLflow Official Documentation</a></li>
                            <li><a href="https://mlflow.org/docs/latest/tracking.html" target="_blank">MLflow Tracking</a></li>
                            <li><a href="https://mlflow.org/docs/latest/models.html" target="_blank">MLflow Models</a></li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>Generated by GitHub Actions • MLflow Model Tracking Pipeline</p>
                <p>© 2026 Odoo Educational ERP System • All Rights Reserved</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content


def save_metrics_json(summary):
    """Save metrics summary as JSON."""
    
    metrics_data = {
        "timestamp": datetime.now().isoformat(),
        "github_run_id": os.getenv("GITHUB_RUN_ID", "N/A"),
        "github_run_number": os.getenv("GITHUB_RUN_NUMBER", "N/A"),
        "services": summary
    }
    
    with open("mlflow_metrics_summary.json", "w") as f:
        json.dump(metrics_data, f, indent=2, default=str)


def main():
    """Main report generation function."""
    
    print("=" * 70)
    print("📊 Generating MLflow Comprehensive Report")
    print("=" * 70)
    print()
    
    try:
        # Extract metrics
        print("📈 Extracting metrics from experiments...")
        summary = extract_metrics_summary()
        
        if not summary:
            print("⚠️  No tracked experiments found")
            return 1
        
        print(f"✅ Found {len(summary)} services with tracking data")
        print()
        
        # Generate HTML report
        print("📝 Generating HTML report...")
        html_report = generate_html_report(summary)
        
        with open("mlflow_report.html", "w") as f:
            f.write(html_report)
        
        print("✅ HTML report generated: mlflow_report.html")
        
        # Save JSON metrics
        print("💾 Saving metrics summary...")
        save_metrics_json(summary)
        print("✅ Metrics saved: mlflow_metrics_summary.json")
        
        print()
        print("=" * 70)
        print("✅ Report generation complete!")
        print("=" * 70)
        print()
        
        # Print summary
        print("📊 Service Tracking Summary:")
        for service_name, service_data in summary.items():
            print(f"\n   {service_name}:")
            print(f"      Status: {service_data['status']}")
            print(f"      Metrics: {len(service_data['metrics'])}")
            if service_data['metrics']:
                for metric_name, metric_value in list(service_data['metrics'].items())[:3]:
                    print(f"         - {metric_name}: {metric_value}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
