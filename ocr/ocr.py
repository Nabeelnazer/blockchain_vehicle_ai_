from paddleocr import PaddleOCR
import cv2
import numpy as np
from PIL import Image

class OCRProcessor:
    def __init__(self, lang='en'):
        self.ocr = PaddleOCR(use_angle_cls=True, lang=lang)
        
    def process_image(self, image_input):
        """
        Process an image and return the OCR results
        Args:
            image_input: Can be either a file path or a PIL Image object
        """
        try:
            # Handle different input types
            if isinstance(image_input, str):
                img = cv2.imread(image_input)
                if img is None:
                    raise ValueError(f"Unable to load image at {image_input}")
            elif isinstance(image_input, Image.Image):
                img = cv2.cvtColor(np.array(image_input), cv2.COLOR_RGB2BGR)
            else:
                raise ValueError("Input must be either a file path or PIL Image object")
            
            # Run OCR
            result = self.ocr.ocr(img, cls=True)
            
            # Format results
            extracted_text = []
            if result is not None:  # Add null check
                for line in result:
                    for word_info in line:
                        text = word_info[1][0]  # Get the text
                        confidence = word_info[1][1]  # Get the confidence score
                        extracted_text.append({
                            'text': text,
                            'confidence': confidence,
                            'bbox': word_info[0]
                        })
                    
            return extracted_text
            
        except Exception as e:
            raise Exception(f"OCR processing failed: {str(e)}")
