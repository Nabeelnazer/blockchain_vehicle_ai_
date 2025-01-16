import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import cv2
from plate_detection.detector import PlateDetector
from blockchain.blockchain_manager import BlockchainManager
import time
from datetime import datetime
import pandas as pd

def main():
    # Page config
    st.set_page_config(
        page_title="Vehicle License Plate Detection",
        page_icon="🚗",
        layout="wide"
    )

    # Title and description
    st.title("Vehicle License Plate Detection & Verification")
    
    # Initialize session state for dashboard
    if 'daily_entries' not in st.session_state:
        st.session_state.daily_entries = {}
    if 'vehicle_logs' not in st.session_state:
        st.session_state.vehicle_logs = []
    
    # Sidebar controls
    with st.sidebar:
        st.header("Controls")
        
        # Camera selection
        camera_option = st.selectbox(
            "Select Camera Source",
            options=["Webcam", "IP Camera"]
        )
        
        if camera_option == "IP Camera":
            camera_url = st.text_input("Enter IP Camera URL")
        else:
            camera_index = st.number_input("Webcam Index", min_value=0, value=0)
            
        # Detection controls
        confidence_threshold = st.slider(
            "Detection Confidence",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05
        )
        
        # Start/Stop button
        if 'detection_on' not in st.session_state:
            st.session_state.detection_on = False
            
        if st.button('Start Detection' if not st.session_state.detection_on else 'Stop Detection'):
            st.session_state.detection_on = not st.session_state.detection_on

        # Display blockchain balance
        if 'blockchain' not in st.session_state:
            st.session_state.blockchain = BlockchainManager()
        try:
            balance = st.session_state.blockchain.w3.eth.get_balance(
                st.session_state.blockchain.account.address
            )
            st.info(f"💰 Balance: {st.session_state.blockchain.w3.from_wei(balance, 'ether')} ETH")
        except Exception as e:
            st.error("Could not fetch blockchain balance")

    # Main content area - Three columns
    col1, col2, col3 = st.columns([2, 1, 1])

    # Initialize detector if not exists
    if 'detector' not in st.session_state:
        st.session_state.detector = PlateDetector()

    # Initialize video capture
    if camera_option == "IP Camera" and camera_url:
        cap = cv2.VideoCapture(camera_url)
    else:
        cap = cv2.VideoCapture(camera_index)

    # Video feed column
    with col1:
        st.header("Live Feed")
        video_placeholder = st.empty()
        
    # Detections column
    with col2:
        st.header("Current Detection")
        detection_container = st.container()
        with detection_container:
            detection_text = st.empty()
            confidence_bar = st.empty()
            blockchain_status = st.empty()
    
    # Dashboard column
    with col3:
        st.header("Today's Dashboard")
        dashboard_container = st.container()
        with dashboard_container:
            # Display today's stats
            today = datetime.now().date()
            today_count = len([log for log in st.session_state.vehicle_logs 
                             if datetime.strptime(log['time'], "%Y-%m-%d %H:%M:%S").date() == today])
            
            st.metric("Vehicles Today", today_count)
            
            # Display recent entries
            st.subheader("Recent Entries")
            if st.session_state.vehicle_logs:
                df = pd.DataFrame(st.session_state.vehicle_logs)
                st.dataframe(df, height=300)
            
            # Download button for logs
            if st.button("Download Logs"):
                df = pd.DataFrame(st.session_state.vehicle_logs)
                df.to_csv("vehicle_logs.csv", index=False)
                st.success("Logs downloaded as vehicle_logs.csv")

    try:
        while st.session_state.detection_on:
            ret, frame = cap.read()
            if not ret:
                st.error("Error accessing camera feed")
                break

            # Process frame
            processed_frame, plates = st.session_state.detector.process_frame(frame)

            # Display processed frame
            video_placeholder.image(cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB))

            # Display detections
            if plates:
                for plate in plates:
                    if plate['confidence'] >= confidence_threshold:
                        # Update current detection
                        detection_text.write(f"📝 Plate: {plate['text']}")
                        confidence_bar.progress(float(plate['confidence']))

                        # Verify on blockchain
                        try:
                            receipt = st.session_state.blockchain.store_ocr_hash(plate)
                            blockchain_status.success(f"✅ Verified: {receipt.verification_hash[:20]}...")
                            
                            # Add to vehicle logs
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            log_entry = {
                                'time': timestamp,
                                'plate': plate['text'],
                                'confidence': f"{plate['confidence']:.2f}",
                                'verification': receipt.verification_hash[:10]
                            }
                            
                            # Only add if plate not detected in last 5 minutes
                            if not st.session_state.vehicle_logs or \
                               plate['text'] != st.session_state.vehicle_logs[0]['plate']:
                                st.session_state.vehicle_logs.insert(0, log_entry)
                            
                        except Exception as e:
                            blockchain_status.error(f"❌ Blockchain verification failed: {str(e)}")

            time.sleep(0.1)  # Small delay to prevent high CPU usage

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    finally:
        cap.release()

    # Display message when detection is off
    if not st.session_state.detection_on:
        video_placeholder.info("Detection is currently stopped. Click 'Start Detection' to begin.")

if __name__ == "__main__":
    main() 