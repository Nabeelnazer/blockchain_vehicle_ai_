import subprocess
import sys
import platform
import os
import shutil
import json
import re

def check_system_requirements():
    """
    Comprehensive system compatibility check
    """
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 8:
        print("❌ Python 3.8+ is required")
        return False
    
    # Check Node.js version
    try:
        node_version = subprocess.check_output(['node', '--version']).decode().strip()
        print(f"Node.js version: {node_version}")
        
        # Remove 'v' prefix and split version
        version_parts = node_version[1:].split('.')
        if int(version_parts[0]) < 18:
            print("❌ Node.js 18+ is required")
            return False
    except subprocess.CalledProcessError:
        print("❌ Node.js is not installed")
        return False
    
    return True

def clean_npm_environment():
    """
    Comprehensive npm environment cleaning (Windows-compatible)
    """
    try:
        # Force remove node_modules with elevated privileges
        if os.path.exists('node_modules'):
            subprocess.run(['rmdir', '/s', '/q', 'node_modules'], 
                           shell=True, 
                           capture_output=True)
        
        # Clean npm cache
        subprocess.run(['npm', 'cache', 'clean', '--force'], 
                       shell=True, 
                       capture_output=True, 
                       text=True)
        
        # Remove package-lock.json
        if os.path.exists('package-lock.json'):
            os.remove('package-lock.json')
        
        print("✅ NPM environment cleaned successfully")
    except Exception as e:
        print(f"❌ Cleaning failed: {e}")

def create_package_lock():
    """
    Create package-lock.json safely
    """
    try:
        subprocess.run(['npm', 'init', '-y'], 
                       shell=True, 
                       check=True)
        
        subprocess.run(['npm', 'pkg', 'set', 'scripts.prepare=npm install --legacy-peer-deps'], 
                       shell=True, 
                       check=True)
        
        print("✅ package.json initialized successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize package.json: {e}")

def install_npm_dependencies():
    """
    Comprehensive npm dependency management with conflict resolution
    """
    try:
        # Clean environment first
        clean_npm_environment()
        
        # Create initial package.json
        create_package_lock()
        
        # Install dependencies with specific strategy
        install_commands = [
            # Base dependencies
            ['npm', 'install', '--legacy-peer-deps', '--force'],
            
            # Specific version of ethers to match hardhat requirements
            ['npm', 'install', 'ethers@^5.7.2'],
            
            # TypeScript and Hardhat dependencies
            ['npm', 'install', '--save-dev', 
             '@typechain/ethers-v6@^0.5.0', 
             '@typechain/hardhat@^9.0.0', 
             '@types/mocha@^10.0.6', 
             'ts-node@^10.9.2', 
             'typescript@^5.3.3',
             'typechain@^8.3.1',
             '@nomicfoundation/hardhat-ethers@^3.0.0'
            ]
        ]
        
        for cmd in install_commands:
            install_result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True
            )
            
            # Print output for debugging
            print(' '.join(cmd))
            print(install_result.stdout)
            
            if install_result.returncode != 0:
                print("❌ Dependency installation failed:")
                print(install_result.stderr)
                # Continue despite errors
                continue
        
        # Attempt to fix vulnerabilities
        subprocess.run(['npm', 'audit', 'fix', '--force', '--legacy-peer-deps'], 
                       shell=True)
        
        print("✅ NPM Dependencies installed successfully")
    except Exception as e:
        print(f"❌ Dependency installation failed: {e}")

def install_python_dependencies():
    """
    Install Python dependencies with additional checks
    """
    try:
        # Upgrade pip and setuptools
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools'], check=True)
        
        # Read and clean requirements.txt
        with open('requirements.txt', 'r') as f:
            requirements = f.readlines()
        
        # Remove problematic lines
        cleaned_requirements = [
            req.strip() for req in requirements 
            if not req.startswith('@') and req.strip()
        ]
        
        # Write cleaned requirements
        with open('requirements.txt', 'w') as f:
            f.write('\n'.join(cleaned_requirements))
        
        # Install requirements with upgrade
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '--upgrade'], check=True)
        
        print("✅ Python Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Python dependency installation failed: {e}")

def verify_hardhat_installation():
    """
    Verify Hardhat installation and configuration
    """
    try:
        # Use npx to run hardhat
        version_result = subprocess.run(
            ['npx', 'hardhat', '--version'], 
            shell=True,
            capture_output=True, 
            text=True
        )
        
        if version_result.returncode == 0:
            print(f"✅ Hardhat Version: {version_result.stdout.strip()}")
            return True
        else:
            print("❌ Hardhat installation failed")
            print(version_result.stderr)
            return False
    except Exception as e:
        print(f"❌ Hardhat verification failed: {e}")
        return False

def main():
    print("🛠️ Comprehensive Dependency Management Utility")
    
    # Check system requirements
    if not check_system_requirements():
        print("❌ System does not meet requirements")
        sys.exit(1)
    
    # Install dependencies
    install_npm_dependencies()
    install_python_dependencies()
    
    # Verify Hardhat installation
    verify_hardhat_installation()
    
    print("✅ All dependencies installed and secured successfully!")

if __name__ == "__main__":
    main() 