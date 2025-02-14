import sys
import subprocess
import platform
import importlib

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Python Version Check:")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} - Upgrade required")
        return False

def check_dependencies():
    """Check critical dependencies"""
    dependencies = [
        'cv2', 'numpy', 'ultralytics', 'paddleocr', 
        'web3', 'streamlit', 'eth_account'
    ]
    
    print("\n📦 Dependency Check:")
    for dep in dependencies:
        try:
            importlib.import_module(dep)
            print(f"✅ {dep} - Installed")
        except ImportError:
            print(f"❌ {dep} - Not Installed")
            return False
    return True

def check_blockchain_setup():
    """Verify blockchain environment"""
    print("\n⛓️ Blockchain Environment Check:")
    try:
        # Check Hardhat installation
        hardhat_version = subprocess.check_output(['npx', 'hardhat', '--version'], text=True)
        print(f"✅ Hardhat Version: {hardhat_version.strip()}")
        
        # Check deployment info exists
        import os
        if os.path.exists('deployment-info.json'):
            print("✅ Contract Deployment Info Found")
            return True
        else:
            print("❌ No deployment information found")
            return False
    except Exception as e:
        print(f"❌ Blockchain setup error: {e}")
        return False

def check_camera_compatibility():
    """Check camera compatibility"""
    print("\n📷 Camera Compatibility:")
    try:
        import cv2
        cameras = []
        for i in range(3):  # Check first 3 camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cameras.append(i)
                cap.release()
        
        if cameras:
            print(f"✅ Available Camera Indices: {cameras}")
            return True
        else:
            print("❌ No cameras detected")
            return False
    except Exception as e:
        print(f"❌ Camera check failed: {e}")
        return False

def main():
    print("🔍 Vehicle Detection System - System Diagnostic")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_blockchain_setup(),
        check_camera_compatibility()
    ]
    
    if all(checks):
        print("\n🎉 System is ready for deployment!")
        print("Run 'streamlit run ui/app.py' to start the application")
    else:
        print("\n⚠️ Some system checks failed. Please resolve the issues.")

if __name__ == "__main__":
    main() 