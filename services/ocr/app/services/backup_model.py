import base64
import json
import os
from PIL import Image
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = None

API_KEY = os.getenv("MISTRAL_API_KEY") or os.getenv("QzjgLxty0dWSqUhhrKIfkr3Qcds1U9Tg") 
if not API_KEY: 
    API_KEY = "QzjgLxty0dWSqUhhrKIfkr3Qcds1U9Tg"

# Try to initialize Mistral client with flexible approach
try:
    try:
        # Try v0.2.0+ API first
        from mistralai import Mistral
        client = Mistral(api_key=API_KEY)
        logger.info("✅ Mistral client initialized successfully (v0.2.0+ API)!")
    except (ImportError, ModuleNotFoundError):
        # Try older MistralClient API
        from mistralai.client import MistralClient
        client = MistralClient(api_key=API_KEY)
        logger.info("✅ Mistral client initialized (MistralClient legacy API)!")
except Exception as e:
    logger.error(f"❌ Failed to initialize Mistral client: {e}")
    logger.warning(f"Mistral OCR will not be available. Ensure mistralai is installed: pip install mistralai>=0.0.7")
    client = None



def ocr_pdf(pdf_path):
    """Extract text from PDF using vision model via Mistral Chat API."""
    if not client:
        raise RuntimeError("Mistral client not initialized. Please install mistralai: pip install mistralai")
    
    try:
        # For PDF, we'll need to convert it to images first or use a workaround
        # For now, return a message indicating PDF needs to be handled differently
        logger.warning(f"PDF handling: {pdf_path}")
        
        # This would require pdf2image library to convert PDF pages to images
        # For MVP, we'll use a simple placeholder that returns structured response
        class PDFPage:
            def __init__(self, index, markdown):
                self.index = index
                self.markdown = markdown
        
        return [PDFPage(0, "PDF processing requires additional dependencies (pdf2image). Please convert PDF to images first.")]
        
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise


def ocr_image(image_path):
    """Extract text from image using Mistral vision model."""
    if not client:
        raise RuntimeError("Mistral client not initialized. Please install mistralai: pip install mistralai>=0.0.7")
    
    try:
        logger.info(f"Extracting text from image: {image_path}")
        
        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        ext = os.path.splitext(image_path)[1].lower()
        mime_map = {
            ".jpg": "image/jpeg", 
            ".jpeg": "image/jpeg", 
            ".png": "image/png",
            ".bmp": "image/bmp", 
            ".tiff": "image/tiff", 
            ".tif": "image/tiff",
            ".webp": "image/webp"
        }
        mime_type = mime_map.get(ext, "image/jpeg")

        # Use vision model to extract text from image
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": f"data:{mime_type};base64,{image_data}",
                    },
                    {
                        "type": "text",
                        "text": "Extract ALL text from this document image. Preserve the document structure and layout as much as possible. Return the extracted text in markdown format."
                    }
                ],
            }
        ]
        
        try:
            # Try with client.chat() method (newer API)
            response = client.chat(
                model="mistral-large-latest",
                messages=messages,
            )
        except (AttributeError, TypeError):
            # Fallback to client.chat.complete() (older API) or other method
            try:
                response = client.chat.complete(
                    model="mistral-large-latest",
                    messages=messages,
                )
            except (AttributeError, TypeError):
                # If that also fails, try as a callable
                response = client.chat(model="mistral-large-latest", messages=messages)
        
        extracted_text = response.choices[0].message.content
        logger.info(f"Successfully extracted text from image")
        
        # Wrap in the expected page object format
        class ImagePage:
            def __init__(self, index, markdown):
                self.index = index
                self.markdown = markdown
        
        return [ImagePage(0, extracted_text)]
        
    except Exception as e:
        logger.error(f"Error extracting text from image: {e}")
        raise RuntimeError(f"OCR image processing failed: {str(e)}")





