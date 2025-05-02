import requests
import random
import datetime
import time
import json
import os
from urllib.parse import quote, urlparse
from bs4 import BeautifulSoup

# Cache directory for archive data
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache', 'web_archive')

def ensure_cache_dir():
    """Ensure the cache directory exists"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_key(url):
    """Generate a cache key for a URL"""
    # Remove protocol and normalize
    parsed = urlparse(url)
    domain = parsed.netloc
    path = parsed.path
    
    # Create a safe filename
    if not domain:
        # Handle case where URL might not have proper format
        domain = url.replace('://', '').split('/', 1)[0]
    
    # Replace invalid filename characters
    safe_key = f"{domain}{path}".replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    
    return safe_key[:200]  # Limit length for filesystem compatibility

def get_cached_data(url):
    """Get cached archive data for a URL"""
    ensure_cache_dir()
    cache_key = get_cache_key(url)
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    if os.path.exists(cache_file):
        # Check if cache is fresh (less than 1 day old)
        cache_age = time.time() - os.path.getmtime(cache_file)
        if cache_age < 86400:  # 24 hours in seconds
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except:
                # If there's an error reading the cache, ignore it
                pass
    
    return None

def save_to_cache(url, data):
    """Save archive data to cache"""
    ensure_cache_dir()
    cache_key = get_cache_key(url)
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving to cache: {e}")

def fetch_archive_cdx(url):
    """Fetch archive data using the CDX API"""
    print(f"Fetching archive data for {url} using CDX API")
    
    try:
        # Format the URL for the API
        encoded_url = quote(url, safe='')
        
        # Call the Wayback Machine API to get available snapshots
        api_url = f"https://web.archive.org/cdx/search/cdx?url={encoded_url}&output=json&fl=timestamp,original,statuscode,mimetype,digest"
        print(f"Calling API: {api_url}")
        
        response = requests.get(api_url, timeout=30)
        
        if response.status_code != 200:
            print(f"API error: {response.status_code}")
            return None
        
        # Parse the response
        snapshots_data = response.json()
        
        # If there are no snapshots, return not found
        if len(snapshots_data) <= 1:  # First row is column headers
            print("No snapshots found")
            return None
        
        # Process the snapshots (skip the first row which is column headers)
        snapshots = []
        for snapshot in snapshots_data[1:]:
            timestamp, original_url, status_code, mime_type, digest = snapshot
            
            # Format the snapshot URL
            snapshot_url = f"https://web.archive.org/web/{timestamp}/{original_url}"
            
            # Format the timestamp for display
            formatted_date = format_timestamp(timestamp)
            
            snapshots.append({
                'timestamp': timestamp,
                'formatted_date': formatted_date,
                'url': snapshot_url,
                'status': status_code,
                'mime_type': mime_type,
                'digest': digest
            })
        
        # Sort snapshots by timestamp (newest first)
        snapshots.sort(key=lambda x: x['timestamp'], reverse=True)
        
        result = {
            'status': 'found',
            'url': snapshots[0]['url'] if snapshots else None,
            'snapshots': snapshots,
            'total_snapshots': len(snapshots)
        }
        
        # Cache the result
        save_to_cache(url, result)
        
        return result
    
    except Exception as e:
        print(f"Error in CDX API: {e}")
        return None

def fetch_archive_availability(url):
    """Fetch archive availability using the Availability API"""
    print(f"Fetching archive availability for {url}")
    
    try:
        # Format the URL for the API
        encoded_url = quote(url, safe='')
        
        # Call the Wayback Machine Availability API
        api_url = f"https://archive.org/wayback/available?url={encoded_url}"
        print(f"Calling API: {api_url}")
        
        response = requests.get(api_url, timeout=30)
        
        if response.status_code != 200:
            print(f"API error: {response.status_code}")
            return None
        
        # Parse the response
        data = response.json()
        
        # Check if there are archived snapshots
        if 'archived_snapshots' in data and data['archived_snapshots']:
            # The API returns limited data, so we'll enhance it
            snapshots = []
            
            for key, snapshot in data['archived_snapshots'].items():
                timestamp = snapshot.get('timestamp', '')
                
                # Format the timestamp for display
                formatted_date = format_timestamp(timestamp)
                
                snapshots.append({
                    'timestamp': timestamp,
                    'formatted_date': formatted_date,
                    'url': snapshot.get('url', ''),
                    'status': snapshot.get('status', ''),
                    'mime_type': 'text/html',  # Assumed
                    'closest': key == 'closest'
                })
            
            # Sort snapshots by timestamp (newest first)
            snapshots.sort(key=lambda x: x['timestamp'], reverse=True)
            
            result = {
                'status': 'found',
                'url': snapshots[0]['url'] if snapshots else None,
                'snapshots': snapshots,
                'total_snapshots': len(snapshots),
                'note': 'Limited data from availability API'
            }
            
            # Cache the result
            save_to_cache(url, result)
            
            return result
        else:
            print("No archived snapshots found")
            return None
    
    except Exception as e:
        print(f"Error in Availability API: {e}")
        return None

def fetch_archive_wayback(url):
    """Fetch archive data by scraping the Wayback Machine calendar page"""
    print(f"Fetching archive data for {url} by scraping Wayback Machine")
    
    try:
        # Format the URL for the calendar page
        encoded_url = quote(url, safe='')
        calendar_url = f"https://web.archive.org/web/*/{encoded_url}"
        print(f"Fetching calendar: {calendar_url}")
        
        response = requests.get(calendar_url, timeout=30)
        
        if response.status_code != 200:
            print(f"Calendar page error: {response.status_code}")
            return None
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for calendar data
        calendar_data = None
        
        # Try to find the calendar data in the page
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and '__INITIAL_DATA__' in script.string:
                # Extract the JSON data
                data_str = script.string.split('__INITIAL_DATA__ = ', 1)[1].rsplit(';', 1)[0]
                try:
                    calendar_data = json.loads(data_str)
                    break
                except:
                    continue
        
        if not calendar_data:
            print("Could not find calendar data")
            return None
        
        # Extract snapshots from the calendar data
        snapshots = []
        
        if 'captures' in calendar_data and 'results' in calendar_data['captures']:
            for capture in calendar_data['captures']['results']:
                timestamp = capture.get('timestamp', '')
                
                # Format the timestamp for display
                formatted_date = format_timestamp(timestamp)
                
                snapshots.append({
                    'timestamp': timestamp,
                    'formatted_date': formatted_date,
                    'url': f"https://web.archive.org/web/{timestamp}/{url}",
                    'status': str(capture.get('status', '')),
                    'mime_type': capture.get('mime', 'text/html'),
                    'digest': capture.get('digest', '')
                })
        
        if not snapshots:
            print("No snapshots found in calendar data")
            return None
        
        # Sort snapshots by timestamp (newest first)
        snapshots.sort(key=lambda x: x['timestamp'], reverse=True)
        
        result = {
            'status': 'found',
            'url': snapshots[0]['url'] if snapshots else None,
            'snapshots': snapshots,
            'total_snapshots': len(snapshots)
        }
        
        # Cache the result
        save_to_cache(url, result)
        
        return result
    
    except Exception as e:
        print(f"Error scraping Wayback Machine: {e}")
        return None

def format_timestamp(timestamp):
    """Format a Wayback Machine timestamp for display"""
    try:
        # Parse the timestamp (format: YYYYMMDDhhmmss)
        year = int(timestamp[0:4])
        month = int(timestamp[4:6])
        day = int(timestamp[6:8])
        hour = int(timestamp[8:10])
        minute = int(timestamp[10:12])
        second = int(timestamp[12:14]) if len(timestamp) >= 14 else 0
        
        # Create a datetime object
        dt = datetime.datetime(year, month, day, hour, minute, second)
        
        # Format it for display
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp

def generate_fake_archive_data(url):
    """Generate fake archive data for a given URL (fallback)"""
    print(f"Generating fake archive data for {url}")
    
    # Generate between 1-5 random archive snapshots
    num_snapshots = random.randint(1, 5)
    snapshots = []
    
    # Current year and past years
    current_year = datetime.datetime.now().year
    years = list(range(current_year - 5, current_year + 1))
    
    for _ in range(num_snapshots):
        # Generate random date
        year = random.choice(years)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        # Format timestamp like archive.org
        timestamp = f"{year}{month:02d}{day:02d}{hour:02d}{minute:02d}{second:02d}"
        
        # Format the timestamp for display
        formatted_date = f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
        
        # Create snapshot data
        snapshot = {
            "timestamp": timestamp,
            "formatted_date": formatted_date,
            "url": f"https://web.archive.org/web/{timestamp}/{url}",
            "status": "200",
            "mime_type": random.choice(["text/html", "application/pdf"]),
            "digest": f"sha1:{random.getrandbits(160):040x}"
        }
        
        snapshots.append(snapshot)
    
    # Sort snapshots by timestamp (newest first)
    snapshots.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "status": "found",
        "url": snapshots[0]["url"] if snapshots else None,
        "snapshots": snapshots,
        "total_snapshots": len(snapshots),
        "note": "Using simulated data"
    }

def fetch_archive(url):
    """Fetch the archived version of a website using multiple methods"""
    print(f"Fetching archive for {url}")
    
    # Check cache first
    cached_data = get_cached_data(url)
    if cached_data:
        print(f"Using cached data for {url}")
        return cached_data
    
    # Try multiple methods to get archive data
    
    # Method 1: CDX API
    result = fetch_archive_cdx(url)
    if result:
        return result
    
    # Method 2: Availability API
    result = fetch_archive_availability(url)
    if result:
        return result
    
    # Method 3: Scrape Wayback Machine
    result = fetch_archive_wayback(url)
    if result:
        return result
    
    # If all methods fail, check if we're in development mode
    if os.environ.get("DARK_WEB_DEV_MODE") == "1":
        print("Development mode detected, generating fake archive data")
        return generate_fake_archive_data(url)
    
    # If all methods fail and we're not in development mode, return not found
    return {'status': 'not found'}
