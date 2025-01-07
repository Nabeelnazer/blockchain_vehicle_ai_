import cv2
import easyocr
import re
from collections import deque
import numpy as np

class OCRStabilizer:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])
        self.history = deque(maxlen=5)
        self.kerala_pattern = re.compile(r'^KL\s*\d{2}\s*[A-Z]{2}\s*\d{4}$')
        
    def preprocess_plate_image(self, plate_image):
        """Enhanced preprocessing for license plates"""
        # Convert to grayscale
        gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        # Dilate to connect components
        kernel = np.ones((2,2), np.uint8)
        dilated = cv2.dilate(denoised, kernel, iterations=1)
        
        return dilated

    def combine_multiline_text(self, results):
        """Combine multiple text lines into one plate number"""
        if not results:
            return None, 0
            
        # Sort results by vertical position (y-coordinate)
        sorted_results = sorted(results, key=lambda x: x[0][0][1])  # Sort by y-coordinate
        
        combined_text = ' '.join(result[1] for result in sorted_results)
        avg_confidence = sum(result[2] for result in sorted_results) / len(sorted_results)
        
        return combined_text, avg_confidence

    def clean_plate_text(self, text):
        """Clean and format detected text"""
        if not text:
            return None
            
        # Remove unwanted characters and convert to uppercase
        text = re.sub(r'[^A-Z0-9]', '', text.upper())
        
        # Try to extract Kerala plate pattern
        kl_match = re.search(r'KL\s*(\d{2})\s*([A-Z]{2})\s*(\d{1,4})', text)
        if kl_match:
            district = kl_match.group(1)
            series = kl_match.group(2)
            number = kl_match.group(3).zfill(4)  # Pad numbers to 4 digits
            return f"KL {district} {series} {number}"
        
        # For other text, clean and format with spaces
        return ' '.join(text[i:i+4] for i in range(0, len(text), 4)).strip()

    def get_stable_plate_number(self, frame):
        """Get stable plate number reading"""
        try:
            # Process frame
            processed_image = self.preprocess_plate_image(frame)
            
            # Perform OCR
            results = self.reader.readtext(processed_image)
            
            if results:
                # Combine multi-line text
                text, confidence = self.combine_multiline_text(results)
                
                # Clean and format text
                cleaned_text = self.clean_plate_text(text)
                
                if cleaned_text:
                    # Add to history
                    self.history.append(cleaned_text)
                    
                    # Check if we have a stable reading
                    if len(self.history) >= 2:  # Reduced from 3 to 2 for faster response
                        # Get most common reading in history
                        from collections import Counter
                        counts = Counter(self.history)
                        most_common = counts.most_common(1)[0]
                        
                        # If we have a consistent reading with good confidence
                        if most_common[1] >= 2 and confidence > 0.3:  # Lowered confidence threshold
                            return most_common[0]
            
            return None
            
        except Exception as e:
            print(f"Error in OCR: {str(e)}")
            return None