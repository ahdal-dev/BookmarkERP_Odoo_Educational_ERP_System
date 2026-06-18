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
    "birth_certificate": """This is an Egyptian civil registry birth certificate (صورة قيد الميلاد).
Extract ALL Arabic text EXACTLY as it appears, field by field.

The document has this exact structure — read right to left:

BELOW THE TITLE — before any section label:
- الرقم القومي: child's 14-digit national ID (appears here, before "بيانات المولود")

SECTION — بيانات المولود (child's data):
- First field: child's full name (e.g. خديجة) — appears as the FIRST item inside this section
- الجنسية: nationality
- محل الميلاد: place of birth (city / district)
- تاريخ الميلاد: date of birth written entirely in Arabic words (e.g. سبعة مارس ألفان وخمسة عشر) — NEVER in numbers
- النوع: gender (ذكر or أنثى)
- الديانة: religion

SECTION — بيانات الأب (father's data):
- Father's full Arabic name
- الرقم القومي: father's 14-digit national ID
- الديانة: father's religion
- الجنسية: father's nationality

SECTION — بيانات الأم (mother's data):
- Mother's full Arabic name
- الرقم القومي: mother's 14-digit national ID
- الديانة: mother's religion
- الجنسية: mother's nationality

BOTTOM REGISTRATION TABLE:
- رقم مسلسل: serial/registration number at the bottom
- Witness names (س من row)
- Event date, registration date, issue date

CRITICAL:
- The child's national ID is at the TOP of the document — do NOT confuse it with father's or mother's ID.
- تاريخ الميلاد is written in Arabic words — copy verbatim, it will be converted later.
- Preserve all Arabic-Indic numerals exactly as printed (٠١٢٣٤٥٦٧٨٩).
- Output as structured markdown with clear section labels.""",

    "thanawiya_amma": """This is an Egyptian Thanawiya Amma (ثانوية عامة) secondary school certificate.
Extract ALL text EXACTLY as it appears.

HEADER (top area, each field as "Label : Value", read right to left):
- رقم الجلوس : [number]           ← seat number (6-7 digits, shorter than national ID)
- الرقم القومي : [14-digit number] ← student's national ID
- اسم الطالب / اسم الطالبة : [full Arabic name, may be 4-5 words]
- المديرية : [value]
- الإدارة التعليمية : [value]
- المدرسة : [full school name, may include words like ثانوية / بنين / بنات]
- اللغة الأولى : [value]
- اللغة الثانية : [value]

SUBJECTS TABLE (subject names printed vertically/rotated):
For each subject column, extract:
  - Subject name (rotated header text)
  - Top row = max_score. If it appears as "X/Y" (e.g. 80/40), the max_score = X (the larger number).
  - Bottom row = actual score achieved
  - Dash or empty = not taken, skip entirely
The column "المجموع الكلي" = grand total, label it clearly, do NOT treat as a subject.

NON-COUNTED SUBJECTS (small table, bottom-right):
- التربية الدينية, التربية الوطنية, الاقتصاد والإحصاء
- Each shows: اجتياز or رسوب, and a score fraction

TOTAL SCORE:
- Arabic words line: e.g. مائتان وأربعة وستون درجات فقط
- Fraction line: e.g. ٢٦٤ من ٥٠٠

BOTTOM:
- Certificate number (e.g. 1-1/21-0218493)
- Stamp, barcode, photo presence

Extract every value exactly. Do NOT skip any subject.""",

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

    "_default": """This is an Arabic or bilingual document image. Your task is to extract ALL text for document type identification.

CRITICAL — read carefully:
1. Extract ALL Arabic text exactly as it appears — preserve every word, do NOT translate or summarize.
2. Extract ALL English text exactly as it appears.
3. Keep every label next to its value (e.g. "الجنسية: مصر").
4. Include ALL section headers (e.g. بيانات المولود, بيانات الأب, بيانات الأم, صورة قيد الميلاد).
5. Include ALL numbers exactly as printed (Arabic-Indic or Western).
6. Include website URLs, watermarks, stamps, and any small printed text.
7. Maintain document structure — list items in the order they appear top to bottom.

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


# Single keyword that alone is 100% conclusive for a doc type
STRONG_KEYWORDS = {
    "birth_certificate": [
        "صورة قيد الميلاد", "قيد الميلاد", "www.cso.gov.eg", "cso.gov.eg",
        "بيانات المولود", "بيانات الأب", "بيانات الأم",
    ],
    "passport": ["p<egy", "date of expiry", "mrz", "جواز سفر"],
    "thanawiya_amma": ["اللغة الاولي",
        "رقم الجلوس", "المجموع الكلي", "ثانوية عامة",
        "الإدارة التعليمية", "مراجعة أولى", "مراجعة ثانية",
        "درجات فقط", "اجتياز", "التربية الدينية",
        "1-1/21", "1-1/20", "1-1/22", "1-1/23",  # certificate number prefix pattern
    ],
    "ig_transcript":     ["igcse", "cambridge", "centre number"],
    "american_transcript": ["grade point average", "credits earned"],
}


def detect_doc_type(ocr_text):
    """Three-stage detection: strong keyword → scored keywords → LLM fallback."""
    # Arabic text is not affected by .lower() but keep it for English keywords
    text_lower = ocr_text.lower()

    # Stage 1: single strong keyword is conclusive
    # Check both lowercased (for English) and original (for Arabic)
    for doc_type, keywords in STRONG_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower or kw in ocr_text:
                logger.info(f"✅ Strong keyword match → {doc_type} ('{kw}')")
                return doc_type

    # Stage 2: scored keywords — check both lowercased and original for Arabic
    scores = {
        doc_type: sum(1 for kw in keywords if kw in text_lower or kw in ocr_text)
        for doc_type, keywords in DETECTION_HINTS.items()
    }
    logger.info(f"Keyword scores: {scores}")

    sorted_scores = sorted(scores.values(), reverse=True)
    best_type = max(scores, key=scores.get)
    best_score = sorted_scores[0]
    second_score = sorted_scores[1] if len(sorted_scores) > 1 else 0

    if best_score >= 1 and best_score > second_score:
        logger.info(f"✅ Heuristic confident: {best_type} (score={best_score})")
        return best_type

    logger.info("Heuristic uncertain — LLM fallback...")
    return _llm_detect(ocr_text, scores)


def _llm_detect(ocr_text, hint_scores=None):
    """LLM-based detection with hint context."""
    hint_str = f"\nKeyword hint scores: {hint_scores}\n" if hint_scores else ""

    prompt = f"""You are a document type classifier for Egyptian government and academic documents.
