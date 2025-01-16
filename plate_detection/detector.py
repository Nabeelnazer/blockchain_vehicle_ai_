import cv2
from ultralytics import YOLO
from paddleocr import PaddleOCR
import os

class PlateDetector:
    def __init__(self):
        # Use the custom model from main directory
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'best.pt')
        self.plate_detector = YOLO(model_path)
        # Initialize PaddleOCR for text recognition
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
        
    def process_frame(self, frame):
        """Process a single frame to detect and read license plates"""
        # Detect plates using custom model (no need to specify classes)
        results = self.plate_detector(frame)
        
        plates_found = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                
                # Only process high confidence detections
                if confidence > 0.5:
                    # Extract plate region
                    plate_region = frame[y1:y2, x1:x2]
                    
                    # Perform OCR on plate region
                    ocr_result = self.ocr.ocr(plate_region, cls=True)
                    
                    if ocr_result and ocr_result[0]:
                        text = ocr_result[0][0][1][0]  # Get the text
                        ocr_confidence = ocr_result[0][0][1][1]  # Get confidence
                        
                        plates_found.append({
                            'text': text,
                            'confidence': ocr_confidence,
                            'detection_confidence': confidence,
                            'bbox': [x1, y1, x2, y2]
                        })
                        
                        # Draw rectangle around plate
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, f"{text} ({confidence:.2f})", 
                                  (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 
                                  0.9, (0, 255, 0), 2)
        
        return frame, plates_found 