import os
import subprocess

def connect_vpn():
    """Function to connect to a VPN"""
    vpn_config_file = '/path/to/your/vpn/config.ovpn'
    command = f'openvpn --config {vpn_config_file} --daemon'

    try:
        subprocess.run(command, shell=True, check=True)
        print("VPN connected successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error connecting to VPN: {e}")
