from app.services.processing_service import process_image
from app.services.detection_service import model_id_card, model_job

def process_uploaded_image(image_path):

    result = process_image(
        image_path,
        model_id_card,
        model_job
    )

    return result