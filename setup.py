import os
import sys
import subprocess
import json

def install_dependencies():
    """Install project dependencies"""
    # Ensure pip is up to date
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    
    # Install dependencies
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

def setup_blockchain():
    """
    Setup blockchain environment with Hardhat
    """
    try:
        # Ensure Hardhat is installed
        subprocess.check_call(['npx', '-v'])
        
        # Compile contracts
        compile_result = subprocess.run(
            ['npx', 'hardhat', 'compile'], 
            capture_output=True, 
            text=True
        )
        
        if compile_result.returncode != 0:
            print("Compilation failed:")
            print(compile_result.stderr)
            return None
        
        # Deploy contract
        deploy_result = subprocess.run(
            ['npx', 'hardhat', 'run', 'blockchain/scripts/deploy.js'], 
            capture_output=True, 
            text=True
        )
        
        if deploy_result.returncode != 0:
            print("Deployment failed:")
            print(deploy_result.stderr)
            return None
        
        # Read deployment info
        deployment_path = 'deployment-info.json'
        if not os.path.exists(deployment_path):
            print(f"Deployment info file not found at {deployment_path}")
            return None
        
        with open(deployment_path, 'r') as f:
            deployment_info = json.load(f)
        
        return {
            'address': deployment_info['address'],
            'abi': deployment_info['abi']
        }
    
    except Exception as e:
        print(f"Blockchain setup failed: {e}")
        return None

def main():
    print("Setting up Vehicle Detection System...")
    
    # Install dependencies
    install_dependencies()
    
    # Setup blockchain
    contract_info = setup_blockchain()
    
    if contract_info:
        print("Blockchain setup complete!")
        print(f"Contract Address: {contract_info['address']}")
    else:
        print("Blockchain setup encountered issues.")

if __name__ == "__main__":
    main() 