import requests
from stem import Signal
from stem.control import Controller
from bs4 import BeautifulSoup
import re
import json
import os
import time
import datetime
import hashlib
import random
import logging
import queue
import threading
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
import socks
import socket

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('tor_crawler')

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', '.env'))

# Import local modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dark_web_scripts.dark_web_filters import calculate_risk_score, categorize_site
from dark_web_scripts.ip_reveal import reveal_ip_and_geo
from dark_web_scripts.seller_tracking import identify_marketplace, extract_seller_id

# Constants
MAX_PAGES_PER_SITE = 50
MAX_DEPTH = 3
CRAWL_DELAY = 2  # seconds between requests to the same domain
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0'
]

# Seed URLs for crawling (known .onion directories)
SEED_URLS = [
    'http://darkfailllnkf4vf.onion',  # Dark.fail
    'http://jaz45aabn5vkemy4jkg4mi4syheisqn2wn2n4fsuitpccdackjwxplad.onion',  # Recon
    'http://zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otjiycgwqbym2qad.onion',  # The Hidden Wiki
    'http://s4k4ceiapwwgcm3mkb6e4diqecpo7kvdnfr5gg7sph7jjppqkvwwqtyd.onion',  # Torch
    'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion',  # Ahmia
]

# Keywords to look for in content
ILLEGAL_KEYWORDS = [
    "drugs", "cocaine", "heroin", "fentanyl", "mdma", "ecstasy", "meth", "amphetamine", 
    "lsd", "cannabis", "marijuana", "weed", "ketamine", "opioids", "steroids", "pills",
    "weapons", "guns", "firearms", "pistol", "rifle", "ammunition", "ammo", "explosives",
    "grenades", "knives", "tactical", "silencer", "suppressor", "armor", "bulletproof",
    "hacking", "malware", "ransomware", "spyware", "botnet", "ddos", "phishing", "exploit",
    "vulnerability", "zero-day", "rootkit", "keylogger", "cracking", "breach", "backdoor",
    "counterfeit", "fake", "forged", "documents", "passports", "id cards", "driver license",
    "credit cards", "currency", "money", "bills", "banknotes", "hologram", "clone",
    "carding", "dumps", "cvv", "fullz", "bank drops", "money laundering", "bitcoin tumbler",
    "crypto mixer", "paypal accounts", "wire transfer", "western union", "bank login",
    "hitman", "murder", "assassination", "kidnapping", "torture", "human trafficking",
    "organ trafficking", "smuggling", "bribery", "extortion", "blackmail", "fraud",
    "stolen data", "leaked database", "hacked accounts", "personal information", "doxing",
    "social security", "medical records", "financial data", "corporate secrets", "credentials"
]

def connect_to_tor():
    """Create a session using the Tor network"""
    try:
        # Configure socket to use Tor
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket
        
        # Create session
        session = requests.Session()
        session.proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        
        # Test connection
        try:
            response = session.get('https://check.torproject.org/', timeout=15)
            if 'Congratulations. This browser is configured to use Tor' in response.text:
                logger.info("Successfully connected to Tor network")
            else:
                logger.warning("Connected to Tor but verification failed")
        except Exception as e:
            logger.warning(f"Could not verify Tor connection: {e}")
        
        return session
    except Exception as e:
        logger.error(f"Error connecting to Tor: {e}")
        return None

def new_tor_circuit():
    """Create a new Tor circuit to get a new IP address"""
    try:
        with Controller.from_port(port=9051) as controller:
            # Try to authenticate with no password
            try:
                controller.authenticate()
            except:
                # Try with cookie authentication
                controller.authenticate(cookie_auth=True)
            
            # Signal for new identity
            controller.signal(Signal.NEWNYM)
            logger.info("New Tor circuit created")
            
            # Wait for the circuit to be established
            time.sleep(5)
            return True
    except Exception as e:
        logger.error(f"Error creating new Tor circuit: {e}")
        
        # Try alternative method for Tor Browser
        try:
            with Controller.from_port(port=9151) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                logger.info("New Tor circuit created using Tor Browser control port")
                time.sleep(5)
                return True
        except Exception as e2:
            logger.error(f"Error creating new Tor circuit with alternative method: {e2}")
            return False

