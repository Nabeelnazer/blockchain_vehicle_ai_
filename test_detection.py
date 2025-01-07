import cv2
from detection.yolo_detector import NumberPlateDetector
import numpy as np
import os
from datetime import datetime

def test_detection():
    # Initialize detector
    detector = NumberPlateDetector('best.pt')
    
    # Create output directory
    output_dir = 'detection_results'
    os.makedirs(output_dir, exist_ok=True)
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
        
    print("Camera opened successfully. Running detection...")
    
    frame_count = 0
    while frame_count < 100:  # Capture 100 frames
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
            
        # Detect plates
        plates = detector.detect_plates(frame)
        
        # Draw rectangles around detected plates
        for x, y, w, h in plates:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Plate", (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Add detection count
        cv2.putText(frame, f"Detected: {len(plates)}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Save frame if plates are detected
        if len(plates) > 0:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/detection_{timestamp}_{len(plates)}plates.jpg"
            cv2.imwrite(filename, frame)
            print(f"Found {len(plates)} plate(s). Saved to {filename}")
        
        frame_count += 1
    
    cap.release()
    print("Detection test completed. Check the detection_results directory for saved images.")

if __name__ == "__main__":
    test_detection()