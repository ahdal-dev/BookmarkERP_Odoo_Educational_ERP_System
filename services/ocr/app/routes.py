import os
import logging
from fastapi import APIRouter, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.controllers.ocr_controller import process_uploaded_image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

templates = Jinja2Templates(directory=os.path.join("app", "templates"))

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}


def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension."""
    return os.path.splitext(filename.lower())[1] in ALLOWED_EXTENSIONS


@router.get("/health")
async def health():
    """Health check endpoint for container orchestration"""
    return {"status": "healthy", "service": "ocr-microservice"}


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@router.post("/ocr", response_class=JSONResponse)
async def ocr(request: Request, file: UploadFile = File(...)):
    """Process uploaded image and extract text using OCR."""
    filepath = None

    try:
        # Validate file
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")

        if not allowed_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Read file content
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        # Save file
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(filepath, "wb") as buffer:
            buffer.write(contents)

        # Verify file was saved
        if not os.path.exists(filepath):
            raise HTTPException(status_code=500, detail="Failed to save uploaded file")

        # Process the image
        result = process_uploaded_image(filepath)

        # Check if result contains error
        if isinstance(result, dict) and "error" in result:
            logger.warning(f"OCR processing error: {result['error']}")
            return JSONResponse(
                content={"result": {}, "error": result["error"]},
                status_code=400
            )

        return JSONResponse(content={"result": result})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in OCR endpoint: {str(e)}")
        return JSONResponse(
            content={"result": {}, "error": f"Processing failed: {str(e)}"},
            status_code=500
        )

    finally:
        # Cleanup uploaded files
        try:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)

            for filename in os.listdir(UPLOAD_FOLDER):
                if filename.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        logger.warning(f"Failed to remove {file_path}: {str(e)}")
        except Exception as e:
            logger.warning(f"Error during cleanup: {str(e)}")