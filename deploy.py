import subprocess
import sys
import os
import platform

def get_npm_command():
    """
    Get the appropriate npm command based on the operating system
    """
    system = platform.system().lower()
    if system == 'windows':
        return ['npm.cmd']
    return ['npm']

def run_command(command, error_message, shell=False):
    """
    Run a shell command with comprehensive error handling
    """
    try:
        # Ensure command is a list
        if isinstance(command, str):
            command = [command]
        
        # Add shell=True for Windows compatibility
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True,
            shell=shell if platform.system().lower() == 'windows' else False
        )
        print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"{error_message}: {e}")
        print("Error Output:", e.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def prepare_blockchain_environment():
    """
    Comprehensive blockchain environment preparation
    """
    print("🛠️ Preparing Blockchain Environment")
    
    # Get appropriate npm command
    npm_cmd = get_npm_command()
    
    # Check and install npm dependencies
    run_command(
        npm_cmd + ['install'], 
        "Failed to install npm dependencies"
    )
    
    # Install Hardhat and related dependencies
    run_command(
        npm_cmd + ['install', '--save-dev', 
         'hardhat', 
         '@nomicfoundation/hardhat-toolbox', 
         '@nomicfoundation/hardhat-network-helpers', 
         'ethers'],
        "Failed to install Hardhat dependencies"
    )
    
    # Initialize Hardhat project if not already initialized
    if not os.path.exists('hardhat.config.js'):
        run_command(
            ['npx', 'hardhat', 'init'], 
            "Failed to initialize Hardhat project"
        )

def deploy_blockchain():
    """
    Deploy blockchain contracts with comprehensive error handling
    """
    # Prepare environment
    prepare_blockchain_environment()
    
    try:
        # Compile contracts
        run_command(
            ['npx', 'hardhat', 'compile'], 
            "Blockchain contract compilation failed"
        )
        
        # Deploy to local network
        deploy_result = run_command(
            ['npx', 'hardhat', 'run', 'blockchain/scripts/deploy.js', '--network', 'localhost'], 
            "Blockchain deployment failed"
        )
        
        if deploy_result:
            print("✅ Blockchain contracts deployed successfully")
        else:
            print("❌ Blockchain deployment encountered issues")
    
    except Exception as e:
        print(f"Deployment Error: {e}")
        sys.exit(1)

def start_hardhat_node():
    """
    Start local Hardhat Ethereum node with robust error handling
    """
    try:
        # Determine the appropriate command based on the operating system
        if platform.system().lower() == 'windows':
            # Use npx.cmd for Windows
            node_process = subprocess.Popen(
                ['npx.cmd', 'hardhat', 'node'], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
        else:
            # Use npx for Unix-like systems
            node_process = subprocess.Popen(
                ['npx', 'hardhat', 'node'], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
        
        print("✅ Local Hardhat node started")
        return node_process
    
    except Exception as e:
        print(f"❌ Failed to start Hardhat node: {e}")
        sys.exit(1)

def main():
    print("🚀 Vehicle Detection System - Deployment Utility")
    
    # Verify Node.js and npm
    try:
        # Use appropriate command for Windows
        if platform.system().lower() == 'windows':
            subprocess.run(['node.exe', '--version'], check=True)
            subprocess.run(['npm.cmd', '--version'], check=True)
        else:
            subprocess.run(['node', '--version'], check=True)
            subprocess.run(['npm', '--version'], check=True)
    except subprocess.CalledProcessError:
        print("❌ Node.js or npm is not installed. Please install Node.js.")
        sys.exit(1)
    
    # Start Hardhat node
    node_process = start_hardhat_node()
    
    try:
        # Deploy blockchain contracts
        deploy_blockchain()
        
        # Provide instructions
        print("\n🎉 Deployment Complete!")
        print("Next steps:")
        print("1. Run system diagnostic: python system_diagnostic.py")
        print("2. Start application: streamlit run ui/app.py")
    
    except KeyboardInterrupt:
        print("\n🛂 Deployment interrupted")
    finally:
        # Terminate Hardhat node
        if node_process:
            node_process.terminate()

if __name__ == "__main__":
    main() 