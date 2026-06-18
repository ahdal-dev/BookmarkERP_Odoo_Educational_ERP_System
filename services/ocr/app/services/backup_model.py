# import base64
# import json
# import os
# from dotenv import load_dotenv
# import logging

# load_dotenv()

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # --------------------------------------------------
# # 🔑 API Key & Client Initialization
# # --------------------------------------------------
# API_KEY = os.getenv("MISTRAL_API_KEY") or "QzjgLxty0dWSqUhhrKIfkr3Qcds1U9Tg"

# client = None
# try:
#     try:
#         from mistralai import Mistral
#         client = Mistral(api_key=API_KEY)
#         logger.info("✅ Mistral client initialized (v0.2.0+ API)")
#     except (ImportError, ModuleNotFoundError):
#         from mistralai.client import MistralClient
#         client = MistralClient(api_key=API_KEY)
#         logger.info("✅ Mistral client initialized (legacy API)")
# except Exception as e:
#     logger.error(f"❌ Failed to initialize Mistral client: {e}")
#     client = None


# # --------------------------------------------------
# # 🔧 Unified Chat Helper
# # --------------------------------------------------
# def _chat(messages, response_format=None):
#     """Call Mistral chat, handling v0.2+ and legacy APIs transparently."""
#     if not client:
#         raise RuntimeError("Mistral client not initialized.")

#     kwargs = dict(model="mistral-large-latest", messages=messages)
#     if response_format:
#         kwargs["response_format"] = response_format

#     for method in [
#         lambda: client.chat(**kwargs),
#         lambda: client.chat.complete(**kwargs),
#     ]:
#         try:
#             resp = method()
#             return resp.choices[0].message.content
#         except (AttributeError, TypeError):
#             continue

#     raise RuntimeError("Could not call Mistral chat API with either known method.")


# from PIL import Image, ImageFilter, ImageEnhance
# import cv2
# import numpy as np

# def preprocess_image(image_path):
#     """Enhance image quality before OCR."""
#     img = cv2.imread(image_path)

#     # Convert to grayscale
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     # Deskew (straighten tilted documents)
#     coords = np.column_stack(np.where(gray > 0))
#     angle = cv2.minAreaRect(coords)[-1]
#     if angle < -45:
#         angle = -(90 + angle)
#     else:
#         angle = -angle
#     (h, w) = gray.shape
#     center = (w // 2, h // 2)
#     M = cv2.getRotationMatrix2D(center, angle, 1.0)
#     gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

#     # Denoise
#     gray = cv2.fastNlMeansDenoising(gray, h=10)

#     # Increase contrast
#     gray = cv2.equalizeHist(gray)

#     # Upscale if small (vision models perform better on larger images)
#     if max(h, w) < 1500:
#         scale = 1500 / max(h, w)
#         gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

#     # Save preprocessed version
#     out_path = image_path.replace(".", "_processed.")
#     cv2.imwrite(out_path, gray)
#     logger.info(f"Preprocessed image saved: {out_path}")
#     return out_path
# # --------------------------------------------------
# # 🖼️  OCR Functions
# # --------------------------------------------------
# MIME_MAP = {
#     ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
#     ".bmp": "image/bmp", ".tiff": "image/tiff", ".tif": "image/tiff",
#     ".webp": "image/webp",
# }

# OCR_INSTRUCTIONS = {
#     "birth_certificate": """This is an Egyptian birth certificate (صورة قيد الميلاد).
# Extract ALL Arabic and English text exactly as it appears. Pay special attention to:
# 1. The three labeled sections: بيانات المولود، بيانات الأب، بيانات الأم
# 2. All 14-digit national ID numbers (الرقم القومي)
# 3. The date of birth written in Arabic words under تاريخ الميلاد
# 4. The bottom registration table with witness names and dates
# 5. The serial/registration number (رقم مسلسل)
# Preserve all labels next to their values. Output as structured markdown.""",

#     "thanawiya_amma": """This is an Egyptian Thanawiya Amma (ثانوية عامة) certificate.
# Extract ALL text exactly. Pay special attention to:
# 1. Student info: name, seat number (رقم الجلوس), national ID
# 2. All subject rows with their scores — format is score/max_score (e.g., ٦٠/١٣٠)
# 3. The explicitly printed total score (المجموع)
# 4. Pass/fail status (ناجح / راسب)
# 5. School, educational administration, directorate
# Output as structured markdown preserving table rows.""",

   

#     "passport": """This is a passport document.
# Extract ALL text exactly. Pay special attention to:
# 1. The two MRZ lines at the bottom (starting with P<)
# 2. Passport number, nationality, dates
# 3. Full name as it appears
# Output as structured markdown preserving MRZ lines verbatim.""",

#     "_default": """Extract ALL text from this document image.
# Preserve document structure: keep labels next to their values.
# For Arabic documents, maintain right-to-left reading order.
# Include ALL numbers, dates, and names exactly as written.
# Return as structured markdown.""",
# }


# def ocr_image(image_path, doc_hint=None):
#     """Extract text from image using Mistral vision model."""
#     logger.info(f"Running OCR on: {image_path}" + (f" [hint: {doc_hint}]" if doc_hint else ""))

#     with open(image_path, "rb") as f:
#         image_data = base64.standard_b64encode(f.read()).decode("utf-8")

#     ext = os.path.splitext(image_path)[1].lower()
#     mime_type = MIME_MAP.get(ext, "image/jpeg")
#     instruction = OCR_INSTRUCTIONS.get(doc_hint, OCR_INSTRUCTIONS["_default"])

#     messages = [{
#         "role": "user",
#         "content": [
#             {"type": "image_url", "image_url": f"data:{mime_type};base64,{image_data}"},
#             {"type": "text", "text": instruction},
#         ],
#     }]

