import requests
from bs4 import BeautifulSoup
import re
import json
import os
import time
import datetime
import hashlib
import logging
from dotenv import load_dotenv
import socks
import socket

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('seller_tracking')

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', '.env'))

# Common marketplace patterns to identify seller profiles
MARKETPLACE_PATTERNS = {
    "darkmarket": {
        "url_pattern": r"darkmarket[a-z0-9]+\.onion",
        "seller_pattern": r"/vendor/([a-zA-Z0-9_-]+)",
        "profile_selector": "div.vendor-profile",
        "name_selector": "h1.vendor-name",
        "rating_selector": "div.vendor-rating",
        "products_selector": "div.product-list .product",
        "feedback_selector": "div.feedback-list .feedback-item",
        "pgp_selector": "pre.vendor-pgp"
    },
    "whitehouse": {
        "url_pattern": r"white[a-z0-9]+\.onion",
        "seller_pattern": r"/seller/([a-zA-Z0-9_-]+)",
        "profile_selector": "div.seller-profile",
        "name_selector": "h2.seller-name",
        "rating_selector": "div.seller-stats .rating",
        "products_selector": "div.listing-list .listing",
        "feedback_selector": "div.reviews .review",
        "pgp_selector": "pre.pgp-key"
    },
    "alphabay": {
        "url_pattern": r"alphabay[a-z0-9]+\.onion",
        "seller_pattern": r"/user/([a-zA-Z0-9_-]+)",
        "profile_selector": "div.user-profile",
        "name_selector": "h1.username",
        "rating_selector": "div.user-rating",
        "products_selector": "div.listings .listing",
        "feedback_selector": "div.feedback-list .feedback",
        "pgp_selector": "pre.pgp-key"
    },
    "versus": {
        "url_pattern": r"versus[a-z0-9]+\.onion",
        "seller_pattern": r"/vendor/([a-zA-Z0-9_-]+)",
        "profile_selector": "div.vendor-profile",
        "name_selector": "h2.vendor-name",
        "rating_selector": "div.vendor-rating",
        "products_selector": "div.product-list .product",
        "feedback_selector": "div.feedback-list .feedback",
        "pgp_selector": "pre.pgp-key"
    },
    "torrez": {
        "url_pattern": r"torrez[a-z0-9]+\.onion",
        "seller_pattern": r"/vendor/([a-zA-Z0-9_-]+)",
        "profile_selector": "div.vendor-profile",
        "name_selector": "h1.vendor-name",
        "rating_selector": "div.vendor-rating",
        "products_selector": "div.listings .listing",
        "feedback_selector": "div.reviews .review",
        "pgp_selector": "pre.pgp-key"
    },
    "darkfox": {
        "url_pattern": r"darkfox[a-z0-9]+\.onion",
        "seller_pattern": r"/vendor/([a-zA-Z0-9_-]+)",
        "profile_selector": "div.vendor-profile",
        "name_selector": "h1.vendor-name",
        "rating_selector": "div.vendor-rating",
        "products_selector": "div.product-list .product",
        "feedback_selector": "div.feedback-list .feedback",
        "pgp_selector": "pre.pgp-key"
    }
}

def get_tor_session():
    """Create a session using the Tor network"""
    session = requests.Session()
    # Configure Tor SOCKS proxy
    session.proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    return session

def identify_marketplace(url):
    """Identify which marketplace the URL belongs to"""
    for marketplace, patterns in MARKETPLACE_PATTERNS.items():
        if re.search(patterns["url_pattern"], url, re.IGNORECASE):
            return marketplace
    return None

def extract_seller_id(url, marketplace):
    """Extract seller ID from URL based on marketplace pattern"""
    if marketplace not in MARKETPLACE_PATTERNS:
        return None
        
    pattern = MARKETPLACE_PATTERNS[marketplace]["seller_pattern"]
    match = re.search(pattern, url)
    
    if match:
        return match.group(1)
    return None