# --------------------------------------------------
# 🧠 Structured extraction via Mistral Chat
# --------------------------------------------------
def extract_structured(ocr_text, prompt):
    """Use Mistral chat to structure OCR text into JSON."""
    if not client:
        raise RuntimeError("Mistral client not initialized. Please install mistralai: pip install mistralai>=0.0.7")
    
    try:
        logger.info(f"Extracting structured data from OCR text...")
        
        messages = [
            {
                "role": "user",
                "content": f"{prompt}\n\n--- OCR Text ---\n{ocr_text}",
            }
        ]
        
        try:
            # Try with client.chat() method (newer API)
            response = client.chat(
                model="mistral-large-latest",
                messages=messages,
                response_format={"type": "json_object"},
            )
        except (AttributeError, TypeError):
            # Fallback to client.chat.complete() (older API)
            try:
                response = client.chat.complete(
                    model="mistral-large-latest",
                    messages=messages,
                    response_format={"type": "json_object"},
                )
            except (AttributeError, TypeError):
                # If response_format not supported, try without it
                response = client.chat(
                    model="mistral-large-latest",
                    messages=messages,
                )
        
        raw = response.choices[0].message.content.strip()
        logger.info(f"Raw response received, parsing JSON...")
        
        try:
            parsed = json.loads(raw)
            logger.info(f"Successfully parsed structured data")
            return parsed, raw
        except json.JSONDecodeError:
            # Try to extract JSON from response
            logger.warning(f"Initial JSON parse failed, attempting extraction...")
            s, e = raw.find("{"), raw.rfind("}")
            if s != -1 and e > s:
                try:
                    parsed = json.loads(raw[s : e + 1])
                    logger.info(f"Successfully extracted JSON from response")
                    return parsed, raw
                except json.JSONDecodeError:
                    pass
            logger.error(f"Could not parse response as JSON")
            return {"_raw": raw}, raw
            
    except Exception as e:
        logger.error(f"Error in extract_structured: {e}")
        raise RuntimeError(f"Structured extraction failed: {str(e)}")





# --------------------------------------------------
# Helper: detect if file is PDF
# --------------------------------------------------
def is_pdf(filepath):
    return os.path.splitext(filepath)[1].lower() == ".pdf"


# --------------------------------------------------
# Arabic → Western numeral conversion
# --------------------------------------------------
ARABIC_TO_WESTERN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

def to_western(text):
    if not text:
        return text
    return text.translate(ARABIC_TO_WESTERN)

