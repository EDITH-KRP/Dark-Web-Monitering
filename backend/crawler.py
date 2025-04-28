import requests
from stem import Signal
from stem.control import Controller
from bs4 import BeautifulSoup
import random


ONION_SITES = [
    'http://example1.onion',
    'http://example2.onion'
]

def get_tor_session():
    """Create a session using the Tor network"""
    session = requests.Session()
    session.proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    return session

def renew_tor_ip():
    """Renew the TOR IP address by sending a signal to the Tor Controller"""
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()  # Authenticate with the Tor network
        controller.signal(Signal.NEWNYM)  # Request a new IP
        print("New Tor IP assigned.")

def start_crawl(keywords=None, geo_location=None):
    """Crawl Dark Web and filter results"""
    crawled_data = []

    
    for site in ONION_SITES:
        try:
            session = get_tor_session()
            response = session.get(site)
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.title.string if soup.title else 'No Title'
            description = soup.find('meta', {'name': 'description'})
            description = description['content'] if description else 'No Description'

            data = {
                'url': site,
                'title': title,
                'description': description
            }
            crawled_data.append(data)

            
            if random.random() > 0.8:
                renew_tor_ip()

        except requests.RequestException as e:
            print(f"Error crawling {site}: {e}")

    return crawled_data
