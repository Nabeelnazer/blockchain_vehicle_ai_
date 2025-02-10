import logging
import sys
import os

# Ensure the project root is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vehicle_detection.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_blockchain_setup():
    """Setup blockchain environment"""
    try:
        from setup import setup_blockchain
        logger.info("Setting up blockchain environment...")
        return setup_blockchain()
    except Exception as e:
        logger.error(f"Blockchain setup failed: {e}")
        return None

def run_detection_system():
    """Run the main vehicle detection system"""
    try:
        from ui.app import main as run_ui
        logger.info("Starting Vehicle Detection UI...")
        run_ui()
    except Exception as e:
        logger.error(f"Detection system failed: {e}")

def run_api_server():
    """Start the FastAPI server"""
    try:
        import uvicorn
        logger.info("Starting FastAPI server...")
        uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        logger.error(f"API server failed: {e}")

def main():
    """Main entry point for the vehicle detection system"""
    try:
        # Setup blockchain
        blockchain_setup = run_blockchain_setup()
        
        # Verify blockchain setup
        if blockchain_setup is None:
            logger.warning("Blockchain setup incomplete. Continuing with limited functionality.")
        
        # Run detection system
        run_detection_system()
        
        # Optional: Run API server in a separate thread or process
        # Uncomment if you want to run API server alongside UI
        # from multiprocessing import Process
        # api_process = Process(target=run_api_server)
        # api_process.start()
        
    except Exception as e:
        logger.critical(f"System startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
