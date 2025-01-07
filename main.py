import cv2
import easyocr
import numpy as np
from detection.yolo_detector import NumberPlateDetector
from database.vehicle_log import VehicleLogger
from datetime import datetime
import threading
from queue import Queue
import time
import os

class ParkingManagementSystem:
    def __init__(self, model_path='best.pt'):
        self.detector = NumberPlateDetector(model_path)
        self.reader = easyocr.Reader(['en'], gpu=True)
        self.vehicle_logger = VehicleLogger()
        self.processed_plates = set()
        self.plate_queue = Queue()
        self.recent_plates = []
        self.max_recent = 5
        
        # Create output directory
        self.output_dir = 'detected_plates'
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Start logging thread
        self.logging_thread = threading.Thread(target=self._process_plate_queue, daemon=True)
        self.logging_thread.start()

    def create_info_panel(self, frame, recent_detections):
        """Create a modern information panel overlay"""
        # Create dark semi-transparent overlay for the entire left side
        overlay = frame.copy()
        panel_width = 300
        height = frame.shape[0]
        cv2.rectangle(overlay, (0, 0), (panel_width, height), (33, 33, 33), -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame[:, 0:panel_width])

        # Add title with accent bar
        cv2.rectangle(frame, (10, 20), (15, 45), (0, 255, 200), -1)  # Accent bar
        cv2.putText(frame, "Vehicle Detection", (25, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Add status indicator
        status_color = (0, 255, 100)  # Green for active
        cv2.circle(frame, (20, 70), 5, status_color, -1)  # Status dot
        cv2.putText(frame, "System Active", (35, 75),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        # Add separator line
        cv2.line(frame, (20, 90), (panel_width-20, 90), (100, 100, 100), 1)

        # Recent detections section
        cv2.putText(frame, "Recent Detections", (20, 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        # Display recent detections with boxes
        y_offset = 150
        for i, plate in enumerate(recent_detections[:5]):
            # Draw detection box
            cv2.rectangle(frame, (15, y_offset-5), (panel_width-15, y_offset+25), 
                        (45, 45, 45), -1)
            
            # Plate number
            cv2.putText(frame, plate['plate'], (25, y_offset+15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            
            # Time and confidence
            time_conf = f"{plate['time']} ({plate['confidence']:.2f})"
            cv2.putText(frame, time_conf, (25, y_offset+35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)
            
            y_offset += 50

        # Add system stats at bottom
        bottom_y = height - 100
        cv2.line(frame, (20, bottom_y), (panel_width-20, bottom_y), (100, 100, 100), 1)
        
        # Stats
        total_detected = len(self.processed_plates)
        cv2.putText(frame, f"Total Detected: {total_detected}", (20, bottom_y + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, f"Session Time: {self.get_session_time()}", (20, bottom_y + 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    def get_session_time(self):
        """Calculate session duration"""
        if not hasattr(self, 'start_time'):
            self.start_time = datetime.now()
        duration = datetime.now() - self.start_time
        minutes = duration.seconds // 60
        seconds = duration.seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def process_frame(self, frame):
        output_frame = frame.copy()
        plates = self.detector.detect_plates(frame)
        
        for x, y, w, h in plates:
            plate_image = self.extract_plate_image(frame, (x, y, w, h))
            processed_plate = self.preprocess_plate_image(plate_image)
            
            try:
                results = self.reader.readtext(processed_plate)
                if results:
                    text, confidence = max(results, key=lambda x: x[2])[1:3]
                    cleaned_plate = self.clean_plate_number(text)
                    
                    if cleaned_plate and cleaned_plate not in self.processed_plates:
                        self.plate_queue.put({
                            'plate': cleaned_plate,
                            'confidence': confidence
                        })
                        self.processed_plates.add(cleaned_plate)
                        
                        # Modern detection box
                        # Draw main box
                        cv2.rectangle(output_frame, (x, y), (x+w, y+h), (0, 255, 200), 2)
                        
                        # Draw corner accents
                        accent_length = 20
                        # Top-left
                        cv2.line(output_frame, (x, y), (x+accent_length, y), (0, 255, 200), 3)
                        cv2.line(output_frame, (x, y), (x, y+accent_length), (0, 255, 200), 3)
                        # Top-right
                        cv2.line(output_frame, (x+w, y), (x+w-accent_length, y), (0, 255, 200), 3)
                        cv2.line(output_frame, (x+w, y), (x+w, y+accent_length), (0, 255, 200), 3)
                        # Bottom-left
                        cv2.line(output_frame, (x, y+h), (x+accent_length, y+h), (0, 255, 200), 3)
                        cv2.line(output_frame, (x, y+h), (x, y+h-accent_length), (0, 255, 200), 3)
                        # Bottom-right
                        cv2.line(output_frame, (x+w, y+h), (x+w-accent_length, y+h), (0, 255, 200), 3)
                        cv2.line(output_frame, (x+w, y+h), (x+w, y+h-accent_length), (0, 255, 200), 3)
                        
                        # Add text with background
                        text_size = cv2.getTextSize(cleaned_plate, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                        cv2.rectangle(output_frame, (x, y-30), (x+text_size[0]+10, y), (0, 255, 200), -1)
                        cv2.putText(output_frame, cleaned_plate, (x+5, y-8),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (33, 33, 33), 2)
                        
                        # Save detection images
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        
                        # Save full frame with detection
                        frame_filename = f"{self.output_dir}/frame_{cleaned_plate}_{timestamp}.jpg"
                        cv2.imwrite(frame_filename, output_frame)
                        
                        # Save cropped plate
                        plate_filename = f"{self.output_dir}/plate_{cleaned_plate}_{timestamp}.jpg"
                        cv2.imwrite(plate_filename, plate_image)
                        
                        # Save processed plate (after preprocessing)
                        processed_filename = f"{self.output_dir}/processed_{cleaned_plate}_{timestamp}.jpg"
                        cv2.imwrite(processed_filename, processed_plate)
                        
                        print(f"\nSaved detections:")
                        print(f"Frame: {frame_filename}")
                        print(f"Plate: {plate_filename}")
                        print(f"Processed: {processed_filename}")
                
            except Exception as e:
                print(f"OCR Error: {str(e)}")
        
        # Add info panel
        self.create_info_panel(output_frame, self.recent_plates)
        return output_frame

    def _process_plate_queue(self):
        while True:
            if not self.plate_queue.empty():
                plate_info = self.plate_queue.get()
                self.vehicle_logger.log_vehicle_entry(plate_info['plate'], plate_info['confidence'])
                self.recent_plates.insert(0, {
                    'plate': plate_info['plate'],
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'confidence': plate_info['confidence']
                })
                self.recent_plates = self.recent_plates[:self.max_recent]
                
                # Print detection info
                print(f"\nDetected plate: {plate_info['plate']}")
                print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
                print(f"Confidence: {plate_info['confidence']:.2f}")
                print("-" * 50)
            
            time.sleep(0.1)

    def preprocess_plate_image(self, plate_image):
        gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        return thresh
    
    def extract_plate_image(self, frame, plate_region):
        x, y, w, h = plate_region
        return frame[y:y+h, x:x+w]
    
    def clean_plate_number(self, plate_number):
        return ''.join(char for char in plate_number if char.isalnum())

def main():
    system = ParkingManagementSystem()
    
    # Set up video capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Set up window
    window_name = "Vehicle Detection System"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)
    
    print("System started. Press 'q' to quit.")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process and display frame
            display_frame = system.process_frame(frame)
            cv2.imshow(window_name, display_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nStopping system...")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
