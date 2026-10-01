from .database_manager import DatabaseManager
import logging

class VehicleLogger:
    def __init__(self, config=None):
        """
        Initialize the vehicle logger
        config: Optional configuration dictionary
        """
        self.db_manager = DatabaseManager()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Add console handler if not already added
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def log_vehicle_entry(self, plate_number, confidence=None):
        """
        Log a vehicle entry to both database and log file.
        Returns the entry's row id, or None if it could not be saved.
        """
        try:
            entry_id = self.db_manager.log_entry(plate_number, confidence)

            shown = f"{confidence:.2f}" if confidence is not None else "n/a"
            self.logger.info(f"Vehicle Entry - Plate: {plate_number} Confidence: {shown}")

            return entry_id

        except Exception as e:
            self.logger.error(f"Error logging vehicle entry: {str(e)}")
            return None

    def record_blockchain_tx(self, entry_id, blockchain_tx):
        """
        Attach the blockchain result to a saved entry
        """
        if entry_id is None:
            return
        try:
            self.db_manager.update_blockchain_tx(entry_id, blockchain_tx)
        except Exception as e:
            self.logger.error(f"Error saving blockchain tx: {str(e)}")

    def get_recent_entries(self, limit=5):
        """
        Get recent vehicle entries
        """
        try:
            return self.db_manager.get_recent_entries(limit)
        except Exception as e:
            self.logger.error(f"Error getting recent entries: {str(e)}")
            return []