#     try:
#         text = _chat(messages)
#         logger.info("✅ OCR complete")

#         class ImagePage:
#             def __init__(self, index, markdown):
#                 self.index = index
#                 self.markdown = markdown

#         return [ImagePage(0, text)]

#     except Exception as e:
#         logger.error(f"OCR failed: {e}")
#         raise RuntimeError(f"OCR image processing failed: {e}")


# def ocr_pdf(pdf_path):
#     """Extract text from PDF (requires pdf2image for full support)."""
#     logger.warning("PDF support requires pdf2image. Install with: pip install pdf2image")

#     class PDFPage:
#         def __init__(self, index, markdown):
#             self.index = index
#             self.markdown = markdown

#     return [PDFPage(0, "PDF processing requires pdf2image. Please convert to images first.")]


# def is_pdf(filepath):
#     return os.path.splitext(filepath)[1].lower() == ".pdf"


# # --------------------------------------------------
# # 🔢 Arabic → Western Numeral Conversion
# # --------------------------------------------------
# ARABIC_TO_WESTERN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


# def force_convert_numerals(obj):
#     """Recursively convert Arabic numerals to Western in any structure."""
#     if isinstance(obj, str):
#         return obj.translate(ARABIC_TO_WESTERN)
#     elif isinstance(obj, dict):
#         return {k: force_convert_numerals(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [force_convert_numerals(item) for item in obj]
#     return obj


# # --------------------------------------------------
# # 🔍 Document Type Detection
# # --------------------------------------------------
# DETECTION_HINTS = {
#     "passport":           ["passport", "جواز سفر", "جواز", "nationality", "mrz", "p<egy", "egyptian passport"],
#     "birth_certificate":  ["شهادة ميلاد", "birth certificate", "قيد الميلاد", "بيانات المولود", "بيانات الأب", "بيانات الأم"],
#     "thanawiya_amma":     ["ثانوية عامة", "thanawiya", "مجموع", "رقم الجلوس", "الإدارة التعليمية", "لجنة"],
#     "ig_transcript":      ["igcse", "cambridge", "centre number", "candidate number", "gcse", "a level"],
#     "american_transcript":["gpa", "credits", "grade level", "transcript", "high school", "semester"],
# }


# def detect_doc_type(ocr_text):
#     """
#     Two-stage detection:
#     1. Fast keyword heuristic — no API call needed
#     2. LLM fallback if heuristic is ambiguous
#     """
#     text_lower = ocr_text.lower()

#     scores = {
#         doc_type: sum(1 for kw in keywords if kw in text_lower)
#         for doc_type, keywords in DETECTION_HINTS.items()
#     }
#     logger.info(f"Keyword scores: {scores}")

#     sorted_scores = sorted(scores.values(), reverse=True)
#     best_type = max(scores, key=scores.get)
#     best_score, second_score = sorted_scores[0], sorted_scores[1]

#     if best_score >= 2 and best_score > second_score:
#         logger.info(f"✅ Heuristic confident: {best_type}")
#         return best_type

#     logger.info("Heuristic uncertain — falling back to LLM...")
#     return _llm_detect(ocr_text, scores)


# def _llm_detect(ocr_text, hint_scores=None):
#     """LLM-based detection with keyword hint scores passed as context."""
#     hint_str = f"\nKeyword hint scores (higher = more likely): {hint_scores}\n" if hint_scores else ""

#     prompt = f"""You are a document classifier for Egyptian and international academic/identity documents.
# The OCR text below may contain Arabic, English, or mixed content with OCR noise.
# {hint_str}
# Classify the document as EXACTLY one of:
# passport | birth_certificate | thanawiya_amma | ig_transcript | american_transcript

# Rules:
# - passport: travel document with MRZ lines or جواز سفر
# - birth_certificate: birth record with بيانات المولود / بيانات الأب / بيانات الأم sections
# - thanawiya_amma: Egyptian secondary school certificate with subjects, scores, رقم الجلوس
# - ig_transcript: Cambridge/IGCSE result slip with centre/candidate numbers
# - american_transcript: US-style transcript with GPA and credits

# Reply with ONLY the document type key. No punctuation, no explanation.

# --- OCR Text (first 1500 chars) ---
# {ocr_text[:1500]}"""

#     try:
#         detected = _chat([{"role": "user", "content": prompt}]).strip().lower()
#         for valid in DETECTION_HINTS:
#             if valid in detected:
#                 logger.info(f"LLM detected: {valid}")
#                 return valid
#         logger.warning(f"LLM returned unrecognized type: {detected}")
#     except Exception as e:
#         logger.error(f"LLM detection failed: {e}")

#     return None


# # --------------------------------------------------
# # 📋 Extraction Prompts
# # --------------------------------------------------
# PROMPTS = {
    
#     "passport": """You are extracting data from a passport. OCR may include MRZ lines at the bottom.

# Return ONLY a JSON object with these keys:
# full_name, passport_number, nationality, date_of_birth, gender, issue_date, expiry_date, mrz_line1, mrz_line2

# Rules:
# - MRZ lines start with P< — extract verbatim if present
# - passport_number: alphanumeric, usually 8-9 chars
# - dates: YYYY-MM-DD; MRZ dates are YYMMDD (e.g., 900115 = 1990-01-15)
# - nationality: 3-letter ISO code from MRZ (EGY=Egyptian)
# - gender: "male" or "female"
# - Use null for missing. No markdown. JSON only.""",

#     "birth_certificate": """You are extracting data from an Egyptian birth certificate (صورة قيد الميلاد).

# This document has labeled sections — extract each carefully:

