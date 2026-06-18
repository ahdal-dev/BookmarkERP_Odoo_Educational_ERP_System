import os
import logging
from fastapi import APIRouter, UploadFile, File, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
try:
    from fastapi.templating import Jinja2Templates
except ImportError:
    Jinja2Templates = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

templates = (
    Jinja2Templates(directory=os.path.join("app", "templates"))
    if Jinja2Templates is not None
    else None
)


def process_uploaded_image(*args, **kwargs):
    from app.controllers.ocr_controller import process_uploaded_image as _process_uploaded_image
    return _process_uploaded_image(*args, **kwargs)


def process_with_yolo_only(*args, **kwargs):
    from app.controllers.ocr_controller import process_with_yolo_only as _process_with_yolo_only
    return _process_with_yolo_only(*args, **kwargs)


def process_with_mistral_only(*args, **kwargs):
    from app.controllers.ocr_controller import process_with_mistral_only as _process_with_mistral_only
    return _process_with_mistral_only(*args, **kwargs)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp', '.pdf'}


def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension."""
    return os.path.splitext(filename.lower())[1] in ALLOWED_EXTENSIONS


@router.get("/health")
async def health():
    """Health check endpoint for container orchestration"""
    return {"status": "healthy", "service": "ocr-microservice"}


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if templates is None:
        raise HTTPException(status_code=500, detail="Jinja2 is required for template rendering")
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


@router.post("/ocr/yolo", response_class=JSONResponse)
async def ocr_yolo(request: Request, file: UploadFile = File(...)):
    """
    Process uploaded image using YOLO detection only.
    Detects National ID cards using YOLO models.
    """
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

        logger.info(f"Processing file with YOLO detection: {file.filename}")

        # Process the image with YOLO only
        result = process_with_yolo_only(filepath)

        # Check if result contains error
        if isinstance(result, dict) and "error" in result:
            logger.warning(f"YOLO detection error: {result['error']}")
            return JSONResponse(
                content=result,
                status_code=400
            )

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in OCR YOLO endpoint: {str(e)}")
        return JSONResponse(
            content={"error": f"Processing failed: {str(e)}"},
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


@router.post("/ocr/mistral", response_class=JSONResponse)
async def ocr_mistral(
    request: Request,
    file: UploadFile = File(...),
    doc_type: str = Query(None, description="Document type: thanawiya_amma, national_id, passport, ig_transcript, american_transcript. If None, will auto-detect.")
):
    """
    Process uploaded image/PDF with Mistral OCR and extract structured data based on document type.
    
    Supported document types:
    - national_id: Egyptian National ID
    - passport: Passport document
    - thanawiya_amma: Egyptian Thanawiya Amma transcript
    - ig_transcript: IGCSE/Cambridge transcript
    - american_transcript: American school transcript
    
    If doc_type is not provided, the service will attempt to auto-detect the document type.
    """
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

        logger.info(f"Processing file with Mistral OCR: {file.filename}, doc_type: {doc_type}")

        # Process the file with Mistral OCR only
        result = process_with_mistral_only(filepath, doc_type)

        # Check if result contains error
        if isinstance(result, dict) and "error" in result:
            logger.warning(f"Mistral OCR processing error: {result['error']}")
            return JSONResponse(
                content=result,
                status_code=400
            )

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in OCR Mistral endpoint: {str(e)}")
        return JSONResponse(
            content={"error": f"Processing failed: {str(e)}"},
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


@router.get("/doc-types", response_class=JSONResponse)
async def get_supported_doc_types():
    """Get list of supported document types for auto-detection and extraction."""
    return {
        "supported_types": [
            {
                "key": "national_id",
                "name": "Egyptian National ID",
                "description": "Egyptian National ID Card"
            },
            {
                "key": "passport",
                "name": "Passport",
                "description": "International Passport"
            },
            {
                "key": "thanawiya_amma",
                "name": "Thanawiya Amma",
                "description": "Egyptian Secondary School Certificate"
            },
            {
                "key": "ig_transcript",
                "name": "IGCSE/Cambridge Transcript",
                "description": "Cambridge International Examinations Transcript"
            },
            {
                "key": "american_transcript",
                "name": "American Transcript",
                "description": "American School Transcript"
            }
        ]
    }