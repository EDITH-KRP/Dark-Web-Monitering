import os 
import subprocess 
import time 
 
print("Testing OpenVPN connection...") 
 
# Get OpenVPN path from .env file or use default 
openvpn_path = "C:\Program Files\Proton\VPN\v3.5.3\Resources\openvpn.exe" 
config_path = os.path.join(os.path.dirname(__file__), 'vpn_configs', 'vpn_config.ovpn') 
 
print(f"OpenVPN path: {openvpn_path}") 
print(f"Config path: {config_path}") 
 
# Command to connect to VPN 
cmd = [openvpn_path, "--config", config_path] 
 
try: 
    # Start OpenVPN in a separate process 
    print("Starting OpenVPN process...") 
    vpn_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True) 
 
    # Wait for connection to establish (look for "Initialization Sequence Completed") 
    print("Waiting for connection to establish...") 
    connection_established = False 
    for i in range(30):  # Wait up to 30 seconds 
        if vpn_process.poll() is not None: 
            # Process exited 
            stdout, stderr = vpn_process.communicate() 
            print(f"OpenVPN process exited with code {vpn_process.returncode}") 
            print(f"Output: {stdout}") 
            print(f"Error: {stderr}") 
            break 
 
        line = vpn_process.stdout.readline() 
        print(f"OpenVPN output: {line.strip()}") 
        if "Initialization Sequence Completed" in line: 
            connection_established = True 
            print("VPN connection established successfully!") 
            break 
        time.sleep(1) 
 
    if not connection_established: 
        print("Failed to establish VPN connection within timeout period.") 
 
    # Clean up 
    if vpn_process and vpn_process.poll() is None: 
        print("Terminating VPN process...") 
        vpn_process.terminate() 
 
except Exception as e: 
    print(f"Error testing VPN connection: {e}") 
 
input("Press Enter to exit...") 
