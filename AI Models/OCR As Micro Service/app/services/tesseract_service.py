import os

import cv2
import pytesseract
import os
import platform
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Only set tesseract path on Windows
if platform.system() == 'Windows':
    pytesseract.pytesseract.tesseract_cmd = r"Tesseract-OCR/tesseract.exe"
# On Linux (Docker), tesseract is installed via apt and is in PATH

def extract_text(image, bbox, lang='ara'):
    """Extract text from a region of an image using Tesseract OCR."""
    try:
        if image is None or image.size == 0:
            logger.error("Invalid or empty image provided")
            return ""

        x1, y1, x2, y2 = bbox

        # Validate bbox coordinates
        if x1 >= x2 or y1 >= y2:
            logger.warning(f"Invalid bbox coordinates: {bbox}")
            return ""

        # Ensure bbox is within image bounds
        height, width = image.shape[:2]
        x1 = max(0, min(x1, width))
        x2 = max(0, min(x2, width))
        y1 = max(0, min(y1, height))
        y2 = max(0, min(y2, height))

        cropped_image = image[y1:y2, x1:x2]

        if cropped_image is None or cropped_image.size == 0:
            logger.warning("Cropped image is empty")
            return ""

        gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)

        _, thresh = cv2.threshold(
            gray, 0, 255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        config = r'--oem 3 --psm 6'

        text = pytesseract.image_to_string(
            thresh,
            lang=lang,
            config=config
        )

        return text.strip()

    except Exception as e:
        logger.error(f"Error extracting text: {str(e)}")
        return ""