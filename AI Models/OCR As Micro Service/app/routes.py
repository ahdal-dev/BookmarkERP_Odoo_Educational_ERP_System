import os
from flask import Blueprint, request, render_template

from app.controllers.ocr_controller import process_uploaded_image

main = Blueprint("main", __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@main.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@main.route("/ocr", methods=["POST"])
def ocr():
    file = request.files["file"]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    # Process image (YOLO + OCR)
    result = process_uploaded_image(path)

    # --- DELETE TEMPORARY IMAGES ---
    
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            os.remove(os.path.join(UPLOAD_FOLDER, filename))
    # ------------------------------

    return render_template("index.html", result=result)