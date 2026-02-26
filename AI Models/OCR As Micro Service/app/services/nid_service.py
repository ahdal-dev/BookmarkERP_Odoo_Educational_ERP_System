import cv2
import easyocr
import numpy as np
def nid_ocr(image_path):
    img = cv2.imread(image_path)
    if img is None: return "Error: Image not found."

    b, g, r = cv2.split(img)
    thresh = cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 25, 15)

    kernel = np.ones((2,2), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    input_for_ocr = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)

    # 2. Initialize and Read with DETAIL=1
    reader = easyocr.Reader(['ar'])
    # detail=1 returns [[box, text, confidence], ...]
    results = reader.readtext(input_for_ocr, detail=1)

    # 3. Setup Mapping for Display
    mapping = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')

    # 4. Plotting the individual detections
    num_detections = len(results)
    if num_detections > 0:
        # fig, axes = plt.subplots(1, num_detections, figsize=(15, 3))
        # Ensure axes is an array even if only 1 digit is found
        # if num_detections == 1: axes = [axes]

        full_arabic = ""
        for i, (bbox, text, prob) in enumerate(results):
            # Extract coordinates for cropping: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            (tl, tr, br, bl) = bbox
            x_min, y_min = int(tl[0]), int(tl[1])
            x_max, y_max = int(br[0]), int(br[1])

            # Crop the digit from the 'cleaned' image
            digit_crop = cleaned[y_min:y_max, x_min:x_max]

            # Plot
            # if digit_crop.size > 0:
            #     axes[i].imshow(digit_crop, cmap='gray')
            #     western_digit = text.translate(mapping)
            #     axes[i].set_title(f"OCR: {text}\n({western_digit})", fontsize=10)
            # axes[i].axis('off')

            full_arabic += text

        # plt.tight_layout()
        # plt.show()
    else:
        print("No digits detected.")
        full_arabic = ""

    # 5. Final Outputs (Reversed for correct reading order)
    arabic_final = full_arabic
    western_final = ""
    j = ""
    for i in arabic_final.split(" "):
      k = ''.join(reversed(i))
      # print(k)
      j += k

    ll = ''.join(reversed(j))
    for i in ll:
      if i == "٠":
        western_final+="0"
      elif i == "١":
        western_final+="1"
      elif i == "٢":
        western_final+="2"
      elif i == "٣":
        western_final+="3"
      elif i == "٤":
        western_final+="4"
      elif i == "٥":
        western_final+="5"
      elif i == "٦":
        western_final+="6"
      elif i == "٧":
        western_final+="7"
      elif i == "٨":
        western_final+="8"
      elif i == "٩":
        western_final+="9"
      else:
        western_final+= " "

    return western_final