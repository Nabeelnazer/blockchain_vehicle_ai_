def retrieve_vehicle_entries(blockchain_manager, plate_number=None):
    """
    Retrieve vehicle entries
    """
    return blockchain_manager.get_vehicle_entries(plate_number)

def filter_entries_by_date(blockchain_manager, start_date, end_date):
    """
    Filter entries by date range
    """
    return blockchain_manager.get_entries_by_date_range(start_date, end_date)

def export_entries(blockchain_manager, filename=None):
    """
    Export entries to a file
    """
    return blockchain_manager.export_entries(filename) 