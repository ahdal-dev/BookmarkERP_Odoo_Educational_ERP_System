from fastapi import FastAPI
from app.schemas import StudentRequest, StudentResponse
from app.predictor import predict

app = FastAPI(title="Student Performance Service", version="2.0")


@app.post("/predict", response_model=StudentResponse)
def predict_student(request: StudentRequest):
    result = predict(request.transcript_summary.model_dump())
    return {
        "student_id": request.student_id,
        "predictions": result["predictions"],
        "alerts": result["alerts"],
        "recommendations": result["recommendations"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}
