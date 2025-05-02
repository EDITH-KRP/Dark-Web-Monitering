#!/usr/bin/env python
"""
Test script to simulate running the Dark Web Monitoring Tool in real mode.
This script checks the configuration and simulates the application behavior.
"""

import os
import sys
import platform
import time
import json
from pathlib import Path

def check_python_packages():
    """Check if required Python packages are installed"""
    print("\n=== Checking Python Packages ===")
    
    required_packages = [
        "Flask",
        "requests",
        "beautifulsoup4",
        "lxml",
        "stem",
        "geoip2",
        "pandas",
        "openpyxl",
        "flask-cors",
        "psutil",
        "pycryptodome",
        "pysocks",
        "cryptography",
        "python-dotenv",
        "waybackpy",
        "maxminddb",
        "maxminddb-geolite2",
        "dnspython",
        "tldextract",
        "ipwhois",
        "pyOpenSSL",
        "shodan"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is not installed")
    
    if missing_packages:
        print(f"\n❌ Missing {len(missing_packages)} required packages:")
        print(f"   {', '.join(missing_packages)}")
        print("   Run: pip install -r backend/requirements.txt")
        return False
    else:
        print("\n✅ All required packages are installed")
        return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\n=== Checking Environment Configuration ===")
    
    env_file = os.path.join(os.path.dirname(__file__), 'backend', '.env')
    if os.path.exists(env_file):
        print(f"✅ Found .env file at: {env_file}")
        
        # Read .env file
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        # Check required variables
        required_vars = [
            "DARK_WEB_DEV_MODE",
            "SHODAN_API_KEY",
            "ABUSEIPDB_API_KEY",
            "IPINFO_API_KEY",
            "IP2LOCATION_API_KEY",
            "TOR_CONTROL_PORT",
            "TOR_SOCKS_PORT",
            "VPN_PROVIDER",
            "VPN_CONFIG_FILE",
            "FILEBASE_BUCKET",
            "FILEBASE_ACCESS_KEY",
            "FILEBASE_SECRET_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if var + "=" not in env_content:
                missing_vars.append(var)
                print(f"❌ {var} is not set in .env file")
            else:
                print(f"✅ {var} is set in .env file")
        
        if missing_vars:
            print(f"\n❌ Missing {len(missing_vars)} required environment variables:")
            print(f"   {', '.join(missing_vars)}")
            return False
        else:
            print("\n✅ All required environment variables are set")
            
            # Check if dev mode is disabled
            if "DARK_WEB_DEV_MODE=0" in env_content:
                print("✅ Development mode is disabled (production mode)")
            else:
                print("❌ Development mode is enabled")
                print("   Set DARK_WEB_DEV_MODE=0 in the .env file for production mode")
                return False
            
            return True
    else:
        print(f"❌ .env file not found at: {env_file}")
        return False

def check_vpn_config():
    """Check if VPN configuration is valid"""
    print("\n=== Checking VPN Configuration ===")
    
    # Get VPN config path from .env file
    env_file = os.path.join(os.path.dirname(__file__), 'backend', '.env')
    vpn_config_file = "vpn_config.ovpn"  # Default
    
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        for line in env_content.splitlines():
            if line.startswith('VPN_CONFIG_FILE='):
                vpn_config_file = line.split('=', 1)[1].strip()
    
    vpn_config_path = os.path.join(os.path.dirname(__file__), 'backend', 'vpn_configs', vpn_config_file)
    
    if os.path.exists(vpn_config_path):
        print(f"✅ Found VPN config file at: {vpn_config_path}")
        
        # Check if the OpenVPN config file contains inline certificates
        with open(vpn_config_path, 'r') as f:
            config_content = f.read()
        
        has_inline_certs = '<ca>' in config_content and '<cert>' in config_content and '<key>' in config_content
        
        if has_inline_certs:
            print("✅ VPN config file contains inline certificates")
            return True
        else:
            # Check for required certificate files
            vpn_config_dir = os.path.dirname(vpn_config_path)
            required_files = ["ca.crt", "client.crt", "client.key"]
            missing_files = [f for f in required_files if not os.path.exists(os.path.join(vpn_config_dir, f))]
            
            if missing_files:
                print(f"❌ Missing required certificate files: {', '.join(missing_files)}")
                print("   Please ensure all required certificate files are in the vpn_configs directory")
                return False
            else:
                print("✅ All required certificate files are present")
                return True
    else:
        print(f"❌ VPN config file not found at: {vpn_config_path}")
        return False

def simulate_real_mode():
    """Simulate running the application in real mode"""
    print("\n=== Simulating Real Mode ===")
    
    # Simulate starting Tor
    print("Starting Tor... [SIMULATED]")
    time.sleep(1)
    print("✅ Tor started successfully")
    
    # Simulate connecting to VPN
    print("\nConnecting to VPN... [SIMULATED]")
    time.sleep(1)
    print("✅ VPN connected successfully")
    
    # Simulate starting backend server
    print("\nStarting backend server... [SIMULATED]")
    time.sleep(1)
    print("✅ Backend server started at http://localhost:5000/")
    
    # Simulate starting frontend server
    print("\nStarting frontend server... [SIMULATED]")
    time.sleep(1)
    print("✅ Frontend server started at http://localhost:8000/")
    
    # Simulate crawling
    print("\nPerforming test crawl... [SIMULATED]")
    time.sleep(2)
    
    # Create sample crawl results
    sample_results = [
        {
            "url": "http://example.onion/marketplace",
            "title": "Dark Market - Buy and Sell",
            "content_snippet": "Welcome to the marketplace. Browse categories.",
            "timestamp": time.time(),
            "risk_score": 85,
            "is_seller": True,
            "location": {
                "country": "Unknown",
                "region": "Unknown"
            }
        },
        {
            "url": "http://example2.onion/forum",
            "title": "Dark Web Forum",
            "content_snippet": "Discussion forum for various topics.",
            "timestamp": time.time() - 3600,
            "risk_score": 65,
            "is_seller": False,
            "location": {
                "country": "Unknown",
                "region": "Unknown"
            }
        }
    ]
    
    # Save sample results
    data_dir = os.path.join(os.path.dirname(__file__), 'backend', 'data_storage')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    data_path = os.path.join(data_dir, 'crawled_data.json')
    with open(data_path, 'w') as f:
        json.dump(sample_results, f, indent=2)
    
    print(f"✅ Test crawl completed with {len(sample_results)} results")
    print(f"✅ Results saved to {data_path}")
    
    return True

def main():
    """Main function to test real mode"""
    print("=== Dark Web Monitoring Tool Real Mode Test ===")
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run checks
    packages_ok = check_python_packages()
    env_ok = check_env_file()
    vpn_ok = check_vpn_config()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Python Packages: {'✅' if packages_ok else '❌'}")
    print(f"Environment Configuration: {'✅' if env_ok else '❌'}")
    print(f"VPN Configuration: {'✅' if vpn_ok else '❌'}")
    
    if packages_ok and env_ok and vpn_ok:
        print("\n✅ All checks passed! The system is properly configured for real mode.")
        
        # Ask if user wants to simulate real mode
        print("\nWould you like to simulate running in real mode? (y/n)")
        choice = input().lower()
        
        if choice == 'y':
            simulate_real_mode()
            print("\n✅ Real mode simulation completed successfully!")
            return 0
        else:
            print("\nReal mode simulation skipped.")
            return 0
    else:
        print("\n❌ Some checks failed. Please fix the issues before running in real mode.")
        return 1

if __name__ == "__main__":
    sys.exit(main())