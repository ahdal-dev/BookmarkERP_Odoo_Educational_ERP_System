from fastapi import FastAPI
from app.schemas import StudentRequest
from app.predictor import predict

app = FastAPI(title="Student Performance Service")


@app.post("/predict")
def predict_student(request: StudentRequest):

    result = predict(request.transcript_summary.dict())

    return {
        "student_id": request.student_id,
        "predictions": result
    }


@app.get("/health")
def health():
    return {"status": "ok"}