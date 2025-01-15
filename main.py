from ultralytics import YOLO
import cv2

class NumberPlateDetector:
    def __init__(self, model_path):
        # Load the pre-trained YOLOv8 model
        self.model = YOLO(model_path)

    def detect_plates(self, frame):
        # Perform inference on the input frame
        results = self.model(frame)

        # Extract bounding boxes and confidence scores
        plates = []
        for result in results:
            # Iterate through detected objects
            for box in result.boxes:
                # Get the bounding box coordinates and confidence
                x1, y1, x2, y2 = box.xyxy[0]  # Get coordinates
                confidence = box.conf[0]      # Get confidence score
                class_id = int(box.cls[0])    # Get class ID

                # Assuming class_id 0 corresponds to number plates
                if class_id == 0 and confidence > 0.5:  # Adjust confidence threshold as needed
                    plates.append((x1, y1, x2, y2))

        return plates
