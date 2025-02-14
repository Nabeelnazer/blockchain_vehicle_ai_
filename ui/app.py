import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import cv2
import numpy as np
from detection.yolo_detector import NumberPlateDetector
from blockchain.blockchain_manager import BlockchainManager
from database.vehicle_log import VehicleLogger
import time
import threading
import pandas as pd
from datetime import datetime

# Fallback blockchain manager
try:
    from blockchain.blockchain_manager import BlockchainManager
except ImportError:
    class BlockchainManager:
        def log_vehicle_entry(self, plate_number, confidence=0.9):
            return "MOCK_TRANSACTION"
        
        def verify_vehicle_entry(self, plate_number):
            return True

class ParkingManagementSystem:
    def __init__(self):
        """
        Advanced Parking Management System with Elite Dashboard
        """
        # Use YOLO detector with best.pt model
        self.plate_detector = NumberPlateDetector('best.pt')
        self.blockchain_manager = BlockchainManager()
        self.vehicle_logger = VehicleLogger()
        
        # Camera state management
        self.camera_active = False
        self.camera = None
        self.detection_thread = None
        
        # Tracking vehicles in parking
        self.parked_vehicles = {}
        
        # Performance optimization
        self.frame_skip = 3
        self.frame_count = 0
        
        # Dashboard tracking
        self.vehicle_log = []
        
        # Indian state plate prefixes with regex patterns for more robust matching
        self.INDIAN_PLATE_PATTERNS = [
            r'^KL\d{2}[A-Z]{1,2}\d{4}$',  # Kerala
            r'^KA\d{2}[A-Z]{1,2}\d{4}$',  # Karnataka
            r'^TN\d{2}[A-Z]{1,2}\d{4}$',  # Tamil Nadu
            r'^AP\d{2}[A-Z]{1,2}\d{4}$',  # Andhra Pradesh
            r'^TS\d{2}[A-Z]{1,2}\d{4}$',  # Telangana
            r'^MH\d{2}[A-Z]{1,2}\d{4}$',  # Maharashtra
            r'^DL\d{2}[A-Z]{1,2}\d{4}$',  # Delhi
            r'^WB\d{2}[A-Z]{1,2}\d{4}$',  # West Bengal
            r'^GJ\d{2}[A-Z]{1,2}\d{4}$',  # Gujarat
            r'^RJ\d{2}[A-Z]{1,2}\d{4}$'   # Rajasthan
        ]
    
    def _start_camera(self):
        """
        Elite Camera Initialization
        """
        try:
            if self.camera_active:
                st.toast("🚨 Camera Already Running!", icon="⚠️")
                return

            self.camera = cv2.VideoCapture(0)
            
            # Pro Camera Configuration
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            ret, frame = self.camera.read()
            if not ret:
                st.error("Camera Initialization Failed. Check connections.")
                self.camera.release()
                return

            self.camera_active = True
            frame_placeholder = st.empty()
            
            self.detection_thread = threading.Thread(
                target=self._process_camera_frame, 
                args=(frame_placeholder,),
                daemon=True
            )
            self.detection_thread.start()
            
            st.toast("🎥 Camera Activated Successfully!", icon="✅")

        except Exception as e:
            st.error(f"Camera Error: {e}")
            if self.camera:
                self.camera.release()
            self.camera_active = False
    
    def _process_camera_frame(self, frame_placeholder):
        """
        Advanced Frame Processing
        """
        while self.camera_active and self.camera.isOpened():
            try:
                ret, frame = self.camera.read()
                if not ret:
                    st.error("Frame Capture Failed")
                    break
                
                # Detect plates
                plates = self.plate_detector.detect_plates(frame)
                
                for x1, y1, x2, y2 in plates:
                    # Extract plate region
                    plate_img = frame[y1:y2, x1:x2]
                    
                    plate_info = self.plate_detector.process_plate(plate_img)
                    
                    if plate_info and plate_info['text']:
                        plate_number = plate_info['text']
                        
                        # Entry/Exit Logic
                        if plate_number not in [v['plate'] for v in self.vehicle_log]:
                            self._handle_vehicle_entry(plate_info, frame)
                        else:
                            self._handle_vehicle_exit(plate_info)
                        
                        # Visualization
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, plate_number, 
                                    (x1, y1-10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 
                                    0.6, (0, 255, 0), 1)
                
                frame_placeholder.image(frame, channels="BGR")
                time.sleep(0.05)

            except Exception as e:
                st.error(f"Processing Error: {e}")
                break
    
    def _handle_vehicle_entry(self, plate_info, frame):
        """
        Sophisticated Vehicle Entry Handler
        """
        plate_number = plate_info['text']
        
        try:
            # Blockchain Transaction
            blockchain_tx = self.blockchain_manager.log_vehicle_entry(
                plate_number, 
                plate_info.get('confidence', 0.9)
            )
            
            # Log Entry
            entry_record = {
                'plate': plate_number,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'INSIDE',
                'blockchain_tx': blockchain_tx.get('transaction_hash', 'N/A') if blockchain_tx else 'N/A'
            }
            
            self.vehicle_log.append(entry_record)
            
            # Optional: Save plate image
            cv2.imwrite(f"detected_plates/{plate_number}_entry.jpg", frame)
            
            st.toast(f"🚗 {plate_number} Entered Parking", icon="🟢")
        
        except Exception as e:
            st.error(f"Entry Logging Failed: {e}")
    
    def _handle_vehicle_exit(self, plate_info):
        """
        Sophisticated Vehicle Exit Handler
        """
        plate_number = plate_info['text']
        
        try:
            # Find and update entry record
            for record in self.vehicle_log:
                if record['plate'] == plate_number and record['status'] == 'INSIDE':
                    # Blockchain Exit Transaction
                    blockchain_tx = self.blockchain_manager.log_vehicle_exit(plate_number)
                    
                    record.update({
                        'exit_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'status': 'OUTSIDE',
                        'exit_blockchain_tx': blockchain_tx.get('transaction_hash', 'N/A') if blockchain_tx else 'N/A'
                    })
                    
                    st.toast(f"🚪 {plate_number} Exited Parking", icon="🔴")
                    break
        
        except Exception as e:
            st.error(f"Exit Logging Failed: {e}")
    
    def _stop_camera(self):
        """
        Graceful Camera Shutdown
        """
        try:
            self.camera_active = False
            
            if self.camera:
                self.camera.release()
                self.camera = None
            
            if self.detection_thread:
                self.detection_thread.join(timeout=2)
                self.detection_thread = None
            
            st.toast("📷 Camera Deactivated", icon="⚠️")
        
        except Exception as e:
            st.error(f"Camera Shutdown Error: {e}")
    
    def run(self):
        """
        Elite Dashboard Design
        """
        st.set_page_config(
            page_title="🚗 Smart Parking AI", 
            page_icon="🚦", 
            layout="wide"
        )
        
        # Custom CSS for Elite Design
        st.markdown("""
        <style>
        .stApp {
            background-color: #0E1117;
            color: #FFFFFF;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            transition-duration: 0.4s;
            cursor: pointer;
        }
        .stDataFrame {
            background-color: #1E2130;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Dashboard Layout
        st.title("🚦 Smart Parking Management System")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🎥 Live Camera Feed")
            camera_placeholder = st.empty()
            
            cam_col1, cam_col2 = st.columns(2)
            with cam_col1:
                if st.button("Start Camera", key="start_cam"):
                    self._start_camera()
            
            with cam_col2:
                if st.button("Stop Camera", key="stop_cam"):
                    self._stop_camera()
        
        with col2:
            st.subheader("📊 Vehicle Dashboard")
            
            # Convert vehicle log to DataFrame
            if self.vehicle_log:
                df = pd.DataFrame(self.vehicle_log)
                st.dataframe(
                    df[['plate', 'timestamp', 'status']],
                    column_config={
                        "plate": "Number Plate",
                        "timestamp": "Entry Time",
                        "status": st.column_config.TextColumn(
                            "Status",
                            help="Vehicle Location Status",
                            width="small"
                        )
                    },
                    hide_index=True
                )
            else:
                st.info("No vehicles detected yet")

def main():
    app = ParkingManagementSystem()
    app.run()

if __name__ == "__main__":
    main() 