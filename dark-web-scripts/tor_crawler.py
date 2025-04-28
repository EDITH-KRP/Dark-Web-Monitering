import requests
from stem import Signal
from stem.control import Controller


def connect_to_tor():
    try:
        
        session = requests.Session()
        session.proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
        return session
    except Exception as e:
        print(f"Error connecting to Tor: {e}")
        return None


def new_tor_circuit():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()  
        controller.signal(Signal.NEWNYM) 


def scrape_onion_site(url):
    session = connect_to_tor()
    if not session:
        return {"error": "Could not connect to Tor"}

    
    try:
        response = session.get(url, timeout=30)
        if response.status_code == 200:
            return {"url": url, "content": response.text}
        else:
            return {"error": f"Failed to retrieve {url}, Status code: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Error scraping {url}: {e}"}

if __name__ == "__main__":
   
    onion_url = 'http://example.onion'  
    result = scrape_onion_site(onion_url)
    print(result)
