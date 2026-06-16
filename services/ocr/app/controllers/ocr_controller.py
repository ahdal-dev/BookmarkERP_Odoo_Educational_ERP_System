from app.services.processing_service import process_image, detect_id_card
from app.services.detection_service import model_id_card, model_job
from app.services.backup_model import (
    ocr_image, 
    ocr_pdf, 
    detect_doc_type, 
    extract_structured,
    force_convert_numerals,
    PROMPTS,
    is_pdf
)
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_with_yolo_only(image_path):
    """
    Process uploaded image using YOLO detection only.
    Detects National ID using YOLO models.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Dictionary with extracted data or error message
    """
    try:
        if not os.path.exists(image_path):
            logger.error(f"File not found: {image_path}")
            return {"error": f"File not found: {image_path}"}

        # Check if models are loaded
        if model_id_card is None:
            logger.error("ID card detection model is not loaded")
            return {"error": "ID card detection model not available"}

        if model_job is None:
            logger.error("Object detection model is not loaded")
            return {"error": "Object detection model not available"}

        logger.info(f"Using YOLO detection...")
        
        # Detect National ID
        image, id_card_bboxes = detect_id_card(image_path, model_id_card)
        
        # If National ID detected, process with YOLO pipeline
        if id_card_bboxes and len(id_card_bboxes) > 0:
            logger.info(f"National ID detected! Processing with YOLO pipeline...")
            result = process_image(image_path, model_id_card, model_job)
            result["detection_method"] = "YOLO"
            return result
        else:
            logger.warning(f"No National ID detected with YOLO")
            return {"error": "No National ID detected", "detection_method": "YOLO"}

    except Exception as e:
        logger.error(f"Error in process_with_yolo_only: {str(e)}")
        return {"error": f"YOLO detection failed: {str(e)}", "detection_method": "YOLO"}


def process_with_mistral_only(image_path, doc_type=None):
    """
    Process uploaded image using Mistral OCR detection only.
    
    Args:
        image_path: Path to the image/PDF file
        doc_type: Optional document type. If None, will auto-detect.
    
    Returns:
        Dictionary with extracted structured data or error message
    """
    try:
        if not os.path.exists(image_path):
            logger.error(f"File not found: {image_path}")
            return {"error": f"File not found: {image_path}"}

        logger.info(f"Using Mistral OCR detection...")
        result = process_uploaded_image_with_mistral(image_path, doc_type=doc_type)
        
        if isinstance(result, dict) and "error" not in result:
            result["detection_method"] = "Mistral"
        
        return result

    except Exception as e:
        logger.error(f"Error in process_with_mistral_only: {str(e)}")
        return {"error": f"Mistral detection failed: {str(e)}", "detection_method": "Mistral"}


def process_uploaded_image(image_path):
    """
    Process uploaded image and extract text using OCR models.
    
    Priority:
    1. Try to detect as National ID using YOLO models
    2. If not National ID, use Mistral OCR for other document types
    """
    try:
        if not os.path.exists(image_path):
            logger.error(f"File not found: {image_path}")
            return {"error": f"File not found: {image_path}"}

        # Check if models are loaded
        if model_id_card is None:
            logger.error("ID card detection model is not loaded")
            return {"error": "ID card detection model not available"}

        if model_job is None:
            logger.error("Object detection model is not loaded")
            return {"error": "Object detection model not available"}

        logger.info(f"Step 1: Attempting to detect National ID...")
        
        # Step 1: Try to detect National ID
        image, id_card_bboxes = detect_id_card(image_path, model_id_card)
        
        # If National ID detected, process with existing pipeline
        if id_card_bboxes and len(id_card_bboxes) > 0:
            logger.info(f"National ID detected! Processing with YOLO pipeline...")
            result = process_image(image_path, model_id_card, model_job)
            return result
        
        # Step 2: Not a National ID, fall back to Mistral OCR for other documents
        logger.info(f"National ID not detected. Attempting to detect other document types with Mistral OCR...")
        result = process_uploaded_image_with_mistral(image_path, doc_type=None)
        
        return result

    except Exception as e:
        logger.error(f"Error in process_uploaded_image: {str(e)}")
        return {"error": f"Failed to process image: {str(e)}"}


