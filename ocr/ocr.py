import cv2
from paddleocr import PaddleOCR
import re
from collections import deque
import numpy as np

class OCRStabilizer:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')

    def get_plate_number(self, image):
        result = self.ocr.ocr(image, cls=True)
        # Process result to extract plate number
        return plate_number
