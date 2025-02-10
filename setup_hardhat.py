import os
import subprocess
import sys

def clone_hardhat_repo():
    """
    Clone Hardhat repository
    """
    repo_url = "https://github.com/NomicFoundation/hardhat.git"
    
    # Create blockchain-integration directory if not exists
    os.makedirs('blockchain-integration', exist_ok=True)
    
    # Change to blockchain-integration directory
    os.chdir('blockchain-integration')
    
    # Clone repository
    try:
        subprocess.check_call(['git', 'clone', repo_url, '.'])
        print("✅ Hardhat repository cloned successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to clone Hardhat repository")
        sys.exit(1)

def install_dependencies():
    """
    Install Hardhat and project dependencies
    """
    try:
        # Initialize npm project
        subprocess.check_call(['npm', 'init', '-y'])
        
        # Install Hardhat and related dependencies
        hardhat_deps = [
            'hardhat', 
            '@nomicfoundation/hardhat-toolbox',
            '@nomicfoundation/hardhat-network-helpers',
            '@nomiclabs/hardhat-ethers', 
            'ethers',
            'chai'
        ]
        
        subprocess.check_call(['npm', 'install', '--save-dev'] + hardhat_deps)
        
        # Initialize Hardhat project
        subprocess.check_call(['npx', 'hardhat'])
        
        print("✅ Hardhat dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Dependency installation failed: {e}")
        sys.exit(1)

def main():
    print("🚀 Hardhat Project Setup")
    print("=" * 30)
    
    # Ensure Node.js and npm are installed
    try:
        subprocess.check_call(['node', '--version'])
        subprocess.check_call(['npm', '--version'])
    except subprocess.CalledProcessError:
        print("❌ Node.js or npm not installed. Please install Node.js first.")
        sys.exit(1)
    
    # Clone repository
    clone_hardhat_repo()
    
    # Install dependencies
    install_dependencies()
    
    print("\n🎉 Hardhat project setup complete!")

if __name__ == "__main__":
    main() 