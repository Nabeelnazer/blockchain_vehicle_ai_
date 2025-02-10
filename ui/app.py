import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import cv2
import numpy as np
from plate_detection.detector import PlateDetector
from blockchain.blockchain_manager import BlockchainManager
from database.vehicle_log import VehicleLogger
import time

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
        Advanced Parking Management System
        """
        self.plate_detector = PlateDetector()
        self.blockchain_manager = BlockchainManager()
        self.vehicle_logger = VehicleLogger()
        
        # Enhanced tracking mechanisms
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """
        Initialize advanced tracking states
        """
        if 'parking_entries' not in st.session_state:
            st.session_state.parking_entries = {}
        
        if 'current_occupancy' not in st.session_state:
            st.session_state.current_occupancy = 0
        
        if 'total_capacity' not in st.session_state:
            st.session_state.total_capacity = 50  # Configurable parking capacity
    
    def run(self):
        """
        Main application interface
        """
        st.set_page_config(
            page_title="Smart Parking Management", 
            page_icon="🚗", 
            layout="wide"
        )
        
        # Enhanced sidebar navigation
        page = st.sidebar.radio(
            "Parking Management", 
            [
                "Live Entry/Exit", 
                "Current Occupancy", 
                "Vehicle History", 
                "Analytics", 
                "Settings"
            ]
        )
        
        # Dynamic page rendering
        page_methods = {
            "Live Entry/Exit": self._live_detection_page,
            "Current Occupancy": self._occupancy_page,
            "Vehicle History": self._vehicle_history_page,
            "Analytics": self._parking_analytics_page,
            "Settings": self._system_settings_page
        }
        
        page_methods[page]()
    
    def _live_detection_page(self):
        """
        Advanced entry/exit detection
        """
        st.header("🚦 Vehicle Entry/Exit Monitoring")
        
        # Detection mode selection
        detection_mode = st.radio(
            "Detection Mode", 
            ["Entry", "Exit"]
        )
        
        # Camera feed setup
        cap = cv2.VideoCapture(0)
        frame_placeholder = st.empty()
        detection_info = st.empty()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                st.error("Camera capture failed")
                break
            
            # Detect plates
            plates = self.plate_detector.detect_plates(frame)
            
            for x, y, w, h in plates:
                plate_img = frame[int(y):int(y+h), int(x):int(x+w)]
                plate_info = self.plate_detector.process_plate(plate_img)
                
                if plate_info and plate_info['text']:
                    # Advanced vehicle tracking
                    if detection_mode == "Entry":
                        self._handle_vehicle_entry(plate_info)
                    else:
                        self._handle_vehicle_exit(plate_info)
                    
                    # Visualization
                    cv2.rectangle(frame, 
                                  (int(x), int(y)), 
                                  (int(x+w), int(y+h)), 
                                  (0, 255, 0), 2)
                    cv2.putText(frame, 
                                plate_info['text'], 
                                (int(x), int(y-10)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                0.9, (0, 255, 0), 2)
            
            frame_placeholder.image(frame, channels="BGR")
            time.sleep(0.1)
    
    def _handle_vehicle_entry(self, plate_info):
        """
        Advanced vehicle entry logic
        """
        plate_number = plate_info['text']
        
        # Check parking capacity
        if st.session_state.current_occupancy >= st.session_state.total_capacity:
            st.warning("Parking is full!")
            return
        
        # Prevent duplicate entries
        if plate_number not in st.session_state.parking_entries:
            # Log entry
            entry_tx = self.blockchain_manager.log_vehicle_entry(
                plate_number, 
                plate_info['confidence']
            )
            
            # Update parking state
            st.session_state.parking_entries[plate_number] = {
                'entry_time': time.strftime("%Y-%m-%d %H:%M:%S"),
                'blockchain_tx': entry_tx,
                'confidence': plate_info['confidence']
            }
            
            st.session_state.current_occupancy += 1
            st.success(f"Vehicle {plate_number} entered")
    
    def _handle_vehicle_exit(self, plate_info):
        """
        Advanced vehicle exit logic
        """
        plate_number = plate_info['text']
        
        if plate_number in st.session_state.parking_entries:
            # Calculate parking duration
            entry_time = st.session_state.parking_entries[plate_number]['entry_time']
            exit_time = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Remove from active parking
            del st.session_state.parking_entries[plate_number]
            
            st.session_state.current_occupancy -= 1
            st.info(f"Vehicle {plate_number} exited")
    
    def _occupancy_page(self):
        """
        Real-time parking occupancy dashboard
        """
        st.header("📊 Parking Occupancy")
        
        # Occupancy visualization
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Current Occupancy", 
                f"{st.session_state.current_occupancy}/{st.session_state.total_capacity}"
            )
        
        with col2:
            occupancy_percentage = (
                st.session_state.current_occupancy / st.session_state.total_capacity
            ) * 100
            st.progress(occupancy_percentage / 100)
        
        # Current vehicles
        st.subheader("Vehicles in Parking")
        st.dataframe(st.session_state.parking_entries)
    
    def _vehicle_history_page(self):
        """
        Comprehensive vehicle history
        """
        st.header("🕒 Vehicle Entry/Exit History")
        
        # Filtering options
        col1, col2 = st.columns(2)
        with col1:
            plate_filter = st.text_input("Filter by Plate")
        with col2:
            date_filter = st.date_input("Filter by Date")
        
        # Implement filtering logic here
    
    def _parking_analytics_page(self):
        """
        Advanced parking analytics
        """
        st.header("📈 Parking Analytics")
        # Implement peak hours, average stay duration, etc.
    
    def _system_settings_page(self):
        """
        System configuration
        """
        st.header("⚙️ Parking System Settings")
        
        # Capacity configuration
        new_capacity = st.number_input(
            "Total Parking Capacity", 
            min_value=10, 
            max_value=500, 
            value=st.session_state.total_capacity
        )
        
        if st.button("Update Capacity"):
            st.session_state.total_capacity = new_capacity
            st.success("Parking capacity updated")

def main():
    app = ParkingManagementSystem()
    app.run()

if __name__ == "__main__":
    main() 