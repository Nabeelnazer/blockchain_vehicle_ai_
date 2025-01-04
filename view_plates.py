from database_manager import DatabaseManager
import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox

class LicensePlateViewer:
    def __init__(self):
        # Use the same database manager
        self.db_manager = DatabaseManager()
        self.setup_ui()
    
    def fetch_plates(self):
        """Retrieve all stored license plates"""
        conn = sqlite3.connect(self.db_manager.db_path)
        query = "SELECT * FROM entries ORDER BY entry_time DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def setup_ui(self):
        """Create Tkinter UI for plate viewing"""
        self.root = tk.Tk()
        self.root.title("Stored License Plates")
        self.root.geometry("800x600")
        
        # Treeview for displaying plates
        self.tree = ttk.Treeview(self.root, columns=(
            'Plate', 'Entry Time', 'Confidence', 'Image Path'
        ), show='headings')
        
        # Column headings
        self.tree.heading('Plate', text='Plate Number')
        self.tree.heading('Entry Time', text='Entry Time')
        self.tree.heading('Confidence', text='Confidence')
        self.tree.heading('Image Path', text='Image Path')
        
        # Populate treeview
        self.populate_treeview()
        
        self.tree.pack(expand=True, fill='both')
        
        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Refresh", command=self.populate_treeview).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Export to CSV", command=self.export_to_csv).pack(side=tk.LEFT, padx=5)
    
    def populate_treeview(self):
        """Fill treeview with plate data"""
        # Clear existing items
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Fetch and display plates
        df = self.fetch_plates()
        for index, row in df.iterrows():
            self.tree.insert('', 'end', values=(
                row['plate_number'], 
                row['entry_time'], 
                f"{row['confidence']:.2f}", 
                row['image_path']
            ))
    
    def export_to_csv(self):
        """Export plates to CSV"""
        df = self.fetch_plates()
        export_path = 'detected_plates/license_plates_export.csv'
        df.to_csv(export_path, index=False)
        tk.messagebox.showinfo("Export Successful", f"Plates exported to {export_path}")
    
    def run(self):
        """Start Tkinter main loop"""
        self.root.mainloop()

def main():
    viewer = LicensePlateViewer()
    viewer.run()

if __name__ == "__main__":
    main() 