def is_onion_url(url):
    """Check if a URL is a valid .onion URL"""
    try:
        # Extract domain from URL
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Check if it's an onion domain
        if domain.endswith('.onion'):
            # Validate the onion address format (v2 or v3)
            onion_part = domain.split('.')[0]
            # v3 onion addresses are 56 characters, v2 are 16
            if len(onion_part) in [16, 56] and all(c in 'abcdefghijklmnopqrstuvwxyz234567' for c in onion_part):
                return True
        
        # Check if onion is in the path (for redirect URLs)
        if '.onion' in url.lower():
            return True
            
        return False
    except Exception as e:
        logger.warning(f"Error checking onion URL {url}: {e}")
        return False

def normalize_url(url):
    """Normalize a URL by removing fragments and trailing slashes"""
    try:
        # Ensure URL has a scheme
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        parsed = urlparse(url)
        
        # Validate the URL has a host
        if not parsed.netloc:
            logger.warning(f"Invalid URL with no host: {url}")
            return url  # Return original to avoid breaking the flow
        
        # Construct normalized URL
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Add query parameters if present
        if parsed.query:
            normalized += f"?{parsed.query}"
            
        # Remove trailing slash
        if normalized.endswith('/'):
            normalized = normalized[:-1]
            
        return normalized
    except Exception as e:
        logger.warning(f"Error normalizing URL {url}: {e}")
        return url  # Return original to avoid breaking the flow

def extract_links(html, base_url):
    """Extract links from HTML content"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        # Ensure base_url has a valid scheme and host
        parsed_base = urlparse(base_url)
        if not parsed_base.netloc:
            logger.warning(f"Invalid base URL: {base_url}")
            return []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Skip empty links, javascript, and mailto
            if not href or href.startswith(('javascript:', 'mailto:', '#')):
                continue
            
            try:
                # Handle redirect URLs that might contain onion addresses
                if 'redirect' in href and 'redirect_url=' in href:
                    # Extract the redirect_url parameter
                    redirect_parts = href.split('redirect_url=')
                    if len(redirect_parts) > 1:
                        redirect_url = redirect_parts[1].split('&')[0]  # Get the URL part
                        # If it's an onion URL, use it directly
                        if '.onion' in redirect_url:
                            if not redirect_url.startswith(('http://', 'https://')):
                                redirect_url = 'http://' + redirect_url
                            links.append(redirect_url)
                            continue
                
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, href)
                
                # Validate the URL
                parsed = urlparse(absolute_url)
                if not parsed.netloc:  # Missing host
                    logger.warning(f"Skipping URL with missing host: {absolute_url}")
                    continue
                
                # Only include .onion URLs
                if is_onion_url(absolute_url):
                    links.append(absolute_url)
            except Exception as e:
                logger.warning(f"Error processing link {href}: {e}")
                continue
        
        return links
    except Exception as e:
        logger.error(f"Error extracting links from {base_url}: {e}")
        return []

def extract_content(html, url):
    """Extract relevant content from HTML"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get the title
        title = soup.title.string if soup.title else ""
        
        # Get meta description
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag and "content" in meta_tag.attrs:
            meta_desc = meta_tag["content"]
        
        # Get main content (prioritize main content areas)
        content_areas = soup.select("main, article, .content, #content, .main, #main")
        if content_areas:
            # Use the largest content area
            main_content = max(content_areas, key=lambda x: len(x.get_text()))
            content = main_content.get_text(separator=' ', strip=True)
        else:
            # Fall back to body text
            content = soup.get_text(separator=' ', strip=True)
        
        # Clean up content (remove excessive whitespace)
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Limit content length
        if len(content) > 10000:
            content = content[:10000] + "..."
        
        return {
            "title": title,
            "description": meta_desc,
            "content": content,
            "html": html  # Keep the original HTML for further analysis
        }
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {e}")
        return {
            "title": "",
            "description": "",
            "content": "",
            "html": html
        }

