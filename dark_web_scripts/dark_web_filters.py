import json
import re
import os
import datetime
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('dark_web_filters')

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', '.env'))

# Get keywords from environment or use defaults
def get_illegal_keywords():
    env_keywords = os.getenv('ILLEGAL_KEYWORDS')
    if env_keywords:
        try:
            return json.loads(env_keywords)
        except:
            pass
    
    # Default keywords if not in environment
    return [
        # Drugs
        "drugs", "cocaine", "heroin", "fentanyl", "mdma", "ecstasy", "meth", "amphetamine", 
        "lsd", "cannabis", "marijuana", "weed", "ketamine", "opioids", "steroids", "pills",
        
        # Weapons
        "weapons", "guns", "firearms", "pistol", "rifle", "ammunition", "ammo", "explosives",
        "grenades", "knives", "tactical", "silencer", "suppressor", "armor", "bulletproof",
        
        # Hacking
        "hacking", "malware", "ransomware", "spyware", "botnet", "ddos", "phishing", "exploit",
        "vulnerability", "zero-day", "rootkit", "keylogger", "cracking", "breach", "backdoor",
        
        # Counterfeit
        "counterfeit", "fake", "forged", "documents", "passports", "id cards", "driver license",
        "credit cards", "currency", "money", "bills", "banknotes", "hologram", "clone",
        
        # Financial crimes
        "carding", "dumps", "cvv", "fullz", "bank drops", "money laundering", "bitcoin tumbler",
        "crypto mixer", "paypal accounts", "wire transfer", "western union", "bank login",
        
        # Illegal services
        "hitman", "murder", "assassination", "kidnapping", "torture", "human trafficking",
        "organ trafficking", "smuggling", "bribery", "extortion", "blackmail", "fraud",
        
        # Data
        "stolen data", "leaked database", "hacked accounts", "personal information", "doxing",
        "social security", "medical records", "financial data", "corporate secrets", "credentials",
        
        # Other illegal content
        "child", "underage", "abuse", "exploitation", "rape", "snuff", "torture", "terrorism",
        "extremist", "jihad", "bomb making", "suicide", "genocide", "violence"
    ]

# Risk categories with weights
RISK_CATEGORIES = {
    "drugs": {
        "weight": 60,
        "keywords": [
            "drugs", "cocaine", "heroin", "fentanyl", "mdma", "ecstasy", "meth", "amphetamine", 
            "lsd", "cannabis", "marijuana", "weed", "ketamine", "opioids", "steroids", "pills"
        ]
    },
    "weapons": {
        "weight": 80,
        "keywords": [
            "weapons", "guns", "firearms", "pistol", "rifle", "ammunition", "ammo", "explosives",
            "grenades", "knives", "tactical", "silencer", "suppressor", "armor", "bulletproof"
        ]
    },
    "hacking": {
        "weight": 50,
        "keywords": [
            "hacking", "malware", "ransomware", "spyware", "botnet", "ddos", "phishing", "exploit",
            "vulnerability", "zero-day", "rootkit", "keylogger", "cracking", "breach", "backdoor"
        ]
    },
    "counterfeit": {
        "weight": 60,
        "keywords": [
            "counterfeit", "fake", "forged", "documents", "passports", "id cards", "driver license",
            "credit cards", "currency", "money", "bills", "banknotes", "hologram", "clone"
        ]
    },
    "financial_crime": {
        "weight": 70,
        "keywords": [
            "carding", "dumps", "cvv", "fullz", "bank drops", "money laundering", "bitcoin tumbler",
            "crypto mixer", "paypal accounts", "wire transfer", "western union", "bank login"
        ]
    },
    "illegal_services": {
        "weight": 90,
        "keywords": [
            "hitman", "murder", "assassination", "kidnapping", "torture", "human trafficking",
            "organ trafficking", "smuggling", "bribery", "extortion", "blackmail", "fraud"
        ]
    },
    "data_breach": {
        "weight": 65,
        "keywords": [
            "stolen data", "leaked database", "hacked accounts", "personal information", "doxing",
            "social security", "medical records", "financial data", "corporate secrets", "credentials"
        ]
    },
    "extreme_illegal": {
        "weight": 100,
        "keywords": [
            "child", "underage", "abuse", "exploitation", "rape", "snuff", "torture", "terrorism",
            "extremist", "jihad", "bomb making", "suicide", "genocide", "violence"
        ]
    }
}

