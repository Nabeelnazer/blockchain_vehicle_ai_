from database.vehicle_log import VehicleLogger
import time

def test_database():
    # Initialize logger
    logger = VehicleLogger()
    
    # Test logging some entries
    test_plates = ['ABC123', 'XYZ789', 'DEF456']
    
    for plate in test_plates:
        # Log entry
        logger.log_vehicle_entry(plate, confidence=0.95)
        print(f"Logged plate: {plate}")
        
        # Get recent entries
        recent = logger.get_recent_entries()
        print("Recent entries:", recent)
        time.sleep(1)

if __name__ == "__main__":
    test_database()