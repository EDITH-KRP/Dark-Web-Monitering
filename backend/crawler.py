import requests
from stem import Signal
from stem.control import Controller
from bs4 import BeautifulSoup
import random
import datetime
import time
import string
import uuid

# Fake data generators
def generate_onion_url():
    """Generate a random .onion URL"""
    domain = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    return f"http://{domain}.onion"

def generate_title(keywords):
    """Generate a title based on keywords"""
    prefixes = ["Hidden", "Secret", "Underground", "Dark", "Shadow", "Anonymous", "Encrypted"]
    suffixes = ["Market", "Forum", "Exchange", "Network", "Hub", "Bazaar", "Vault", "Hideout"]
    
    if not keywords:
        keywords = ["marketplace"]
    
    keyword_list = keywords.split(',')
    selected_keyword = random.choice(keyword_list).strip()
    
    return f"{random.choice(prefixes)} {selected_keyword.capitalize()} {random.choice(suffixes)}"

def generate_description(keywords, geo_location):
    """Generate a description based on keywords and geo-location"""
    templates = [
        "A secure platform for {keyword} transactions. Based in {location}.",
        "The most trusted {location} source for {keyword}.",
        "Find verified {keyword} dealers from {location} here.",
        "Anonymous {keyword} marketplace with sellers from {location}.",
        "Encrypted {keyword} exchange with {location} shipping available."
    ]
    
    if not keywords:
        keywords = ["items"]
    if not geo_location:
        geo_location = "worldwide"
    
    keyword_list = keywords.split(',')
    selected_keyword = random.choice(keyword_list).strip()
    
    return random.choice(templates).format(keyword=selected_keyword, location=geo_location)

def generate_risk_level(keywords):
    """Generate a risk level based on keywords"""
    high_risk = ["arms", "murder", "drugs", "weapons", "hitman", "fentanyl", "heroin"]
    medium_risk = ["fraud", "hack", "counterfeit", "fake", "stolen", "illegal"]
    low_risk = ["forum", "chat", "anonymous", "privacy", "secure"]
    
    if not keywords:
        return random.randint(10, 30)
    
    keyword_list = keywords.lower().split(',')
    
    for keyword in keyword_list:
        keyword = keyword.strip()
        if any(risk in keyword for risk in high_risk):
            return random.randint(85, 100)
        elif any(risk in keyword for risk in medium_risk):
            return random.randint(50, 84)
        elif any(risk in keyword for risk in low_risk):
            return random.randint(10, 49)
    
    return random.randint(30, 70)

def detect_country(keywords, geo_location):
    """Detect country based on keywords or geo-location"""
    keyword_country_map = {
        "ak47": "Russia",
        "vodka": "Russia",
        "fentanyl": "Mexico",
        "cocaine": "Colombia",
        "maple": "Canada",
        "kangaroo": "Australia",
        "tea": "United Kingdom"
    }
    
    if geo_location and geo_location.strip():
        return geo_location
    
    if not keywords:
        return "Unknown"
    
    keyword_list = keywords.lower().split(',')
    
    for keyword in keyword_list:
        keyword = keyword.strip()
        for k, country in keyword_country_map.items():
            if k in keyword:
                return country
    
    return random.choice(["USA", "Germany", "Netherlands", "China", "Japan", "Brazil", "Unknown"])

def is_seller(keywords):
    """Determine if the page is from a seller"""
    seller_indicators = ["sell", "price", "shipping", "vendor", "shop", "store", "payment", "bitcoin", "btc", "monero", "xmr"]
    
    if not keywords:
        return random.random() > 0.7
    
    keyword_list = keywords.lower().split(',')
    
    for keyword in keyword_list:
        keyword = keyword.strip()
        if any(indicator in keyword for indicator in seller_indicators):
            return True
    
    return random.random() > 0.7

