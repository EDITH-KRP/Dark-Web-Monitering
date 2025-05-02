"""
Configuration module for the Dark Web Monitoring Tool.
Loads settings from .env file and provides them to the application.
"""

import os
import dotenv
from pathlib import Path

# Load environment variables from .env file
dotenv.load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Development mode
DEV_MODE = os.getenv('DARK_WEB_DEV_MODE', '1') == '1'

# API Keys
SHODAN_API_KEY = os.getenv('SHODAN_API_KEY', '')
ABUSEIPDB_API_KEY = os.getenv('ABUSEIPDB_API_KEY', '')
IPINFO_API_KEY = os.getenv('IPINFO_API_KEY', '')
IP2LOCATION_API_KEY = os.getenv('IP2LOCATION_API_KEY', '')

# Tor Configuration
TOR_CONTROL_PORT = int(os.getenv('TOR_CONTROL_PORT', 9051))
TOR_SOCKS_PORT = int(os.getenv('TOR_SOCKS_PORT', 9050))
TOR_BROWSER_CONTROL_PORT = int(os.getenv('TOR_BROWSER_CONTROL_PORT', 9151))
TOR_BROWSER_SOCKS_PORT = int(os.getenv('TOR_BROWSER_SOCKS_PORT', 9150))

# VPN Configuration
VPN_PROVIDER = os.getenv('VPN_PROVIDER', 'OpenVPN')
VPN_CONFIG_FILE = os.getenv('VPN_CONFIG_FILE', 'vpn_config.ovpn')
VPN_CONFIG_PATH = BASE_DIR / 'vpn_configs' / VPN_CONFIG_FILE

# Web Archive Configuration
WEB_ARCHIVE_CACHE_TTL = int(os.getenv('WEB_ARCHIVE_CACHE_TTL', 86400))
WEB_ARCHIVE_CACHE_DIR = BASE_DIR / 'cache' / 'web_archive'

# Database Configuration
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
DB_PATH = BASE_DIR / os.getenv('DB_PATH', 'data/darkweb.db')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = BASE_DIR / os.getenv('LOG_FILE', 'logs/darkweb.log')

# Ensure required directories exist
def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        BASE_DIR / 'vpn_configs',
        BASE_DIR / 'cache',
        BASE_DIR / 'cache' / 'web_archive',
        BASE_DIR / 'data',
        BASE_DIR / 'logs',
        BASE_DIR / 'data_storage',
        BASE_DIR / 'exports'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Create directories when module is imported
ensure_directories()

# Print configuration in development mode
if DEV_MODE:
    print("=== Dark Web Monitoring Tool Configuration ===")
    print(f"Development Mode: {DEV_MODE}")
    print(f"Base Directory: {BASE_DIR}")
    print(f"VPN Config Path: {VPN_CONFIG_PATH}")
    print(f"Web Archive Cache Directory: {WEB_ARCHIVE_CACHE_DIR}")
    print(f"Database Path: {DB_PATH}")
    print(f"Log File: {LOG_FILE}")
    print("==============================================")