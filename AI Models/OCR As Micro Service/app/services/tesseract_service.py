import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"Tesseract-OCR/tesseract.exe"

def extract_text(image, bbox, lang='ara'):

    x1, y1, x2, y2 = bbox

    cropped_image = image[y1:y2, x1:x2]

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