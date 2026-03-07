import cv2
import os
import logging
from app.services.nid_service import nid_ocr
from app.services.tesseract_service import extract_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def detect_id_card(image_path, model):
    """Detect ID card in the image using YOLO model."""
    try:
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return None, []

        results = model(image_path)
        image = cv2.imread(image_path)

        if image is None:
            logger.error(f"Failed to read image: {image_path}")
            return None, []

        id_card_bboxes = []

        for result in results:
            if result.boxes is not None and len(result.boxes) > 0:
                id_card_bboxes.extend(
                    [box.xyxy[0].tolist() for box in result.boxes]
                )

        return image, id_card_bboxes

    except Exception as e:
        logger.error(f"Error detecting ID card: {str(e)}")
        return None, []


def process_image(image_path, model_id_card, model_job):
    """Process the uploaded image and extract text using OCR."""
    res = {}

    try:
        image, id_card_bboxes = detect_id_card(
            image_path,
            model_id_card
        )

        if image is None:
            return {"error": "Failed to read or process the image"}

        if not id_card_bboxes:
            return {"error": "No ID card detected in the image"}

        if id_card_bboxes:

            bbox = id_card_bboxes[0]

            x1, y1, x2, y2 = map(int, bbox)

            # Validate bounding box coordinates
            if x1 >= x2 or y1 >= y2:
                return {"error": "Invalid ID card bounding box coordinates"}

            id_card_image = image[y1:y2, x1:x2]

            # Check if cropped image is valid
            if id_card_image is None or id_card_image.size == 0:
                return {"error": "Failed to crop ID card from image"}

            results = model_job(id_card_image)

            for result in results:

                if result.boxes is None or len(result.boxes) == 0:
                    continue

                for box in result.boxes:

                    bbox = box.xyxy[0].tolist()

                    class_id = int(box.cls[0])

                    class_name = result.names[class_id]

                    bbox = list(map(int, bbox))

                    # Validate bbox coordinates
                    if len(bbox) < 4 or bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
                        logger.warning(f"Invalid bbox for {class_name}: {bbox}")
                        continue

                    # Ensure bbox is within image bounds
                    bbox[0] = max(0, bbox[0])
                    bbox[1] = max(0, bbox[1])
                    bbox[2] = min(id_card_image.shape[1], bbox[2])
                    bbox[3] = min(id_card_image.shape[0], bbox[3])

                    if class_name in ['nid','back_nid']:

                        try:
                            region = id_card_image[
                                bbox[1]:bbox[3],
                                bbox[0]:bbox[2]
                            ]

                            if region is None or region.size == 0:
                                logger.warning(f"Empty region for {class_name}")
                                res[class_name] = ""
                                continue

                            nid_region_path = "nid_region.png"
                            cv2.imwrite(nid_region_path, region)

                            nid = nid_ocr(nid_region_path)

                            res[class_name] = nid if nid else ""

                        except Exception as e:
                            logger.error(f"Error processing NID region: {str(e)}")
                            res[class_name] = ""

                        finally:
                            # Always cleanup the temporary file
                            if os.path.exists("nid_region.png"):
                                try:
                                    os.remove("nid_region.png")
                                except Exception as e:
                                    logger.warning(f"Failed to remove temp file: {str(e)}")

                    else:

                        try:
                            text = extract_text(
                                id_card_image,
                                bbox
                            )

                            res[class_name] = text if text else ""

                        except Exception as e:
                            logger.error(f"Error extracting text for {class_name}: {str(e)}")
                            res[class_name] = ""

        if not res:
            return {"error": "No text extracted from the ID card"}

        return res

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return {"error": f"Processing failed: {str(e)}"}
    finally:
        # Cleanup any leftover temporary files
        if os.path.exists("nid_region.png"):
            try:
                os.remove("nid_region.png")
            except Exception:
                pass