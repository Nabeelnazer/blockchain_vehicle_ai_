import cv2
import numpy as np
from ultralytics import YOLO
from paddleocr import PaddleOCR

class NumberPlateDetector:
    def __init__(self, yolo_model_path='best.pt'):
        """
        Initialize detector with YOLO and PaddleOCR
        """
        # YOLO for plate detection
        self.yolo_model = YOLO(yolo_model_path)
        
        # PaddleOCR for plate reading
        self.ocr = PaddleOCR(
            use_angle_cls=True,  # Enable angle classification
            lang='en',           # Language
            show_log=False       # Disable verbose logging
        )
    
    def detect_plates(self, frame):
        """
        Detect plates using YOLO
        """
        results = self.yolo_model(frame)
        plates = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                confidence = box.conf[0]
                class_id = int(box.cls[0])
                
                # Confidence and class filtering
                if class_id == 0 and confidence > 0.5:
                    plates.append((int(x1), int(y1), int(x2), int(y2)))
        
        return plates
    
    def process_plate(self, plate_img):
        """
        Process plate image with PaddleOCR
        """
        try:
            # Perform OCR on plate image
            results = self.ocr.ocr(plate_img, cls=True)
            
            if results and results[0]:
                text = results[0][0][1][0]  # Detected text
                confidence = results[0][0][1][1]  # Confidence score
                
                # Clean and validate plate number
                cleaned_text = self._clean_plate_text(text)
                
                return {
                    'text': cleaned_text,
                    'confidence': confidence
                }
            
            return None
        except Exception as e:
            print(f"Plate processing error: {e}")
            return None
    
    def _clean_plate_text(self, text):
        """
        Clean and validate plate number
        """
        # Remove non-alphanumeric characters
        import re
        cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
        
        # Indian plate validation regex patterns
        indian_plate_patterns = [
            r'^KL\d{2}[A-Z]{1,2}\d{4}$',   # Kerala
            r'^KA\d{2}[A-Z]{1,2}\d{4}$',   # Karnataka
            r'^TN\d{2}[A-Z]{1,2}\d{4}$',   # Tamil Nadu
            r'^AP\d{2}[A-Z]{1,2}\d{4}$',   # Andhra Pradesh
            r'^TS\d{2}[A-Z]{1,2}\d{4}$',   # Telangana
            r'^MH\d{2}[A-Z]{1,2}\d{4}$',   # Maharashtra
            r'^DL\d{2}[A-Z]{1,2}\d{4}$',   # Delhi
        ]
        
        # Check against patterns
        if any(re.match(pattern, cleaned) for pattern in indian_plate_patterns):
            # Format plate number
            return f"{cleaned[:2]} {cleaned[2:4]} {cleaned[4:6]} {cleaned[6:]}"
        
        return None
