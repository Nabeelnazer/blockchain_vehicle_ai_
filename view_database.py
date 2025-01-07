import sqlite3
from tabulate import tabulate

def view_database():
    # Connect to database
    conn = sqlite3.connect('vehicle_logs.db')
    cursor = conn.cursor()
    
    # Get all entries
    cursor.execute('''
    SELECT id, plate_number, entry_time, confidence, status 
    FROM vehicle_entries 
    ORDER BY entry_time DESC
    ''')
    
    entries = cursor.fetchall()
    
    # Print in table format
    headers = ['ID', 'Plate Number', 'Entry Time', 'Confidence', 'Status']
    print(tabulate(entries, headers=headers, tablefmt='grid'))
    
    # Print summary
    print(f"\nTotal entries: {len(entries)}")
    
    conn.close()

if __name__ == "__main__":
    view_database() 