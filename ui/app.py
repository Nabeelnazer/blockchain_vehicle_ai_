import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import cv2
from detection.yolo_detector import NumberPlateDetector
from blockchain.blockchain_manager import BlockchainManager
from database.vehicle_log import VehicleLogger
import time
import pandas as pd
from datetime import datetime

# Seconds a plate must be out of sight before seeing it again counts as the
# next event. Without this, the frame after an entry logs an exit.
EVENT_COOLDOWN_SECONDS = 30
DETECTED_PLATES_DIR = "detected_plates"


def _connect_blockchain():
    """BlockchainManager, or None when the node or contract is unavailable"""
    try:
        manager = BlockchainManager()
        return manager if manager.contract is not None else None
    except Exception:
        return None


class ParkingManagementSystem:
    def __init__(self):
        """
        Advanced Parking Management System with Elite Dashboard.
        Built once per browser session and kept in st.session_state.
        """
        # Use YOLO detector with best.pt model
        self.plate_detector = NumberPlateDetector('best.pt')
        self.blockchain_manager = _connect_blockchain()
        self.vehicle_logger = VehicleLogger()
        os.makedirs(DETECTED_PLATES_DIR, exist_ok=True)

        # Camera state management
        self.camera_active = False
        self.camera = None

        # Performance optimization
        self.frame_skip = 3
        self.frame_count = 0

        # Dashboard tracking
        self.vehicle_log = []
        # plate -> time it was last seen, for the entry/exit cooldown
        self.last_seen = {}

    def _start_camera(self):
        """
        Elite Camera Initialization
        """
        if self.camera_active:
            st.toast("🚨 Camera Already Running!", icon="⚠️")
            return

        self.camera = cv2.VideoCapture(0)

        # Pro Camera Configuration
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        ret, _ = self.camera.read()
        if not ret:
            st.error("Camera Initialization Failed. Check connections.")
            self.camera.release()
            self.camera = None
            return

        self.camera_active = True
        st.toast("🎥 Camera Activated Successfully!", icon="✅")

    def _run_camera_loop(self, frame_placeholder):
        """
        Frame processing, on the script thread: Streamlit calls only render
        from there. Clicking Stop reruns the script, which ends this loop.
        """
        while self.camera_active and self.camera is not None and self.camera.isOpened():
            ret, frame = self.camera.read()
            if not ret:
                st.error("Frame Capture Failed")
                self._stop_camera()
                break

            self.frame_count += 1
            if self.frame_count % self.frame_skip == 0:
                self._process_frame(frame)

            frame_placeholder.image(frame, channels="BGR")
            time.sleep(0.05)

    def _process_frame(self, frame):
        """
        Detect, read and log the plates in one frame (draws boxes onto it)
        """
        for x1, y1, x2, y2 in self.plate_detector.detect_plates(frame):
            # Extract plate region
            plate_img = frame[y1:y2, x1:x2]

            plate_info = self.plate_detector.process_plate(plate_img)
            if not plate_info:
                continue

            plate_number = plate_info['text']
            now = time.time()
            last = self.last_seen.get(plate_number)
            self.last_seen[plate_number] = now

            # Entry/Exit Logic: a sighting after the cooldown toggles the state
            if last is None or now - last > EVENT_COOLDOWN_SECONDS:
                if self._is_inside(plate_number):
                    self._handle_vehicle_exit(plate_info)
                else:
                    self._handle_vehicle_entry(plate_info, frame)

            # Visualization
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, plate_number,
                        (x1, max(y1 - 10, 0)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 1)

    def _is_inside(self, plate_number):
        return any(r['plate'] == plate_number and r['status'] == 'INSIDE'
                   for r in self.vehicle_log)

    def _handle_vehicle_entry(self, plate_info, frame):
        """
        Sophisticated Vehicle Entry Handler
        """
        plate_number = plate_info['text']
        confidence = plate_info.get('confidence')

        try:
            entry_id = self.vehicle_logger.log_vehicle_entry(plate_number, confidence)

            # Blockchain Transaction (skipped while the node is down)
            blockchain_tx = None
            if self.blockchain_manager:
                blockchain_tx = self.blockchain_manager.log_vehicle_entry(
                    plate_number,
                    confidence if confidence is not None else 0.9
                )
                self.vehicle_logger.record_blockchain_tx(entry_id, blockchain_tx)

            # Log Entry
            entry_record = {
                'plate': plate_number,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'INSIDE',
                'blockchain_tx': blockchain_tx['transaction_hash'] if blockchain_tx else 'N/A'
            }

            self.vehicle_log.append(entry_record)

            # Optional: Save plate image
            safe_name = plate_number.replace(' ', '')
            cv2.imwrite(os.path.join(DETECTED_PLATES_DIR, f"{safe_name}_entry.jpg"), frame)

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
                    blockchain_tx = None
                    if self.blockchain_manager:
                        blockchain_tx = self.blockchain_manager.log_vehicle_exit(plate_number)

                    record.update({
                        'exit_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'status': 'OUTSIDE',
                        'exit_blockchain_tx': blockchain_tx['transaction_hash'] if blockchain_tx else 'N/A'
                    })

                    st.toast(f"🚪 {plate_number} Exited Parking", icon="🔴")
                    break

        except Exception as e:
            st.error(f"Exit Logging Failed: {e}")

    def _stop_camera(self):
        """
        Graceful Camera Shutdown
        """
        self.camera_active = False

        if self.camera:
            self.camera.release()
            self.camera = None

        st.toast("📷 Camera Deactivated", icon="⚠️")

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

            if self.blockchain_manager is None:
                st.warning("Blockchain node unavailable: entries are saved locally only.")

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

        # Last, so the controls and dashboard are drawn before the loop blocks
        if self.camera_active:
            self._run_camera_loop(camera_placeholder)

def main():
    # Streamlit reruns this script on every click; keep one system per session
    if "parking_system" not in st.session_state:
        st.session_state.parking_system = ParkingManagementSystem()
    st.session_state.parking_system.run()

if __name__ == "__main__":
    main()
