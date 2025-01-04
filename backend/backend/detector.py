import cv2
import numpy as np
from ultralytics import YOLO

class LicensePlateDetector:
    def __init__(self, model_path='../model/best.pt'):
        self.model = YOLO(model_path)

    def detect_plates(self, frame):
        # Detect license plates
        results = self.model(frame)[0]
        
        detected_plates = []
        for box in results.boxes:
            # Extract bounding box coordinates
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            confidence = box.conf[0].cpu().numpy()
            
            # Crop the license plate
            plate_img = frame[y1:y2, x1:x2]
            
            detected_plates.append({
                'coordinates': [x1, y1, x2, y2],
                'confidence': float(confidence)
            })
        
        return detected_plates

    def draw_detections(self, frame, detections):
        for det in detections:
            x1, y1, x2, y2 = det['coordinates']
            conf = det['confidence']
            
            # Draw rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Add confidence label
            label = f'Plate: {conf:.2f}'
            cv2.putText(frame, label, (x1, y1-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        return frame