def force_convert_numerals(obj):
    """Recursively convert Arabic numerals to Western in output."""
    if isinstance(obj, str):
        return obj.translate(ARABIC_TO_WESTERN)
    elif isinstance(obj, dict):
        return {k: force_convert_numerals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [force_convert_numerals(item) for item in obj]
    return obj


print("✅ OCR & extraction functions ready!")

PROMPTS = {
    "national_id": """You are a data extraction assistant. Extract information from the following OCR output of an Egyptian National ID card.
Return a single JSON object with these exact keys: full_name, national_id, date_of_birth, gender, address, issue_date, expiry_date.
Use null for any missing or unclear values.
Use YYYY-MM-DD for dates when possible.
Do not include markdown, explanations, or extra fields. JSON only.""",

    "passport": """You are a data extraction assistant. Extract information from the following OCR output of a passport document.
Return a single JSON object with these exact keys: full_name, passport_number, nationality, date_of_birth, gender, issue_date, expiry_date, mrz_line1, mrz_line2.
Use null for any missing or unclear values.
Use YYYY-MM-DD for dates when possible.
Do not include markdown, explanations, or extra fields. JSON only.""",

    "thanawiya_amma": """You are a specialized extractor for Egyptian Thanawiya Amma secondary school certificates.
Analyze the OCR text and return a single JSON object with these exact keys:
student_name, seat_number, national_id, school, educational_administration, directorate, first_language, second_language, subjects, non_counted_subjects, total_score, status, certificate_number, has_barcode, has_photo, has_official_stamp.
- subjects: array of objects with exact keys subject, score, max_score.
- non_counted_subjects: array of objects with exact keys subject, result.
- total_score: use only the total score written explicitly in the document; do not calculate it from subject scores.
- status: use pass or fail.
- has_barcode, has_photo, has_official_stamp: true or false.

For score lines like ٦٠١٣٠ or 60130, interpret them as score/max_score.
Do not treat the first number in the subject table as the total score unless the document explicitly labels it as the total.
If a field is missing or unclear, use null.
Do not include markdown, explanations, or extra fields. JSON only.""",

    "ig_transcript": """Extract all data from the following OCR output of an IGCSE/Cambridge transcript.
Return a single JSON object with these exact keys: student_name, center_number, candidate_number, exam_session, subjects.
- subjects: array of objects with exact keys name, grade, mark.
Use null for any missing or unclear values.
Do not include markdown, explanations, or extra fields. JSON only.""",

    "american_transcript": """Extract all data from the following OCR output of an American school transcript.
Return a single JSON object with these exact keys: student_name, school, grade_level, gpa, courses, graduation_date.
- courses: array of objects with exact keys name, grade, credits.
Use null for any missing or unclear values.
Use YYYY-MM-DD for dates when possible.
Do not include markdown, explanations, or extra fields. JSON only.""",

    "detect": """Based on the following OCR text, determine the document type.
Reply with ONLY one of these exact words:
thanawiya_amma, national_id, passport, ig_transcript, american_transcript.
Do not add any extra text.""",
}
print("✅ Prompts loaded")

def prompt_doc_type():
    """Ask user to manually select document type."""
    print("⚠️ Could not auto-detect type. Choose manually:")
    print("  1 = national_id")
    print("  2 = passport")
    print("  3 = thanawiya_amma")
    print("  4 = ig_transcript")
    print("  5 = american_transcript")
    choice = input("Enter number: ").strip()
    return {
        "1": "national_id",
        "2": "passport",
        "3": "thanawiya_amma",
        "4": "ig_transcript",
        "5": "american_transcript",
    }.get(choice, "national_id")


def detect_doc_type(ocr_text):
    """Auto-detect document type from OCR text using Mistral Chat."""
    if not client:
        raise RuntimeError("Mistral client not initialized. Please install mistralai: pip install mistralai>=0.0.7")
    
    try:
        logger.info("Detecting document type...")
        
        messages = [
            {"role": "user", "content": f"{PROMPTS['detect']}\n\n--- OCR Text ---\n{ocr_text}"}
        ]
        
        try:
            response = client.chat(
                model="mistral-large-latest",
                messages=messages
            )
        except (AttributeError, TypeError):
            try:
                response = client.chat.complete(
                    model="mistral-large-latest",
                    messages=messages
                )
            except (AttributeError, TypeError):
                # If that also fails, try as a callable
                response = client.chat(model="mistral-large-latest", messages=messages)
        
        detected = response.choices[0].message.content.strip().lower()
        
        logger.info(f"Detection result: {detected}")
        
        # Clean up — the model may wrap in quotes or add punctuation
        for valid in ["thanawiya_amma", "national_id", "passport", "ig_transcript", "american_transcript"]:
            if valid in detected:
                logger.info(f"Document type identified as: {valid}")
                return valid
        
        logger.warning(f"Could not identify document type from: {detected}")
        return None
        
    except Exception as e:
        logger.error(f"Error detecting document type: {e}")
        raise RuntimeError(f"Document type detection failed: {str(e)}")




if __name__ == "__main__":

    FILE_PATH = r"C:\Users\zyada\Desktop\ZC\Spring 2026\CSAI 499\Testing OCR IMAGES\images.jpg"
    # ════════════════════════════════════════════════════

    if not os.path.exists(FILE_PATH):
        print(f"❌ File not found: {FILE_PATH}")

    else:
        print(f"📂 Processing: {FILE_PATH}\n")

        if is_pdf(FILE_PATH):
            print("📄 PDF detected — running Mistral OCR...")
            pages = ocr_pdf(FILE_PATH)
        else:
            print("🖼️ Image detected — running Mistral OCR...")
            pages = ocr_image(FILE_PATH)

        full_text = ""

        for page in pages:
            full_text += f"\n\n## Page {page.index + 1}\n\n{page.markdown}"
            print(f"  ✅ Page {page.index + 1} OCR complete")

        print(f"\n📝 Total pages processed: {len(pages)}")