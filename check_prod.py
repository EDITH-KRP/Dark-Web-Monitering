#!/usr/bin/env python
"""
Check if the Dark Web Monitoring Tool is properly configured for production mode.
This script verifies that all required components are available and configured.
"""

import os
import sys
import platform
import subprocess
import time
import json
from pathlib import Path

def check_openvpn():
    """Check if OpenVPN is installed and configured"""
    print("\n=== Checking OpenVPN Configuration ===")
    
    # Check if OpenVPN is installed
    openvpn_path = None
    system = platform.system()
    
    # Try to get OpenVPN path from environment variable
    openvpn_path_env = os.environ.get('OPENVPN_PATH')
    if openvpn_path_env and os.path.exists(openvpn_path_env):
        openvpn_path = openvpn_path_env
        print(f"[OK] Found OpenVPN from environment variable: {openvpn_path}")
    else:
        # Try to use the Proton VPN's OpenVPN executable
        proton_openvpn_paths = [
            "C:\\Program Files\\Proton\\VPN\\v3.5.3\\Resources\\openvpn.exe",
            "C:\\Program Files\\Proton\\VPN\\v3.5.2\\Resources\\openvpn.exe"
        ]
        
        for path in proton_openvpn_paths:
            if os.path.exists(path):
                openvpn_path = path
                print(f"[OK] Found OpenVPN at: {openvpn_path}")
                break
    
    if not openvpn_path:
        # Fall back to checking if OpenVPN is in PATH
        if system == "Windows":
            openvpn_check = subprocess.run(["where", "openvpn"], 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE,
                                          text=True)
            if openvpn_check.returncode == 0:
                openvpn_path = "openvpn"
                print(f"[OK] Found OpenVPN in PATH")
        else:  # Linux or macOS
            openvpn_check = subprocess.run(["which", "openvpn"], 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE,
                                          text=True)
            if openvpn_check.returncode == 0:
                openvpn_path = "openvpn"
                print(f"[OK] Found OpenVPN in PATH")
    
    if not openvpn_path:
        print("[ERROR] OpenVPN is not installed or not in PATH")
        print("   Please install OpenVPN or set the OPENVPN_PATH environment variable")
        return False
    
    # Check if VPN config file exists
    config_path = os.path.join(os.path.dirname(__file__), 'backend', 'vpn_configs', 'vpn_config.ovpn')
    if os.path.exists(config_path):
        print(f"[OK] Found VPN config file at: {config_path}")
        
        # Check if the OpenVPN config file contains inline certificates
        with open(config_path, 'r') as f:
            config_content = f.read()
        
        has_inline_certs = '<ca>' in config_content and '<cert>' in config_content and '<key>' in config_content
        
        if has_inline_certs:
            print("[OK] VPN config file contains inline certificates")
        else:
            # Check for required certificate files
            vpn_config_dir = os.path.dirname(config_path)
            required_files = ["ca.crt", "client.crt", "client.key"]
            missing_files = [f for f in required_files if not os.path.exists(os.path.join(vpn_config_dir, f))]
            
            if missing_files:
                print(f"[ERROR] Missing required certificate files: {', '.join(missing_files)}")
                print("   Please ensure all required certificate files are in the vpn_configs directory")
                return False
            else:
                print("[OK] All required certificate files are present")
    else:
        print(f"[ERROR] VPN config file not found at: {config_path}")
        print("   Please ensure you have a valid OpenVPN configuration file")
        return False
    
    return True