# SECTION 1 — بيانات المولود (Child's Data):
# - الجنسية: child's nationality
# - محل الميلاد: place of birth
# - تاريخ الميلاد: date of birth written in Arabic words (e.g., "سبعة مارس ألفان و خمسة عشر" = 2015-03-07)
# - الديانة: religion
# - النوع: gender (ذكر=male, أنثى=female)
# - بيانات المُبلِّغ: the REPORTER of the birth (NOT the child's name)

# SECTION 2 — بيانات الأب (Father's Data):
# - Father's full name (line above الرقم القومي)
# - الرقم القومي: 14-digit national ID
# - الديانة، الجنسية

# SECTION 3 — بيانات الأم (Mother's Data):
# - Mother's full name (line above الرقم القومي)
# - الرقم القومي: 14-digit national ID
# - الديانة، الجنسية

# SECTION 4 — Bottom registration table:
# - رقم مسلسل / رقم السجل: serial/registration number
# - Witness names (شاهد / س من)
# - Dates: تاريخ الواقعة (event), تاريخ التسجيل (registration), تاريخ الإخراج (issue)
# - Issuing authority name

# CRITICAL:
# - The child's name is NOT explicitly labeled — infer from context or registration record
# - تاريخ الميلاد is in Arabic words — convert to YYYY-MM-DD
# - All national IDs are 14 digits — convert Arabic numerals to Western

# Return ONLY a JSON object with these keys:
# child_name, father_name, father_national_id, father_religion, father_nationality,
# mother_name, mother_national_id, mother_religion, mother_nationality,
# date_of_birth, place_of_birth, gender, religion, nationality,
# reporter_name, registration_number, serial_number,
# event_date, registration_date, issue_date,
# authority, witnesses, additional_details

# - witnesses: array of witness name strings
# - additional_details: dict of anything else (document number, website, governorate, notes)
# - dates: YYYY-MM-DD
# - gender: "male" or "female"
# - Use null for missing. No markdown. JSON only.""",

#     "thanawiya_amma": """You are extracting data from an Egyptian Thanawiya Amma (ثانوية عامة) certificate.

# Return ONLY a JSON object with these keys:
# student_name, seat_number, national_id, school, educational_administration,
# directorate, first_language, second_language, subjects, non_counted_subjects,
# total_score, status, certificate_number, has_barcode, has_photo, has_official_stamp

# Rules:
# - subjects: array of {subject, score, max_score} — convert Arabic numerals to Western
# - non_counted_subjects: array of {subject, result}
# - Score format: ٦٠/١٣٠ or 60/130 means score=60, max_score=130
# - total_score: use ONLY the explicitly printed total — NEVER calculate from subjects
# - status: "pass" or "fail" (ناجح=pass, راسب=fail)
# - has_barcode / has_photo / has_official_stamp: true or false
# - Convert all Arabic numerals: ٠١٢٣٤٥٦٧٨٩ → 0123456789
# - Use null for missing. No markdown. JSON only.""",

#     "ig_transcript": """You are extracting data from a Cambridge/IGCSE results transcript.

# Return ONLY a JSON object with these keys:
# student_name, center_number, candidate_number, exam_session, subjects

# Rules:
# - subjects: array of {name, grade, mark}
# - exam_session: e.g. "May/June 2024" or "October/November 2023"
# - grade: letter grade (A*, A, B, C, D, E, F, U)
# - mark: numeric if shown, else null
# - Use null for missing. No markdown. JSON only.""",

#     "american_transcript": """You are extracting data from an American high school transcript.

# Return ONLY a JSON object with these keys:
# student_name, school, grade_level, gpa, courses, graduation_date

# Rules:
# - courses: array of {name, grade, credits}
# - gpa: numeric (e.g., 3.85)
# - grade: letter or percentage
# - credits: numeric
# - graduation_date: YYYY-MM-DD or YYYY if only year known
# - Use null for missing. No markdown. JSON only.""",
# }


# # --------------------------------------------------
# # 🧠 Structured Extraction
# # --------------------------------------------------
# def extract_structured(ocr_text, prompt):
#     """Extract structured JSON from OCR text using Mistral."""
#     messages = [{"role": "user", "content": f"{prompt}\n\n--- OCR Text ---\n{ocr_text}"}]

#     try:
#         raw = _chat(messages, response_format={"type": "json_object"})
#     except Exception:
#         raw = _chat(messages)  # retry without response_format if unsupported

#     raw = raw.strip()

#     try:
#         return json.loads(raw), raw
#     except json.JSONDecodeError:
#         pass

#     # Attempt to extract JSON block from noisy response
#     s, e = raw.find("{"), raw.rfind("}")
#     if s != -1 and e > s:
#         try:
#             parsed = json.loads(raw[s:e + 1])
#             logger.info("Extracted JSON from noisy response")
#             return parsed, raw
#         except json.JSONDecodeError:
#             pass

#     logger.error("Could not parse response as JSON")
#     return {"_raw": raw}, raw


# # --------------------------------------------------
# # 🙋 Manual Fallback Type Selection
# # --------------------------------------------------
# def prompt_doc_type():
#     """Ask user to manually select document type."""
#     options = {
#         "1": "passport",
#         "2": "birth_certificate",
#         "3": "thanawiya_amma",
#         "4": "ig_transcript",
#         "5": "american_transcript",
#     }
#     print("\n⚠️  Could not auto-detect document type. Choose manually:")
#     for k, v in options.items():
#         print(f"  {k} = {v}")
#     choice = input("Enter number: ").strip()
#     return options.get(choice)

# def clean_ocr_text(raw_ocr, doc_type):
#     """Ask the model to self-correct OCR noise before extraction."""
#     prompt = f"""The following text was extracted via OCR from an Arabic/English document ({doc_type}).
# It may contain:
# - Merged or split Arabic words
# - Garbled numbers or dates
# - Broken table rows
# - Mixed Arabic/English OCR errors

