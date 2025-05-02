import requests
import logging
import subprocess
import os
import platform
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_running_in_tails():
    """Check if the script is running in a TAILS environment"""
    try:
        # Check for TAILS-specific files or environment variables
        if os.path.exists('/etc/amnesia/version'):
            with open('/etc/amnesia/version', 'r') as f:
                tails_version = f.read().strip()
                logger.info(f"Running in TAILS environment version {tails_version}")
                return True
        
        # Alternative check: look for TAILS in /etc/os-release
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                content = f.read()
                if 'TAILS' in content:
                    logger.info("Running in TAILS environment")
                    return True
        
        logger.info("Not running in TAILS environment")
        return False
    except Exception as e:
        logger.error(f"Error checking for TAILS environment: {e}")
        return False

def get_tails_tor_session():
    """Get a Tor session configured for TAILS
    
    In TAILS, all traffic is automatically routed through Tor,
    so we don't need to configure a proxy.
    """
    if not is_running_in_tails():
        logger.warning("Not running in TAILS. Using explicit Tor proxy configuration.")
        # Fall back to regular Tor configuration
        session = requests.Session()
        session.proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        return session
    
    # In TAILS, we can use a regular session as all traffic goes through Tor
    logger.info("Using TAILS built-in Tor routing")
    return requests.Session()

def check_tails_networking():
    """Check if TAILS networking is properly configured"""
    if not is_running_in_tails():
        return {"status": "error", "message": "Not running in TAILS environment"}
    
    try:
        # Try to connect to the Tor check page
        session = get_tails_tor_session()
        response = session.get('https://check.torproject.org/', timeout=30)
        
        if 'Congratulations' in response.text:
            return {
                "status": "success",
                "message": "TAILS networking is properly configured and using Tor"
            }
        else:
            return {
                "status": "warning",
                "message": "TAILS is connected but Tor verification failed"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"TAILS networking error: {e}"
        }

def browse_with_tails(url):
    """Browse a URL using TAILS Tor Browser"""
    if not is_running_in_tails():
        return {"status": "error", "message": "Not running in TAILS environment"}
    
    try:
        # In TAILS, we can use the torbrowser-launcher command
        subprocess.Popen(['torbrowser-launcher', url])
        return {
            "status": "success",
            "message": f"Opened {url} in TAILS Tor Browser"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error opening TAILS Tor Browser: {e}"
        }

def fetch_url_with_tails(url):
    """Fetch a URL using TAILS Tor routing"""
    session = get_tails_tor_session()
    
    try:
        response = session.get(url, timeout=60)
        if response.status_code == 200:
            return {
                "url": url,
                "content": response.text,
                "status": "success"
            }
        else:
            return {
                "url": url,
                "status": "error",
                "error": f"Failed to retrieve {url}, Status code: {response.status_code}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "url": url,
            "status": "error",
            "error": f"Error accessing {url}: {e}"
        }