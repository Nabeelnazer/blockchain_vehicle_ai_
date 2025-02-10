import os
import sys
import subprocess

def install_dependencies():
    """Install project dependencies"""
    # Ensure pip is up to date
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    
    # Install dependencies
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

def setup_blockchain():
    """Setup blockchain environment"""
    try:
        # Ensure solcx is installed
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'py-solc-x'])
        
        # Now import after installation
        try:
            from solcx import compile_standard, install_solc
        except ImportError:
            print("Failed to import solcx. Please install manually.")
            return None
        
        # Install Solidity compiler
        install_solc('0.8.0')
        
        # Compile contract
        contract_path = 'blockchain/contracts/VehicleRegistry.sol'
        if not os.path.exists(contract_path):
            print(f"Contract file not found at {contract_path}")
            return None
        
        with open(contract_path, 'r') as file:
            contract_source_code = file.read()
        
        compiled_sol = compile_standard({
            "language": "Solidity",
            "sources": {
                "VehicleRegistry.sol": {
                    "content": contract_source_code
                }
            },
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                    }
                }
            }
        }, solc_version="0.8.0")
        
        print("Blockchain setup completed successfully!")
        return compiled_sol
    except Exception as e:
        print(f"Blockchain setup failed: {e}")
        return None

def main():
    print("Setting up Vehicle Detection System...")
    
    # Install dependencies
    install_dependencies()
    
    # Setup blockchain
    compiled_contract = setup_blockchain()
    
    if compiled_contract:
        print("Setup complete! Ready to run the project.")
    else:
        print("Setup encountered issues. Please check the error messages.")

if __name__ == "__main__":
    main() 