# Please clean and reconstruct the text while preserving ALL original content and structure.
# Fix obvious OCR errors but do NOT add or invent any information.
# Return the cleaned text only — no explanation.

# --- RAW OCR ---
# {raw_ocr}"""

#     return _chat([{"role": "user", "content": prompt}])
# # --------------------------------------------------
# # 🚀 Main
# # --------------------------------------------------
# if __name__ == "__main__":

#     FILE_PATH = r"C:\Users\zyada\Desktop\ZC\Spring 2026\CSAI 499\Testing OCR IMAGES\images.jpg"

#     if not os.path.exists(FILE_PATH):
#         print(f"❌ File not found: {FILE_PATH}")

#     else:
#         print(f"📂 Processing: {FILE_PATH}\n")

#         # ── Step 1: Generic OCR pass ──────────────────────────
#         print("🖼️  Running initial OCR...")
#         # In __main__, Step 1:
#         processed_path = preprocess_image(FILE_PATH)
#         pages = ocr_image(processed_path, doc_hint=doc_type)
#         full_text = "".join(f"\n\n## Page {p.index + 1}\n\n{p.markdown}" for p in pages)
#         print(f"✅ Pages processed: {len(pages)}")
#         print("\n--- RAW OCR PREVIEW ---")
#         print(full_text[:600])

#         # ── Step 2: Detect document type ─────────────────────
#         print("\n🔍 Detecting document type...")
#         doc_type = detect_doc_type(full_text)
#         if not doc_type:
#             doc_type = prompt_doc_type()
#         print(f"📄 Document type: {doc_type}")

#         # ── Step 3: Re-OCR with document-aware prompt ─────────
#         if not is_pdf(FILE_PATH):
#             print(f"\n🔁 Re-running OCR with {doc_type}-aware prompt...")
#             pages = ocr_image(FILE_PATH, doc_hint=doc_type)
#             full_text = "".join(f"\n\n## Page {p.index + 1}\n\n{p.markdown}" for p in pages)

#         # ── Step 4: Extract structured data ──────────────────
#         prompt = PROMPTS.get(doc_type)
#         if not prompt:
#             print(f"❌ No extraction prompt for type: {doc_type}")
#         else:
#             print("\n🧠 Extracting structured data...")
#             parsed, _ = extract_structured(full_text, prompt)
#             parsed = force_convert_numerals(parsed)
#             print("\n✅ Extracted Data:")
#             print(json.dumps(parsed, ensure_ascii=False, indent=2))

import base64
import json
import os
import cv2
import numpy as np
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# 🔑 API Key & Client Initialization
# --------------------------------------------------
API_KEY = os.getenv("MISTRAL_API_KEY") or "QzjgLxty0dWSqUhhrKIfkr3Qcds1U9Tg"

client = None
try:
    try:
        from mistralai import Mistral
        client = Mistral(api_key=API_KEY)
        logger.info("✅ Mistral client initialized (v0.2.0+ API)")
    except (ImportError, ModuleNotFoundError):
        from mistralai.client import MistralClient
        client = MistralClient(api_key=API_KEY)
        logger.info("✅ Mistral client initialized (legacy API)")
except Exception as e:
    logger.error(f"❌ Failed to initialize Mistral client: {e}")
    client = None


# --------------------------------------------------
# 🔧 Unified Chat Helper
# --------------------------------------------------
def _chat(messages, response_format=None):
    """Call Mistral chat, handling v0.2+ and legacy APIs transparently."""
    if not client:
        raise RuntimeError("Mistral client not initialized.")

    kwargs = dict(model="mistral-large-latest", messages=messages)
    if response_format:
        kwargs["response_format"] = response_format

    for method in [
        lambda: client.chat(**kwargs),
        lambda: client.chat.complete(**kwargs),
    ]:
        try:
            resp = method()
            return resp.choices[0].message.content
        except (AttributeError, TypeError):
            continue

    raise RuntimeError("Could not call Mistral chat API with either known method.")


# --------------------------------------------------
# 🖼️ Image Preprocessing
# --------------------------------------------------
def preprocess_image(image_path):
    """
    Enhance image quality before OCR:
    - Grayscale, deskew, denoise, contrast, upscale
    Returns path to processed image (or original if cv2 fails).
    """
    img = cv2.imread(image_path)
    if img is None:
        logger.warning(f"cv2 could not read image, skipping preprocessing: {image_path}")
        return image_path

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Deskew
    coords = np.column_stack(np.where(gray > 0))
    if len(coords) > 0:
        angle = cv2.minAreaRect(coords)[-1]
        angle = -(90 + angle) if angle < -45 else -angle
        (h, w) = gray.shape
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC,
                              borderMode=cv2.BORDER_REPLICATE)

    gray = cv2.fastNlMeansDenoising(gray, h=10)
    gray = cv2.equalizeHist(gray)

    h, w = gray.shape
    if max(h, w) < 1500:
        scale = 1500 / max(h, w)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    out_path = image_path.replace(".", "_processed.")
    cv2.imwrite(out_path, gray)
    logger.info(f"Preprocessed image saved: {out_path}")
    return out_path


# --------------------------------------------------
# 🖼️ OCR
# --------------------------------------------------
MIME_MAP = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".bmp": "image/bmp", ".tiff": "image/tiff", ".tif": "image/tiff",
    ".webp": "image/webp",
}