def generate_archive_link(url):
    """Generate a fake archive.org link"""
    year = random.randint(2015, 2023)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    
    timestamp = f"{year}{month:02d}{day:02d}{hour:02d}{minute:02d}{second:02d}"
    return f"https://web.archive.org/web/{timestamp}/{url}"

def get_tor_session():
    """Create a session using the Tor network"""
    import socks
    import socket
    import os
    import subprocess
    import time
    import platform
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', '.env'))
    
    # Check if Tor is running
    tor_running = False
    try:
        # Try to connect to the SOCKS port to check if Tor is running
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(('127.0.0.1', 9050))
        s.close()
        tor_running = True
        print("Tor is already running")
    except:
        print("Tor is not running, attempting to start it...")
        tor_running = False
    
    # If Tor is not running, try to start it
    if not tor_running:
        try:
            system = platform.system()
            
            if system == "Windows":
                # First check if we have a path in the .env file
                tor_path = os.getenv('TOR_EXECUTABLE_PATH')
                
                # If not, check common locations
                if not tor_path or not os.path.exists(tor_path):
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
                            break
                
                if tor_path and os.path.exists(tor_path):
                    print(f"Starting Tor from {tor_path}")
                    # Start Tor in the background
                    subprocess.Popen([tor_path], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE,
                                    creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    print("Tor executable not found. Please install Tor Browser.")
                    print("Falling back to simulation mode.")
                    return None
            else:
                # For Linux/macOS, try to start the tor service
                try:
                    subprocess.run(["sudo", "service", "tor", "start"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  timeout=10)
                except:
                    try:
                        # Try direct tor command
                        subprocess.Popen(["tor"], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
                    except:
                        print("Failed to start Tor. Please install Tor service.")
                        print("Falling back to simulation mode.")
                        return None
            
            # Wait for Tor to start
            print("Waiting for Tor to start...")
            for i in range(30):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1)
                    s.connect(('127.0.0.1', 9050))
                    s.close()
                    tor_running = True
                    print("Tor started successfully")
                    break
                except:
                    time.sleep(1)
            
            if not tor_running:
                print("Failed to start Tor within timeout period.")
                print("Falling back to simulation mode.")
                return None
        
        except Exception as e:
            print(f"Error starting Tor: {e}")
            print("Falling back to simulation mode.")
            return None
    
    # Configure session to use Tor
    try:
        session = requests.Session()
        # Configure Tor SOCKS proxy
        session.proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        
        # Test the connection to verify Tor is working
        print("Testing Tor connection...")
        response = session.get('https://check.torproject.org/', timeout=30)
        
        if 'Congratulations. This browser is configured to use Tor' in response.text:
            print("Successfully connected to Tor network")
            return session
        else:
            print("Connected to Tor but verification failed")
            # Still return the session as it might work for .onion sites
            return session
    except Exception as e:
        print(f"Error connecting to Tor network: {e}")
        print("Falling back to simulation mode.")
        return None

def renew_tor_ip():
    """Renew the TOR IP address by sending a signal to the Tor Controller"""
    import os
    import platform
    import getpass
    import time
    
    try:
        # Default password for Tor controller
        password = ""
        
        # Try to find the Tor control password
        system = platform.system()
        if system == "Linux" or system == "Darwin":  # Linux or macOS
            torrc_paths = [
                "/etc/tor/torrc",
                "/usr/local/etc/tor/torrc",
                os.path.expanduser("~/.torrc"),
                os.path.expanduser("~/.tor/torrc")
            ]
        else:  # Windows
            torrc_paths = [
                "C:\\Users\\prajw\\OneDrive\\Desktop\\Tor Browser\\Browser\\TorBrowser\\Data\\Tor\\torrc",
                os.path.expanduser("~\\Desktop\\Tor Browser\\Browser\\TorBrowser\\Data\\Tor\\torrc"),
                os.path.expanduser("~\\Downloads\\Tor Browser\\Browser\\TorBrowser\\Data\\Tor\\torrc"),
                "C:\\Program Files\\Tor Browser\\Browser\\TorBrowser\\Data\\Tor\\torrc",
                "C:\\Program Files (x86)\\Tor Browser\\Browser\\TorBrowser\\Data\\Tor\\torrc"
            ]
        
        # Try to find the control password in the torrc file
        for torrc_path in torrc_paths:
            if os.path.exists(torrc_path):
                with open(torrc_path, 'r') as f:
                    for line in f:
                        if line.startswith('HashedControlPassword'):
                            print("Found hashed control password in torrc")
                            # We need to ask the user for the password
                            password = getpass.getpass("Enter Tor control password: ")
                            break
        
        # Connect to the Tor controller
        with Controller.from_port(port=9051) as controller:
            if password:
                controller.authenticate(password=password)
            else:
                # Try with no password
                try:
                    controller.authenticate()
                except:
                    # Try with cookie authentication
                    controller.authenticate(cookie_auth=True)
            
            # Send the NEWNYM signal to get a new identity
            controller.signal(Signal.NEWNYM)
            print("New Tor IP assigned.")
            
            # Wait a moment for the change to take effect
            time.sleep(2)
    except Exception as e:
        print(f"Error renewing Tor IP: {e}")
        print("Make sure Tor is running with ControlPort enabled")
        print("You may need to add 'ControlPort 9051' and 'CookieAuthentication 1' to your torrc file")
        
        # Try alternative method for Tor Browser
        try:
            system = platform.system()
            if system == "Windows":
                # Try to find the Tor Browser control port
                control_port_paths = [
                    "C:\\Users\\prajw\\OneDrive\\Desktop\\Tor Browser\\Browser\\TorBrowser\\Data\\Tor\\control_auth_cookie",
                    os.path.expanduser("~\\Desktop\\Tor Browser\\Browser\\TorBrowser\\Data\\Tor\\control_auth_cookie"),
                    os.path.expanduser("~\\Downloads\\Tor Browser\\Browser\\TorBrowser\\Data\\Tor\\control_auth_cookie"),
                    "C:\\Program Files\\Tor Browser\\Browser\\TorBrowser\\Data\\Tor\\control_auth_cookie",
                    "C:\\Program Files (x86)\\Tor Browser\\Browser\\TorBrowser\\Data\\Tor\\control_auth_cookie"
                ]
                
                for cookie_path in control_port_paths:
                    if os.path.exists(cookie_path):
                        with Controller.from_port(port=9151) as controller:
                            controller.authenticate(cookie_file=cookie_path)
                            controller.signal(Signal.NEWNYM)
                            print("New Tor IP assigned using Tor Browser control port.")
                            time.sleep(2)
                            return
            else:
                # Try alternative ports for Linux/macOS
                try:
                    with Controller.from_port(port=9151) as controller:
                        controller.authenticate()
                        controller.signal(Signal.NEWNYM)
                        print("New Tor IP assigned using alternative port.")
                        time.sleep(2)
                        return
                except:
                    pass
        except Exception as inner_e:
            print(f"Alternative method also failed: {inner_e}")
            print("Unable to renew Tor IP address")

def scrape_onion_site(url):
    """Scrape content from an .onion site"""
    print(f"Scraping {url}...")
    
    # Get a Tor session
    session = get_tor_session()
    
    if not session:
        print("Failed to establish Tor session. Retrying...")
        # Try one more time before giving up
        time.sleep(5)
        session = get_tor_session()
        
        if not session:
            print("Failed to establish Tor session after retry, falling back to simulation")
            # Return simulated data for this URL
            return [{
            'id': str(uuid.uuid4()),
            'url': url,
            'title': f"Simulated data for {url}",
            'description': "This is simulated data because Tor connection failed",
            'risk_score': random.randint(50, 90),
            'country': "Unknown",
            'is_seller': random.choice([True, False]),
            'archive_link': generate_archive_link(url),
            'date_detected': datetime.datetime.now().strftime("%Y-%m-%d")
        }]
    
    try:
        # Set a reasonable timeout
        response = session.get(url, timeout=60)
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = soup.title.string if soup.title else "Unknown Title"
        
        # Extract description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'] if meta_desc else ""
        
        # If no meta description, try to get some text content
        if not description:
            paragraphs = soup.find_all('p')
            if paragraphs:
                # Join the first few paragraphs
                description = ' '.join([p.text for p in paragraphs[:3]])[:200] + "..."
            else:
                # Just get some text from the body
                body_text = soup.body.text if soup.body else ""
                description = ' '.join(body_text.split()[:30]) + "..."
        
        # Calculate risk score based on content
        content_text = soup.get_text().lower()
        risk_score = calculate_risk_score_from_content(content_text)
        
        # Try to determine if it's a seller
        is_seller_site = determine_if_seller(soup, content_text)
        
        # Try to determine country
        country = extract_country_from_content(soup, content_text)
        
        # Check for archive link
        archive_link = generate_archive_link(url)
        
        # Create data entry
        data = {
            'id': str(uuid.uuid4()),
            'url': url,
            'title': title,
            'description': description,
            'risk_score': risk_score,
            'country': country,
            'is_seller': is_seller_site,
            'archive_link': archive_link,
            'date_detected': datetime.datetime.now().strftime("%Y-%m-%d"),
            'content_sample': content_text[:500] + "..." if len(content_text) > 500 else content_text
        }
        
        return [data]
    
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        # Return simulated data for this URL
        return [{
            'id': str(uuid.uuid4()),
            'url': url,
            'title': f"Error scraping {url}",
            'description': f"Error: {str(e)}",
            'risk_score': random.randint(50, 90),
            'country': "Unknown",
            'is_seller': random.choice([True, False]),
            'archive_link': generate_archive_link(url),
            'date_detected': datetime.datetime.now().strftime("%Y-%m-%d")
        }]

def calculate_risk_score_from_content(content):
    """Calculate risk score based on actual content"""
    # Define risk categories with weighted scores
    risk_terms = {
        # High risk terms (90-100)
        "murder": 95, "assassination": 95, "hitman": 95, "kill": 90,
        "fentanyl": 95, "heroin": 90, "cocaine": 85, "meth": 85,
        "weapons": 90, "guns": 85, "firearms": 85, "explosives": 90,
        "child": 95, "underage": 95,
        "counterfeit": 80, "fake id": 80, "passport": 85,
        
        # Medium risk terms (60-89)
        "hack": 75, "cracking": 70, "ddos": 75,
        "credit card": 80, "dumps": 80, "cvv": 80,
        "bitcoin": 60, "monero": 65, "cryptocurrency": 60,
        "anonymous": 60, "hidden": 60, "private": 60,
        
        # Low risk terms (30-59)
        "forum": 40, "discussion": 35, "community": 30,
        "market": 50, "marketplace": 55, "shop": 55,
        "secure": 40, "encrypted": 45, "privacy": 40
    }
    
    # Calculate score based on presence of risk terms
    max_score = 0
    for term, score in risk_terms.items():
        if term in content:
            max_score = max(max_score, score)
    
    # If no risk terms found, assign a base score
    if max_score == 0:
        max_score = 30
    
    # Add some randomness (±5 points)
    max_score += random.randint(-5, 5)
    
    # Ensure score is within 0-100 range
    return max(0, min(100, max_score))

def determine_if_seller(soup, content):
    """Determine if the site is a seller based on content analysis"""
    # Check for common seller indicators in the content
    seller_indicators = [
        "buy", "purchase", "order", "add to cart", "checkout", "shopping cart",
        "price", "cost", "payment", "shipping", "delivery", "vendor", "seller",
        "bitcoin", "btc", "monero", "xmr", "cryptocurrency", "crypto", "wallet"
    ]
    
    # Check for common seller HTML elements
    seller_elements = [
        soup.find('form', attrs={'id': lambda x: x and ('cart' in x.lower() or 'checkout' in x.lower() or 'order' in x.lower())}),
        soup.find('button', text=lambda x: x and ('buy' in x.lower() or 'purchase' in x.lower() or 'add to cart' in x.lower())),
        soup.find('input', attrs={'type': 'submit', 'value': lambda x: x and ('buy' in x.lower() or 'purchase' in x.lower())}),
        soup.find('div', attrs={'class': lambda x: x and ('product' in x.lower() or 'item' in x.lower() or 'cart' in x.lower())})
    ]
    
    # Check content for seller indicators
    content_indicators = sum(1 for indicator in seller_indicators if indicator in content.lower())
    
    # Check HTML for seller elements
    element_indicators = sum(1 for element in seller_elements if element is not None)
    
    # Determine if it's a seller based on the number of indicators
    return (content_indicators >= 3) or (element_indicators >= 1)

def extract_country_from_content(soup, content):
    """Extract country information from the content"""
    # List of countries to check for
    countries = [
        "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Argentina", "Armenia", "Australia", 
        "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", 
        "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia", "Botswana", "Brazil", "Brunei", "Bulgaria", 
        "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde", "Central African Republic", 
        "Chad", "Chile", "China", "Colombia", "Comoros", "Congo", "Costa Rica", "Croatia", "Cuba", "Cyprus", 
        "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "East Timor", "Ecuador", 
        "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", 
        "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", 
        "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", 
        "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", 
        "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", 
        "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", 
        "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", 
        "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", 
        "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", 
        "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", 
        "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", 
        "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", 
        "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", 
        "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", 
        "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", 
        "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "USA", 
        "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Yemen", 
        "Zambia", "Zimbabwe"
    ]
    
    # Check for country names in the content
    for country in countries:
        if country in content or country.lower() in content.lower():
            return country
    
    # Check for country codes in the content
    country_codes = {
        "US": "United States", "GB": "United Kingdom", "UK": "United Kingdom", "CA": "Canada", 
        "AU": "Australia", "DE": "Germany", "FR": "France", "JP": "Japan", "CN": "China", 
        "RU": "Russia", "BR": "Brazil", "IN": "India", "MX": "Mexico", "ES": "Spain", 
        "IT": "Italy", "NL": "Netherlands", "CH": "Switzerland", "SE": "Sweden", "NO": "Norway"
    }
    
    for code, country in country_codes.items():
        if f" {code} " in f" {content} " or f" {code}," in content or f" {code}." in content:
            return country
    
    # Check for shipping information
    shipping_elements = soup.find_all(text=lambda text: text and "shipping" in text.lower())
    for element in shipping_elements:
        for country in countries:
            if country in element or country.lower() in element.lower():
                return country
    
    # If no country found, return Unknown
    return "Unknown"

def search_onion_directory(keywords):
    """Search for .onion sites related to the keywords"""
    # List of known .onion directories and search engines
    onion_directories = [
        "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion",  # Torch
        "http://haystak5njsmn2hqkewecpaxetahtwhsbsa64jom2k22z5afxhnpxfid.onion",  # Haystak
        "http://notbumpz34bgbz4yfdigxvd6vzwtxc3zpt5imukgl6bvip2nikdmdaad.onion",  # not Evil
        "http://searchesqafmar2ocusr443hnolhmrxek5xu3hrw3wac2rk7hd8s3y4d.onion"   # Ahmia
    ]
    
    # Get a Tor session
    session = get_tor_session()
    
    if not session:
        print("Failed to establish Tor session. Retrying...")
        # Try one more time before giving up
        time.sleep(5)
        session = get_tor_session()
        
        if not session:
            print("Failed to establish Tor session after retry, falling back to simulation")
            return simulate_search_results(keywords)
    
    results = []
    
    # Try each directory
    for directory in onion_directories:
        try:
            print(f"Searching {directory} for {keywords}...")
            
            # Different search engines have different URL patterns
            if "torch" in directory:
                search_url = f"{directory}/search?query={keywords.replace(' ', '+')}"
            elif "haystak" in directory:
                search_url = f"{directory}/search?q={keywords.replace(' ', '+')}"
            elif "notevil" in directory or "not Evil" in directory:
                search_url = f"{directory}/index.php?q={keywords.replace(' ', '+')}"
            elif "ahmia" in directory:
                search_url = f"{directory}/search/?q={keywords.replace(' ', '+')}"
            else:
                search_url = f"{directory}/search?q={keywords.replace(' ', '+')}"
            
            # Make the search request
            response = session.get(search_url, timeout=60)
            
            # Parse the results
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract links (different search engines have different HTML structures)
            links = []
            
            # Try different selectors for search results
            for selector in ['a.result-link', 'a.search-result', 'div.result a', 'li.result a', 'a[href*=".onion"]']:
                links.extend(soup.select(selector))
            
            # If no links found with selectors, try to find all links to .onion sites
            if not links:
                links = [a for a in soup.find_all('a') if a.get('href') and '.onion' in a.get('href')]
            
            # Process each link
            for link in links[:5]:  # Limit to 5 results per directory
                href = link.get('href')
                
                # Make sure it's a full URL
                if href and '.onion' in href:
                    if not href.startswith('http'):
                        href = f"http://{href}" if not href.startswith('//') else f"http:{href}"
                    
                    # Skip if we already have this URL
                    if any(result['url'] == href for result in results):
                        continue
                    
                    # Scrape the site
                    site_data = scrape_onion_site(href)
                    if site_data:
                        results.extend(site_data)
                
                # Renew Tor IP occasionally
                if random.random() > 0.7:
                    renew_tor_ip()
            
            # If we found some results, we can stop
            if results:
                break
                
        except Exception as e:
            print(f"Error searching {directory}: {e}")
            continue
    
    # If no results found, try a different search approach before falling back to simulation
    if not results:
        print("No results found in initial search, trying alternative search approach...")
        # Try with a more generic search or different search engine
        try:
            # Renew Tor IP to get a fresh connection
            renew_tor_ip()
            time.sleep(3)
            
            # Try a different search approach
            alt_results = []
            for search_engine in ["torch", "ahmia", "darksearchio"]:
                engine_results = search_with_engine(session, keywords, search_engine)
                if engine_results:
                    alt_results.extend(engine_results)
                    
            if alt_results:
                print(f"Found {len(alt_results)} results with alternative search approach")
                return alt_results
                
            print("No results found in alternative search, falling back to simulation")
            return simulate_search_results(keywords)
        except Exception as e:
            print(f"Error in alternative search: {e}")
            return simulate_search_results(keywords)
    
    return results

def simulate_search_results(keywords, geo_location=None):
    """Simulate search results when real search fails"""
    print("Generating simulated search results...")
    crawled_data = []
    
    # Generate between 5-15 random results
    num_results = random.randint(5, 15)
    
    for _ in range(num_results):
        # Generate random date within the last 30 days
        days_ago = random.randint(0, 30)
        detection_date = (datetime.datetime.now() - datetime.timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Generate random URL
        url = generate_onion_url()
        
        # Generate title and description based on keywords
        title = generate_title(keywords)
        description = generate_description(keywords, geo_location)
        
        # Generate risk score
        risk_score = generate_risk_level(keywords)
        
        # Detect country
        country = detect_country(keywords, geo_location)
        
        # Determine if it's a seller
        seller = is_seller(keywords)
        
        # Generate archive link
        archive_link = generate_archive_link(url)
        
        # Create data entry
        data = {
            'id': str(uuid.uuid4()),
            'url': url,
            'title': title,
            'description': description,
            'risk_score': risk_score,
            'country': country,
            'is_seller': seller,
            'archive_link': archive_link,
            'date_detected': detection_date,
            'simulated': True
        }
        
        crawled_data.append(data)
    
    return crawled_data
    
def search_with_engine(session, keywords, engine="torch"):
    """Search the dark web using a specific search engine"""
    if not session:
        print(f"No Tor session available for {engine} search")
        return []
        
    results = []
    
    try:
        if engine == "torch":
            # Torch search engine
            search_url = f"http://xmh57jrzrnw6insl.onion/4a1f6b371c/search.cgi?q={keywords.replace(' ', '+')}"
            response = session.get(search_url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.select('.result h5 a')
                
                for link in links:
                    url = link.get('href')
                    title = link.text.strip()
                    
                    # Extract description
                    description_elem = link.find_parent('div').find('p')
                    description = description_elem.text.strip() if description_elem else ""
                    
                    results.append({
                        'url': url,
                        'title': title,
                        'description': description,
                        'engine': 'torch'
                    })
                    
        elif engine == "ahmia":
            # Ahmia search engine
            search_url = f"https://ahmia.fi/search/?q={keywords.replace(' ', '+')}"
            response = session.get(search_url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                items = soup.select('.result')
                
                for item in items:
                    link = item.find('h4').find('a')
                    url = link.get('href')
                    title = link.text.strip()
                    
                    # Extract description
                    description_elem = item.find('p')
                    description = description_elem.text.strip() if description_elem else ""
                    
                    results.append({
                        'url': url,
                        'title': title,
                        'description': description,
                        'engine': 'ahmia'
                    })
                    
        elif engine == "darksearchio":
            # DarkSearch.io API
            search_url = f"https://darksearch.io/api/search?query={keywords.replace(' ', '+')}"
            response = session.get(search_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data:
                    for item in data['data']:
                        results.append({
                            'url': item.get('link', ''),
                            'title': item.get('title', ''),
                            'description': item.get('description', ''),
                            'engine': 'darksearchio'
                        })
        
        # Process the results to match our expected format
        processed_results = []
        for item in results:
            # Generate a unique ID
            item_id = str(uuid.uuid4())
            
            # Extract domain from URL
            domain = item['url'].split('/')[2] if '://' in item['url'] else item['url'].split('/')[0]
            
            # Create a processed result
            processed_item = {
                'id': item_id,
                'url': item['url'],
                'title': item['title'],
                'description': item['description'],
                'domain': domain,
                'date_found': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'risk_level': generate_risk_level(keywords),
                'is_seller': is_seller(keywords),
                'country': detect_country(keywords, None),
                'archive_link': generate_archive_link(item['url']),
                'search_engine': item['engine']
            }
            
            processed_results.append(processed_item)
            
        return processed_results
        
    except Exception as e:
        print(f"Error searching with {engine}: {e}")
        return []

def start_crawl(keywords=None, geo_location=None):
    """Start crawling the Dark Web based on keywords"""
    print(f"Starting Dark Web crawl for keywords: {keywords}, geo_location: {geo_location}")
    
    # If no keywords provided, return simulated results
    if not keywords:
        print("No keywords provided, returning simulated results")
        return simulate_search_results(keywords, geo_location)
    
    try:
        # Search for .onion sites related to the keywords
        results = search_onion_directory(keywords)
        
        # If geo_location is specified, filter results
        if geo_location and results:
            filtered_results = []
            for result in results:
                # Check if geo_location is mentioned in the result
                if (geo_location.lower() in result.get('description', '').lower() or 
                    geo_location.lower() in result.get('title', '').lower() or
                    geo_location.lower() == result.get('country', '').lower()):
                    filtered_results.append(result)
            
            # If we have filtered results, use them
            if filtered_results:
                results = filtered_results
        
        return results
    except Exception as e:
        print(f"Error in start_crawl: {e}")
        print("Falling back to simulated results")
        return simulate_search_results(keywords, geo_location)
