# import cv2
# import pytesseract
# from ultralytics import YOLO
# import easyocr
# import numpy as np
# pytesseract.pytesseract.tesseract_cmd = r"Tesseract-OCR/tesseract.exe"
# def nid_ocr(image_path):
#     img = cv2.imread(image_path)
#     if img is None: return "Error: Image not found."

#     b, g, r = cv2.split(img)
#     thresh = cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#                                    cv2.THRESH_BINARY_INV, 25, 15)

#     kernel = np.ones((2,2), np.uint8)
#     cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
#     input_for_ocr = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)

#     # 2. Initialize and Read with DETAIL=1
#     reader = easyocr.Reader(['ar'])
#     # detail=1 returns [[box, text, confidence], ...]
#     results = reader.readtext(input_for_ocr, detail=1)

#     # 3. Setup Mapping for Display
#     mapping = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')

#     # 4. Plotting the individual detections
#     num_detections = len(results)
#     if num_detections > 0:
#         # fig, axes = plt.subplots(1, num_detections, figsize=(15, 3))
#         # Ensure axes is an array even if only 1 digit is found
#         if num_detections == 1: axes = [axes]

#         full_arabic = ""
#         for i, (bbox, text, prob) in enumerate(results):
#             # Extract coordinates for cropping: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
#             (tl, tr, br, bl) = bbox
#             x_min, y_min = int(tl[0]), int(tl[1])
#             x_max, y_max = int(br[0]), int(br[1])

#             # Crop the digit from the 'cleaned' image
#             digit_crop = cleaned[y_min:y_max, x_min:x_max]

#             # Plot
#             if digit_crop.size > 0:
#                 axes[i].imshow(digit_crop, cmap='gray')
#                 western_digit = text.translate(mapping)
#                 axes[i].set_title(f"OCR: {text}\n({western_digit})", fontsize=10)
#             axes[i].axis('off')

#             full_arabic += text

#         # plt.tight_layout()
#         # plt.show()
#     else:
#         print("No digits detected.")
#         full_arabic = ""

#     # 5. Final Outputs (Reversed for correct reading order)
#     arabic_final = full_arabic
#     western_final = ""
#     j = ""
#     for i in arabic_final.split(" "):
#       k = ''.join(reversed(i))
#       # print(k)
#       j += k

#     ll = ''.join(reversed(j))
#     for i in ll:
#       if i == "٠":
#         western_final+="0"
#       elif i == "١":
#         western_final+="1"
#       elif i == "٢":
#         western_final+="2"
#       elif i == "٣":
#         western_final+="3"
#       elif i == "٤":
#         western_final+="4"
#       elif i == "٥":
#         western_final+="5"
#       elif i == "٦":
#         western_final+="6"
#       elif i == "٧":
#         western_final+="7"
#       elif i == "٨":
#         western_final+="8"
#       elif i == "٩":
#         western_final+="9"
#       else:
#         western_final+= " "

#     return western_final


# uploaded = files.upload()
# image_path = next(iter(uploaded))

# model_id_card = YOLO('models/detect_id_card.pt')
# model_job = YOLO('models/detect_odjects.pt')
# def extract_text(image, bbox, lang='ara'):

#     x1, y1, x2, y2 = bbox
#     cropped_image = image[y1:y2, x1:x2]

    
#     gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
#     _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

#     custom_config = r'--oem 3 --psm 6'

#     text = pytesseract.image_to_string(thresh, lang=lang, config=custom_config)
#     return text.strip()

# # Function to plot image with bounding boxes
# # def plot_image_with_boxes(image, boxes):
#     # plt.figure(figsize=(10, 10))
#     # plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#     # ax = plt.gca()
#     # for box in boxes:
#         # x1, y1, x2, y2 = [int(coord) for coord in box]
#         # rect = plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, color='red', linewidth=2)
#         # ax.add_patch(rect)
#     # plt.show()

# # Function to detect ID card using the ID card detection model
# def detect_id_card(image_path, model):
#     results = model(image_path)
#     image = cv2.imread(image_path)

#     id_card_bboxes = []
#     for result in results:
#         # Extract bounding boxes
#         id_card_bboxes.extend([box.xyxy[0].tolist() for box in result.boxes])

#     return image, id_card_bboxes

# # Function to process ID card image and extract job field
# def process_image(image_path, model_id_card, model_job):
#     # Detect ID card
#     res = {}
#     image, id_card_bboxes = detect_id_card(image_path, model_id_card)

#     # Assuming only one ID card detected, process the first one
#     if id_card_bboxes:
#         bbox = id_card_bboxes[0]  # Get the first detected ID card bbox

#         # Crop the ID card region
#         x1, y1, x2, y2 = [int(coord) for coord in bbox]
#         id_card_image = image[y1:y2, x1:x2]

#         # Use the cropped ID card image as input for the job detection model
#         results = model_job(id_card_image)  # Pass the cropped image directly

#         # Loop through the results
#         job = ''
#         for result in results:

#             # Display the results
#             # result.show()  # Shows the image with bounding boxes

#             # Save the output image
#             output_path = '/content/job_output.jpg'
#             result.save(output_path)

#             # Visualize the saved output image
#             # display(Image(filename=output_path))

#             # Extract bounding boxes and class names
#             boxes = [box.xyxy[0].tolist() for box in result.boxes]
#             # plot_image_with_boxes(id_card_image, boxes)  # Use id_card_image for plotting

#             # Extract text for the "job" field
#             for box in result.boxes:
#                 bbox = box.xyxy[0].tolist()  # Get bounding box coordinates
#                 class_id = int(box.cls[0].item())  # Get class ID
#                 class_name = result.names[class_id]  # Get class name

#                 # Convert bounding box coordinates to integers
#                 bbox = [int(coord) for coord in bbox]

#                 if class_name == 'nid' or class_name == "back_nid":

#                   x1, y1, x2, y2 = bbox

#                   # Crop ONLY the detected region
#                   specific_region = id_card_image[y1:y2, x1:x2]

#                   # Show it (optional)
#                   # cv2_imshow(specific_region)

#                   # Save it
#                   cv2.imwrite("nid_region.png", specific_region)

#                   # OCR only this region
#                   nid = nid_ocr("nid_region.png")
#                   res[class_name] = nid
#                 else:
#                   text = extract_text(id_card_image, bbox, lang='ara')
#                   res[class_name] = text

#         # print(f"Job: {job}")
#     else:
#         print("No ID card detected")
#     return res

# process_image(image_path, model_id_card, model_job)


from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)