import os
import cv2
import torch
import numpy as np
from ultralytics import YOLO
import easyocr
import sqlite3
from datetime import datetime
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
from database_manager import DatabaseManager
import logging

# Add verbose logging
logging.basicConfig(level=logging.DEBUG)

class LicensePlateDetector:
    def __init__(self, model_path='best.pt', database_path='detected_plates/license_plates.db'):
        logging.debug("Initializing detector")
        # Create directories
        os.makedirs('detected_plates', exist_ok=True)
        
        # Model Initialization
        self.model = YOLO(model_path)
        self.model.conf = 0.4  # Confidence threshold
        self.model.iou = 0.45  # Intersection over Union
        
        # OCR Initialization
        self.ocr = AdvancedOCR()
        
        # Database Connection
        self.database_path = database_path
        self.init_database()
        
        # Detection State
        self.is_detecting = False
        self.capture_thread = None
        self.cap = None
        
        # UI Components
        self.setup_ui()
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
    
    def init_database(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plate_number TEXT,
                    entry_time DATETIME,
                    image_path TEXT,
                    confidence REAL
                )
            ''')
            conn.commit()
    
    def setup_ui(self):
        """Create Tkinter UI for Camera Control"""
        self.root = tk.Tk()
        self.root.title("License Plate Detection")
        self.root.geometry("1000x800")
        
        # Camera Control Frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        # Camera Control Button
        self.camera_button = tk.Button(
            control_frame, 
            text="Start Camera", 
            command=self.toggle_camera,
            bg='green', 
            fg='white',
            font=('Arial', 12, 'bold'),
            width=15
        )
        self.camera_button.pack(side=tk.LEFT, padx=10)
        
        # Status Label
        self.status_label = tk.Label(
            control_frame, 
            text="Camera: Stopped", 
            font=('Arial', 10)
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Detected Plates Frame
        detected_frame = tk.Frame(self.root)
        detected_frame.pack(expand=True, fill=tk.BOTH)
        
        # Matplotlib Figure for Display
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=detected_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        # Detected Plates Log
        self.plates_log = scrolledtext.ScrolledText(
            detected_frame, 
            wrap=tk.WORD, 
            width=40, 
            height=20
        )
        self.plates_log.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)
    
    def toggle_camera(self):
        """Toggle camera detection on/off"""
        if not self.is_detecting:
            self.start_camera()
        else:
            self.stop_camera()
    
    def start_camera(self):
        """Start camera detection"""
        try:
            # Release any existing capture
            if self.cap is not None:
                self.cap.release()
            
            # Open camera
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Cannot open camera")
                return
            
            self.is_detecting = True
            self.camera_button.config(text="Stop Camera", bg='red')
            self.status_label.config(text="Camera: Running", fg='green')
            
            # Start detection in a separate thread
            self.capture_thread = threading.Thread(target=self.detect_and_save)
            self.capture_thread.start()
        
        except Exception as e:
            messagebox.showerror("Camera Error", str(e))
    
    def stop_camera(self):
        """Stop camera detection"""
        self.is_detecting = False
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        
        if self.capture_thread:
            self.capture_thread.join()
        
        self.camera_button.config(text="Start Camera", bg='green')
        self.status_label.config(text="Camera: Stopped", fg='black')
    
    def extract_plate_text(self, plate_img):
        """Extract text from license plate"""
        try:
            # Resize and convert to grayscale
            plate_img = cv2.resize(plate_img, (300, 150))
            gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
            
            # Perform OCR
            results = self.ocr.readtext(gray)
            
            if results:
                # Get text with highest confidence
                best_result = max(results, key=lambda x: x[2])
                text = best_result[1]
                confidence = best_result[2]
                
                return {
                    'text': text.upper(),
                    'confidence': confidence
                }
            
            return None
        
        except Exception as e:
            print(f"OCR Error: {e}")
            return None
    
    def save_entry(self, plate_number, image_path, confidence):
        """Save license plate entry to database"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO entries 
                (plate_number, entry_time, image_path, confidence) 
                VALUES (?, ?, ?, ?)
            ''', (plate_number, datetime.now(), image_path, confidence))
            conn.commit()
    
    def detect_and_save(self):
        """Real-time license plate detection"""
        logging.debug("Starting detection")
        while self.is_detecting and self.cap is not None:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # YOLO Detection
            results = self.model(frame)
            
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    # Bounding Box Coordinates
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Extract Plate Region
                    plate_img = frame[y1:y2, x1:x2]
                    
                    # Perform OCR
                    ocr_result = self.extract_plate_text(plate_img)
                    
                    if ocr_result:
                        plate_text = ocr_result['text']
                        confidence = ocr_result['confidence']
                        
                        # Generate unique filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"plate_{plate_text}_{timestamp}.jpg"
                        filepath = os.path.join('detected_plates', filename)
                        
                        # Save plate image
                        cv2.imwrite(filepath, plate_img)
                        
                        # Use database manager to save entry
                        self.db_manager.save_plate_entry(
                            plate_number=plate_text, 
                            image_path=filepath, 
                            confidence=confidence
                        )
                        
                        # Update plates log
                        log_entry = f"Plate: {plate_text}\nConfidence: {confidence:.2f}\nTime: {datetime.now()}\n\n"
                        self.plates_log.insert(tk.END, log_entry)
                        self.plates_log.see(tk.END)
                        
                        # Draw bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, 
                                    f"{plate_text} ({confidence:.2f})", 
                                    (x1, y1-10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 
                                    0.9, (0, 255, 0), 2)
            
            # Update Matplotlib display
            self.ax.clear()
            self.ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            self.ax.set_title('License Plate Detection')
            self.ax.axis('off')
            self.canvas.draw()
            self.root.update()
        
        # Ensure camera is released when detection stops
        if self.cap is not None:
            self.cap.release()
    
    def run(self):
        """Start Tkinter main loop"""
        self.root.mainloop()
    
    def log_to_file(self, log_entry):
        with open('license_plate_log.txt', 'a') as log_file:
            log_file.write(log_entry + '\n')
    
    def validate_plate(self, text):
        """Comprehensive plate validation"""
        patterns = [
            r'^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$',   # Standard Indian
            r'^KL\d{2}[A-Z]{2}\d{4}$',            # Kerala
            r'^[A-Z]{2}\s?\d{2}\s?[A-Z]{1,2}\s?\d{4}$'  # Flexible format
        ]
        
        return any(
            re.match(pattern, text.replace(' ', '').upper()) 
            for pattern in patterns
        )