The OCR text below may be noisy, partially Arabic, or have garbled words.
{hint_str}
Classify the document as EXACTLY one of these five types:
  passport | birth_certificate | thanawiya_amma | ig_transcript | american_transcript

HOW TO IDENTIFY EACH TYPE:
- birth_certificate : Egyptian civil registry record. Look for ANY of:
    صورة قيد الميلاد, قيد الميلاد, بيانات المولود, بيانات الأب, بيانات الأم,
    cso.gov.eg, مصلحة الأحوال المدنية, رقم مسلسل, تاريخ الميلاد, محل الميلاد
    It has THREE people sections (child, father, mother). NO MRZ lines.

- passport : travel document. Look for:
    P<EGY, MRZ lines (two rows of letters/numbers/<<), Date of Expiry,
    passport number (alphanumeric ~9 chars), جواز سفر
    It has MRZ lines at the bottom. birth_certificate does NOT.

- thanawiya_amma : Egyptian secondary certificate. Look for:
    ثانوية عامة, رقم الجلوس, المجموع الكلي, subject score table

- ig_transcript : Cambridge/IGCSE result. Look for:
    IGCSE, Cambridge, centre number, candidate number, A* grades

- american_transcript : US school transcript. Look for:
    GPA, credits, semester, grade point average

⚠️  If you see Arabic sections for child/father/mother data → it is birth_certificate, NOT passport.
⚠️  Only classify as passport if you see MRZ lines or جواز سفر explicitly.

Reply with ONLY the document type key. No punctuation. No explanation.

--- OCR Text ---
{ocr_text[:2000]}"""

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
    "birth_certificate": """You are extracting data from an Egyptian civil registry birth certificate (صورة قيد الميلاد).