def calculate_risk_score(content, title=None):
    """
    Calculate a risk score (0-100) based on content and title
    Higher score = higher risk
    """
    if not content:
        return 0
        
    # Combine title and content if title is provided
    if title:
        full_text = f"{title} {content}".lower()
    else:
        full_text = content.lower()
    
    # Initialize score and matched categories
    base_score = 0
    matched_categories = {}
    
    # Check each category
    for category, data in RISK_CATEGORIES.items():
        category_matches = []
        for keyword in data["keywords"]:
            # Look for whole word matches
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            matches = re.findall(pattern, full_text)
            if matches:
                category_matches.extend(matches)
        
        # If we found matches in this category
        if category_matches:
            # Calculate category score based on number of matches and category weight
            category_score = min(100, len(category_matches) * data["weight"] / 5)
            matched_categories[category] = {
                "score": category_score,
                "matches": category_matches
            }
            
            # Add to base score (weighted by category importance)
            base_score += category_score * (data["weight"] / 100)
    
    # Normalize final score to 0-100 range
    final_score = min(100, base_score)
    
    return {
        "score": round(final_score),
        "categories": matched_categories
    }

def categorize_site(site):
    """Categorize a site based on its content"""
    # Default category
    category = "unknown"
    
    # Extract text to analyze
    text_to_analyze = ""
    if "title" in site:
        text_to_analyze += site["title"] + " "
    if "description" in site:
        text_to_analyze += site["description"] + " "
    if "content" in site:
        text_to_analyze += site["content"]
    
    text_to_analyze = text_to_analyze.lower()
    
    # Check for category matches
    category_matches = {}
    
    for category, data in RISK_CATEGORIES.items():
        matches = 0
        for keyword in data["keywords"]:
            if keyword.lower() in text_to_analyze:
                matches += 1
        
        if matches > 0:
            category_matches[category] = matches
    
    # Determine primary category (the one with most matches)
    if category_matches:
        primary_category = max(category_matches.items(), key=lambda x: x[1])[0]
        return primary_category
    
    return category

def is_seller_profile(site):
    """Determine if a site is likely a seller profile"""
    seller_indicators = [
        "vendor", "seller", "shop", "store", "market", "price", "pricing", "cost",
        "shipping", "payment", "bitcoin", "btc", "monero", "xmr", "escrow", "buy",
        "purchase", "order", "checkout", "cart", "product", "listing", "feedback",
        "rating", "review", "trusted", "verified", "pgp", "contact"
    ]
    
    # Extract text to analyze
    text_to_analyze = ""
    if "title" in site:
        text_to_analyze += site["title"] + " "
    if "description" in site:
        text_to_analyze += site["description"] + " "
    if "content" in site:
        text_to_analyze += site["content"]
    
    text_to_analyze = text_to_analyze.lower()
    
    # Count seller indicators
    indicator_count = sum(1 for indicator in seller_indicators if indicator in text_to_analyze)
    
    # If more than 3 indicators are found, it's likely a seller
    return indicator_count >= 3