def parse_seller_profile(html, marketplace):
    """Parse seller profile HTML based on marketplace selectors"""
    if not html or marketplace not in MARKETPLACE_PATTERNS:
        return None
        
    try:
        soup = BeautifulSoup(html, 'html.parser')
        patterns = MARKETPLACE_PATTERNS[marketplace]
        
        # Initialize profile data
        profile = {
            "marketplace": marketplace,
            "timestamp": datetime.datetime.now().isoformat(),
            "products": [],
            "feedback": [],
            "pgp_key": None
        }
        
        # Extract profile name
        name_element = soup.select_one(patterns["name_selector"])
        if name_element:
            profile["name"] = name_element.text.strip()
        
        # Extract rating
        rating_element = soup.select_one(patterns["rating_selector"])
        if rating_element:
            profile["rating"] = rating_element.text.strip()
            # Try to convert rating to numeric value
            try:
                rating_text = profile["rating"]
                # Extract numbers from text (e.g., "4.8/5" -> 4.8)
                rating_match = re.search(r'(\d+\.\d+|\d+)', rating_text)
                if rating_match:
                    profile["rating_value"] = float(rating_match.group(1))
            except:
                pass
        
        # Extract products
        product_elements = soup.select(patterns["products_selector"])
        for product in product_elements:
            product_data = {"raw_html": str(product)}
            
            # Try to extract product name
            name_element = product.select_one("h3, h4, .title, .name")
            if name_element:
                product_data["name"] = name_element.text.strip()
            
            # Try to extract price
            price_element = product.select_one(".price, .cost")
            if price_element:
                product_data["price"] = price_element.text.strip()
            
            # Try to extract description
            desc_element = product.select_one(".description, .desc")
            if desc_element:
                product_data["description"] = desc_element.text.strip()
            
            profile["products"].append(product_data)
        
        # Extract feedback
        feedback_elements = soup.select(patterns["feedback_selector"])
        for feedback in feedback_elements:
            feedback_data = {"raw_html": str(feedback)}
            
            # Try to extract rating
            rating_element = feedback.select_one(".rating, .stars")
            if rating_element:
                feedback_data["rating"] = rating_element.text.strip()
            
            # Try to extract comment
            comment_element = feedback.select_one(".comment, .text")
            if comment_element:
                feedback_data["comment"] = comment_element.text.strip()
            
            # Try to extract date
            date_element = feedback.select_one(".date, .time")
            if date_element:
                feedback_data["date"] = date_element.text.strip()
            
            profile["feedback"].append(feedback_data)
        
        # Extract PGP key
        pgp_element = soup.select_one(patterns["pgp_selector"])
        if pgp_element:
            profile["pgp_key"] = pgp_element.text.strip()
        
        return profile
    
    except Exception as e:
        logger.error(f"Error parsing seller profile: {e}")
        return None

