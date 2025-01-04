import os
import cv2
import numpy as np
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from detector import LicensePlateDetector

app = Flask(__name__)
CORS(app)

# Initialize detector
detector = LicensePlateDetector()

# Ensure uploads directory exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/detect', methods=['POST'])
def detect_license_plate():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    
    # Read image
    img_array = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    
    # Detect plates
    detections = detector.detect_plates(frame)
    
    # Draw detections on frame
    result_frame = detector.draw_detections(frame, detections)
    
    # Save result image
    result_path = os.path.join(UPLOAD_FOLDER, 'detected_plate.jpg')
    cv2.imwrite(result_path, result_frame)
    
    return jsonify({
        'detections': detections,
        'result_image': 'detected_plate.jpg'
    })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
