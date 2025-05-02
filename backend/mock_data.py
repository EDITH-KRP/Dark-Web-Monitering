"""
Mock data generator for testing the Dark Web Monitoring Tool
"""
import random
import datetime
import json
import os

def generate_mock_data(num_items=10, keywords=None):
    """Generate mock data for testing"""
    if keywords is None:
        keywords = ["drugs", "bitcoin", "weapons", "hacking"]
    
    # Sample onion URLs
    onion_domains = [
        "darkfailllnkf4vf.onion",
        "jaz45aabn5vkemy4jkg4mi4syheisqn2wn2n4fsuitpccdackjwxplad.onion",
        "zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otjiycgwqbym2qad.onion",
        "s4k4ceiapwwgcm3mkb6e4diqecpo7kvdnfr5gg7sph7jjppqkvwwqtyd.onion",
        "juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion",
        "rambleeeo4vhxgorpmgunoo276nkiw7bos74cg7tjlgnb3puj3d7ghad.onion",
        "darknetlidvrsli6iso7my54rjayjursyw6gu6kqwpisd3s5mziyerad.onion",
        "darkzzx4avcsuofgfez5zq75cqc4mprjvfqywo45dfcaxrwqg6qrlfid.onion"
    ]
    
    # Sample titles
    titles = [
        "Illegal Marketplace - Buy Drugs, Weapons, and More",
        "Hacking Services - Professional Hackers for Hire",
        "Counterfeit Documents - Passports, IDs, Credit Cards",
        "Bitcoin Mixer - Anonymize Your Cryptocurrency",
        "Stolen Data - Credit Cards, Bank Accounts, Personal Info",
        "Weapons Store - Firearms, Ammunition, Explosives",
        "Drug Marketplace - Premium Quality Products",
        "Hacking Tools - Exploits, Malware, Ransomware",
        "Fake IDs - High Quality Counterfeit Documents",
        "Stolen Accounts - Netflix, Spotify, PayPal, and More"
    ]
    
    # Sample descriptions
    descriptions = [
        "The largest marketplace for illegal goods on the dark web. Buy drugs, weapons, and more with Bitcoin.",
        "Professional hackers for hire. We can hack any website, social media account, or email.",
        "High quality counterfeit documents including passports, IDs, and credit cards.",
        "Anonymize your Bitcoin transactions with our secure mixing service.",
        "Fresh stolen data including credit cards, bank accounts, and personal information.",
        "Wide selection of firearms, ammunition, and explosives shipped worldwide.",
        "Premium quality drugs shipped discreetly worldwide. Bitcoin accepted.",
        "Advanced hacking tools including exploits, malware, and ransomware.",
        "Perfect fake IDs that pass all security checks. Fast shipping worldwide.",
        "Stolen accounts for Netflix, Spotify, PayPal, and more at low prices."
    ]
    
    # Sample countries
    countries = [
        "USA", "Russia", "Mexico", "Colombia", "Canada", "Australia", 
        "United Kingdom", "Germany", "Netherlands", "China", "Japan", 
        "Brazil", "Sweden", "Switzerland", "Panama", "Romania"
    ]
    
    # Generate mock data
    mock_data = []
    
    for i in range(num_items):
        # Generate random date within the last 30 days
        days_ago = random.randint(0, 30)
        date_detected = (datetime.datetime.now() - datetime.timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        # Generate random risk score
        risk_score = random.randint(30, 95)
        
        # Generate random URL
        domain = random.choice(onion_domains)
        path = random.choice(["", "/market", "/products", "/services", "/forum", "/board", "/index.php"])
        url = f"http://{domain}{path}"
        
        # Generate random title and description
        title = random.choice(titles)
        description = random.choice(descriptions)
        
        # Generate random country
        country = random.choice(countries)
        
        # Generate random seller status
        is_seller = random.choice([True, False])
        
        # Create mock item
        mock_item = {
            "url": url,
            "title": title,
            "description": description,
            "content_sample": description[:100] + "...",
            "risk_score": risk_score,
            "country": country,
            "is_seller": is_seller,
            "date_detected": date_detected,
            "archive_link": f"https://web.archive.org/web/{url}",
            "found_keywords": [keyword for keyword in keywords if keyword.lower() in (title + description).lower()]
        }
        
        mock_data.append(mock_item)
    
    return mock_data

def save_mock_data(num_items=10, keywords=None, filename="mock_crawl_data.json"):
    """Generate and save mock data to a file"""
    mock_data = generate_mock_data(num_items, keywords)
    
    # Create directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(__file__), 'data_storage')
    os.makedirs(data_dir, exist_ok=True)
    
    # Save to file
    file_path = os.path.join(data_dir, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(mock_data, f, indent=2)
    
    print(f"Saved {len(mock_data)} mock items to {file_path}")
    return file_path

if __name__ == "__main__":
    # Generate and save mock data
    save_mock_data(20, ["drugs", "bitcoin", "weapons", "hacking"])