import sys
import importlib
import subprocess
import platform

def check_dependencies():
    """Check if all required dependencies are installed"""
    dependencies = [
        'cv2', 'paddleocr', 'ultralytics', 'web3', 
        'easyocr', 'streamlit', 'fastapi', 'solcx'
    ]
    
    print("Dependency Check:")
    for dep in dependencies:
        try:
            # Special handling for solcx
            if dep == 'solcx':
                import solcx
            else:
                importlib.import_module(dep)
            print(f"✓ {dep} is installed")
        except ImportError:
            print(f"✗ {dep} is NOT installed")
            # Attempt to install
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
                print(f"⚠️ Installed {dep}")
            except:
                print(f"❌ Could not install {dep}")

def check_system_components():
    """Check if key system components are working"""
    try:
        from detection.yolo_detector import NumberPlateDetector
        from ocr.ocr import OCRStabilizer
        from database.vehicle_log import VehicleLogger
        
        print("\nSystem Components Check:")
        print("✓ Detector initialized")
        print("✓ OCR initialized")
        print("✓ Database logger initialized")
    except Exception as e:
        print(f"System component check failed: {e}")

def check_system_compatibility():
    """Check system compatibility for PaddlePaddle"""
    print("\nSystem Compatibility Check:")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()[0]}")

def check_paddle_dependencies():
    """Comprehensive check for Paddle and OCR dependencies"""
    try:
        import paddle
        import paddleocr
        
        print("\nPaddle Dependency Check:")
        print(f"✓ PaddlePaddle version: {paddle.__version__}")
        print(f"✓ PaddleOCR version: {paddleocr.__version__}")
        
        # Additional validation
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang='en')
        print("✓ PaddleOCR initialization successful")
    
    except ImportError as e:
        print(f"❌ Paddle Import Error: {e}")
        print("Recommended fix:")
        print("1. Uninstall existing packages:")
        print("   pip uninstall paddlepaddle paddleocr -y")
        print("2. Install compatible versions:")
        print("   pip install paddlepaddle==2.4.2 -i https://pypi.tuna.tsinghua.edu.cn/simple")
        print("   pip install 'paddleocr>=2.0.1'")
        
        # Attempt automatic fix
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
                                   'paddlepaddle==2.4.2', 
                                   '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple'])
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'paddleocr'])
            print("✓ Automatic installation attempted")
        except Exception as install_error:
            print(f"❌ Automatic installation failed: {install_error}")
    
    except Exception as e:
        print(f"❌ Paddle Initialization Error: {e}")

def check_database_connection():
    """Check PostgreSQL database connection"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from dotenv import load_dotenv
        import os

        # Load environment variables
        load_dotenv()

        # Retrieve database connection string from environment
        DATABASE_URL = os.getenv('DATABASE_URL', 
            'postgresql://username:password@localhost:5432/vehicle_detection')
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as connection:
            print("\nDatabase Connection Check:")
            print("✓ PostgreSQL connection successful")
            print(f"✓ Connected to database: {DATABASE_URL.split('@')[-1]}")
    
    except ImportError:
        print("❌ SQLAlchemy or psycopg2 not installed")
        print("Recommended fix:")
        print("pip install sqlalchemy psycopg2-binary")
    
    except Exception as e:
        print(f"❌ Database Connection Error: {e}")
        print("Troubleshooting tips:")
        print("1. Verify DATABASE_URL in .env file")
        print("2. Ensure PostgreSQL server is running")
        print("3. Check network and credentials")

def main():
    print("Vehicle Detection System Diagnostics")
    print("=" * 40)
    
    check_dependencies()
    check_system_compatibility()
    check_paddle_dependencies()
    check_system_components()
    check_database_connection()

if __name__ == "__main__":
    main() 