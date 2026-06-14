from fastapi import FastAPI, Request
from pydantic import BaseModel
import pandas as pd
import joblib
import numpy as np
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "..", "models", "gpa_predictor.pkl")
# Load model once
# model_path = "models/gpa_predictor.pkl"
if os.path.exists(model_path):
    try:
        bundle = joblib.load(model_path)
        enc = bundle["encoders"]
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        # Create dummy encoders for testing
        class DummyEncoder:
            def transform(self, x):
                return [0]
        enc = {
            "gender": DummyEncoder(),
            "persona": DummyEncoder(),
            "program_mean_gpa": {},
            "persona_mean_gpa": {}
        }
        bundle = {
            "features": ["gender_enc", "persona_enc", "program_target_enc", "persona_target_enc"],
            "model": None
        }
else:
    print(f"Model not found at {model_path}")
    # Create dummy encoders for testing
    class DummyEncoder:
        def transform(self, x):
            return [0]
    enc = {
        "gender": DummyEncoder(),
        "persona": DummyEncoder(),
        "program_mean_gpa": {},
        "persona_mean_gpa": {}
    }
    bundle = {
        "features": ["gender_enc", "persona_enc", "program_target_enc", "persona_target_enc"],
        "model": None
    }


class Student(BaseModel):
    gender: str
    persona: str
    program: str
    entry_year: int
    is_transfer: int
    semester_number: int
    cumgpa_before: float
    last_term_gpa: float
    avg_gpa_so_far: float
    min_gpa: float
    max_gpa: float
    gpa_std: float
    gpa_trend: float
    recent_trend: float
    terms_below_2: int
    terms_below_25: int
    is_recovering: int
    credits_so_far: int
    withdrawals_so_far: int
    failures_so_far: int
    pct_A_grades: float
    pct_B_plus_grades: float
    pct_below_C_grades: float
    pct_retakes: float
    pct_lab_courses: float
    avg_grade_pts: float
    quality_pts_total: float
    summer_taken: int
    next_season: int


def predict_student(data: dict):
    try:
        data["gender_enc"] = enc["gender"].transform([data["gender"]])[0]
        data["persona_enc"] = enc["persona"].transform([data["persona"]])[0]
        data["program_target_enc"] = enc["program_mean_gpa"].get(data["program"], 2.887)
        data["persona_target_enc"] = enc["persona_mean_gpa"].get(data["persona"], 2.887)

        # Use only features that exist
        available_features = [f for f in bundle["features"] if f in data]
        row = pd.DataFrame([{f: data[f] for f in available_features}])

        if bundle["model"] is not None:
            pred = bundle["model"].predict(row)[0]
        else:
            # Fallback prediction
            pred = data.get('cumgpa_before', 2.5) * 0.6 + data.get('last_term_gpa', 2.5) * 0.4
        
        pred = float(np.clip(pred, 0, 4))

        return {
            "predicted_gpa": round(pred, 3),
            "status": "AT RISK" if pred < 2.0 else "Safe"
        }
    except Exception as e:
        return {"error": str(e), "predicted_gpa": 2.5, "status": "Error"}


@app.post("/predict")
def predict(student: Student):
    return predict_student(student.dict())


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    # Simple HTML response without template
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>GPA Predictor API</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                background: #f5f5f5;
            }
            .container { 
                max-width: 800px; 
                margin: auto; 
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #333; }
            .endpoint {
                background: #f0f0f0;
                padding: 10px;
                margin: 10px 0;
                border-left: 4px solid #007bff;
                font-family: monospace;
            }
            button { 
                background: #007bff; 
                color: white; 
                padding: 10px 20px; 
                border: none; 
                cursor: pointer;
                margin: 10px 0;
            }
            button:hover { background: #0056b3; }
            pre {
                background: #f4f4f4;
                padding: 10px;
                overflow-x: auto;
            }
            .result { 
                margin-top: 20px; 
                padding: 15px; 
                border-radius: 5px; 
            }
            .safe { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .risk { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .error { background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 GPA Predictor API</h1>
            <p>This API predicts student GPA based on academic history.</p>
            
            <h2>📡 Available Endpoints:</h2>
            <div class="endpoint">
                <strong>POST /predict</strong> - Predict GPA for a student
            </div>
            <div class="endpoint">
                <strong>GET /docs</strong> - Interactive API documentation (Swagger UI)
            </div>
            <div class="endpoint">
                <strong>GET /health</strong> - Health check
            </div>
            
            <h2>🧪 Test the API:</h2>
            <button onclick="testPrediction()">Run Test Prediction</button>
            
            <h3>📝 Example cURL command:</h3>
            <pre>
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "Male",
    "persona": "Traditional",
    "program": "CS",
    "entry_year": 2020,
    "is_transfer": 0,
    "semester_number": 3,
    "cumgpa_before": 3.2,
    "last_term_gpa": 3.5,
    "avg_gpa_so_far": 3.3,
    "min_gpa": 2.8,
    "max_gpa": 3.7,
    "gpa_std": 0.4,
    "gpa_trend": 0.1,
    "recent_trend": 0.2,
    "terms_below_2": 0,
    "terms_below_25": 0,
    "is_recovering": 0,
    "credits_so_far": 45,
    "withdrawals_so_far": 0,
    "failures_so_far": 0,
    "pct_A_grades": 0.4,
    "pct_B_plus_grades": 0.3,
    "pct_below_C_grades": 0.1,
    "pct_retakes": 0.05,
    "pct_lab_courses": 0.2,
    "avg_grade_pts": 3.2,
    "quality_pts_total": 144,
    "summer_taken": 0,
    "next_season": 1
  }'
            </pre>
            
            <div id="result"></div>
        </div>
        
        <script>
            async function testPrediction() {
                const testData = {
        'gender':            'Male',
        'persona':           'solid_b',
        'program':           'Software Development',
        'entry_year':        2023,
        'is_transfer':       0,
        'semester_number':   3,
        'cumgpa_before':     2.9,
        'last_term_gpa':     2.7,
        'avg_gpa_so_far':    2.85,
        'min_gpa':           2.5,
        'max_gpa':           3.2,
        'gpa_std':           0.25,
        'gpa_trend':         -0.1,
        'recent_trend':      0.1,
        'terms_below_2':     0,
        'terms_below_25':    1,
        'is_recovering':     1,
        'credits_so_far':    51,
        'withdrawals_so_far':0,
        'failures_so_far':   0,
        'pct_A_grades':      0.15,
        'pct_B_plus_grades': 0.55,
        'pct_below_C_grades':0.0,
        'pct_retakes':       0.0,
        'pct_lab_courses':   0.2,
        'avg_grade_pts':     2.9,
        'quality_pts_total': 420.0,
        'summer_taken':      0,
        'next_season':       1,
    };
                
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = '<p>⏳ Predicting...</p>';
                
                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(testData)
                    });
                    
                    const result = await response.json();
                    
                    if (result.error) {
                        resultDiv.innerHTML = `
                            <div class="result error">
                                <h3>❌ Error</h3>
                                <p>${result.error}</p>
                            </div>
                        `;
                    } else {
                        resultDiv.innerHTML = `
                            <div class="result ${result.status === 'Safe' ? 'safe' : 'risk'}">
                                <h3>📊 Prediction Result</h3>
                                <p><strong>Predicted GPA:</strong> ${result.predicted_gpa}</p>
                                <p><strong>Status:</strong> ${result.status}</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `
                        <div class="result error">
                            <h3>❌ Error</h3>
                            <p>${error.message}</p>
                        </div>
                    `;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": bundle["model"] is not None}