def filter_sites(sites, keywords=None, geo_location=None, date_range=None, 
                risk_threshold=None, seller_only=False, country=None, 
                state=None, district=None, category=None):
    """
    Filter sites based on multiple criteria
    """
    if not sites:
        return []
        
    # If no keywords provided, use default illegal keywords
    if not keywords:
        keywords = get_illegal_keywords()
    elif isinstance(keywords, str):
        # Convert comma-separated string to list
        keywords = [k.strip() for k in keywords.split(',')]
    
    # Get risk thresholds from environment
    low_risk = int(os.getenv('LOW_RISK_THRESHOLD', 30))
    medium_risk = int(os.getenv('MEDIUM_RISK_THRESHOLD', 60))
    high_risk = int(os.getenv('HIGH_RISK_THRESHOLD', 80))
    
    # Default risk threshold if not provided
    if risk_threshold is None:
        risk_threshold = low_risk
    
    filtered_sites = []
    
    for site in sites:
        # Skip if no URL (invalid site)
        if "url" not in site:
            continue
            
        # Calculate risk score if not already present
        if "risk_score" not in site or not isinstance(site["risk_score"], dict):
            content = site.get("content", site.get("description", ""))
            title = site.get("title", "")
            risk_data = calculate_risk_score(content, title)
            site["risk_score"] = risk_data["score"]
            site["risk_categories"] = risk_data["categories"]
        
        # Skip if below risk threshold
        if site["risk_score"] < risk_threshold:
            continue
        
        # Determine risk level
        if site["risk_score"] >= high_risk:
            site["risk_level"] = "high"
        elif site["risk_score"] >= medium_risk:
            site["risk_level"] = "medium"
        else:
            site["risk_level"] = "low"
        
        # Filter by keywords if provided
        if keywords and not any(keyword.lower() in (site.get("content", "") + " " + 
                                                  site.get("title", "") + " " + 
                                                  site.get("description", "")).lower() 
                              for keyword in keywords):
            continue
        
        # Filter by geo-location if provided
        if geo_location and "geo_location" in site and geo_location.lower() not in site["geo_location"].lower():
            continue
        
        # Filter by date range if provided
        if date_range and "date_detected" in site:
            try:
                site_date = datetime.datetime.fromisoformat(site["date_detected"].replace('Z', '+00:00'))
                start_date = datetime.datetime.fromisoformat(date_range[0])
                end_date = datetime.datetime.fromisoformat(date_range[1])
                
                if not (start_date <= site_date <= end_date):
                    continue
            except (ValueError, TypeError):
                # If date parsing fails, skip date filtering
                pass
        
        # Filter by seller only if requested
        if seller_only:
            is_seller = site.get("is_seller", False)
            if not is_seller:
                # If not already determined, check if it's a seller
                is_seller = is_seller_profile(site)
                site["is_seller"] = is_seller
            
            if not is_seller:
                continue
        
        # Filter by country if provided
        if country and "country" in site and country.lower() not in site["country"].lower():
            continue
        
        # Filter by state/region if provided
        if state and "state" in site and state.lower() not in site["state"].lower():
            continue
        
        # Filter by district/city if provided
        if district and "district" in site and district.lower() not in site["district"].lower():
            continue
        
        # Filter by category if provided
        if category:
            # Determine category if not already present
            if "category" not in site:
                site["category"] = categorize_site(site)
            
            if category.lower() != site["category"].lower():
                continue
        
        # Add site to filtered results
        filtered_sites.append(site)
    
    # Sort by risk score (highest first)
    filtered_sites.sort(key=lambda x: x["risk_score"], reverse=True)
    
    return filtered_sites

def load_and_filter_sites(file_path='sample_sites.json', keywords=None, risk_threshold=None):
    """
    Load sites from a JSON file and filter them
    """
    try:
        with open(file_path, 'r') as f:
            sites = json.load(f)
        
        if not keywords:
            keywords = get_illegal_keywords()
        
        filtered_sites = filter_sites(sites, keywords, risk_threshold=risk_threshold)
        return filtered_sites
    except Exception as e:
        logger.error(f"Error loading and filtering sites: {e}")
        return []

if __name__ == "__main__":
    # Example usage
    filtered_sites = load_and_filter_sites()
    print(f"Found {len(filtered_sites)} filtered sites:")
    
    for site in filtered_sites:
        print(f"URL: {site['url']}, Risk Score: {site['risk_score']}, Level: {site.get('risk_level', 'unknown')}")
        if 'risk_categories' in site:
            print(f"  Categories: {', '.join(site['risk_categories'].keys())}")
        print(f"  Is Seller: {site.get('is_seller', False)}")
        print()