import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import cv2
import numpy as np
from plate_detection.detector import PlateDetector

# Fallback blockchain manager
try:
    from blockchain.blockchain_manager import BlockchainManager
except ImportError:
    class BlockchainManager:
        def log_vehicle_entry(self, plate_number, confidence=0.9):
            return "MOCK_TRANSACTION"
        
        def verify_vehicle_entry(self, plate_number):
            return True

class VehicleDetectionUI:
    def __init__(self):
        # Initialize components
        self.detector = PlateDetector()
        self.blockchain_manager = BlockchainManager()
        
        # Initialize session state for detection control
        if 'detection_active' not in st.session_state:
            st.session_state.detection_active = False
    
    def run(self):
        st.title("🚗 Vehicle Plate Detection")
        
        # Start/Stop Detection Controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start Detection", key="start_detection"):
                st.session_state.detection_active = True
        
        with col2:
            if st.button("Stop Detection", key="stop_detection"):
                st.session_state.detection_active = False
        
        # Camera input
        st.header("Live Camera Feed")
        
        # Create placeholders
        frame_placeholder = st.empty()
        info_placeholder = st.empty()
        
        # Open camera
        cap = cv2.VideoCapture(0)
        
        while st.session_state.detection_active:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to capture frame")
                break
            
            # Detect plates
            plates = self.detector.detect_plates(frame)
            
            for x, y, w, h in plates:
                # Extract plate region
                plate_img = frame[int(y):int(y+h), int(x):int(x+w)]
                
                # Process plate
                plate_info = self.detector.process_plate(plate_img)
                
                if plate_info and plate_info['text']:
                    # Log to blockchain
                    blockchain_tx = self.blockchain_manager.log_vehicle_entry(
                        plate_info['text'], 
                        plate_info['confidence']
                    )
                    
                    # Draw rectangle and text
                    cv2.rectangle(frame, 
                                  (int(x), int(y)), 
                                  (int(x+w), int(y+h)), 
                                  (0, 255, 0), 2)
                    cv2.putText(frame, 
                                f"{plate_info['text']}", 
                                (int(x), int(y-10)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                0.9, (0, 255, 0), 2)
                    
                    # Display info
                    info_placeholder.write(f"""
                    **Detected Plate:** {plate_info['text']}
                    **Confidence:** {plate_info['confidence']:.2f}
                    **Blockchain TX:** {blockchain_tx}
                    """)
            
            # Display frame
            frame_placeholder.image(frame, channels="BGR")
        
        # Release camera
        cap.release()

def main():
    ui = VehicleDetectionUI()
    ui.run()

if __name__ == "__main__":
    main() 