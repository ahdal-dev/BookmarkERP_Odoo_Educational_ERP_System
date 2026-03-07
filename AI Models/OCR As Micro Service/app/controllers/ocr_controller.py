from app.services.processing_service import process_image
from app.services.detection_service import model_id_card, model_job
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_uploaded_image(image_path):
    """Process uploaded image and extract text using OCR models."""
    try:
        # Check if models are loaded
        if model_id_card is None:
            logger.error("ID card detection model is not loaded")
            return {"error": "ID card detection model not available"}

        if model_job is None:
            logger.error("Object detection model is not loaded")
            return {"error": "Object detection model not available"}

        result = process_image(
            image_path,
            model_id_card,
            model_job
        )

        return result

    except Exception as e:
        logger.error(f"Error in process_uploaded_image: {str(e)}")
        return {"error": f"Failed to process image: {str(e)}"}