from ultralytics import YOLO

model_id_card = YOLO('models/detect_id_card.pt')

model_job = YOLO('models/detect_odjects.pt')