import subprocess
import sys
import os
import platform
import re
import shutil
import json

def get_system_command(command):
    """
    Get the appropriate command for the current operating system
    """
    system = platform.system().lower()
    if system == 'windows':
        # Windows-specific command modifications
        if command == 'npm':
            return 'npm.cmd'
        elif command == 'node':
            return 'node.exe'
    return command

def check_and_install_prerequisites():
    """
    Check and install prerequisite tools
    """
    print("🔍 Checking System Prerequisites")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 8:
        print(f"❌ Python version {python_version.major}.{python_version.minor} is not supported")
        print("Please upgrade to Python 3.8 or higher")
        sys.exit(1)

def check_node_version():
    """
    Check and manage Node.js version
    """
    print("🔍 Checking Node.js Version")
    
    try:
        # Use system-specific command
        node_cmd = get_system_command('node')
        
        # Get current Node.js version
        node_version_output = subprocess.check_output([node_cmd, '--version']).decode().strip()
        
        # Extract version number
        version_match = re.match(r'v(\d+)', node_version_output)
        if version_match:
            current_version = int(version_match.group(1))
            
            # If not version 16, install Node.js 16
            if current_version != 16:
                print(f"❌ Current Node.js version is {current_version}. Switching to version 16.")
                install_node_16()
            else:
                print(f"✅ Node.js version 16 is already installed: {node_version_output}")
        else:
            print("❌ Unable to parse Node.js version")
            install_node_16()
    
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js not found")
        install_node_16()

def install_node_16():
    """
    Install Node.js version 16 with multiple fallback methods
    """
    system = platform.system().lower()
    print("🌐 Installing Node.js 16")
    
    installation_methods = [
        install_via_nvm,
        install_via_official_installer,
        install_via_package_manager
    ]
    
    for method in installation_methods:
        try:
            method(system)
            verify_node_installation()
            return
        except Exception as e:
            print(f"❌ Installation method failed: {method.__name__}")
            print(f"Error: {e}")
            continue
    
    print("❌ All Node.js installation methods failed")
    sys.exit(1)

def install_via_nvm(system):
    """
    Install Node.js using Node Version Manager
    """
    print("🔧 Attempting NVM Installation")
    
    if system == 'windows':
        # NVM for Windows
        nvm_install_url = "https://github.com/coreybutler/nvm-windows/releases/download/1.1.11/nvm-setup.exe"
        subprocess.run([
            'powershell', 
            '-Command', 
            f'Invoke-WebRequest -Uri "{nvm_install_url}" -OutFile "nvm-setup.exe"'
        ], check=True)
        
        subprocess.run(['nvm-setup.exe', '/SILENT'], check=True)
        subprocess.run(['nvm', 'install', '16'], check=True)
        subprocess.run(['nvm', 'use', '16'], check=True)
    
    elif system == 'darwin':
        # macOS NVM installation
        subprocess.run([
            '/bin/bash', 
            '-c', 
            'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash'
        ], check=True)
        
        subprocess.run([
            '/bin/bash', 
            '-c', 
            'source ~/.nvm/nvm.sh && nvm install 16 && nvm use 16'
        ], check=True)
    
    elif system == 'linux':
        # Linux NVM installation
        subprocess.run([
            '/bin/bash', 
            '-c', 
            'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash'
        ], check=True)
        
        subprocess.run([
            '/bin/bash', 
            '-c', 
            'source ~/.nvm/nvm.sh && nvm install 16 && nvm use 16'
        ], check=True)

def install_via_official_installer(system):
    """
    Install Node.js using official installer
    """
    print("🔧 Attempting Official Installer")
    
    if system == 'windows':
        # Windows official installer
        node_url = "https://nodejs.org/dist/v16.20.2/node-v16.20.2-x64.msi"
        subprocess.run([
            'powershell', 
            '-Command', 
            f'Invoke-WebRequest -Uri "{node_url}" -OutFile "node-v16-installer.msi"'
        ], check=True)
        
        subprocess.run(['msiexec', '/i', 'node-v16-installer.msi', '/qn'], check=True)
    
    elif system == 'darwin':
        # macOS official installer via Homebrew
        subprocess.run(['brew', 'install', 'node@16'], check=True)
    
    elif system == 'linux':
        # Linux official installation
        subprocess.run([
            'curl', '-fsSL', 'https://deb.nodesource.com/setup_16.x', '|', 'sudo', '-E', 'bash', '-'
        ], check=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'nodejs'], check=True)

