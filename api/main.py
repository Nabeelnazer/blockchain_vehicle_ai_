from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from detection.yolo_detector import NumberPlateDetector
from ocr.ocr import OCRStabilizer
from blockchain.blockchain_manager import BlockchainManager

app = FastAPI()

# Allow CORS for frontend applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
detector = NumberPlateDetector('best.pt')  # Path to your YOLO model
ocr_stabilizer = OCRStabilizer()
blockchain_manager = BlockchainManager()

@app.post("/process_frame/")
async def process_frame(frame: bytes):
    # Process the frame with the detector and OCR
    # Log the vehicle entry on the blockchain
    return {"message": "Frame processed successfully"}