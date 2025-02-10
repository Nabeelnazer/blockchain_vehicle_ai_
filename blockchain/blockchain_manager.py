import hashlib
from datetime import datetime
import json
import os

class BlockchainManager:
    def __init__(self, storage_path='vehicle_blockchain_data.json'):
        """
        Initialize blockchain manager with persistent storage
        """
        self.storage_path = storage_path
        self.vehicle_entries = self._load_entries()
    
    def _load_entries(self):
        """
        Load existing entries from JSON file
        """
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading entries: {e}")
            return {}
    
    def _save_entries(self):
        """
        Save entries to JSON file
        """
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.vehicle_entries, f, indent=4)
        except Exception as e:
            print(f"Error saving entries: {e}")
    
    def log_vehicle_entry(self, plate_number, confidence=0.9):
        """
        Log a vehicle entry with a unique transaction hash
        """
        # Generate unique transaction hash
        timestamp = datetime.now().isoformat()
        entry_data = f"{plate_number}{timestamp}"
        transaction_hash = hashlib.sha256(entry_data.encode()).hexdigest()
        
        # Store entry
        if plate_number not in self.vehicle_entries:
            self.vehicle_entries[plate_number] = []
        
        entry = {
            'plate_number': plate_number,
            'timestamp': timestamp,
            'confidence': confidence,
            'transaction_hash': transaction_hash
        }
        
        self.vehicle_entries[plate_number].append(entry)
        
        # Save to persistent storage
        self._save_entries()
        
        return transaction_hash
    
    def verify_vehicle_entry(self, plate_number):
        """
        Check if a vehicle has been logged
        """
        return plate_number in self.vehicle_entries
    
    def get_vehicle_entries(self, plate_number=None):
        """
        Retrieve vehicle entries
        
        :param plate_number: Optional specific plate number to retrieve
        :return: List of entries
        """
        if plate_number:
            return self.vehicle_entries.get(plate_number, [])
        return self.vehicle_entries
    
    def get_entries_by_date_range(self, start_date=None, end_date=None):
        """
        Retrieve entries within a specific date range
        
        :param start_date: Optional start date (datetime or ISO format string)
        :param end_date: Optional end date (datetime or ISO format string)
        :return: Filtered entries
        """
        # Convert string dates to datetime if needed
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        
        filtered_entries = {}
        for plate, entries in self.vehicle_entries.items():
            plate_entries = [
                entry for entry in entries
                if (start_date is None or datetime.fromisoformat(entry['timestamp']) >= start_date) and
                   (end_date is None or datetime.fromisoformat(entry['timestamp']) <= end_date)
            ]
            
            if plate_entries:
                filtered_entries[plate] = plate_entries
        
        return filtered_entries
    
    def export_entries(self, filename=None):
        """
        Export all entries to a JSON file
        
        :param filename: Optional custom filename
        :return: Path to exported file
        """
        if not filename:
            filename = f"vehicle_entries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.vehicle_entries, f, indent=4)
            return filename
        except Exception as e:
            print(f"Error exporting entries: {e}")
            return None
