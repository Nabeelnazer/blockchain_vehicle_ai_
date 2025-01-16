from ocr.ocr import OCRProcessor
from blockchain.blockchain_manager import BlockchainManager
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_document(image_path):
    try:
        # Initialize components
        ocr_processor = OCRProcessor()
        blockchain_manager = BlockchainManager()
        
        # Process image with OCR
        logger.info(f"Processing image: {image_path}")
        ocr_results = ocr_processor.process_image(image_path)
        
        # Store results on blockchain
        logger.info("Storing results on blockchain")
        tx_receipt = blockchain_manager.store_ocr_hash(ocr_results)
        
        return {
            'ocr_results': ocr_results,
            'blockchain_tx': tx_receipt.transactionHash.hex()
        }
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage
    image_path = "path/to/your/image.jpg"
    results = process_document(image_path)
    print(f"OCR Results: {results['ocr_results']}")
    print(f"Blockchain Transaction: {results['blockchain_tx']}")
