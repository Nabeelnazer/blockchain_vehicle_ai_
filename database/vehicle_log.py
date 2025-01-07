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
        Log a vehicle entry to both database and log file
        """
        try:
            # Log to database
            self.db_manager.log_entry(plate_number, confidence)
            
            # Log to console/file
            self.logger.info(f"Vehicle Entry - Plate: {plate_number} Confidence: {confidence:.2f}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error logging vehicle entry: {str(e)}")
            return False
    
    def get_recent_entries(self, limit=5):
        """
        Get recent vehicle entries
        """
        try:
            return self.db_manager.get_recent_entries(limit)
        except Exception as e:
            self.logger.error(f"Error getting recent entries: {str(e)}")
            return []