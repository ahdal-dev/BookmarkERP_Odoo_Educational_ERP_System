from ultralytics import YOLO
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load models with error handling
try:
    model_id_card_path = 'models/detect_id_card.pt'
    if not os.path.exists(model_id_card_path):
        raise FileNotFoundError(f"Model file not found: {model_id_card_path}")
    model_id_card = YOLO(model_id_card_path)
    logger.info("ID card detection model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load ID card model: {str(e)}")
    model_id_card = None

try:
    model_job_path = 'models/detect_odjects.pt'
    if not os.path.exists(model_job_path):
        raise FileNotFoundError(f"Model file not found: {model_job_path}")
    model_job = YOLO(model_job_path)
    logger.info("Object detection model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load object detection model: {str(e)}")
    model_job = None