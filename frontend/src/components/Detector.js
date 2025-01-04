import React, { useState } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000';

function Detector() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [detections, setDetections] = useState([]);
    const [resultImage, setResultImage] = useState(null);

    const handleFileSelect = (event) => {
        setSelectedFile(event.target.files[0]);
    };

    const handleDetect = async () => {
        if (!selectedFile) {
            alert('Please select an image');
            return;
        }

        const formData = new FormData();
        formData.append('image', selectedFile);

        try {
            const response = await axios.post(`${API_URL}/detect`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            setDetections(response.data.detections);
            setResultImage(`${API_URL}/uploads/${response.data.result_image}`);
        } catch (error) {
            console.error('Detection error:', error);
            alert('Detection failed');
        }
    };

    return (
        <div>
            <h1>License Plate Detector</h1>
            <input 
                type="file" 
                onChange={handleFileSelect} 
                accept="image/*" 
            />
            <button onClick={handleDetect}>Detect Plates</button>

            {resultImage && (
                <div>
                    <h2>Detected Plates</h2>
                    <img 
                        src={resultImage} 
                        alt="Detected Plates" 
                        style={{ maxWidth: '100%' }} 
                    />
                    <div>
                        {detections.map((det, index) => (
                            <p key={index}>
                                Plate Confidence: {det.confidence.toFixed(2)}
                            </p>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export default Detector; 