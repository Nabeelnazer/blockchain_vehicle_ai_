import cv2
from ultralytics import YOLO

class NumberPlateDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect_plates(self, frame):
        results = self.model(frame)
        # Extract bounding boxes and confidence scores
        plates = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                confidence = box.conf[0]
                class_id = int(box.cls[0])
                if class_id == 0 and confidence > 0.5:
                    plates.append((x1, y1, x2, y2))
        return plates
