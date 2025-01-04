import os
import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='detected_plates/license_plates.db'):
        # Ensure directory exists
        os.makedirs('detected_plates', exist_ok=True)
        
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with consistent schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plate_number TEXT,
                    entry_time DATETIME,
                    image_path TEXT,
                    confidence REAL,
                    detection_count INTEGER DEFAULT 1
                )
            ''')
            conn.commit()
    
    def save_plate_entry(self, plate_number, image_path, confidence):
        """
        Save plate entry with intelligent duplicate handling
        
        Args:
            plate_number (str): Detected plate number
            image_path (str): Path to plate image
            confidence (float): OCR confidence
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check for existing plate
            cursor.execute('''
                SELECT id, detection_count 
                FROM entries 
                WHERE plate_number = ?
            ''', (plate_number,))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing entry
                cursor.execute('''
                    UPDATE entries 
                    SET 
                        detection_count = detection_count + 1,
                        entry_time = ?,
                        confidence = ?,
                        image_path = ?
                    WHERE plate_number = ?
                ''', (
                    datetime.now(), 
                    confidence, 
                    image_path, 
                    plate_number
                ))
            else:
                # Insert new entry
                cursor.execute('''
                    INSERT INTO entries 
                    (plate_number, entry_time, image_path, confidence) 
                    VALUES (?, ?, ?, ?)
                ''', (
                    plate_number, 
                    datetime.now(), 
                    image_path, 
                    confidence
                ))
            
            conn.commit() 