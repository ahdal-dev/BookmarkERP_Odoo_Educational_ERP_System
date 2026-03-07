# OCR-Enabled Student Admission

## Overview
The Student Admission form now includes OCR (Optical Character Recognition) capability to automatically extract information from uploaded ID documents.

## Features
- **Auto-fill from ID Document**: Upload a national ID card photo and automatically populate:
  - National ID Number
  - Full Name
  - Address

## How to Use

### Method 1: Using the Server Action Button
1. Navigate to **Education → Students → Student Admission**
2. Click **Create** to start a new admission
3. In the "Quick Upload - Auto Fill with OCR" section, click **Upload an attachment**
4. Select a clear photo of the national ID card (JPG, PNG, or BMP format)
5. Click **Process ID Document** button
6. The system will process the image and auto-fill the fields below
7. Review and edit the auto-filled information if needed
8. Complete the remaining fields (Email, Phone, Date of Birth, etc.)
9. Click **Save**

### Method 2: Direct OCR Processing
- The form will automatically attempt to process the uploaded ID document
- Watch for notification messages indicating success or any errors
- Fields will be updated in real-time

## Requirements
- OCR Microservice must be running on `http://localhost:5000`
- Clear, well-lit photos of ID documents
- Supported image formats: JPG, JPEG, PNG, BMP, TIFF, WEBP

## Troubleshooting

### OCR Service Not Available
- Ensure the OCR microservice is running: `python run.py` in the OCR service directory
- Check that port 5000 is accessible
- Verify network connectivity

### Fields Not Auto-Filling
- Check that the uploaded image is clear and readable
- Ensure the ID document is properly aligned in the photo
- Try uploading a higher quality image
- Check the browser console for any JavaScript errors

### Supported ID Document Types
- National ID cards (front and back)
- Clear, unobstructed photos
- Proper lighting and contrast

## Technical Details
- **Model**: `education.student`
- **Controller**: `/education/ocr/process`
- **OCR Service**: FastAPI microservice with YOLOv8 and Tesseract OCR
- **Supported Languages**: Arabic and English
