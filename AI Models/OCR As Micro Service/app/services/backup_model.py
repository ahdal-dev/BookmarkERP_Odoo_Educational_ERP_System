import base64
import json
import os
# import fitz
from PIL import Image
import os
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

API_KEY = os.getenv("QzjgLxty0dWSqUhhrKIfkr3Qcds1U9Tg")
if not API_KEY:
    API_KEY = "QzjgLxty0dWSqUhhrKIfkr3Qcds1U9Tg"

client = Mistral(api_key=API_KEY)
print("✅ Mistral client initialized!")
def ocr_pdf(pdf_path):
    """Send a PDF to Mistral OCR and return extracted markdown per page."""
    with open(pdf_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{b64}",
        },
        include_image_base64=False,
    )
    return response.pages


# --------------------------------------------------
# 🖼️ OCR: Process an image file via Mistral OCR API
# --------------------------------------------------
def ocr_image(image_path):
    """Send an image to Mistral OCR and return extracted markdown."""
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    ext = os.path.splitext(image_path)[1].lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
                ".bmp": "image/bmp", ".tiff": "image/tiff", ".tif": "image/tiff"}
    mime = mime_map.get(ext, "image/jpeg")

    response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "image_url",
            "image_url": f"data:{mime};base64,{b64}",
        },
        include_image_base64=False,
    )
    return response.pages


# --------------------------------------------------
# 🧠 Structured extraction via Mistral Chat
# --------------------------------------------------
def extract_structured(ocr_text, prompt):
    """Use Mistral chat to structure OCR text into JSON."""
    messages = [
        {
            "role": "user",
            "content": f"{prompt}\n\n--- OCR Text ---\n{ocr_text}",
        }
    ]
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=messages,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw), raw
    except json.JSONDecodeError:
        # Try to extract JSON from response
        s, e = raw.find("{"), raw.rfind("}")
        if s != -1 and e > s:
            try:
                return json.loads(raw[s : e + 1]), raw
            except json.JSONDecodeError:
                pass
        return {"_raw": raw}, raw


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
    "national_id": """Extract all text from the following OCR output of an Egyptian National ID card.
Return JSON with: full_name, national_id, date_of_birth, gender, address, issue_date, expiry_date.
JSON only.""",

    "passport": """Extract all text from the following OCR output of a passport.
Return JSON with: full_name, passport_number, nationality, date_of_birth, gender, issue_date, expiry_date, mrz_line1, mrz_line2.
JSON only.""",


"thanawiya_amma": """أنت نظام متخصص في استخراج البيانات من شهادة الثانوية العامة المصرية.

المهمة:
تحليل نص OCR لشهادة الثانوية العامة واستخراج البيانات بدقة.

قواعد مهمة:

1) تنسيق الدرجات في الجدول غالباً يكون بهذا الشكل:
٦٠١٣٠
٤٠١٢٠
٥٠١٢٥

وهذا يعني:
الدرجة / الدرجة النهائية

مثال:
٦٠١٣٠ → الدرجة = 60 ، الدرجة_النهائية = 130
٤٠١٢٠ → الدرجة = 40 ، الدرجة_النهائية = 120
٥٠١٢٥ → الدرجة = 50 ، الدرجة_النهائية = 125

2) لا تعتبر أول رقم في الجدول هو المجموع.
غالباً يظهر المجموع في الجدول كرقم مثل:
٣٠١٢٥

لكن هذا ليس المجموع الحقيقي.

3) المجموع الحقيقي يكون مكتوب صراحة في الشهادة مثل:
المجموع: 250
أو
المجموع الكلي: 250

4) لا تحسب المجموع من المواد.
استخرج فقط الرقم المكتوب كمجموع في الوثيقة.

5) المواد التالية لا تضاف للمجموع:
- التربية الدينية
- التربية الوطنية

إذا كانت النتيجة مكتوبة "إجتياز" فاستخرجها كالتالي:

{
"المادة": "التربية الدينية",
"النتيجة": "إجتياز"
}

6) إذا كان النص غير واضح ضع القيمة null.

استخرج البيانات التالية:

البيانات الشخصية:
- اسم الطالب
- رقم الجلوس
- الرقم القومي
- المدرسة
- الإدارة التعليمية
- المديرية
- اللغة الأولى
- اللغة الثانية

الدرجات:
استخرج قائمة المواد مع:

{
"المادة": "",
"الدرجة": "",
"الدرجة_النهائية": ""
}

المواد غير المضافة للمجموع:

{
"المادة": "",
"النتيجة": "إجتياز"
}

الإجمالي:
- المجموع_الكلي
- الحالة (ناجح / راسب)

معلومات إضافية:
- رقم الشهادة
- يوجد باركود (true/false)
- يوجد صورة (true/false)
- يوجد ختم رسمي (true/false)

أعد النتيجة في JSON فقط بدون أي شرح.
""",