def process_uploaded_image_with_mistral(image_path, doc_type=None):
    """
    Process uploaded image with Mistral OCR and extract structured data.
    
    Args:
        image_path: Path to the image/PDF file
        doc_type: Optional document type. If None, will auto-detect.
    
    Returns:
        Dictionary with extracted structured data or error message
    """
    try:
        if not os.path.exists(image_path):
            logger.error(f"File not found: {image_path}")
            return {"error": f"File not found: {image_path}"}

        logger.info(f"Processing file with Mistral OCR: {image_path}")

        # Step 1: Run Mistral OCR
        pages = None
        try:
            if is_pdf(image_path):
                logger.info("PDF detected — running Mistral OCR...")
                pages = ocr_pdf(image_path)
            else:
                logger.info("Image detected — running Mistral OCR...")
                pages = ocr_image(image_path)
                
            if not pages:
                logger.error("No pages extracted from document")
                return {"error": "Failed to extract text from document"}
                
        except RuntimeError as re:
            logger.error(f"Mistral initialization error: {str(re)}")
            return {"error": f"OCR service unavailable: {str(re)}"}
        except Exception as e:
            logger.error(f"Mistral OCR failed: {str(e)}")
            return {"error": f"OCR processing failed: {str(e)}"}

        # Combine all page markdown
        full_text = ""
        try:
            for page in pages:
                if hasattr(page, 'markdown'):
                    full_text += f"\n\n## Page {page.index + 1}\n\n{page.markdown}"
                    logger.info(f"Page {page.index + 1} OCR complete")
                else:
                    logger.warning(f"Page object missing markdown attribute")
        except Exception as e:
            logger.error(f"Error processing pages: {e}")
            return {"error": f"Failed to process extracted pages: {str(e)}"}

        logger.info(f"Total pages processed: {len(pages)}")

        # Step 2: Auto-detect or validate document type
        if doc_type is None:
            logger.info("Auto-detecting document type...")
            try:
                detected_type = detect_doc_type(full_text)
                if detected_type:
                    doc_type = detected_type
                    logger.info(f"Document type detected: {doc_type}")
                else:
                    logger.warning("Could not auto-detect document type")
                    return {"error": "Could not automatically detect document type. Please specify doc_type parameter."}
            except RuntimeError as re:
                logger.error(f"Document detection error: {str(re)}")
                return {"error": f"Document detection failed: {str(re)}"}
            except Exception as e:
                logger.error(f"Error during document type detection: {e}")
                return {"error": f"Document type detection error: {str(e)}"}
        else:
            logger.info(f"Using specified document type: {doc_type}")

        # Validate doc_type is in PROMPTS
        if doc_type not in PROMPTS:
            valid_types = [k for k in PROMPTS.keys() if k != "detect"]
            return {"error": f"Invalid document type: {doc_type}. Valid types: {valid_types}"}

        # Step 3: Structured extraction
        logger.info(f"Extracting structured data as '{doc_type}'...")

        try:
            if len(pages) == 1:
                result, raw = extract_structured(full_text, PROMPTS[doc_type])
                result = force_convert_numerals(result)
                
                logger.info(f"Extraction complete for single page document")
                return {
                    "document_type": doc_type,
                    "extracted_data": result,
                    "raw_text": raw,
                    "pages_processed": 1
                }
            else:
                # Process each page separately for multi-page PDFs
                all_results = []
                for i, page in enumerate(pages):
                    try:
                        page_text = page.markdown if hasattr(page, 'markdown') else str(page)
                        result, raw = extract_structured(page_text, PROMPTS[doc_type])
                        result = force_convert_numerals(result)
                        all_results.append(result)
                        logger.info(f"Page {page.index + 1} structured extraction complete")
                    except Exception as page_error:
                        logger.error(f"Error extracting page {i + 1}: {page_error}")
                        all_results.append({"error": f"Failed to extract page {i + 1}"})

                logger.info(f"Extraction complete for {len(pages)} page document")
                return {
                    "document_type": doc_type,
                    "extracted_data": all_results,
                    "pages_processed": len(pages)
                }
                
        except RuntimeError as re:
            logger.error(f"Extraction runtime error: {str(re)}")
            return {"error": f"Extraction failed: {str(re)}"}
        except Exception as e:
            logger.error(f"Error in structured extraction: {str(e)}")
            return {"error": f"Extraction failed: {str(e)}"}

    except Exception as e:
        logger.error(f"Error in process_uploaded_image_with_mistral: {str(e)}")
        return {"error": f"Processing failed: {str(e)}"}