class AdvancedOCR:
    def __init__(self):
        # English-only OCR
        self.reader = easyocr.Reader(
            ['en'],  # Strictly English
            gpu=torch.cuda.is_available()
        )
    
    def preprocess_image(self, image):
        """Advanced image preprocessing for English plates"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Enhanced thresholding
        _, binary = cv2.threshold(
            gray, 
            0, 
            255, 
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        
        # Noise reduction
        denoised = cv2.fastNlMeansDenoising(binary)
        
        # Contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        return enhanced
    
    def extract_text(self, image):
        """Intelligent text extraction for English plates"""
        preprocessed = self.preprocess_image(image)
        
        # Optimized reading parameters
        results = self.reader.readtext(
            preprocessed, 
            detail=1,
            paragraph=False,
            min_size=10,
            contrast_ths=0.1,
            adjust_contrast=0.5
        )
        
        # Strict confidence filtering
        valid_results = [
            result for result in results 
            if result[2] > 0.7  # Higher confidence threshold
            and re.match(r'^[A-Z0-9]+$', result[1])  # Alphanumeric only
        ]
        
        if valid_results:
            best_result = max(valid_results, key=lambda x: x[2])
            return {
                'text': best_result[1],
                'confidence': best_result[2]
            }
        
        return None

class DatabaseManager:
    def __init__(self, db_path='license_plates.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        """Enhanced table structure"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY,
                plate_number TEXT UNIQUE,
                entry_count INTEGER DEFAULT 1,
                first_seen DATETIME,
                last_seen DATETIME,
                confidence REAL,
                image_paths TEXT
            )
        ''')
        self.conn.commit()
    
    def log_plate(self, plate_number, confidence, image_path):
        """Intelligent plate logging"""
        cursor = self.conn.cursor()
        
        # Check existing entry
        cursor.execute('''
            SELECT entry_count, image_paths 
            FROM entries 
            WHERE plate_number = ?
        ''', (plate_number,))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing entry
            entry_count, prev_paths = existing
            updated_paths = f"{prev_paths},{image_path}"
            
            cursor.execute('''
                UPDATE entries 
                SET 
                    entry_count = ?, 
                    last_seen = ?, 
                    confidence = ?,
                    image_paths = ?
                WHERE plate_number = ?
            ''', (
                entry_count + 1, 
                datetime.now(), 
                confidence, 
                updated_paths, 
                plate_number
            ))
        else:
            # Insert new entry
            cursor.execute('''
                INSERT INTO entries 
                (plate_number, first_seen, last_seen, confidence, image_paths) 
                VALUES (?, ?, ?, ?, ?)
            ''', (
                plate_number, 
                datetime.now(), 
                datetime.now(), 
                confidence, 
                image_path
            ))
        
        self.conn.commit()

def main():
    detector = LicensePlateDetector()
    detector.run()

if __name__ == "__main__":
    main()