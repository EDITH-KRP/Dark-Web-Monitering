#!/usr/bin/env python
"""
Start script for the Dark Web Monitoring System
"""
import os
import sys
import time
import socket
import subprocess
import webbrowser
import platform
import signal
import atexit

def check_tor_running():
    """Check if Tor is running by testing connection to SOCKS port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 9050))
        sock.close()
        return result == 0
    except:
        return False

def start_tor():
    """Start the Tor process"""
    # Get Tor executable path from .env file
    tor_path = None
    try:
        with open(os.path.join('backend', '.env'), 'r') as f:
            for line in f:
                if line.startswith('TOR_EXECUTABLE_PATH='):
                    tor_path = line.split('=', 1)[1].strip().strip('"\'')
                    break
    except:
        pass
    
    if not tor_path or not os.path.exists(tor_path):
        print("Tor executable not found. Please make sure Tor is installed and the path is correct in backend/.env")
        return False
    
    print(f"Starting Tor from {tor_path}...")
    
    # Start Tor in the background
    if platform.system() == "Windows":
        tor_process = subprocess.Popen([tor_path], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE,
                                      creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        tor_process = subprocess.Popen([tor_path], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE)
    
    # Wait for Tor to start
    print("Waiting for Tor to initialize...")
    for _ in range(30):
        if check_tor_running():
            print("Tor started successfully")
            return True
        time.sleep(1)
    
    print("Failed to start Tor within timeout period")
    return False

def start_backend():
    """Start the backend Flask server"""
    print("Starting backend server...")
    
    # Determine the Python executable
    python_exe = sys.executable
    
    # Start the backend server
    backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'app.py')
    
    if platform.system() == "Windows":
        backend_process = subprocess.Popen([python_exe, backend_path], 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE,
                                          creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        backend_process = subprocess.Popen([python_exe, backend_path], 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE)
    
    # Register function to terminate backend on exit
    atexit.register(lambda: backend_process.terminate())
    
    # Wait for backend to start
    print("Waiting for backend to initialize...")
    time.sleep(5)
    
    return backend_process

def open_frontend():
    """Open the frontend in the default web browser"""
    print("Opening frontend...")
    frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend', 'index.html')
    frontend_url = 'file://' + os.path.abspath(frontend_path)
    webbrowser.open(frontend_url)

def main():
    """Main function to start the Dark Web Monitoring System"""
    print("Starting Dark Web Monitoring System...")
    
    # Check if Tor is running
    print("Checking Tor status...")
    if check_tor_running():
        print("Tor is already running")
    else:
        # Start Tor
        if not start_tor():
            print("WARNING: Could not start Tor. Some functionality may be limited.")
    
    # Start the backend
    backend_process = start_backend()
    
    # Open the frontend
    open_frontend()
    
    print("\nDark Web Monitoring System started successfully!")
    print("Press Ctrl+C to stop the system...")
    
    try:
        # Keep the script running until user interrupts
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping the system...")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())