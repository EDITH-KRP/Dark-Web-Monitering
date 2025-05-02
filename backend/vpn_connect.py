import os
import subprocess
import requests
import json
import time
import random
import platform
import signal
import psutil
from threading import Thread, Lock

# Global variables to track VPN status
vpn_status = {
    "connected": False,
    "ip_address": None,
    "location": None,
    "provider": None,
    "last_checked": None,
    "is_masked": False,
    "process_id": None
}

status_lock = Lock()
vpn_process = None

def connect_vpn():
    """Function to connect to a VPN using OpenVPN"""
    global vpn_process
    
    print("Attempting to connect to VPN...")
    
    try:
        # Check if OpenVPN is installed
        system = platform.system()
        
        # Check if OpenVPN is installed
        openvpn_path = None
        
        # Try to get OpenVPN path from environment variable
        openvpn_path_env = os.environ.get('OPENVPN_PATH')
        if openvpn_path_env and os.path.exists(openvpn_path_env):
            openvpn_path = openvpn_path_env
            print(f"Using OpenVPN from environment variable: {openvpn_path}")
        else:
            # Try to use the Proton VPN's OpenVPN executable
            proton_openvpn_paths = [
                "C:\\Program Files\\Proton\\VPN\\v3.5.3\\Resources\\openvpn.exe",
                "C:\\Program Files\\Proton\\VPN\\v3.5.2\\Resources\\openvpn.exe"
            ]
            
            for path in proton_openvpn_paths:
                if os.path.exists(path):
                    openvpn_path = path
                    print(f"Found OpenVPN at: {openvpn_path}")
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
            else:  # Linux or macOS
                openvpn_check = subprocess.run(["which", "openvpn"], 
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.PIPE,
                                              text=True)
                if openvpn_check.returncode == 0:
                    openvpn_path = "openvpn"
        
        if not openvpn_path:
            print("OpenVPN is not installed or not in PATH. Please install OpenVPN.")
            
            # Check if we're in production mode
            if os.environ.get("DARK_WEB_DEV_MODE") == "0":
                raise Exception("OpenVPN is required in production mode but was not found")
            else:
                print("Falling back to simulated VPN for development")
                return _simulate_vpn_connection()
        
        # Path to OpenVPN config file
        config_path = os.path.join(os.path.dirname(__file__), 'vpn_configs', 'vpn_config.ovpn')
        
        if not os.path.exists(config_path):
            print(f"VPN config file not found at {config_path}")
            print("Please ensure you have a valid OpenVPN configuration file.")
            
            # Check if we're in production mode
            if os.environ.get("DARK_WEB_DEV_MODE") == "0":
                raise Exception("VPN configuration file is required in production mode but was not found")
            else:
                print("Falling back to simulated VPN for development")
                return _simulate_vpn_connection()
        
        # Check if the OpenVPN config file contains inline certificates
        with open(config_path, 'r') as f:
            config_content = f.read()
        
        has_inline_certs = '<ca>' in config_content and '<cert>' in config_content and '<key>' in config_content
        
        if not has_inline_certs:
            # Check for required certificate files
            vpn_config_dir = os.path.dirname(config_path)
            required_files = ["ca.crt", "client.crt", "client.key"]
            missing_files = [f for f in required_files if not os.path.exists(os.path.join(vpn_config_dir, f))]
            
            if missing_files:
                print(f"Missing required certificate files: {', '.join(missing_files)}")
                print("Please ensure all required certificate files are in the vpn_configs directory.")
                
                # Check if we're in production mode
                if os.environ.get("DARK_WEB_DEV_MODE") == "0":
                    raise Exception(f"VPN certificate files {', '.join(missing_files)} are required in production mode but were not found")
                else:
                    print("Falling back to simulated VPN for development")
                    return _simulate_vpn_connection()
        
        # Command to connect to VPN
        if system == "Windows":
            cmd = [openvpn_path, "--config", config_path]
        else:  # Linux or macOS
            cmd = ["sudo", openvpn_path, "--config", config_path]
        
        # Start OpenVPN in a separate process
        print("Starting OpenVPN process...")
        vpn_process = subprocess.Popen(cmd, 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE,
                                      universal_newlines=True)
        
        # Wait for connection to establish (look for "Initialization Sequence Completed")
        connection_established = False
        for i in range(30):  # Wait up to 30 seconds
            if vpn_process.poll() is not None:
                # Process exited
                stdout, stderr = vpn_process.communicate()
                print(f"OpenVPN process exited with code {vpn_process.returncode}")
                print(f"Error: {stderr}")
                break
                
            line = vpn_process.stdout.readline()
            if "Initialization Sequence Completed" in line:
                connection_established = True
                break
            time.sleep(1)
        
        if not connection_established:
            print("Failed to establish VPN connection within timeout period.")
            if vpn_process and vpn_process.poll() is None:
                vpn_process.terminate()
                
            # Check if we're in production mode
            if os.environ.get("DARK_WEB_DEV_MODE") == "0":
                # Try one more time with a longer timeout
                print("In production mode - trying VPN connection again with longer timeout...")
                
                # Start OpenVPN in a separate process
                print("Starting OpenVPN process (second attempt)...")
                vpn_process = subprocess.Popen(cmd, 
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.PIPE,
                                              universal_newlines=True)
                
                # Wait for connection to establish with a longer timeout
                connection_established = False
                for i in range(60):  # Wait up to 60 seconds
                    if vpn_process.poll() is not None:
                        # Process exited
                        stdout, stderr = vpn_process.communicate()
                        print(f"OpenVPN process exited with code {vpn_process.returncode}")
                        print(f"Error: {stderr}")
                        break
                        
                    line = vpn_process.stdout.readline()
                    if "Initialization Sequence Completed" in line:
                        connection_established = True
                        break
                    time.sleep(1)
                
                if not connection_established:
                    raise Exception("Failed to establish VPN connection after multiple attempts in production mode")
            else:
                print("Falling back to simulated VPN for development")
                return _simulate_vpn_connection()
        
        with status_lock:
            vpn_status["connected"] = True
            vpn_status["last_checked"] = time.time()
            vpn_status["provider"] = "OpenVPN"
            vpn_status["process_id"] = vpn_process.pid
        
        # Start background thread to monitor VPN status
        monitor_thread = Thread(target=monitor_vpn_status, daemon=True)
        monitor_thread.start()
        
        print("VPN connected successfully.")
        return check_vpn_status()
    
    except Exception as e:
        print(f"Error connecting to VPN: {e}")
        
        # Check if we're in production mode
        if os.environ.get("DARK_WEB_DEV_MODE") == "0":
            # In production mode, we need to raise the error
            raise Exception(f"Failed to connect to VPN in production mode: {e}")
        else:
            print("Falling back to simulated VPN for development")
            return _simulate_vpn_connection()