"ig_transcript": """Extract all data from the following OCR output of an IGCSE/Cambridge transcript.
Return JSON with: student_name, center_number, candidate_number, subjects (array with name, grade, mark), exam_session.
JSON only.""",

"american_transcript": """Extract all data from the following OCR output of an American school transcript.
Return JSON with: student_name, school, grade_level, gpa, courses (array with name, grade, credits), graduation_date.
JSON only.""",

"detect": """Based on the following OCR text, determine the document type.
Reply with ONLY one of these exact words:
thanawiya_amma, national_id, passport, ig_transcript, american_transcript""",
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
    messages = [
        {"role": "user", "content": f"{PROMPTS['detect']}\n\n--- OCR Text ---\n{ocr_text}"}
    ]
    response = client.chat.complete(model="mistral-large-latest", messages=messages)
    detected = response.choices[0].message.content.strip().lower()
    # Clean up — the model may wrap in quotes or add punctuation
    for valid in ["thanawiya_amma", "national_id", "passport", "ig_transcript", "american_transcript"]:
        if valid in detected:
            return valid
    return None


# ════════════════════════════════════════════════════
# 📂 SET YOUR FILE PATH HERE
# ════════════════════════════════════════════════════
FILE_PATH = r"C:\Users\zyada\Desktop\ZC\Spring 2026\CSAI 499\Testing OCR IMAGES\images.jpg"  # ← Change this to your file path
# ════════════════════════════════════════════════════

if not os.path.exists(FILE_PATH):
    print(f"❌ File not found: {FILE_PATH}")
else:
    print(f"📂 Processing: {FILE_PATH}\n")

    # ── Step 1: Run Mistral OCR ──
    if is_pdf(FILE_PATH):
        print("📄 PDF detected — running Mistral OCR...")
        pages = ocr_pdf(FILE_PATH)
    else:
        print("🖼️ Image detected — running Mistral OCR...")
        pages = ocr_image(FILE_PATH)

    # Combine all page markdown
    full_text = ""
    for page in pages:
        full_text += f"\n\n## Page {page.index + 1}\n\n{page.markdown}"
        print(f"  ✅ Page {page.index + 1} OCR complete")

    print(f"\n📝 Total pages processed: {len(pages)}")

    # ── Step 2: Auto-detect document type ──
    print("\n🔍 Auto-detecting document type...")
    doc_type = detect_doc_type(full_text)

    if doc_type:
        print(f"📄 Detected: {doc_type}")
    else:
        doc_type = prompt_doc_type()
        print(f"📄 Selected: {doc_type}")

    # ── Step 3: Structured extraction ──
    print(f"\n📋 Extracting structured data as '{doc_type}'...")

    if len(pages) == 1:
        result, raw = extract_structured(full_text, PROMPTS[doc_type])
        result = force_convert_numerals(result)

        print("\n" + "=" * 60)
        print("📊 EXTRACTED DATA (ERP Auto-Fill Ready)")
        print("=" * 60)
        print(json.dumps(result, ensure_ascii=False, indent=2))

        print("\n" + "-" * 60)
        print("🔤 Raw OCR Markdown:")
        print("-" * 60)
        print(full_text)
    else:
        # Process each page separately for multi-page PDFs
        all_results = []
        for page in pages:
            page_text = page.markdown
            result, raw = extract_structured(page_text, PROMPTS[doc_type])
            result = force_convert_numerals(result)
            all_results.append(result)
            print(f"  ✅ Page {page.index + 1} structured")

        print("\n" + "=" * 60)
        print("📊 EXTRACTED DATA — ALL PAGES (ERP Auto-Fill Ready)")
        print("=" * 60)
        for i, res in enumerate(all_results):
            print(f"\n━━━ Page {i + 1} ━━━")
            print(json.dumps(res, ensure_ascii=False, indent=2))

        print("\n" + "-" * 60)
        print("🔤 Raw OCR Markdown:")
        print("-" * 60)
        print(full_text)