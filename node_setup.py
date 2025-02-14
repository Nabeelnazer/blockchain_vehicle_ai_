import subprocess
import sys
import os
import platform

def install_node():
    """
    Install Node.js based on the operating system
    """
    system = platform.system().lower()
    
    print("🌐 Node.js Installation Utility")
    
    try:
        # Check if Node.js is already installed
        subprocess.run(['node', '--version'], check=True)
        print("✅ Node.js is already installed")
        return
    
    except subprocess.CalledProcessError:
        print("❌ Node.js not found. Proceeding with installation...")
    
    if system == 'windows':
        # Windows installation via official installer
        print("🖥️ Downloading Node.js installer for Windows...")
        subprocess.run([
            'powershell', 
            '-Command', 
            'Invoke-WebRequest -Uri "https://nodejs.org/dist/v18.16.0/node-v18.16.0-x64.msi" -OutFile "nodejs_installer.msi"'
        ], check=True)
        
        print("🔧 Installing Node.js...")
        subprocess.run(['msiexec', '/i', 'nodejs_installer.msi', '/qn'], check=True)
    
    elif system == 'darwin':  # macOS
        subprocess.run(['brew', 'install', 'node'], check=True)
    
    elif system == 'linux':
        # For Ubuntu/Debian
        subprocess.run(['sudo', 'apt-get', 'update'], check=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'nodejs', 'npm'], check=True)
    
    print("✅ Node.js installation complete")

def install_hardhat():
    """
    Install Hardhat globally
    """
    print("🛠️ Installing Hardhat...")
    
    try:
        subprocess.run(['npm', 'install', '-g', 'hardhat'], check=True)
        print("✅ Hardhat installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Hardhat installation failed")
        sys.exit(1)

def verify_installation():
    """
    Verify Node.js and Hardhat installation
    """
    try:
        node_version = subprocess.check_output(['node', '--version']).decode().strip()
        npm_version = subprocess.check_output(['npm', '--version']).decode().strip()
        hardhat_version = subprocess.check_output(['npx', 'hardhat', '--version']).decode().strip()
        
        print(f"🔍 Verification Results:")
        print(f"Node.js Version: {node_version}")
        print(f"npm Version: {npm_version}")
        print(f"Hardhat Version: {hardhat_version}")
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Verification failed: {e}")
        sys.exit(1)

def main():
    install_node()
    install_hardhat()
    verify_installation()

if __name__ == "__main__":
    main() 