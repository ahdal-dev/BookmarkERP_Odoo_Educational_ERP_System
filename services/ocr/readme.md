
- Tesseract OCR installed inside the Docker image (including Arabic language support).
- Enhanced error handling and validation for image processing
- Automatic cleanup of temporary files
- Comprehensive logging for debugging

---

## Features

- **ID Card Detection**: Automatically detects ID cards in uploaded images
- **Multi-language OCR**: Supports Arabic and English text extraction
- **NID Extraction**: Specialized extraction for National ID numbers
- **Robust Error Handling**: Validates images, bounding boxes, and handles processing errors gracefully
- **Health Check Endpoint**: `/health` endpoint for container orchestration
- **Automatic File Cleanup**: Removes temporary files after processing

---

## Error Handling

The microservice includes comprehensive error handling:

- **Invalid Images**: Returns error if image cannot be read or is empty
- **No ID Card Detected**: Returns error if no ID card is found in the image
- **Invalid Bounding Boxes**: Validates and clamps coordinates to prevent crashes
- **Model Loading Errors**: Checks if YOLO models are loaded before processing
- **File Format Validation**: Only accepts valid image formats (PNG, JPG, JPEG, BMP, TIFF, WEBP)
- **Automatic Cleanup**: Ensures temporary files are removed even if processing fails

---

## Build Docker Image

From the project root (where your `Dockerfile` is):

```bash
docker build -t ocr-microservice .