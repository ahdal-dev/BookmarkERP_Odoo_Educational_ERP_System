import os
from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.controllers.ocr_controller import process_uploaded_image

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

templates = Jinja2Templates(directory=os.path.join("app", "templates"))


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@router.post("/ocr", response_class=HTMLResponse)
async def ocr(request: Request, file: UploadFile = File(...)):

    path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(path, "wb") as buffer:
        buffer.write(await file.read())

    result = process_uploaded_image(path)

    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            os.remove(os.path.join(UPLOAD_FOLDER, filename))
    
    return JSONResponse(content={"result": result})