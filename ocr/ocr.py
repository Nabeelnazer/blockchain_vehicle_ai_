import cv2
import numpy as np
import re
import easyocr
from collections import deque

class OCRStabilizer:
    def __init__(self, lang=['en']):
        # Initialize EasyOCR
        self.reader = easyocr.Reader(lang)
        
        # History for stabilizing detections
        self.history = deque(maxlen=5)
    
    def preprocess_image(self, image):
        """
        Preprocess image for better OCR detection
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return thresh
    
    def clean_plate_text(self, text):
        """
        Clean and format detected text
        """
        # Remove non-alphanumeric characters
        cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
        
        # Kerala plate format validation (optional)
        if cleaned.startswith('KL'):
            # Try to format as KL DD XX NNNN
            if len(cleaned) >= 8:
                return f"KL {cleaned[2:4]} {cleaned[4:6]} {cleaned[6:]}"
        
        return cleaned
    
    def get_stable_plate_number(self, frame):
        """
        Get stable plate number reading
        """
        try:
            # Preprocess image
            processed_frame = self.preprocess_image(frame)
            
            # Perform OCR
            results = self.reader.readtext(processed_frame)
            
            # Process detected texts
            detected_texts = []
            for detection in results:
                text = detection[1]  # Detected text
                confidence = detection[2]  # Confidence score
                
                # Clean text
                cleaned_text = self.clean_plate_text(text)
                
                if cleaned_text and len(cleaned_text) >= 4:
                    detected_texts.append({
                        'text': cleaned_text,
                        'confidence': confidence
                    })
            
            # If no texts detected, return None
            if not detected_texts:
                return None
            
            # Get the most confident text
            best_text = max(detected_texts, key=lambda x: x['confidence'])
            
            # Add to history
            self.history.append(best_text['text'])
            
            # Check for stable reading
            from collections import Counter
            counts = Counter(self.history)
            most_common = counts.most_common(1)[0]
            
            # If we have a consistent reading
            if most_common[1] >= 2:
                return most_common[0]
            
            return None
        
        except Exception as e:
            print(f"OCR Error: {str(e)}")
            return None