def generic_seller_extraction(html):
    """Generic extraction for unknown marketplaces"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Initialize profile data
        profile = {
            "marketplace": "unknown",
            "timestamp": datetime.datetime.now().isoformat(),
            "products": [],
            "feedback": []
        }
        
        # Try to find seller name (look for prominent headings)
        name_candidates = soup.select("h1, h2, h3, .profile-name, .vendor-name, .seller-name, .username")
        for candidate in name_candidates:
            if candidate.text.strip():
                profile["name"] = candidate.text.strip()
                break
        
        # Try to find rating information
        rating_candidates = soup.select(".rating, .stars, .score, .feedback-score")
        for candidate in rating_candidates:
            text = candidate.text.strip()
            if re.search(r'\d', text):  # Contains at least one digit
                profile["rating"] = text
                break
        
        # Try to find product listings
        product_containers = soup.select(".product, .listing, .item, .product-item, .product-listing")
        for container in product_containers:
            product = {}
            
            # Try to get product name
            name_elem = container.select_one("h3, h4, .title, .name, .product-title")
            if name_elem:
                product["name"] = name_elem.text.strip()
            
            # Try to get price
            price_elem = container.select_one(".price, .cost, .btc, .amount")
            if price_elem:
                product["price"] = price_elem.text.strip()
            
            if product:
                profile["products"].append(product)
        
        # Try to find feedback/reviews
        feedback_containers = soup.select(".feedback, .review, .comment, .rating-item")
        for container in feedback_containers:
            feedback = {}
            
            # Try to get comment text
            comment_elem = container.select_one(".text, .comment-text, .review-text")
            if comment_elem:
                feedback["comment"] = comment_elem.text.strip()
            
            # Try to get rating
            rating_elem = container.select_one(".stars, .rating-value, .score")
            if rating_elem:
                feedback["rating"] = rating_elem.text.strip()
            
            if feedback:
                profile["feedback"].append(feedback)
        
        # Try to find PGP key
        pgp_candidates = soup.select("pre, .pgp, .pgp-key, .public-key")
        for candidate in pgp_candidates:
            text = candidate.text.strip()
            if text.startswith("-----BEGIN PGP PUBLIC KEY BLOCK-----"):
                profile["pgp_key"] = text
                break
        
        return profile
    
    except Exception as e:
        logger.error(f"Error in generic seller extraction: {e}")
        return None

def track_seller_profile(url):
    """Track a seller profile on a dark web marketplace"""
    try:
        # Create Tor session
        session = get_tor_session()
        
        # Set a realistic user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
        }
        
        # Fetch the page
        response = session.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return {
                "error": f"Failed to fetch seller profile: HTTP {response.status_code}",
                "url": url
            }
        
        # Identify marketplace
        marketplace = identify_marketplace(url)
        
        # Parse the profile based on marketplace
        if marketplace:
            profile = parse_seller_profile(response.text, marketplace)
        else:
            # Try generic extraction for unknown marketplace
            profile = generic_seller_extraction(response.text)
        
        if not profile:
            return {
                "error": "Failed to parse seller profile",
                "url": url,
                "marketplace": marketplace
            }
        
        # Add URL and seller ID to profile
        profile["url"] = url
        
        if marketplace:
            seller_id = extract_seller_id(url, marketplace)
            if seller_id:
                profile["seller_id"] = seller_id
        
        # Generate a unique ID for this profile snapshot
        profile_id = hashlib.md5(f"{url}_{profile.get('name', '')}_{int(time.time())}".encode()).hexdigest()
        profile["profile_id"] = profile_id
        
        # Save the profile to disk
        save_seller_profile(profile)
        
        return profile
    
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Error accessing seller profile: {e}",
            "url": url
        }
    except Exception as e:
        return {
            "error": f"Unexpected error tracking seller profile: {e}",
            "url": url
        }

def save_seller_profile(profile):
    """Save seller profile to disk for historical tracking"""
    try:
        # Create directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'data', 'sellers')
        os.makedirs(data_dir, exist_ok=True)
        
        # Generate filename based on marketplace and seller ID/name
        if "seller_id" in profile:
            base_name = f"{profile['marketplace']}_{profile['seller_id']}"
        elif "name" in profile:
            # Clean name for filename
            clean_name = re.sub(r'[^\w\-]', '_', profile['name'])
            base_name = f"{profile['marketplace']}_{clean_name}"
        else:
            base_name = f"unknown_{profile['profile_id']}"
        
        # Add timestamp to filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_name}_{timestamp}.json"
        
        # Save to file
        file_path = os.path.join(data_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2)
        
        logger.info(f"Saved seller profile to {file_path}")
        
        # Also update the latest version
        latest_path = os.path.join(data_dir, f"{base_name}_latest.json")
        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"Error saving seller profile: {e}")
        return False

def get_seller_history(marketplace, seller_id=None, seller_name=None):
    """Get historical data for a seller"""
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'data', 'sellers')
        
        if not os.path.exists(data_dir):
            return {"error": "No seller data available"}
        
        # Determine file pattern to search for
        if seller_id:
            pattern = f"{marketplace}_{seller_id}_*.json"
        elif seller_name:
            clean_name = re.sub(r'[^\w\-]', '_', seller_name)
            pattern = f"{marketplace}_{clean_name}_*.json"
        else:
            return {"error": "Either seller_id or seller_name must be provided"}
        
        # Find matching files
        import glob
        files = glob.glob(os.path.join(data_dir, pattern))
        
        # Exclude latest file
        files = [f for f in files if not f.endswith('_latest.json')]
        
        # Sort by timestamp (newest first)
        files.sort(reverse=True)
        
        # Load data from files
        history = []
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                    history.append(profile)
            except:
                continue
        
        return {
            "marketplace": marketplace,
            "seller_id": seller_id,
            "seller_name": seller_name,
            "history": history,
            "count": len(history)
        }
    
    except Exception as e:
        return {"error": f"Error retrieving seller history: {e}"}

def analyze_seller_trends(history):
    """Analyze trends in seller history"""
    if not history or "history" not in history or not history["history"]:
        return {"error": "No history data available for analysis"}
    
    try:
        profiles = history["history"]
        
        # Initialize analysis
        analysis = {
            "marketplace": history["marketplace"],
            "seller_id": history.get("seller_id"),
            "seller_name": history.get("seller_name"),
            "first_seen": profiles[-1]["timestamp"],
            "last_seen": profiles[0]["timestamp"],
            "total_snapshots": len(profiles),
            "product_trends": [],
            "rating_trend": [],
            "feedback_trend": []
        }
        
        # Analyze product trends
        all_products = {}
        for profile in profiles:
            timestamp = profile["timestamp"]
            
            # Track products
            for product in profile.get("products", []):
                if "name" in product:
                    product_name = product["name"]
                    if product_name not in all_products:
                        all_products[product_name] = []
                    
                    all_products[product_name].append({
                        "timestamp": timestamp,
                        "price": product.get("price")
                    })
            
            # Track rating
            if "rating_value" in profile:
                analysis["rating_trend"].append({
                    "timestamp": timestamp,
                    "rating": profile["rating_value"]
                })
            
            # Track feedback count
            analysis["feedback_trend"].append({
                "timestamp": timestamp,
                "count": len(profile.get("feedback", []))
            })
        
        # Process product trends
        for product_name, appearances in all_products.items():
            analysis["product_trends"].append({
                "name": product_name,
                "first_seen": appearances[-1]["timestamp"],
                "last_seen": appearances[0]["timestamp"],
                "appearances": len(appearances),
                "price_history": appearances
            })
        
        # Sort product trends by number of appearances (most frequent first)
        analysis["product_trends"].sort(key=lambda x: x["appearances"], reverse=True)
        
        return analysis
    
    except Exception as e:
        return {"error": f"Error analyzing seller trends: {e}"}

if __name__ == "__main__":
    # Example usage
    seller_url = "http://example.onion/vendor/test_seller"  # Replace with actual URL to test
    result = track_seller_profile(seller_url)
    print(json.dumps(result, indent=2))