def check_tor():
    """Check if Tor is installed and running"""
    print("\n=== Checking Tor Configuration ===")
    
    # Check if Tor is installed
    tor_path = None
    system = platform.system()
    
    if system == "Windows":
        # Check if Tor Browser is installed in common locations
        tor_paths = [
            "C:\\Users\\prajw\\OneDrive\\Desktop\\Tor Browser\\Browser\\TorBrowser\\Tor\\tor.exe",
            os.path.expanduser("~\\Desktop\\Tor Browser\\Browser\\TorBrowser\\Tor\\tor.exe"),
            os.path.expanduser("~\\Downloads\\Tor Browser\\Browser\\TorBrowser\\Tor\\tor.exe"),
            "C:\\Program Files\\Tor Browser\\Browser\\TorBrowser\\Tor\\tor.exe",
            "C:\\Program Files (x86)\\Tor Browser\\Browser\\TorBrowser\\Tor\\tor.exe"
        ]
        
        for path in tor_paths:
            if os.path.exists(path):
                tor_path = path
                print(f"[OK] Found Tor at: {tor_path}")
                break
    else:
        # Check if Tor is installed on Linux/macOS
        tor_check = subprocess.run(["which", "tor"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  text=True)
        if tor_check.returncode == 0:
            tor_path = tor_check.stdout.strip()
            print(f"[OK] Found Tor at: {tor_path}")
    
    if not tor_path:
        print("[ERROR] Tor is not installed or not found in common locations")
        print("   Please install Tor Browser or the Tor service")
        return False
    
    # Check if Tor is running
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(('127.0.0.1', 9050))
        s.close()
        print("[OK] Tor SOCKS proxy is running on port 9050")
        
        # Try to connect to the control port
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect(('127.0.0.1', 9051))
            s.close()
            print("[OK] Tor control port is running on port 9051")
        except:
            print("[WARNING] Tor control port is not running on port 9051")
            print("   Some features like IP rotation may not work")
        
        return True
    except:
        print("[ERROR] Tor SOCKS proxy is not running")
        print("   Please start the Tor service or Tor Browser")
        return False

def check_filebase():
    """Check if Filebase is configured"""
    print("\n=== Checking Filebase Configuration ===")
    
    # Check if Filebase environment variables are set
    env_file = os.path.join(os.path.dirname(__file__), 'backend', '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        filebase_bucket = None
        filebase_access_key = None
        filebase_secret_key = None
        
        for line in env_content.splitlines():
            if line.startswith('FILEBASE_BUCKET='):
                filebase_bucket = line.split('=', 1)[1].strip()
            elif line.startswith('FILEBASE_ACCESS_KEY='):
                filebase_access_key = line.split('=', 1)[1].strip()
            elif line.startswith('FILEBASE_SECRET_KEY='):
                filebase_secret_key = line.split('=', 1)[1].strip()
        
        if filebase_bucket and filebase_access_key and filebase_secret_key:
            print("[OK] Filebase configuration found in .env file")
            
            # Test Filebase connection
            try:
                import boto3
                from botocore.client import Config
                
                # Create an S3 client with Filebase endpoint
                s3_client = boto3.client(
                    's3',
                    endpoint_url="https://s3.filebase.com",
                    aws_access_key_id=filebase_access_key,
                    aws_secret_access_key=filebase_secret_key,
                    config=Config(signature_version='s3v4')
                )
                
                # List objects in the bucket
                response = s3_client.list_objects_v2(
                    Bucket=filebase_bucket,
                    MaxKeys=1
                )
                
                print("[OK] Successfully connected to Filebase")
                return True
            except Exception as e:
                print(f"[ERROR] Error testing Filebase connection: {e}")
                return False
        else:
            print("[ERROR] Filebase configuration not found in .env file")
            print("   Please set FILEBASE_BUCKET, FILEBASE_ACCESS_KEY, and FILEBASE_SECRET_KEY")
            return False
    else:
        print(f"[ERROR] .env file not found at: {env_file}")
        return False

def check_dev_mode():
    """Check if development mode is disabled"""
    print("\n=== Checking Development Mode ===")
    
    env_file = os.path.join(os.path.dirname(__file__), 'backend', '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        for line in env_content.splitlines():
            if line.startswith('DARK_WEB_DEV_MODE='):
                dev_mode = line.split('=', 1)[1].strip()
                if dev_mode == '0':
                    print("[OK] Development mode is disabled (production mode)")
                    return True
                else:
                    print("[ERROR] Development mode is enabled")
                    print("   Set DARK_WEB_DEV_MODE=0 in the .env file for production mode")
                    return False
        
        print("[ERROR] DARK_WEB_DEV_MODE not found in .env file")
        return False
    else:
        print(f"[ERROR] .env file not found at: {env_file}")
        return False

def main():
    """Main function to check production mode configuration"""
    print("=== Dark Web Monitoring Tool Production Mode Check ===")
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all checks
    dev_mode_ok = check_dev_mode()
    openvpn_ok = check_openvpn()
    tor_ok = check_tor()
    filebase_ok = check_filebase()
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Development Mode Disabled: {'[OK]' if dev_mode_ok else '[ERROR]'}")
    print(f"OpenVPN Configuration: {'[OK]' if openvpn_ok else '[ERROR]'}")
    print(f"Tor Configuration: {'[OK]' if tor_ok else '[ERROR]'}")
    print(f"Filebase Configuration: {'[OK]' if filebase_ok else '[ERROR]'}")
    
    if dev_mode_ok and openvpn_ok and tor_ok and filebase_ok:
        print("\n[OK] All checks passed! The system is properly configured for production mode.")
        return 0
    else:
        print("\n[ERROR] Some checks failed. Please fix the issues before running in production mode.")
        return 1

if __name__ == "__main__":
    sys.exit(main())