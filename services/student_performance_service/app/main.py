import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.model import is_loaded
from app.predictor import predict
from app.schemas import PredictRequest, PredictResponse

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="Student Performance Service")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.post("/predict", response_model=PredictResponse)
def predict_student(request: PredictRequest):
    if not is_loaded():
        raise HTTPException(status_code=503, detail="Models not loaded — run train.py first")
    try:
        result = predict(request.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return PredictResponse(student_id=request.student_id, **result)


@app.get("/")
def home():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": is_loaded()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5002, reload=True)
