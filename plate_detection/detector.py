import cv2
import numpy as np
import re

class PlateDetector:
    def __init__(self, model_path='best.pt'):
        """
        Initialize plate detector using PaddleOCR
        """
        try:
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(
                use_angle_cls=True,  # Enable angle classification
                lang='en',           # Language
                show_log=False       # Disable verbose logging
            )
        except ImportError:
            raise ImportError("PaddleOCR is required. Please install with 'pip install paddleocr'")
    
    def detect_plates(self, frame):
        """
        Detect vehicle plates using PaddleOCR
        """
        try:
            results = self.ocr.ocr(frame, cls=True)
            plates = []
            for result in results:
                if result:
                    box = result[0][0]
                    x, y, w, h = self._get_bounding_box(box)
                    plates.append((x, y, w, h))
            return plates
        except Exception as e:
            print(f"PaddleOCR detection error: {e}")
            return []
    
    def _get_bounding_box(self, box):
        """
        Convert detection box to x, y, w, h format
        """
        x_coords = [point[0] for point in box]
        y_coords = [point[1] for point in box]
        
        x = min(x_coords)
        y = min(y_coords)
        w = max(x_coords) - x
        h = max(y_coords) - y
        
        return x, y, w, h
    
    def process_plate(self, plate_img):
        """
        Process and extract text from plate image
        """
        try:
            # Perform OCR on plate image
            results = self.ocr.ocr(plate_img, cls=True)
            
            # Extract and clean text
            if results and results[0]:
                text = results[0][0][1][0]  # Detected text
                confidence = results[0][0][1][1]  # Confidence score
                
                # Clean plate number
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
        Clean and format plate text
        """
        # Remove non-alphanumeric characters
        cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
        
        # Kerala plate format validation
        if cleaned.startswith('KL'):
            # Try to format as KL DD XX NNNN
            if len(cleaned) >= 8:
                return f"KL {cleaned[2:4]} {cleaned[4:6]} {cleaned[6:]}"
        
        return cleaned 