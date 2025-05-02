import os
import sys
import subprocess
import threading
import webbrowser
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Define paths
BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')

# Define ports
BACKEND_PORT = 5000
FRONTEND_PORT = 8000

def start_backend():
    """Start the Flask backend server"""
    print("Starting backend server...")
    os.chdir(BACKEND_DIR)
    
    # Check if Flask is installed
    try:
        import flask
        print("Flask is installed.")
    except ImportError:
        print("Flask is not installed. Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Start the backend server
    # Use subprocess to run the Flask app in a separate process
    subprocess.Popen([sys.executable, "app.py"])

def start_frontend():
    """Start a simple HTTP server for the frontend"""
    print(f"Starting frontend server on port {FRONTEND_PORT}...")
    os.chdir(FRONTEND_DIR)
    
    # Create a simple HTTP server
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(("", FRONTEND_PORT), handler)
    print(f"Frontend server started at http://localhost:{FRONTEND_PORT}")
    httpd.serve_forever()

def open_browser():
    """Open the browser to the frontend URL after a short delay"""
    time.sleep(2)  # Wait for servers to start
    url = f"http://localhost:{FRONTEND_PORT}"
    print(f"Opening browser to {url}")
    webbrowser.open(url)

if __name__ == "__main__":
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Start frontend in a separate thread
    frontend_thread = threading.Thread(target=start_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()
    
    # Open browser
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Keep the main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        sys.exit(0)