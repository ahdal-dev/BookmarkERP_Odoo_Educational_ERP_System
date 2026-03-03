import cv2
import os
from app.services.nid_service import nid_ocr
from app.services.tesseract_service import extract_text


def detect_id_card(image_path, model):

    results = model(image_path)

    image = cv2.imread(image_path)

    id_card_bboxes = []

    for result in results:

        id_card_bboxes.extend(
            [box.xyxy[0].tolist() for box in result.boxes]
        )

    return image, id_card_bboxes



def process_image(image_path, model_id_card, model_job):

    res = {}

    image, id_card_bboxes = detect_id_card(
        image_path,
        model_id_card
    )

    if id_card_bboxes:

        bbox = id_card_bboxes[0]

        x1, y1, x2, y2 = map(int, bbox)

        id_card_image = image[y1:y2, x1:x2]

        results = model_job(id_card_image)

        for result in results:

            for box in result.boxes:

                bbox = box.xyxy[0].tolist()

                class_id = int(box.cls[0])

                class_name = result.names[class_id]

                bbox = list(map(int, bbox))

                if class_name in ['nid','back_nid']:

                    region = id_card_image[
                        bbox[1]:bbox[3],
                        bbox[0]:bbox[2]
                    ]

                    cv2.imwrite(
                        "nid_region.png",
                        region
                    )

                    nid = nid_ocr(
                        "nid_region.png"
                    )

                    res[class_name] = nid
                    if os.path.exists("nid_region.png"):
                        os.remove("nid_region.png")

                else:

                    text = extract_text(
                        id_card_image,
                        bbox
                    )

                    res[class_name] = text

    return res