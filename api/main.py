from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import sqlite3
from typing import List, Optional
from detection.yolo_detector import NumberPlateDetector
from ocr.ocr import OCRStabilizer
import cv2

import numpy as np
import base64

app = FastAPI(title="Vehicle Detection API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class VehicleEntry(BaseModel):
    id: Optional[int]
    plate_number: str
    entry_time: datetime
    confidence: float
    status: str = "pending"
    blockchain_tx: Optional[str] = None
    block_number: Optional[int] = None

class VehicleResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

# Base models for request/response
class DetectionRequest(BaseModel):
    image: str

class DetectionResponse(BaseModel):
    plate_number: str
    confidence: float
    timestamp: datetime

# Database connection
def get_db():
    conn = sqlite3.connect('vehicle_logs.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
async def root():
    return {"message": "Vehicle Detection API"}

@app.get("/entries/", response_model=List[VehicleEntry])
async def get_entries(limit: int = 10, offset: int = 0):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM vehicle_entries 
        ORDER BY entry_time DESC 
        LIMIT ? OFFSET ?
    """, (limit, offset))
    
    entries = cursor.fetchall()
    conn.close()
    
    return [dict(entry) for entry in entries]

@app.get("/entries/{plate_number}", response_model=List[VehicleEntry])
async def get_entry_by_plate(plate_number: str):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM vehicle_entries 
        WHERE plate_number = ? 
        ORDER BY entry_time DESC
    """, (plate_number,))
    
    entries = cursor.fetchall()
    conn.close()
    
    if not entries:
        raise HTTPException(status_code=404, detail="Plate number not found")
    
    return [dict(entry) for entry in entries]

@app.get("/statistics/")
async def get_statistics():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get total entries
    cursor.execute("SELECT COUNT(*) as total FROM vehicle_entries")
    total = cursor.fetchone()['total']
    
    # Get today's entries
    cursor.execute("""
        SELECT COUNT(*) as today 
        FROM vehicle_entries 
        WHERE date(entry_time) = date('now')
    """)
    today = cursor.fetchone()['today']
    
    # Get unique vehicles
    cursor.execute("""
        SELECT COUNT(DISTINCT plate_number) as unique_vehicles 
        FROM vehicle_entries
    """)
    unique = cursor.fetchone()['unique_vehicles']
    
    conn.close()
    
    return {
        "total_entries": total,
        "today_entries": today,
        "unique_vehicles": unique
    }

@app.post("/entries/", response_model=VehicleResponse)
async def add_entry(entry: VehicleEntry):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO vehicle_entries 
            (plate_number, entry_time, confidence, status) 
            VALUES (?, ?, ?, ?)
        """, (
            entry.plate_number,
            entry.entry_time,
            entry.confidence,
            entry.status
        ))
        
        conn.commit()
        entry_id = cursor.lastrowid
        
        return VehicleResponse(
            success=True,
            message="Entry added successfully",
            data={"id": entry_id}
        )
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        conn.close()

@app.delete("/entries/{entry_id}", response_model=VehicleResponse)
async def delete_entry(entry_id: int):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM vehicle_entries WHERE id = ?", (entry_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        return VehicleResponse(
            success=True,
            message="Entry deleted successfully"
        )
    
    finally:
        conn.close()

@app.post("/detect/", response_model=VehicleResponse)
async def detect_plate(image: str):  # Base64 encoded image
    try:
        # Decode base64 image
        img_bytes = base64.b64decode(image)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Initialize detectors
        detector = NumberPlateDetector('best.pt')
        ocr = OCRStabilizer()
        
        # Detect plates
        plates = detector.detect_plates(frame)
        
        results = []
        for x, y, w, h in plates:
            # Extract plate region
            plate_img = frame[y:y+h, x:x+w]
            
            # Perform OCR
            plate_number = ocr.get_stable_plate_number(plate_img)
            
            if plate_number:
                results.append({
                    "plate_number": plate_number,
                    "confidence": 0.8,  # You can get actual confidence from OCR
                    "bbox": [x, y, w, h]
                })
        
        return VehicleResponse(
            success=True,
            message=f"Detected {len(results)} plates",
            data={"detections": results}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))