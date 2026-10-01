import logging
import os

from fastapi import FastAPI, File, UploadFile, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np

from detection.yolo_detector import NumberPlateDetector
from blockchain.blockchain_manager import BlockchainManager
from database.vehicle_log import VehicleLogger

app = FastAPI(
    title="Vehicle Detection API",
    description="Real-time vehicle plate detection and blockchain logging",
    version="1.0.0"
)

logger = logging.getLogger(__name__)

# Uploads larger than this are refused before decoding.
MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_BYTES", 10 * 1024 * 1024))
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}

# CORS: only the origins listed in CORS_ORIGINS (comma-separated), never "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in os.environ.get("CORS_ORIGINS", "http://localhost:8501").split(",") if o],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Initialize components
detector = NumberPlateDetector('best.pt')
vehicle_logger = VehicleLogger()

_blockchain_manager = None


def get_blockchain_manager():
    """Shared connection, or None while the node or contract is unavailable.

    Retried on each call so the API recovers once the node comes up."""
    global _blockchain_manager
    if _blockchain_manager is None:
        try:
            manager = BlockchainManager()
            if manager.contract is not None:
                _blockchain_manager = manager
        except Exception:
            logger.warning("Blockchain unavailable; entries are saved locally only", exc_info=True)
    return _blockchain_manager

@app.post("/detect/")
async def detect_vehicle(file: UploadFile = File(...)):
    """
    Detect vehicle plate from uploaded image
    """
    try:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=415, detail="Upload a JPEG or PNG image")

        # Read one byte past the limit so an oversized upload is caught without reading it all
        contents = await file.read(MAX_UPLOAD_BYTES + 1)
        if len(contents) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Image is too large")

        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            raise HTTPException(status_code=400, detail="Could not decode the image")
        
        # Detect plates
        plates = detector.detect_plates(frame)
        
        detected_plates = []
        for x1, y1, x2, y2 in plates:
            # Extract plate region (the detector returns corners, not width/height)
            plate_img = frame[y1:y2, x1:x2]
            
            # OCR plate number: one read per upload, no multi-frame stabilising
            plate_info = detector.process_plate(plate_img)
            
            if plate_info:
                plate_number = plate_info['text']
                confidence = plate_info['confidence']
                
                # Log to database
                entry_id = vehicle_logger.log_vehicle_entry(plate_number, confidence)
                
                # Optional: Blockchain logging
                blockchain_tx = None
                blockchain_manager = get_blockchain_manager()
                if blockchain_manager:
                    blockchain_tx = blockchain_manager.log_vehicle_entry(plate_number, confidence)
                    vehicle_logger.record_blockchain_tx(entry_id, blockchain_tx)
                
                detected_plates.append({
                    'plate_number': plate_number,
                    'confidence': confidence,
                    'blockchain_tx': blockchain_tx
                })
        
        return {
            "detected_plates": detected_plates,
            "total_plates": len(detected_plates)
        }
    
    except HTTPException:
        raise
    except Exception:
        logger.exception("Request failed")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/recent_entries/")
def get_recent_entries(limit: int = Query(10, ge=1, le=100)):
    """
    Retrieve recent vehicle entries
    """
    try:
        recent_entries = vehicle_logger.get_recent_entries(limit)
        return {"entries": recent_entries}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Request failed")
        raise HTTPException(status_code=500, detail="Internal server error")

# Blockchain-specific endpoints
@app.get("/blockchain/verify/{plate_number}")
def verify_vehicle_entry(plate_number: str = Path(..., min_length=1, max_length=20)):
    """
    Verify a vehicle's blockchain entry
    """
    try:
        blockchain_manager = get_blockchain_manager()
        if blockchain_manager is None:
            raise HTTPException(status_code=503, detail="Blockchain unavailable")
        is_active = blockchain_manager.contract.functions.isVehicleActive(plate_number).call()
        
        return {
            "plate_number": plate_number,
            "is_active": is_active,
            "verified": True
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Request failed")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.environ.get("API_HOST", "127.0.0.1"), port=8000)