The OCR text below was extracted from a scanned document. It contains FOUR people's data. Read carefully — do NOT mix up which data belongs to whom.

══ THE DOCUMENT HAS THIS EXACT ORDER (top to bottom) ══

① Title "صورة قيد الميلاد" — watermark, ignore.

② CHILD'S NATIONAL ID — appears immediately below the title, before the "بيانات المولود" label:
   الرقم القومي : [number] → child_national_id (14 digits)

③ SECTION LABEL "بيانات المولود" — the child's section starts here:
   - FIRST field inside this section = child's name → child_name (e.g. خديجة)
   - الجنسية      → nationality (child's, e.g. مصر)
   - محل الميلاد  → place_of_birth (e.g. القاهرة / السيده زينب)
   - تاريخ الميلاد → ALWAYS written in Arabic WORDS, never as numbers.
                     Example: "سبعة مارس سنة ألف وتسعمائة وخمسة عشر"
                     Convert to YYYY-MM-DD:
                     يناير=01, فبراير=02, مارس=03, إبريل/أبريل=04, مايو=05, يونيو=06,
                     يوليو=07, أغسطس=08, سبتمبر=09, أكتوبر=10, نوفمبر=11, ديسمبر=12
                     Store raw Arabic string in date_of_birth_raw.
                     ⚠️ Numeric dates like 30/12/1981 come from the bottom table — do NOT use for date_of_birth.
   - النوع        → gender (ذكر=male, أنثى=female)
   - الديانة      → religion (child's)

④ SECTION "بيانات الأب" — father's data:
   - Full Arabic name (often preceded by "من") → father_name
   - الرقم القومي → father_national_id (14 digits)
   - الديانة      → father_religion
   - الجنسية      → father_nationality

⑤ SECTION "بيانات الأم" — mother's data:
   - Full Arabic name → mother_name
   - الرقم القومي → mother_national_id (14 digits)
   - الديانة      → mother_religion
   - الجنسية      → mother_nationality

⑥ BOTTOM REGISTRATION TABLE:
   - رقم مسلسل → serial_number (long purely-numeric, e.g. 1849211163)
   - Row "س من" → witnesses (array of names)
   - Row "د.أ"  → event_date
   - Row "د.إ"  → issue_date
   ⚠️ All dates in this table are numeric — do NOT use them as date_of_birth.

══ CRITICAL RULES ══
1. child_national_id = the الرقم القومي that appears BEFORE the "بيانات المولود" label (section ②).
2. child_name = the FIRST name inside the "بيانات المولود" section (section ③).
3. date_of_birth = Arabic word string from section ③ only — never a number.
4. Father and mother have their own national IDs in sections ④ and ⑤ — do NOT mix with child's.
5. Convert all Arabic-Indic digits (٠١٢٣٤٥٦٧٨٩) → Western (0123456789).
6. All national IDs are exactly 14 digits after conversion.

Return ONLY this JSON (no markdown fences, no explanation):
{
  "child_name": null,
  "child_national_id": null,
  "date_of_birth": null,
  "date_of_birth_raw": null,
  "place_of_birth": null,
  "gender": null,
  "religion": null,
  "nationality": null,
  "father_name": null,
  "father_national_id": null,
  "father_religion": null,
  "father_nationality": null,
  "mother_name": null,
  "mother_national_id": null,
  "mother_religion": null,
  "mother_nationality": null,
  "serial_number": null,
  "event_date": null,
  "issue_date": null,
  "witnesses": [],
  "additional_details": {}
}""",

    # ── Thanawiya Amma ────────────────────────────────────────────────────────
    "thanawiya_amma": """You are extracting data from an Egyptian Thanawiya Amma (ثانوية عامة) secondary certificate.

══ HEADER (top area, read right to left) ══
Each field appears as "Label : Value". Extract exactly:
  رقم الجلوس          → seat_number      (numeric, e.g. 1138465)
  الرقم القومي        → national_id      (14 digits, e.g. 30310011405375)
  اسم الطالب / اسم الطالبة → student_name  (full Arabic name, e.g. عبدالوهاب اشرف ابراهيم احمد محمد)
  المديرية            → directorate      (e.g. القاهرة)
  الإدارة التعليمية   → educational_administration (e.g. الساحل)
  المدرسة             → school           (full school name, e.g. ناصر الثانوية العسكرية بنين)
  اللغة الأولى        → first_language   (e.g. لغة انجليزية)
  اللغة الثانية       → second_language  (e.g. لغة فرنسية)

══ SUBJECTS TABLE ══
The table has two score rows. Process it column by column, right to left.

STEP 1 — identify the TWO score rows:
  ROW A (upper row): contains max scores in format "X/Y" (e.g. ٨٠/٤٠ or 80/40)
                     max_score = the FIRST (larger) number only. Ignore the second.
                     e.g. "٨٠/٤٠" → max_score = 80
                     e.g. "٦٠/٣٠" → max_score = 60
                     e.g. "٥٠/٢٥" → max_score = 50
  ROW B (lower row): contains the student's actual score as a plain integer.
                     A dash "—" or "-" = not taken.

STEP 2 — for each subject column (right to left):
  - Read the rotated vertical subject name
  - Read ROW A value → extract max_score (first number before "/")
  - Read ROW B value → extract score
  - If ROW B is a dash or empty → skip this subject entirely, do not include it
  - If both rows have numbers → add to subjects array

STEP 3 — skip the total column:
  The rightmost or leftmost column labeled "المجموع الكلي" contains the grand total.
  Do NOT include it in the subjects array.

Subject names appear in this order (right to left):
  1. اللغة الأجنبية الأولى   (max usually 80)
  2. اللغة الأجنبية الثانية  (max usually 50)
  3. التاريخ                  (max usually 60)
  4. الجغرافيا               (max usually 60)
  5. فلسفة ومنطق             (max usually 60)
  6. علم النفس والاجتماع     (max usually 60)
  7. الكيمياء                (max usually 60)
  8. الجيولوجيا والعلوم البيئية (max usually 60)
  9. الفيزياء                (max usually 60)
  10. الأحياء               (max usually 60)
  11. الرياضيات التطبيقية   (max usually 60)
  12. الرياضيات البحتة      (max usually 60)

Concrete example from a real certificate:
  Column "اللغة الأجنبية الأولى": ROW A = "٨٠/٤٠", ROW B = "٤٩"
  → {"subject": "اللغة الأجنبية الأولى", "score": 49, "max_score": 80}

  Column with ROW B = "-" → skip entirely.

  Column "المجموع الكلي": ROW A = "٤١٠/٢٠٥", ROW B = "٢٦٤" → this is the TOTAL, skip from subjects.

══ NON-COUNTED SUBJECTS (small table, bottom-right) ══
  التربية الدينية, التربية الوطنية, الاقتصاد والإحصاء
  Each shows اجتياز = "pass" or رسوب = "fail"

══ TOTAL SCORE ══
  Arabic words line (e.g. "مائتان وأربعة وستون درجات فقط") → total_score as integer (264)
  Fraction line (e.g. "٢٦٤ من ٥٠٠") → total_max_score = second number (500)
  ⚠️ Use ONLY the printed total — never sum subjects yourself.

══ BOTTOM ══
  Certificate number (e.g. 1-1/21-0218493) → certificate_number
  Photo visible in top-left corner → has_photo: true
  Official stamp visible → has_official_stamp: true
  Barcode visible → has_barcode: true

══ CRITICAL RULES ══
1. Convert ALL Arabic-Indic digits (٠١٢٣٤٥٦٧٨٩) → Western (0123456789) everywhere.
2. national_id is exactly 14 digits.
3. seat_number is the رقم الجلوس — a shorter number (6-7 digits), NOT the national ID.
4. student_name is the full name after "اسم الطالب" or "اسم الطالبة" — can be long (4-5 words).
5. school is the full school name after "المدرسة" — may include words like ثانوية, بنين, بنات.

Return ONLY this JSON (no markdown fences, no explanation):
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
    "birth_certificate":   ["child_name", "child_national_id", "father_name", "mother_name", "date_of_birth", "serial_number"],
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