def install_via_package_manager(system):
    """
    Install Node.js using system package manager
    """
    print("🔧 Attempting Package Manager Installation")
    
    if system == 'windows':
        # Chocolatey for Windows
        subprocess.run(['choco', 'install', 'nodejs-lts', '--version=16.20.2'], check=True)
    
    elif system == 'darwin':
        # Homebrew for macOS
        subprocess.run(['brew', 'install', 'node@16'], check=True)
    
    elif system == 'linux':
        # APT for Ubuntu/Debian
        subprocess.run(['sudo', 'apt-get', 'update'], check=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'nodejs'], check=True)

def verify_node_installation():
    """
    Verify Node.js and npm installation
    """
    try:
        node_cmd = get_system_command('node')
        npm_cmd = get_system_command('npm')
        
        node_version = subprocess.check_output([node_cmd, '--version']).decode().strip()
        npm_version = subprocess.check_output([npm_cmd, '--version']).decode().strip()
        
        print(f"✅ Node.js Version: {node_version}")
        print(f"✅ npm Version: {npm_version}")
    except Exception as e:
        print(f"❌ Node.js verification failed: {e}")
        sys.exit(1)

def install_hardhat():
    """
    Install Hardhat with comprehensive error handling and dependency resolution
    """
    print("🛠️ Installing Hardhat")
    
    try:
        npm_cmd = get_system_command('npm')
        
        # Ensure package.json exists
        if not os.path.exists('package.json'):
            subprocess.run([npm_cmd, 'init', '-y'], check=True)
        
        # Uninstall conflicting packages
        subprocess.run([npm_cmd, 'uninstall', 'ethers', '@nomiclabs/hardhat-ethers', '@nomiclabs/hardhat-waffle', 'ethereum-waffle'], check=True)
        
        # Install compatible versions of dependencies
        install_commands = [
            # Install specific versions of ethers and hardhat-related packages
            [npm_cmd, 'install', '--save-dev', 
             'hardhat', 
             'ethers@^5.7.2', 
             '@nomiclabs/hardhat-ethers@^2.2.3', 
             '@nomiclabs/hardhat-waffle@^2.0.6', 
             'ethereum-waffle@^4.0.10',
             'chai@^4.3.4'
            ],
            # Fallback to legacy peer deps if first method fails
            [npm_cmd, 'install', '--save-dev', 'hardhat', '--legacy-peer-deps'],
            # Last resort: force install
            [npm_cmd, 'install', '--save-dev', 'hardhat', '--force']
        ]
        
        # Try different installation strategies
        for cmd in install_commands:
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(result.stdout)
                break
            except subprocess.CalledProcessError as e:
                print(f"Installation attempt failed: {cmd}")
                print(f"Error: {e.stderr}")
                continue
        
        # Initialize Hardhat project if not already initialized
        if not os.path.exists('hardhat.config.js'):
            subprocess.run(['npx', 'hardhat', 'init'], check=True)
        
        print("✅ Hardhat installed successfully")
    
    except Exception as e:
        print(f"❌ Hardhat installation failed: {e}")
        
        # Additional diagnostic information
        print("\n🔍 Diagnostic Information:")
        try:
            # Check npm configuration
            npm_config = subprocess.check_output([npm_cmd, 'config', 'list'], text=True)
            print("NPM Configuration:")
            print(npm_config)
        except Exception:
            print("Could not retrieve npm configuration")
        
        sys.exit(1)

def verify_blockchain_setup():
    """
    Comprehensive blockchain environment verification
    """
    print("🔬 Verifying Blockchain Environment")
    
    try:
        # Check Hardhat version
        hardhat_version = subprocess.check_output(['npx', 'hardhat', '--version']).decode().strip()
        print(f"✅ Hardhat Version: {hardhat_version}")
        
        # Verify package.json dependencies
        with open('package.json', 'r') as f:
            package_config = json.load(f)
        
        # Check for critical dependencies
        critical_deps = [
            'hardhat', 
            'ethers', 
            '@nomiclabs/hardhat-ethers', 
            '@nomiclabs/hardhat-waffle'
        ]
        
        print("\n📦 Dependency Verification:")
        for dep in critical_deps:
            dev_dep = package_config.get('devDependencies', {}).get(dep)
            if dev_dep:
                print(f"✅ {dep}: {dev_dep}")
            else:
                print(f"❌ {dep} not found")
        
        # Compile contracts
        subprocess.run(['npx', 'hardhat', 'compile'], check=True)
        print("✅ Contracts compiled successfully")
    
    except Exception as e:
        print(f"❌ Blockchain setup verification failed: {e}")
        sys.exit(1)

def main():
    print("🚀 Blockchain Environment Troubleshooter")
    
    # Check system prerequisites
    check_and_install_prerequisites()
    
    # Check and install Node.js 16
    check_node_version()
    
    # Install Hardhat locally
    install_hardhat()
    
    # Verify blockchain setup
    verify_blockchain_setup()
    
    print("\n🎉 Blockchain environment is ready!")

if __name__ == "__main__":
    main() 