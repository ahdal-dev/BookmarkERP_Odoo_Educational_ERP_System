
// Test data for prediction
const testData = {
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
    "next_season": 1
};

// Function to test prediction
async function testPrediction() {
    const resultDiv = document.getElementById('result');
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '<div class="result"><span class="loading"></span> Predicting...</div>';
    resultDiv.className = 'result';
    
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

// Function to copy cURL command to clipboard
function copyToClipboard() {
    const curlCommand = `curl -X POST "http://localhost:8000/predict" \\\n  -H "Content-Type: application/json" \\\n  -d '${JSON.stringify(testData, null, 2)}'`;
    
    navigator.clipboard.writeText(curlCommand).then(() => {
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✓ Copied!';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy: ', err);
        alert('Failed to copy command');
    });
}

// Function to check model status
async function checkModelStatus() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        const statusDiv = document.getElementById('modelStatus');
        if (data.model_loaded) {
            statusDiv.innerHTML = `
                <div class="status-card loaded">
                    ✅ Model loaded successfully<br>
                    Status: ${data.status}
                </div>
            `;
        } else {
            statusDiv.innerHTML = `
                <div class="status-card not-loaded">
                    ⚠️ Using fallback predictor (model file not found)
                </div>
            `;
        }
    } catch (error) {
        document.getElementById('modelStatus').innerHTML = `
            <div class="status-card not-loaded">
                ❌ Unable to check model status: ${error.message}
            </div>
        `;
    }
}

// Display cURL command on page load
function displayCurlCommand() {
    const curlCommand = `curl -X POST "http://localhost:8000/predict" \\\n  -H "Content-Type: application/json" \\\n  -d '${JSON.stringify(testData, null, 2)}'`;
    document.getElementById('curlCommand').textContent = curlCommand;
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    displayCurlCommand();
    checkModelStatus();
});
