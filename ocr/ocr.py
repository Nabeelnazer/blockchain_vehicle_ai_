import cv2
from paddleocr import PaddleOCR
import re
from collections import deque
import numpy as np

class OCRStabilizer:
    def __init__(self, languages=['en'], confidence_threshold=0.6, stability_attempts=3):
        # Initialize PaddleOCR
        self.ocr = PaddleOCR(use_angle_cls=True, lang=languages[0])  # use_angle_cls for better accuracy
        self.confidence_threshold = confidence_threshold
        self.stability_attempts = stability_attempts
    
    def preprocess_plate_image(self, plate_image):
        """
        Advanced image preprocessing for better OCR
        """
        # Convert to grayscale
        gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return thresh
    
    def get_stable_plate_number(self, plate_image):
        # Preprocess image
        processed_image = self.preprocess_plate_image(plate_image)
        
        # Collect multiple readings
        readings = []
        
        for _ in range(self.stability_attempts):
            # Perform OCR
            results = self.ocr.ocr(processed_image, cls=True)
            
            for result in results:
                for line in result:
                    text, confidence = line[1][0], line[1][1]
                    
                    # Filter by confidence
                    if confidence > self.confidence_threshold:
                        readings.append(text)
        
        # Determine most consistent reading
        if readings:
            return self._get_most_consistent_reading(readings)
        
        return None
    
    def _get_most_consistent_reading(self, readings):
        """
        Advanced reading selection strategy
        """
        # If multiple readings, use most frequent
        if len(set(readings)) > 1:
            from collections import Counter
            most_common = Counter(readings).most_common(1)
            return most_common[0][0]
        
        # If all readings are the same, return the first
        return readings[0]
    
    def clean_plate_number(self, plate_number):
        """
        Clean and standardize plate number
        """
        return ''.join(char for char in plate_number if char.isalnum())
