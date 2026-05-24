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

def process_uploaded_image(image_path):
    """
    Process uploaded image/PDF and extract text using OCR models.
    
    Detects document type automatically and extracts structured data.
    Supports: national_id, passport, thanawiya_amma, ig_transcript, american_transcript
    """
    try:
        if not os.path.exists(image_path):
            logger.error(f"File not found: {image_path}")
            return {"error": f"File not found: {image_path}"}

        logger.info(f"Processing file with multi-document detection: {image_path}")
        
        # Use Mistral OCR for comprehensive document detection
        # This automatically detects document type and extracts structured data
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
        try:
            if is_pdf(image_path):
                logger.info("PDF detected — running Mistral OCR...")
                pages = ocr_pdf(image_path)
            else:
                logger.info("Image detected — running Mistral OCR...")
                pages = ocr_image(image_path)
        except Exception as e:
            logger.error(f"Mistral OCR failed: {str(e)}")
            return {"error": f"OCR processing failed: {str(e)}"}

        # Combine all page markdown
        full_text = ""
        for page in pages:
            full_text += f"\n\n## Page {page.index + 1}\n\n{page.markdown}"
            logger.info(f"Page {page.index + 1} OCR complete")

        logger.info(f"Total pages processed: {len(pages)}")

        # Step 2: Auto-detect or validate document type
        if doc_type is None:
            logger.info("Auto-detecting document type...")
            detected_type = detect_doc_type(full_text)
            if detected_type:
                doc_type = detected_type
                logger.info(f"Document type detected: {doc_type}")
            else:
                logger.warning("Could not auto-detect document type")
                return {"error": "Could not automatically detect document type. Please specify doc_type parameter."}
        else:
            logger.info(f"Using specified document type: {doc_type}")

        # Validate doc_type is in PROMPTS
        if doc_type not in PROMPTS:
            return {"error": f"Invalid document type: {doc_type}. Valid types: {list(PROMPTS.keys())}"}

        # Step 3: Structured extraction
        logger.info(f"Extracting structured data as '{doc_type}'...")

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
            for page in pages:
                page_text = page.markdown
                result, raw = extract_structured(page_text, PROMPTS[doc_type])
                result = force_convert_numerals(result)
                all_results.append(result)
                logger.info(f"Page {page.index + 1} structured extraction complete")

            logger.info(f"Extraction complete for {len(pages)} page document")
            return {
                "document_type": doc_type,
                "extracted_data": all_results,
                "pages_processed": len(pages)
            }

    except Exception as e:
        logger.error(f"Error in process_uploaded_image_with_mistral: {str(e)}")
        return {"error": f"Processing failed: {str(e)}"}