def check_for_keywords(text, keywords=None):
    """Check if text contains any of the specified keywords"""
    if not keywords:
        keywords = ILLEGAL_KEYWORDS
    
    text = text.lower()
    found_keywords = []
    
    for keyword in keywords:
        if keyword.lower() in text:
            found_keywords.append(keyword)
    
    return found_keywords

def scrape_onion_site(url, session=None, depth=0, visited=None, domain_last_visit=None, keywords=None):
    """Scrape a single .onion site and return its content"""
    if not session:
        session = connect_to_tor()
        if not session:
            return {"error": "Could not connect to Tor"}
    
    if visited is None:
        visited = set()
    
    if domain_last_visit is None:
        domain_last_visit = {}
    
    if keywords is None:
        keywords = ILLEGAL_KEYWORDS
    
    # Normalize URL
    url = normalize_url(url)
    
    # Skip if already visited
    if url in visited:
        return None
    
    # Add to visited set
    visited.add(url)
    
    # Extract domain for rate limiting
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    # Respect crawl delay
    current_time = time.time()
    if domain in domain_last_visit:
        time_since_last_visit = current_time - domain_last_visit[domain]
        if time_since_last_visit < CRAWL_DELAY:
            time.sleep(CRAWL_DELAY - time_since_last_visit)
    
    # Update last visit time
    domain_last_visit[domain] = time.time()
    
    # Random user agent
    headers = {
        'User-Agent': random.choice(USER_AGENTS)
    }
    
    try:
        logger.info(f"Scraping {url}")
        response = session.get(url, headers=headers, timeout=30)
        
        # Update last visit time after request
        domain_last_visit[domain] = time.time()
        
        if response.status_code != 200:
            logger.warning(f"Failed to retrieve {url}, Status code: {response.status_code}")
            return {
                "url": url,
                "error": f"HTTP {response.status_code}",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        # Extract content
        content_data = extract_content(response.text, url)
        
        # Check for keywords
        full_text = f"{content_data['title']} {content_data['description']} {content_data['content']}"
        found_keywords = check_for_keywords(full_text, keywords)
        
        # Calculate risk score
        risk_data = calculate_risk_score(content_data['content'], content_data['title'])
        
        # Determine if it's a marketplace and if it's a seller profile
        marketplace = identify_marketplace(url)
        is_seller = False
        seller_id = None
        
        if marketplace:
            seller_id = extract_seller_id(url, marketplace)
            if seller_id:
                is_seller = True
        
        # Create result object
        result = {
            "url": url,
            "title": content_data['title'],
            "description": content_data['description'],
            "content_sample": content_data['content'][:500] + "..." if len(content_data['content']) > 500 else content_data['content'],
            "found_keywords": found_keywords,
            "risk_score": risk_data["score"],
            "risk_categories": risk_data["categories"],
            "timestamp": datetime.datetime.now().isoformat(),
            "marketplace": marketplace,
            "is_seller": is_seller,
            "seller_id": seller_id,
            "category": categorize_site({
                "title": content_data['title'],
                "description": content_data['description'],
                "content": content_data['content']
            })
        }
        
        # Save the full content to disk
        save_crawled_content(url, content_data, result)
        
        # Extract links for further crawling if not at max depth
        links = []
        if depth < MAX_DEPTH:
            links = extract_links(response.text, url)
            result["links"] = links
        
        return result
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error scraping {url}: {e}")
        return {
            "url": url,
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Unexpected error scraping {url}: {e}")
        return {
            "url": url,
            "error": f"Unexpected error: {str(e)}",
            "timestamp": datetime.datetime.now().isoformat()
        }

def save_crawled_content(url, content_data, metadata):
    """Save crawled content to disk"""
    try:
        # Create directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'data', 'crawled')
        os.makedirs(data_dir, exist_ok=True)
        
        # Create a unique filename based on URL
        url_hash = hashlib.md5(url.encode()).hexdigest()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{url_hash}_{timestamp}.json"
        
        # Combine content and metadata
        data = {
            "url": url,
            "timestamp": datetime.datetime.now().isoformat(),
            "title": content_data["title"],
            "description": content_data["description"],
            "content": content_data["content"],
            "metadata": metadata
        }
        
        # Save to file
        file_path = os.path.join(data_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved content from {url} to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving content from {url}: {e}")
        return False

def crawl_dark_web(start_urls=None, max_pages=100, keywords=None, enable_ip_detection=True):
    """Crawl the Dark Web starting from seed URLs"""
    if not start_urls:
        start_urls = SEED_URLS
    
    if keywords is None:
        keywords = ILLEGAL_KEYWORDS
    
    # Initialize Tor session
    session = connect_to_tor()
    if not session:
        return {"error": "Could not connect to Tor"}
    
    # Initialize crawl state
    visited = set()
    domain_last_visit = {}
    results = []
    to_visit = queue.Queue()
    
    # Add start URLs to queue
    for url in start_urls:
        to_visit.put((url, 0))  # (url, depth)
    
    # Start crawling
    pages_crawled = 0
    
    while not to_visit.empty() and pages_crawled < max_pages:
        # Get new Tor circuit every 10 pages
        if pages_crawled > 0 and pages_crawled % 10 == 0:
            new_tor_circuit()
            # Recreate session after new circuit
            session = connect_to_tor()
            if not session:
                logger.error("Lost connection to Tor, stopping crawl")
                break
        
        # Get next URL to crawl
        url, depth = to_visit.get()
        
        # Skip if already visited
        if url in visited:
            continue
        
        # Crawl the page
        result = scrape_onion_site(
            url, 
            session=session, 
            depth=depth, 
            visited=visited, 
            domain_last_visit=domain_last_visit,
            keywords=keywords
        )
        
        if result:
            # Add to results if it contains keywords or has high risk score
            if (result.get("found_keywords") or 
                result.get("risk_score", 0) > 50 or 
                "error" not in result):
                
                # Try to reveal IP if enabled
                if enable_ip_detection and "error" not in result:
                    try:
                        ip_info = reveal_ip_and_geo(url)
                        if ip_info and ip_info.get("ip_found", False):
                            result["ip_info"] = ip_info
                    except Exception as e:
                        logger.error(f"Error revealing IP for {url}: {e}")
                
                results.append(result)
            
            # Add links to queue if not at max depth
            if "links" in result and depth < MAX_DEPTH:
                for link in result["links"]:
                    if link not in visited:
                        to_visit.put((link, depth + 1))
        
        pages_crawled += 1
        logger.info(f"Crawled {pages_crawled}/{max_pages} pages")
    
    logger.info(f"Crawl completed. Visited {len(visited)} URLs, found {len(results)} relevant pages")
    return results

def search_dark_web(keywords, max_pages=50):
    """Search the Dark Web for specific keywords"""
    if isinstance(keywords, str):
        keywords = [keyword.strip() for keyword in keywords.split(',')]
    
    logger.info(f"Searching Dark Web for keywords: {keywords}")
    
    # Use seed URLs as starting points
    results = crawl_dark_web(
        start_urls=SEED_URLS,
        max_pages=max_pages,
        keywords=keywords,
        enable_ip_detection=True
    )
    
    return results

if __name__ == "__main__":
    # Example usage
    keywords = ["drugs", "bitcoin"]  # Replace with actual keywords to search
    results = search_dark_web(keywords, max_pages=20)
    
    # Save results to file
    output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'data', 'search_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"Search completed. Found {len(results)} results. Saved to {output_file}")
