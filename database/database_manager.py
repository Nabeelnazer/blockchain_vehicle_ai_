import sqlite3
import os
from datetime import datetime
import logging

class DatabaseManager:
    def __init__(self, db_path='vehicle_logs.db'):
        self.db_path = db_path
        self.setup_database()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_database(self):
        """Create database and tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create vehicle_entries table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicle_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT NOT NULL,
            entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confidence REAL,
            blockchain_tx TEXT,
            block_number INTEGER,
            status TEXT DEFAULT 'pending'
        )
        ''')
        
        conn.commit()
        conn.close() 