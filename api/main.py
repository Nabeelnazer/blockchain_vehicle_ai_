from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np

from detection.yolo_detector import NumberPlateDetector
from ocr.ocr import OCRStabilizer
from blockchain.blockchain_manager import BlockchainManager
from database.vehicle_log import VehicleLogger

app = FastAPI(
    title="Vehicle Detection API",
    description="Real-time vehicle plate detection and blockchain logging",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
detector = NumberPlateDetector('best.pt')
ocr = OCRStabilizer()
blockchain_manager = BlockchainManager()
vehicle_logger = VehicleLogger()

@app.post("/detect/")
async def detect_vehicle(file: UploadFile = File(...)):
    """
    Detect vehicle plate from uploaded image
    """
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Detect plates
        plates = detector.detect_plates(frame)
        
        detected_plates = []
        for x, y, w, h in plates:
            # Extract plate region
            plate_img = frame[int(y):int(y+h), int(x):int(x+w)]
            
            # OCR plate number
            plate_number = ocr.get_stable_plate_number(plate_img)
            
            if plate_number:
                # Log to database
                vehicle_logger.log_vehicle_entry(plate_number)
                
                # Optional: Blockchain logging
                blockchain_tx = blockchain_manager.log_vehicle_entry(plate_number)
                
                detected_plates.append({
                    'plate_number': plate_number,
                    'blockchain_tx': blockchain_tx
                })
        
        return {
            "detected_plates": detected_plates,
            "total_plates": len(detected_plates)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recent_entries/")
def get_recent_entries(limit: int = 10):
    """
    Retrieve recent vehicle entries
    """
    try:
        recent_entries = vehicle_logger.get_recent_entries(limit)
        return {"entries": recent_entries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Blockchain-specific endpoints
@app.get("/blockchain/verify/{plate_number}")
def verify_vehicle_entry(plate_number: str):
    """
    Verify a vehicle entry on blockchain
    """
    try:
        is_verified = blockchain_manager.verify_vehicle_entry(plate_number)
        return {"plate_number": plate_number, "verified": is_verified}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)