# Per-document OCR instructions derived from real document layout analysis
OCR_INSTRUCTIONS = {
    "birth_certificate": """This is an Egyptian birth certificate (صورة قيد الميلاد).
Extract ALL Arabic and English text EXACTLY as it appears, label by label.

The document has this exact structure:

TOP AREA:
- Document serial number (top-left corner)
- Date line below it
- Website top-right: www.cso.gov.eg

SECTION bيانات المولود (right column):
- الجنسية: [value]
- محل الميلاد: [value]
- تاريخ الميلاد: [value written in Arabic words]
- الديانة: [value]
- النوع: [value]

SECTION بيانات المُبلِّغ (left column, same row):
- Full name of reporter
- الرقم القومي: [14-digit number]
- الديانة: [value]

SECTION بيانات الأب:
- Father full name
- الرقم القومي: [14-digit number]
- الديانة: [value]
- الجنسية: [value]

SECTION بيانات الأم:
- Mother full name
- الرقم القومي: [14-digit number]
- الديانة: [value]
- الجنسية: [value]

BOTTOM TABLE:
Row فتحة: dates
Row س من: witness names
Row د.أ / د.إ: event date / issue date
رقم مسلسل: serial number at bottom

Extract every label and its value. Preserve Arabic numerals exactly.""",

    "thanawiya_amma": """This is an Egyptian Thanawiya Amma (ثانوية عامة) secondary school certificate.
Extract ALL text EXACTLY as it appears.

TOP-RIGHT HEADER (right to left):
- رقم الجلوس: [number]
- الرقم القومي: [14-digit number]
- اسم الطالب: [full name]
- المديرية: [value]
- الإدارة التعليمية: [value]
- المدرسة: [value]
- اللغة الأولى: [value]
- اللغة الثانية: [value]

SUBJECTS TABLE:
Headers are rotated vertically. Two score rows per subject:
- Top row = max_score
- Bottom row = actual score
A dash means subject not taken — skip it.
The rightmost column المجموع الكلي is the total — NOT a subject.

NON-COUNTED SUBJECTS (bottom-right small table):
- التربية الدينية, التربية الوطنية, الاقتصاد والإحصاء
- Result: اجتياز or رسوب

TOTAL SCORE:
- Written in Arabic words on a dedicated line
- Also shown as fraction (e.g. 264/500)

BOTTOM:
- Certificate number (e.g. 1-1/21-0218493)
- Stamp, barcode, photo presence

Extract every value. Do NOT skip any subject score.""",

    "passport": """This is an Egyptian passport.
Extract ALL text exactly — both Arabic and English.

TOP: Type | Country Code | Passport No
FIELDS (bilingual labels):
- Full Name English: ALL CAPS
- Full Name Arabic: right side
- Date of Birth: DD/MM/YYYY
- Place of Birth (Arabic and English)
- Nationality
- Sex: M or F
- Date of Issue: DD/MM/YYYY
- Date of Expiry: DD/MM/YYYY
- Issuing Office
- National ID (if present)
- Profession (if present)

MRZ LINES (bottom — extract CHARACTER BY CHARACTER verbatim):
- Line 1: starts with P<EGY
- Line 2: starts with passport number

Output as structured markdown.""",

    "_default": """Extract ALL text from this document image.
Keep every label next to its value.
For Arabic, maintain right-to-left reading order.
Include ALL numbers, dates, and names exactly as written.
Return as structured markdown.""",
}


class ImagePage:
    def __init__(self, index, markdown):
        self.index = index
        self.markdown = markdown


def ocr_image(image_path, doc_hint=None):
    """Extract text from image using Mistral vision model."""
    logger.info(f"OCR: {image_path}" + (f" [hint={doc_hint}]" if doc_hint else ""))

    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    ext = os.path.splitext(image_path)[1].lower()
    mime_type = MIME_MAP.get(ext, "image/jpeg")
    instruction = OCR_INSTRUCTIONS.get(doc_hint, OCR_INSTRUCTIONS["_default"])

    messages = [{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": f"data:{mime_type};base64,{image_data}"},
            {"type": "text", "text": instruction},
        ],
    }]

    try:
        text = _chat(messages)
        logger.info("✅ OCR complete")
        return [ImagePage(0, text)]
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        raise RuntimeError(f"OCR failed: {e}")


def ocr_pdf(pdf_path):
    """PDF OCR placeholder — requires pdf2image."""
    logger.warning("PDF support requires pdf2image: pip install pdf2image")
    return [ImagePage(0, "PDF processing requires pdf2image. Convert to images first.")]


def is_pdf(filepath):
    return os.path.splitext(filepath)[1].lower() == ".pdf"


