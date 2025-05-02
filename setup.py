#!/usr/bin/env python3
"""
Setup script for the Dark Web Monitoring Tool.
Installs all required dependencies and sets up the environment.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_header(message):
    """Print a header message"""
    print("\n" + "=" * 80)
    print(f" {message}")
    print("=" * 80)

def print_step(message):
    """Print a step message"""
    print(f"\n>> {message}")

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    print_step("Checking Python version")
    
    major, minor, _ = platform.python_version_tuple()
    print(f"Python version: {platform.python_version()}")
    
    if int(major) < 3 or (int(major) == 3 and int(minor) < 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    
    print("Python version is compatible")

def check_pip():
    """Check if pip is installed"""
    print_step("Checking pip installation")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("pip is installed")
    except subprocess.CalledProcessError:
        print("Error: pip is not installed")
        print("Please install pip and try again")
        sys.exit(1)

def install_dependencies():
    """Install Python dependencies"""
    print_step("Installing Python dependencies")
    
    requirements_file = Path("backend/requirements.txt")
    
    if not requirements_file.exists():
        print(f"Error: {requirements_file} not found")
        sys.exit(1)
    
    result = run_command(
        [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
        cwd=str(Path.cwd())
    )
    
    if result is None:
        print("Error installing dependencies")
        sys.exit(1)
    
    print("Dependencies installed successfully")

def check_tor():
    """Check if Tor is installed"""
    print_step("Checking Tor installation")
    
    system = platform.system()
    
    if system == "Windows":
        # Check for Tor Browser on Windows
        tor_paths = [
            os.path.expanduser("~\\Desktop\\Tor Browser\\Browser\\TorBrowser\\Tor\\tor.exe"),
            os.path.expanduser("~\\Downloads\\Tor Browser\\Browser\\TorBrowser\\Tor\\tor.exe"),
            "C:\\Program Files\\Tor Browser\\Browser\\TorBrowser\\Tor\\tor.exe",
            "C:\\Program Files (x86)\\Tor Browser\\Browser\\TorBrowser\\Tor\\tor.exe"
        ]
        
        tor_found = any(os.path.exists(path) for path in tor_paths)
        
        if tor_found:
            print("Tor Browser found")
        else:
            print("Warning: Tor Browser not found")
            print("Please install Tor Browser from https://www.torproject.org/download/")
            print("The tool will use simulation mode for Tor-related features")
    
    elif system == "Linux":
        # Check for Tor on Linux
        try:
            result = subprocess.run(
                ["which", "tor"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("Tor found at:", result.stdout.strip())
        except subprocess.CalledProcessError:
            print("Warning: Tor not found")
            print("Please install Tor using your package manager")
            print("For example: sudo apt install tor")
            print("The tool will use simulation mode for Tor-related features")
    
    elif system == "Darwin":  # macOS
        # Check for Tor on macOS
        try:
            result = subprocess.run(
                ["which", "tor"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("Tor found at:", result.stdout.strip())
        except subprocess.CalledProcessError:
            print("Warning: Tor not found")
            print("Please install Tor using Homebrew: brew install tor")
            print("The tool will use simulation mode for Tor-related features")

def create_directories():
    """Create required directories"""
    print_step("Creating required directories")
    
    directories = [
        "backend/vpn_configs",
        "backend/cache",
        "backend/cache/web_archive",
        "backend/data",
        "backend/logs",
        "backend/data_storage",
        "backend/exports"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"Creating directory: {directory}")
            dir_path.mkdir(parents=True, exist_ok=True)
        else:
            print(f"Directory already exists: {directory}")

def setup_env_file():
    """Set up the .env file"""
    print_step("Setting up .env file")
    
    env_file = Path("backend/.env")
    env_example = Path("backend/.env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print(f"Copying {env_example} to {env_file}")
            shutil.copy(env_example, env_file)
        else:
            print("Creating default .env file")
            with open(env_file, "w") as f:
                f.write("""# Dark Web Monitoring Tool Configuration

# Development mode (set to 1 for development, 0 for production)
DARK_WEB_DEV_MODE=1

# API Keys (replace with your actual API keys)
SHODAN_API_KEY=your_shodan_api_key
ABUSEIPDB_API_KEY=your_abuseipdb_api_key
IPINFO_API_KEY=your_ipinfo_api_key
IP2LOCATION_API_KEY=your_ip2location_api_key

# Tor Configuration
TOR_CONTROL_PORT=9051
TOR_SOCKS_PORT=9050
TOR_BROWSER_CONTROL_PORT=9151
TOR_BROWSER_SOCKS_PORT=9150

# VPN Configuration
VPN_PROVIDER=OpenVPN
VPN_CONFIG_FILE=vpn_config.ovpn

# Web Archive Configuration
WEB_ARCHIVE_CACHE_TTL=86400  # 24 hours in seconds

# Database Configuration (for future use)
DB_TYPE=sqlite
DB_PATH=data/darkweb.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/darkweb.log
""")
        print(".env file created")
    else:
        print(".env file already exists")

def main():
    """Main setup function"""
    print_header("Dark Web Monitoring Tool Setup")
    
    # Check Python version
    check_python_version()
    
    # Check pip
    check_pip()
    
    # Install dependencies
    install_dependencies()
    
    # Check Tor
    check_tor()
    
    # Create directories
    create_directories()
    
    # Set up .env file
    setup_env_file()
    
    print_header("Setup Complete")
    print("\nYou can now run the Dark Web Monitoring Tool:")
    print("1. Start the backend: python backend/app.py")
    print("2. Open the frontend: open frontend/index.html in your browser")
    print("\nNote: Some features may require additional configuration in the .env file.")

if __name__ == "__main__":
    main()