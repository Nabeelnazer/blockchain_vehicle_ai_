import sqlite3
from datetime import datetime

class ParkingDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('parking.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT NOT NULL,
            entry_time DATETIME NOT NULL,
            exit_time DATETIME,
            status TEXT DEFAULT 'inside'
        )
        ''')
        self.conn.commit()

    def record_entry(self, plate_number, timestamp):
        cursor = self.conn.cursor()
        
        # Check if vehicle is already inside
        cursor.execute('''
        SELECT id FROM parking_records 
        WHERE plate_number = ? AND status = 'inside'
        ''', (plate_number,))
        
        if not cursor.fetchone():
            # Record new entry
            cursor.execute('''
            INSERT INTO parking_records (plate_number, entry_time, status)
            VALUES (?, ?, 'inside')
            ''', (plate_number, timestamp))
            self.conn.commit()

    def record_exit(self, plate_number, timestamp):
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE parking_records 
        SET exit_time = ?, status = 'exited'
        WHERE plate_number = ? AND status = 'inside'
        ''', (timestamp, plate_number))
        self.conn.commit()

    def get_vehicle_status(self, plate_number):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT entry_time, status 
        FROM parking_records 
        WHERE plate_number = ? 
        ORDER BY entry_time DESC 
        LIMIT 1
        ''', (plate_number,))
        return cursor.fetchone()

    def __del__(self):
        self.conn.close() 