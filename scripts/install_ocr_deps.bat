@echo off
echo Installing OCR Microservice Dependencies...
echo ============================================

cd "C:\Odoo\AI Models\OCR As Micro Service"

echo.
echo Installing with venv pip...
C:\Odoo\venv\Scripts\pip.exe install --upgrade pip

echo.
echo Installing FastAPI and Uvicorn...
C:\Odoo\venv\Scripts\pip.exe install fastapi==0.135.1 uvicorn==0.41.0 python-multipart==0.0.9

echo.
echo Installing CV and OCR libraries...
C:\Odoo\venv\Scripts\pip.exe install opencv-python-headless==4.8.1.78
C:\Odoo\venv\Scripts\pip.exe install pytesseract>=0.3.10
C:\Odoo\venv\Scripts\pip.exe install easyocr>=1.7.0
C:\Odoo\venv\Scripts\pip.exe install ultralytics==8.1.47
C:\Odoo\venv\Scripts\pip.exe install numpy==1.26.0

echo.
echo Installing PyTorch CPU version...
C:\Odoo\venv\Scripts\pip.exe install torch==2.5.1+cpu torchvision==0.20.1+cpu --extra-index-url https://download.pytorch.org/whl/cpu

echo.
echo ============================================
echo Installation complete!
echo ============================================
echo.
echo To start OCR service, run: make ocr-run
pause
