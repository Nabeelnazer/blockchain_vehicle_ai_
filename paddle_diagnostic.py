import sys
import subprocess
import platform

def check_paddle_installation():
    """
    Comprehensive diagnostic for PaddlePaddle installation
    """
    print("🔍 PaddlePaddle Diagnostic Tool")
    print("=" * 40)

    # System Information
    print(f"\n📌 System Details:")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()[0]}")

    # Check PaddlePaddle installation
    try:
        import paddle
        print(f"\n✅ PaddlePaddle Installed")
        print(f"Version: {paddle.__version__}")
        print(f"Compiled with CUDA: {paddle.is_compiled_with_cuda()}")
    except ImportError:
        print("\n❌ PaddlePaddle Not Installed")
        
        # Attempt installation
        print("\n🔧 Attempting Installation...")
        try:
            subprocess.check_call([
                sys.executable, 
                '-m', 'pip', 
                'install', 
                'paddlepaddle==2.4.2', 
                '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple'
            ])
            print("✅ PaddlePaddle Installed Successfully")
        except Exception as e:
            print(f"❌ Installation Failed: {e}")
    
    # Check PaddleOCR
    try:
        import paddleocr
        print(f"\n✅ PaddleOCR Installed")
        print(f"Version: {paddleocr.__version__}")
    except ImportError:
        print("\n❌ PaddleOCR Not Installed")
        
        # Attempt installation
        try:
            subprocess.check_call([
                sys.executable, 
                '-m', 'pip', 
                'install', 
                'paddleocr'
            ])
            print("✅ PaddleOCR Installed Successfully")
        except Exception as e:
            print(f"❌ Installation Failed: {e}")

def main():
    check_paddle_installation()

if __name__ == "__main__":
    main() 