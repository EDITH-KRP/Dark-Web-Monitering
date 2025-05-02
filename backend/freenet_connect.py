import requests
import logging
import time
import re
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Freenet uses a local web interface, typically on port 8888
FREENET_BASE_URL = "http://127.0.0.1:8888"

def is_freenet_running():
    """Check if Freenet is running by accessing the web interface"""
    try:
        response = requests.get(f"{FREENET_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def fetch_freenet_key(freenet_key):
    """Fetch content from a Freenet key
    
    Freenet keys look like:
    - CHK@... (Content Hash Keys)
    - SSK@... (Signed Subspace Keys)
    - USK@... (Updateable Subspace Keys)
    """
    if not is_freenet_running():
        return {"error": "Freenet is not running"}
    
    try:
        # Encode the key for URL
        encoded_key = quote(freenet_key)
        url = f"{FREENET_BASE_URL}/freenet:{encoded_key}"
        
        # Freenet can be slow, so we use a longer timeout
        response = requests.get(url, timeout=120)
        
        if response.status_code == 200:
            return {
                "key": freenet_key,
                "content": response.text,
                "status": "success"
            }
        else:
            return {
                "key": freenet_key,
                "status": "error",
                "error": f"Failed to retrieve key, Status code: {response.status_code}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "key": freenet_key,
            "status": "error",
            "error": f"Error accessing Freenet: {e}"
        }

def search_freenet(keywords):
    """Search Freenet for content related to keywords
    
    This uses the Freenet web interface to search for content.
    Note: Freenet's search capabilities are limited compared to the regular web.
    """
    if not is_freenet_running():
        return {"error": "Freenet is not running"}
    
    try:
        # Format keywords for search
        search_terms = "+".join(keywords.split())
        url = f"{FREENET_BASE_URL}/plugins/plugins.Librarian/search?search={search_terms}"
        
        response = requests.get(url, timeout=120)
        
        if response.status_code == 200:
            # In a real implementation, you would parse the HTML to extract search results
            # For now, we'll return the raw content
            return {
                "keywords": keywords,
                "raw_content": response.text,
                "status": "success"
            }
        else:
            return {
                "keywords": keywords,
                "status": "error",
                "error": f"Search failed, Status code: {response.status_code}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "keywords": keywords,
            "status": "error",
            "error": f"Error searching Freenet: {e}"
        }

def upload_to_freenet(content, mime_type="text/html"):
    """Upload content to Freenet and get a CHK key
    
    This is a simplified implementation. In a real app, you would use
    the Freenet Client Protocol (FCP) for more reliable uploads.
    """
    if not is_freenet_running():
        return {"error": "Freenet is not running"}
    
    try:
        # Use the KSK insertion form as a simple way to insert content
        url = f"{FREENET_BASE_URL}/insertfile.html"
        
        # Generate a random key name
        import random
        import string
        key_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        files = {'content': ('content.html', content, mime_type)}
        data = {
            'key': f"KSK@{key_name}",
            'insert': 'Insert'
        }
        
        response = requests.post(url, data=data, files=files, timeout=300)
        
        if response.status_code == 200:
            # Try to extract the CHK from the response
            chk_match = re.search(r'(CHK@[A-Za-z0-9~-]+,[A-Za-z0-9~-]+,[A-Za-z0-9~-]+)', response.text)
            if chk_match:
                return {
                    "key": chk_match.group(1),
                    "status": "success"
                }
            else:
                return {
                    "status": "partial_success",
                    "message": "Content uploaded but couldn't extract CHK key"
                }
        else:
            return {
                "status": "error",
                "error": f"Upload failed, Status code: {response.status_code}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": f"Error uploading to Freenet: {e}"
        }