import os
import sqlite3
from flask import Flask, render_template, jsonify, send_file
import base64
import cv2

app = Flask(__name__)

class LicensePlateDataViewer:
    def __init__(self, db_path='detected_plates/license_plates.db'):
        self.db_path = db_path
        
        # Ensure database exists
        self.initialize_database()
    
    def initialize_database(self):
        """
        Create database if not exists
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detected_plates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate_number TEXT,
                confidence REAL,
                detection_time DATETIME,
                image_path TEXT,
                x1 INTEGER,
                y1 INTEGER,
                x2 INTEGER,
                y2 INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_database_connection(self):
        """
        Create a new database connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_all_plates(self):
        """
        Retrieve all detected license plates
        """
        conn = self.get_database_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM detected_plates ORDER BY detection_time DESC')
            plates = cursor.fetchall()
            return [dict(plate) for plate in plates]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()
    
    def get_plate_image(self, image_path):
        """
        Convert image to base64 for web display
        """
        try:
            # Verify image exists
            if not os.path.exists(image_path):
                print(f"Image not found: {image_path}")
                return None
            
            # Read image
            image = cv2.imread(image_path)
            
            if image is None:
                print(f"Failed to read image: {image_path}")
                return None
            
            # Resize for web
            image = cv2.resize(image, (640, 480))
            
            # Encode image to base64
            _, buffer = cv2.imencode('.jpg', image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return image_base64
        
        except Exception as e:
            print(f"Image processing error: {e}")
            return None

# Flask Routes
@app.route('/')
def index():
    viewer = LicensePlateDataViewer()
    plates = viewer.get_all_plates()
    
    # Debug print
    print(f"Total plates found: {len(plates)}")
    
    return render_template('index.html', plates=plates)

@app.route('/image/<path:filename>')
def serve_image(filename):
    """
    Serve full-resolution image
    """
    viewer = LicensePlateDataViewer()
    
    # Construct full path
    base_dir = os.path.join(os.getcwd(), 'detected_plates')
    full_path = os.path.join(base_dir, filename)
    
    image_base64 = viewer.get_plate_image(full_path)
    
    if image_base64:
        return jsonify({'image': image_base64})
    else:
        return jsonify({'error': 'Image not found'}), 404

# Error Handling
@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404

@app.errorhandler(500)
def internal_server_error(e):
    return "Internal server error", 500

def main():
    # Ensure detected_plates directory exists
    os.makedirs('detected_plates', exist_ok=True)
    
    # Run Flask app
    app.run(debug=True, port=5000)

if __name__ == "__main__":
    main() 