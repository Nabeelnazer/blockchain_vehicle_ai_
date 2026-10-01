import sqlite3
import logging


class DatabaseManager:
    def __init__(self, db_path='vehicle_logs.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.setup_database()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def setup_database(self):
        """Create database and tables if they don't exist"""
        with self._connect() as conn:
            conn.execute('''
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

    def log_entry(self, plate_number, confidence=None):
        """Insert an entry and return its row id"""
        with self._connect() as conn:
            cursor = conn.execute(
                'INSERT INTO vehicle_entries (plate_number, confidence) VALUES (?, ?)',
                (plate_number, confidence),
            )
            return cursor.lastrowid

    def update_blockchain_tx(self, entry_id, blockchain_tx):
        """Record the on-chain transaction for an entry, or mark it failed"""
        with self._connect() as conn:
            if blockchain_tx:
                conn.execute(
                    "UPDATE vehicle_entries SET blockchain_tx = ?, block_number = ?, status = 'confirmed' WHERE id = ?",
                    (blockchain_tx['transaction_hash'], blockchain_tx['block_number'], entry_id),
                )
            else:
                conn.execute(
                    "UPDATE vehicle_entries SET status = 'failed' WHERE id = ?",
                    (entry_id,),
                )

    def get_recent_entries(self, limit=5):
        """Most recent entries first"""
        with self._connect() as conn:
            rows = conn.execute(
                'SELECT * FROM vehicle_entries ORDER BY id DESC LIMIT ?',
                (int(limit),),
            ).fetchall()
            return [dict(row) for row in rows]
