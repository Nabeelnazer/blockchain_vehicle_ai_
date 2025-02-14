import subprocess
import sys
import os
import json
import time

def check_dependencies():
    """
    Check and install required dependencies
    """
    try:
        # Check Node.js and npm
        subprocess.check_call(['node', '--version'])
        subprocess.check_call(['npm', '--version'])
        
        # Verify Hardhat installation
        subprocess.check_call(['npx', 'hardhat', '--version'])
        
        print("✅ All dependencies are installed correctly.")
        return True
    except subprocess.CalledProcessError:
        print("❌ Missing dependencies. Please install Node.js and npm.")
        return False

def install_dependencies():
    """
    Install project dependencies
    """
    try:
        # Install npm dependencies
        subprocess.check_call(['npm', 'install'])
        
        # Install Hardhat and toolbox
        subprocess.check_call([
            'npm', 'install', '--save-dev', 
            'hardhat', 
            '@nomicfoundation/hardhat-toolbox',
            '@nomicfoundation/hardhat-network-helpers',
            'ethers'
        ])
        
        print("✅ Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Dependency installation failed: {e}")
        sys.exit(1)

def setup_blockchain_environment():
    """
    Comprehensive blockchain environment setup
    """
    try:
        # Compile contracts
        subprocess.run(['npx', 'hardhat', 'compile'], check=True)
        
        # Start local Hardhat node
        node_process = subprocess.Popen(
            ['npx', 'hardhat', 'node'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        # Deploy contract
        subprocess.run(['npx', 'hardhat', 'run', 'blockchain/scripts/deploy.js'], check=True)
        
        # Read deployment info
        with open('deployment-info.json', 'r') as f:
            deployment_info = json.load(f)
        
        print("🚀 Blockchain Environment Setup Complete!")
        print(f"Contract Address: {deployment_info['address']}")
        
        return deployment_info
    
    except Exception as e:
        print(f"Blockchain setup failed: {e}")
        return None

def start_local_node():
    """
    Start local Hardhat Ethereum node
    """
    try:
        # Run Hardhat node in a separate process
        node_process = subprocess.Popen(
            ['npx', 'hardhat', 'node'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for the node to start
        time.sleep(3)
        
        return node_process
    except Exception as e:
        print(f"Failed to start local node: {e}")
        return None

def main():
    print("🚀 Blockchain Setup Utility")
    
    # Check and install dependencies
    if not check_dependencies():
        install_dependencies()
    
    # Start local node
    node_process = start_local_node()
    
    if node_process:
        print("✅ Local Ethereum node started successfully!")
        
        # Setup blockchain
        contract_info = setup_blockchain_environment()
        
        if contract_info:
            print("✅ Blockchain setup complete!")
            print(f"Contract Address: {contract_info['address']}")
        else:
            print("❌ Blockchain setup encountered issues.")
        
        # Wait for user input to stop the node
        input("Press Enter to stop the local node...")
        node_process.terminate()
    else:
        print("❌ Failed to start local Ethereum node.")

if __name__ == "__main__":
    main() 