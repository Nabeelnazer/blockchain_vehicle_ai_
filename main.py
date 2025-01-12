import cv2
from detection.yolo_detector import NumberPlateDetector
from ocr.ocr import OCRStabilizer
from database.vehicle_log import VehicleLogger

class ParkingManagementSystem:
    def __init__(self, 
                 weights_path='yolo_weights.weights', 
                 config_path='yolo_config.cfg'):
        # Initialize YOLO Detector
        self.detector = NumberPlateDetector(weights_path, config_path)
        
        # Initialize PaddleOCR
        self.ocr_stabilizer = OCRStabilizer()
        
        # Initialize Vehicle Logger
        self.vehicle_logger = VehicleLogger({
            'database': 'parking_db',
            'user': 'your_username',
            'password': 'your_password'
        })
        
        # Tracking to prevent duplicate entries
        self.processed_plates = set()
    
    def process_frame(self, frame):
        # Detect number plates
        plates = self.detector.detect_plates(frame)
        
        for plate_region in plates:
            # Extract plate image
            plate_image = self.extract_plate_image(frame, plate_region)
            
            # Get stable plate number
            plate_number = self.ocr_stabilizer.get_stable_plate_number(plate_image)
            
            if plate_number and plate_number not in self.processed_plates:
                # Clean plate number
                cleaned_plate = self.ocr_stabilizer.clean_plate_number(plate_number)
                
                # Log vehicle entry
                self.vehicle_logger.log_vehicle_entry(cleaned_plate)
                
                # Prevent duplicate processing
                self.processed_plates.add(cleaned_plate)
    
    def extract_plate_image(self, frame, plate_region):
        x, y, w, h = plate_region
        return frame[y:y+h, x:x+w]

def main():
    # Initialize parking management system
    system = ParkingManagementSystem()
    
    # Open camera
    cap = cv2.VideoCapture(0)
    
    while True:
        # Capture frame
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to grab frame")
            break
        
        # Process frame
        system.process_frame(frame)
        
        # Display frame
        cv2.imshow('Parking Management System', frame)
        
        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
