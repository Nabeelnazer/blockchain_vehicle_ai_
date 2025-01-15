import cv2
from ocr.ocr import OCRStabilizer
import os
from datetime import datetime

def test_ocr():
    # Initialize OCR
    ocr = OCRStabilizer()
    
    # Create output directory
    output_dir = 'ocr_results'
    os.makedirs(output_dir, exist_ok=True)
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
        
    print("Camera opened successfully. Running OCR...")
    print("Testing OCR. Will save results when text is detected.")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    processed_plates = set()  # Keep track of processed plates
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            # Get plate number
            plate_number = ocr.get_stable_plate_number(frame)
            
            if plate_number and plate_number not in processed_plates:
                # Save the frame with detected text
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Save original frame
                orig_filename = f"{output_dir}/original_{plate_number}_{timestamp}.jpg"
                cv2.imwrite(orig_filename, frame)
                
                # Create annotated frame
                display_frame = frame.copy()
                cv2.putText(display_frame, f"Detected: {plate_number}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Save annotated frame
                filename = f"{output_dir}/detected_{plate_number}_{timestamp}.jpg"
                cv2.imwrite(filename, display_frame)
                
                print(f"\nDetected plate number: {plate_number}")
                print(f"Saved original to: {orig_filename}")
                print(f"Saved annotated to: {filename}")
                print("-" * 50)
                
                processed_plates.add(plate_number)
            
    except KeyboardInterrupt:
        print("\nStopping OCR test...")
    finally:
        cap.release()
        print("\nOCR test completed. Check the ocr_results directory for saved images.")
        print(f"Total unique plates detected: {len(processed_plates)}")
        if processed_plates:
            print("\nDetected plates:")
            for plate in processed_plates:
                print(f"- {plate}")

if __name__ == "__main__":
    test_ocr()