# --------------------------------------------------
# 🔢 Arabic → Western Numeral Conversion
# --------------------------------------------------
ARABIC_TO_WESTERN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def force_convert_numerals(obj):
    """Recursively convert Arabic numerals to Western in any structure."""
    if isinstance(obj, str):
        return obj.translate(ARABIC_TO_WESTERN)
    elif isinstance(obj, dict):
        return {k: force_convert_numerals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [force_convert_numerals(item) for item in obj]
    return obj


# --------------------------------------------------
# 🔍 Document Type Detection
# --------------------------------------------------
# Keywords chosen from ACTUAL text found in real documents
DETECTION_HINTS = {
    "passport": [
        "passport", "جواز سفر", "p<egy", "date of expiry",
        "date of birth", "issuing office", "date of issue",
    ],
    "birth_certificate": [
        "صورة قيد الميلاد", "قيد الميلاد", "بيانات المولود",
        "بيانات الأب", "بيانات الأم", "بيانات المُبلِّغ", "www.cso.gov.eg",
    ],
    "thanawiya_amma": [
        "ثانوية عامة", "رقم الجلوس", "الإدارة التعليمية",
        "المجموع الكلي", "اللغة الأولى", "مراجعة أولى",
    ],
    "ig_transcript": [
        "igcse", "cambridge", "centre number", "candidate number", "gcse",
    ],
    "american_transcript": [
        "gpa", "credits", "grade level", "high school", "semester",
    ],
}


def detect_doc_type(ocr_text):
    """Two-stage detection: keyword heuristic then LLM fallback."""
    text_lower = ocr_text.lower()

    scores = {
        doc_type: sum(1 for kw in keywords if kw in text_lower)
        for doc_type, keywords in DETECTION_HINTS.items()
    }
    logger.info(f"Keyword scores: {scores}")

    sorted_scores = sorted(scores.values(), reverse=True)
    best_type = max(scores, key=scores.get)
    best_score = sorted_scores[0]
    second_score = sorted_scores[1] if len(sorted_scores) > 1 else 0

    if best_score >= 2 and best_score > second_score:
        logger.info(f"✅ Heuristic confident: {best_type}")
        return best_type

    logger.info("Heuristic uncertain — LLM fallback...")
    return _llm_detect(ocr_text, scores)


def _llm_detect(ocr_text, hint_scores=None):
    """LLM-based detection with hint context."""
    hint_str = f"\nKeyword hint scores: {hint_scores}\n" if hint_scores else ""

    prompt = f"""You are a document classifier for Egyptian and international documents.
OCR text may contain Arabic, English, or mixed content with noise.
{hint_str}
Classify as EXACTLY one of:
passport | birth_certificate | thanawiya_amma | ig_transcript | american_transcript

- passport: has P<EGY, MRZ lines, Date of Expiry, passport number
- birth_certificate: has صورة قيد الميلاد, three sections بيانات المولود/الأب/الأم
- thanawiya_amma: has رقم الجلوس, subject score table, المجموع الكلي
- ig_transcript: has centre number, candidate number, Cambridge/IGCSE grades
- american_transcript: has GPA, credits, semester, high school

Reply with ONLY the key. No punctuation. No explanation.

--- OCR Text ---
{ocr_text[:1500]}"""

    try:
        detected = _chat([{"role": "user", "content": prompt}]).strip().lower()
        for valid in DETECTION_HINTS:
            if valid in detected:
                logger.info(f"LLM detected: {valid}")
                return valid
        logger.warning(f"LLM unrecognized: {detected}")
    except Exception as e:
        logger.error(f"LLM detection failed: {e}")
    return None


# --------------------------------------------------
# 🧹 OCR Self-Correction
# --------------------------------------------------
def clean_ocr_text(raw_ocr, doc_type):
    """Ask model to fix its own OCR noise before extraction."""
    prompt = f"""The following text was extracted via OCR from an Arabic/English {doc_type} document.
Common issues to fix:
- Merged or split Arabic words
- Garbled 14-digit national ID numbers (should be exactly 14 digits)
- Broken table rows or misaligned score columns
- Arabic and Western numerals mixed in the same number
- Missing spaces between a label and its value

Fix obvious OCR errors. Preserve ALL original content and structure.
Do NOT invent or add any information not visible in the original.
Return ONLY the cleaned text — no explanation.

--- RAW OCR ---
{raw_ocr}"""

    try:
        cleaned = _chat([{"role": "user", "content": prompt}])
        logger.info("✅ OCR text cleaned")
        return cleaned
    except Exception as e:
        logger.warning(f"OCR cleanup failed, using raw: {e}")
        return raw_ocr


# --------------------------------------------------
# 📋 Extraction Prompts
# --------------------------------------------------
PROMPTS = {

    # ── Birth Certificate ─────────────────────────────────────────────────────
    "birth_certificate": """You are extracting data from an Egyptian birth certificate (صورة قيد الميلاد).

The document has FOUR labeled sections:

SECTION 1 — بيانات المولود (right column):
  الجنسية         → child's nationality (e.g. مصر)
  محل الميلاد     → place of birth
  تاريخ الميلاد   → date in Arabic words (e.g. "سبعة مارس ألفان وخمسة عشر" = 2015-03-07)
  الديانة         → religion
  النوع           → gender (ذكر=male, أنثى=female)

SECTION 2 — بيانات المُبلِّغ (left column, same area as section 1):
  This is the REPORTER of the birth — a different person from the father.
  Full Arabic name of reporter
  الرقم القومي    → reporter's 14-digit national ID
  الديانة         → reporter's religion

SECTION 3 — بيانات الأب:
  Father's full Arabic name (line appearing before الرقم القومي)
  الرقم القومي    → father's 14-digit national ID
  الديانة         → father's religion
  الجنسية         → father's nationality

SECTION 4 — بيانات الأم:
  Mother's full Arabic name (line appearing before الرقم القومي)
  الرقم القومي    → mother's 14-digit national ID
  الديانة         → mother's religion
  الجنسية         → mother's nationality

BOTTOM REGISTRATION TABLE:
  Row "فتحة"   → opening/registration entry dates
  Row "س من"   → witness names (شاهد)
  Row "د.أ"    → event date (تاريخ الواقعة)
  Row "د.إ"    → issue date (تاريخ الإخراج)
  رقم مسلسل    → the large serial number printed at bottom

CRITICAL RULES:
1. child_name is NOT labeled on this form — infer only from رقم مسلسل record line.
   If not clearly found, return null. NEVER use reporter_name as child_name.
2. reporter_name and father_name are DIFFERENT people.
3. تاريخ الميلاد is always in Arabic written words — convert to YYYY-MM-DD.
4. All 14-digit national IDs may be in Arabic numerals — convert to Western digits.

Return ONLY this JSON (no markdown, no explanation):
{
  "child_name": null,
  "date_of_birth": null,
  "place_of_birth": null,
  "gender": null,
  "religion": null,
  "nationality": null,
  "reporter_name": null,
  "reporter_national_id": null,
  "reporter_religion": null,
  "father_name": null,
  "father_national_id": null,
  "father_religion": null,
  "father_nationality": null,
  "mother_name": null,
  "mother_national_id": null,
  "mother_religion": null,
  "mother_nationality": null,
  "serial_number": null,
  "registration_number": null,
  "event_date": null,
  "registration_date": null,
  "issue_date": null,
  "authority": null,
  "witnesses": [],
  "additional_details": {}
}""",

    # ── Thanawiya Amma ────────────────────────────────────────────────────────
    "thanawiya_amma": """You are extracting data from an Egyptian Thanawiya Amma (ثانوية عامة) certificate.

HEADER (top-right, read right to left):
  رقم الجلوس         → seat number
  الرقم القومي       → 14-digit national ID
  اسم الطالب         → student full name
  المديرية           → directorate/governorate
  الإدارة التعليمية  → educational administration
  المدرسة            → school name
  اللغة الأولى       → first foreign language
  اللغة الثانية      → second foreign language

SUBJECTS TABLE:
Subject headers are rotated vertically — read carefully.
Two score rows per column:
  Top row    = max_score (الدرجة العظمى)
  Bottom row = actual score achieved

Common subject columns (right to left):
  اللغة الأجنبية الأولى, اللغة الأجنبية الثانية, التاريخ, الجغرافيا,
  فلسفة ومنطق, علم النفس والاجتماع, الكيمياء, الجيولوجيا والعلوم البيئية,
  الفيزياء, الأحياء, الرياضيات التطبيقية, الرياضيات البحتة

Example: top="80", bottom="49" → score=49, max_score=80
A dash "—" or "-" in a cell = subject not taken → skip entirely.
The column labeled المجموع الكلي is the TOTAL — do NOT add it to subjects array.

NON-COUNTED SUBJECTS (bottom-right small table, pass/fail only):
  التربية الدينية, التربية الوطنية, الاقتصاد والإحصاء
  Results: اجتياز = "pass", رسوب = "fail"

TOTAL:
  Arabic words line (e.g. "مائتان وأربعة وستون") → convert to integer (264)
  Fraction line (e.g. "من ٧٣٤/٢٦٤") → total_score=264, total_max_score=500 (or as shown)

CRITICAL RULES:
- Convert ALL Arabic numerals to Western: ٠١٢٣٤٥٦٧٨٩ → 0123456789
- total_score: use the EXPLICITLY printed total ONLY — NEVER sum subjects yourself
- status: "pass" if ناجح, "fail" if راسب
- has_barcode / has_photo / has_official_stamp: true or false based on what is visible

Return ONLY this JSON (no markdown, no explanation):
{
  "student_name": null,
  "seat_number": null,
  "national_id": null,
  "school": null,
  "educational_administration": null,
  "directorate": null,
  "first_language": null,
  "second_language": null,
  "subjects": [
    {"subject": "", "score": 0, "max_score": 0}
  ],
  "non_counted_subjects": [
    {"subject": "", "result": "pass|fail"}
  ],
  "total_score": null,
  "total_max_score": null,
  "status": null,
  "certificate_number": null,
  "has_barcode": false,
  "has_photo": false,
  "has_official_stamp": false
}""",

    # ── Passport ──────────────────────────────────────────────────────────────
    "passport": """You are extracting data from an Egyptian passport.
The document has bilingual (Arabic + English) labels.

DOCUMENT INFO:
  Type/النوع          → document type (P)
  Country Code        → EGY
  Passport No         → alphanumeric (e.g. A23272...)

PERSONAL INFO:
  Full Name (English) → ALL CAPS (e.g. SAMEH SAYED SHAABAN KAMEL)
  Full Name (Arabic)  → Arabic script on right side
  Date of Birth       → DD/MM/YYYY → convert to YYYY-MM-DD
  Place of Birth      → city (Arabic and/or English)
  Nationality         → EGYPTIAN
  Sex                 → M=male, F=female
  Date of Issue       → DD/MM/YYYY → convert to YYYY-MM-DD
  Date of Expiry      → DD/MM/YYYY → convert to YYYY-MM-DD
  Issuing Office      → office code or name
  National ID         → 14-digit number if present
  Profession          → if present

MRZ LINES — extract CHARACTER BY CHARACTER, verbatim, no changes:
  Line 1: starts with P<EGY then name with << separators
  Line 2: starts with passport number digits

CRITICAL:
- MRZ must be exact — every < character and digit matters
- All dates are DD/MM/YYYY on this passport → convert to YYYY-MM-DD

Return ONLY this JSON (no markdown, no explanation):
{
  "full_name_en": null,
  "full_name_ar": null,
  "passport_number": null,
  "nationality": null,
  "date_of_birth": null,
  "place_of_birth": null,
  "gender": null,
  "issue_date": null,
  "expiry_date": null,
  "issuing_office": null,
  "national_id": null,
  "profession": null,
  "mrz_line1": null,
  "mrz_line2": null
}""",

    # ── IGCSE ─────────────────────────────────────────────────────────────────
    "ig_transcript": """You are extracting data from a Cambridge/IGCSE results transcript.

Return ONLY this JSON (no markdown, no explanation):
{
  "student_name": null,
  "center_number": null,
  "candidate_number": null,
  "exam_session": null,
  "subjects": [
    {"name": "", "grade": "", "mark": null}
  ]
}
Rules:
- exam_session: e.g. "May/June 2024"
- grade: A*, A, B, C, D, E, F, U
- mark: numeric if shown, else null""",

    # ── American Transcript ───────────────────────────────────────────────────
    "american_transcript": """You are extracting data from an American high school transcript.

Return ONLY this JSON (no markdown, no explanation):
{
  "student_name": null,
  "school": null,
  "grade_level": null,
  "gpa": null,
  "courses": [
    {"name": "", "grade": "", "credits": null}
  ],
  "graduation_date": null
}
Rules:
- gpa: numeric (e.g. 3.85)
- graduation_date: YYYY-MM-DD or YYYY
- credits: numeric""",
}

# Fields that must be non-null/non-empty for a successful extraction
REQUIRED_FIELDS = {
    "birth_certificate":   ["father_name", "mother_name", "date_of_birth", "serial_number"],
    "thanawiya_amma":      ["student_name", "seat_number", "subjects", "total_score"],
    "passport":            ["full_name_en", "passport_number", "date_of_birth", "expiry_date"],
    "ig_transcript":       ["student_name", "candidate_number", "subjects"],
    "american_transcript": ["student_name", "gpa", "courses"],
}


# --------------------------------------------------
# 🧠 Extraction with Retry
# --------------------------------------------------
def extract_structured(ocr_text, prompt):
    """Extract structured JSON from OCR text."""
    messages = [{"role": "user", "content": f"{prompt}\n\n--- OCR Text ---\n{ocr_text}"}]

    try:
        raw = _chat(messages, response_format={"type": "json_object"})
    except Exception:
        raw = _chat(messages)

    raw = raw.strip()
    try:
        return json.loads(raw), raw
    except json.JSONDecodeError:
        pass

    s, e = raw.find("{"), raw.rfind("}")
    if s != -1 and e > s:
        try:
            parsed = json.loads(raw[s:e + 1])
            logger.info("Extracted JSON from noisy response")
            return parsed, raw
        except json.JSONDecodeError:
            pass

    logger.error("Could not parse response as JSON")
    return {"_raw": raw}, raw


def extract_with_retry(ocr_text, doc_type, max_retries=2):
    """Extract and retry with targeted hints if critical fields are missing."""
    base_prompt = PROMPTS[doc_type]
    required = REQUIRED_FIELDS.get(doc_type, [])
    prompt = base_prompt

    for attempt in range(1, max_retries + 1):
        parsed, _ = extract_structured(ocr_text, prompt)
        parsed = force_convert_numerals(parsed)

        missing = [f for f in required if not parsed.get(f)]
        if not missing:
            logger.info(f"✅ Extraction complete (attempt {attempt})")
            return parsed

        logger.warning(f"Attempt {attempt}/{max_retries} — missing: {missing}")
        if attempt < max_retries:
            prompt = (
                base_prompt
                + f"\n\nATTENTION: The previous attempt could not find: {missing}\n"
                + "Search the OCR text again specifically for these values. "
                + "They may appear with slightly different labels or spacing."
            )

    logger.warning(f"Best-effort result returned. Still missing: {missing}")
    return parsed


# --------------------------------------------------
# 🙋 Manual Fallback
# --------------------------------------------------
def prompt_doc_type():
    options = {
        "1": "passport",
        "2": "birth_certificate",
        "3": "thanawiya_amma",
        "4": "ig_transcript",
        "5": "american_transcript",
    }
    print("\n⚠️  Could not auto-detect. Choose manually:")
    for k, v in options.items():
        print(f"  {k} = {v}")
    return options.get(input("Enter number: ").strip(), "birth_certificate")


# --------------------------------------------------
# 🚀 Main Pipeline
# --------------------------------------------------
if __name__ == "__main__":

    FILE_PATH = r"C:\Users\zyada\Desktop\ZC\Spring 2026\CSAI 499\Testing OCR IMAGES\images.jpg"

    if not os.path.exists(FILE_PATH):
        print(f"❌ File not found: {FILE_PATH}")
    else:
        print(f"📂 Processing: {FILE_PATH}\n")

        # ── Step 1: Preprocess image ──────────────────────────
        print("🔧 Preprocessing image...")
        processed_path = preprocess_image(FILE_PATH)

        # ── Step 2: Generic OCR (no hint) ────────────────────
        print("🖼️  Running initial OCR (generic)...")
        pages = ocr_pdf(FILE_PATH) if is_pdf(FILE_PATH) else ocr_image(processed_path)
        full_text = "".join(f"\n\n## Page {p.index + 1}\n\n{p.markdown}" for p in pages)
        print(f"✅ Pages processed: {len(pages)}")
        print("\n--- RAW OCR PREVIEW ---")
        print(full_text[:800])

        # ── Step 3: Detect document type ─────────────────────
        print("\n🔍 Detecting document type...")
        doc_type = detect_doc_type(full_text)
        if not doc_type:
            doc_type = prompt_doc_type()
        print(f"📄 Document type: {doc_type}")

        # ── Step 4: Re-OCR with document-aware prompt ─────────
        if not is_pdf(FILE_PATH):
            print(f"\n🔁 Re-running OCR with {doc_type}-aware prompt...")
            pages = ocr_image(processed_path, doc_hint=doc_type)
            full_text = "".join(f"\n\n## Page {p.index + 1}\n\n{p.markdown}" for p in pages)

        # ── Step 5: Clean OCR noise ───────────────────────────
        print("\n🧹 Cleaning OCR text...")
        full_text = clean_ocr_text(full_text, doc_type)

        # ── Step 6: Extract with retry ────────────────────────
        if doc_type not in PROMPTS:
            print(f"❌ No extraction prompt for: {doc_type}")
        else:
            print(f"\n🧠 Extracting structured data...")
            parsed = extract_with_retry(full_text, doc_type)
            print("\n✅ Extracted Data:")
            print(json.dumps(parsed, ensure_ascii=False, indent=2))