def _simulate_vpn_connection():
    """Simulate a VPN connection for development purposes"""
    with status_lock:
        vpn_status["connected"] = True
        vpn_status["last_checked"] = time.time()
        vpn_status["provider"] = "Simulated VPN"
    
    # Start background thread to monitor VPN status
    monitor_thread = Thread(target=monitor_vpn_status, daemon=True)
    monitor_thread.start()
    
    return check_vpn_status()

def disconnect_vpn():
    """Function to disconnect from VPN"""
    global vpn_process
    
    print("Disconnecting from VPN...")
    
    try:
        # First try to terminate the process we started
        if vpn_process and vpn_process.poll() is None:
            print(f"Terminating VPN process with PID {vpn_process.pid}")
            vpn_process.terminate()
            vpn_process.wait(timeout=5)
            
            # If it's still running, force kill
            if vpn_process.poll() is None:
                print("VPN process didn't terminate gracefully, forcing kill...")
                if platform.system() == "Windows":
                    os.kill(vpn_process.pid, signal.SIGTERM)
                else:
                    os.kill(vpn_process.pid, signal.SIGKILL)
        
        # Also check for the process ID stored in status
        process_id = vpn_status.get("process_id")
        if process_id:
            try:
                process = psutil.Process(process_id)
                if process.is_running():
                    print(f"Killing VPN process with PID {process_id}")
                    process.terminate()
                    process.wait(timeout=5)
                    if process.is_running():
                        process.kill()
            except psutil.NoSuchProcess:
                pass
        
        # As a fallback, also try to kill all OpenVPN processes
        system = platform.system()
        if system == "Windows":
            # Kill OpenVPN process on Windows
            subprocess.run(["taskkill", "/F", "/IM", "openvpn.exe"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
        else:
            # Kill OpenVPN process on Linux/macOS
            subprocess.run(["sudo", "killall", "openvpn"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
        
        # Reset VPN status
        with status_lock:
            vpn_status["connected"] = False
            vpn_status["ip_address"] = None
            vpn_status["location"] = None
            vpn_status["provider"] = None
            vpn_status["last_checked"] = time.time()
            vpn_status["is_masked"] = False
            vpn_status["process_id"] = None
        
        # Reset the global process variable
        vpn_process = None
        
        print("VPN disconnected.")
        return check_vpn_status()
    
    except Exception as e:
        print(f"Error disconnecting from VPN: {e}")
        
        # Force status update even if command failed
        with status_lock:
            vpn_status["connected"] = False
            vpn_status["ip_address"] = None
            vpn_status["location"] = None
            vpn_status["provider"] = None
            vpn_status["last_checked"] = time.time()
            vpn_status["is_masked"] = False
            vpn_status["process_id"] = None
        
        # Reset the global process variable
        vpn_process = None
        
        return check_vpn_status()

def check_vpn_status():
    """Check if VPN is connected and get current IP details"""
    with status_lock:
        # If we've checked recently, return cached status
        if vpn_status["last_checked"] and time.time() - vpn_status["last_checked"] < 30:
            return vpn_status.copy()
    
    # Check if the VPN process is still running
    process_id = vpn_status.get("process_id")
    if process_id:
        try:
            process = psutil.Process(process_id)
            if not process.is_running():
                print(f"VPN process with PID {process_id} is no longer running")
                with status_lock:
                    vpn_status["connected"] = False
        except psutil.NoSuchProcess:
            print(f"VPN process with PID {process_id} no longer exists")
            with status_lock:
                vpn_status["connected"] = False
    
    # Try multiple IP information services for redundancy
    ip_services = [
        'https://ipinfo.io/json',
        'https://api.ipify.org?format=json',
        'https://ipapi.co/json/',
        'https://api.myip.com'
    ]
    
    for service_url in ip_services:
        try:
            print(f"Checking IP information using {service_url}")
            response = requests.get(service_url, timeout=5)
            
            if response.status_code == 200:
                ip_data = response.json()
                
                # Extract IP address (different services use different field names)
                ip_address = ip_data.get('ip') or ip_data.get('query') or ip_data.get('ipAddress')
                
                if not ip_address:
                    continue  # Try next service if IP not found
                
                # Extract location information
                city = ip_data.get('city', '')
                country = ip_data.get('country', '') or ip_data.get('countryCode', '')
                region = ip_data.get('region', '') or ip_data.get('regionName', '')
                
                # Extract organization/ISP information
                org = ip_data.get('org', '') or ip_data.get('isp', '') or ip_data.get('as', '')
                
                # Check if this looks like a VPN IP
                # This is a more comprehensive check
                is_vpn_ip = False
                
                # List of known VPN providers and hosting companies
                vpn_providers = [
                    "nordvpn", "expressvpn", "protonvpn", "mullvad", "cyberghost", 
                    "private internet access", "surfshark", "ipvanish", "torguard",
                    "digital ocean", "amazon", "aws", "linode", "ovh", "vultr", 
                    "hetzner", "microsoft azure", "google cloud", "rackspace",
                    "hosting", "vpn", "proxy", "anonymous", "data center"
                ]
                
                # Check org field for VPN providers
                if org:
                    org_lower = org.lower()
                    is_vpn_ip = any(provider in org_lower for provider in vpn_providers)
                
                # Additional checks for VPN/proxy
                # Check if the IP is in a known datacenter range
                datacenter_ranges = [
                    "192.168.", "10.", "172.16.", "172.17.", "172.18.", "172.19.", "172.20.",
                    "172.21.", "172.22.", "172.23.", "172.24.", "172.25.", "172.26.", "172.27.",
                    "172.28.", "172.29.", "172.30.", "172.31."
                ]
                
                is_datacenter = any(ip_address.startswith(prefix) for prefix in datacenter_ranges)
                
                # Update VPN status
                with status_lock:
                    vpn_status["ip_address"] = ip_address
                    vpn_status["location"] = f"{city}, {country}" if city else country
                    vpn_status["provider"] = org or "Unknown"
                    vpn_status["last_checked"] = time.time()
                    vpn_status["is_masked"] = is_vpn_ip or is_datacenter
                    
                    # If we're supposed to be connected to a VPN but the IP doesn't look like a VPN IP,
                    # update the connected status
                    if vpn_status["connected"] and not (is_vpn_ip or is_datacenter):
                        print("Warning: VPN connection claimed but IP doesn't appear to be masked")
                        # Don't automatically disconnect - it might be a stealthy VPN
                
                # Successfully got IP info, no need to try other services
                break
                
        except Exception as e:
            print(f"Error checking IP with {service_url}: {e}")
            # Continue to the next service
    
    # If we couldn't get IP info from any service
    if not vpn_status["ip_address"]:
        print("Failed to get IP information from any service")
        
        # Check if we're in development mode
        if os.environ.get("DARK_WEB_DEV_MODE") == "1":
            print("Development mode detected, simulating VPN status")
            _simulate_vpn_status()
        else:
            # In production, assume the worst
            with status_lock:
                vpn_status["connected"] = False
                vpn_status["last_checked"] = time.time()
    
    return vpn_status.copy()

def _simulate_vpn_status():
    """Simulate VPN status for development purposes"""
    if random.random() > 0.2:  # 80% chance VPN is working correctly
        with status_lock:
            vpn_status["connected"] = True
            vpn_status["ip_address"] = f"198.51.{random.randint(1, 254)}.{random.randint(1, 254)}"
            vpn_status["location"] = random.choice(["Netherlands", "Switzerland", "Sweden", "Panama", "Romania"])
            vpn_status["provider"] = random.choice(["NordVPN", "ExpressVPN", "ProtonVPN", "Mullvad", "CyberGhost"])
            vpn_status["last_checked"] = time.time()
            vpn_status["is_masked"] = True
    else:
        # Simulate VPN failure
        with status_lock:
            vpn_status["connected"] = False
            vpn_status["ip_address"] = f"203.0.{random.randint(1, 254)}.{random.randint(1, 254)}"
            vpn_status["location"] = "Your Real Location"
            vpn_status["provider"] = "Your ISP"
            vpn_status["last_checked"] = time.time()
            vpn_status["is_masked"] = False

def monitor_vpn_status():
    """Background thread to periodically check VPN status"""
    while True:
        try:
            # Check VPN status
            status = check_vpn_status()
            
            # If VPN is supposed to be connected but the process is not running, try to reconnect
            if status["connected"] and status.get("process_id"):
                try:
                    process = psutil.Process(status["process_id"])
                    if not process.is_running():
                        print("VPN process died unexpectedly. Attempting to reconnect...")
                        connect_vpn()
                except psutil.NoSuchProcess:
                    print("VPN process no longer exists. Attempting to reconnect...")
                    connect_vpn()
            
            # Log status periodically
            print(f"VPN Status: Connected={status['connected']}, IP={status['ip_address']}, Location={status['location']}")
            
        except Exception as e:
            print(f"Error in VPN monitor thread: {e}")
        
        # Sleep for a while before checking again
        time.sleep(60)  # Check every minute
