import random

def calculate_risk_score(text, keywords=None):
    """Calculate risk score based on NLP-inspired keyword analysis"""
    if not text or not keywords:
        return 30  # Default low risk
    
    # Define risk categories
    high_risk_terms = ["arms", "murder", "drugs", "weapons", "hitman", "fentanyl", "heroin", "cocaine", "assassination"]
    medium_risk_terms = ["fraud", "hack", "counterfeit", "fake", "stolen", "illegal", "scam", "phishing"]
    low_risk_terms = ["forum", "chat", "anonymous", "privacy", "secure", "discussion", "community"]
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Check for high risk terms
    for term in high_risk_terms:
        if term in text_lower:
            return 90 + (10 * random.random())  # 90-100 range
    
    # Check for medium risk terms
    for term in medium_risk_terms:
        if term in text_lower:
            return 60 + (30 * random.random())  # 60-90 range
    
    # Check for low risk terms
    for term in low_risk_terms:
        if term in text_lower:
            return 30 + (30 * random.random())  # 30-60 range
    
    # Default score
    return 10 + (20 * random.random())  # 10-30 range

def detect_country_from_keywords(keywords):
    """Estimate country origin from keywords"""
    keyword_country_map = {
        "ak47": "Russia",
        "vodka": "Russia",
        "fentanyl": "Mexico",
        "cocaine": "Colombia",
        "maple": "Canada",
        "kangaroo": "Australia",
        "tea": "United Kingdom"
    }
    
    if not keywords:
        return None
    
    keywords_lower = keywords.lower()
    
    for keyword, country in keyword_country_map.items():
        if keyword in keywords_lower:
            return country
    
    return None

def detect_seller(text):
    """Detect if the page is from a seller based on text content"""
    seller_indicators = ["sell", "price", "shipping", "vendor", "shop", "store", "payment", "bitcoin", "btc", "monero", "xmr"]
    
    if not text:
        return False
    
    text_lower = text.lower()
    
    for indicator in seller_indicators:
        if indicator in text_lower:
            return True
    
    return False

def filter_data(crawled_data, keywords=None, geo_location=None, date_range=None, risk_threshold=None, 
             seller_only=False, country=None, state=None, district=None, category=None):
    """Filter and enrich crawled data based on given criteria
    
    Parameters:
    - crawled_data: List of dictionaries containing crawled data
    - keywords: Comma-separated string of keywords to filter by
    - geo_location: General location to filter by
    - date_range: Tuple of (start_date, end_date) in 'YYYY-MM-DD' format
    - risk_threshold: Minimum risk score to include (0-100)
    - seller_only: If True, only include results from sellers
    - country: Specific country to filter by
    - state: Specific state/region to filter by
    - district: Specific district/city to filter by
    - category: Category of content to filter by (e.g., 'drugs', 'weapons', 'data')
    
    Returns:
    - Filtered and enriched list of dictionaries
    """
    if not crawled_data:
        return []
    
    # First, enrich the data if needed
    if 'risk_score' not in crawled_data[0]:
        enriched_data = []
        
        for site_data in crawled_data:
            # Calculate risk score based on title and description
            combined_text = f"{site_data.get('title', '')} {site_data.get('description', '')}"
            risk_score = calculate_risk_score(combined_text, keywords)
            
            # Detect country if not already present
            detected_country = site_data.get('country')
            if not detected_country and keywords:
                detected_country = detect_country_from_keywords(keywords)
            
            # Detect if it's a seller
            is_seller = site_data.get('is_seller', detect_seller(combined_text))
            
            # Detect category if not already present
            detected_category = site_data.get('category')
            if not detected_category:
                detected_category = detect_category(combined_text)
            
            # Extract location details
            location_details = extract_location_details(site_data.get('description', ''), detected_country)
            
            # Enrich the data
            enriched_site_data = site_data.copy()
            enriched_site_data['risk_score'] = risk_score
            if detected_country:
                enriched_site_data['country'] = detected_country
            enriched_site_data['is_seller'] = is_seller
            if detected_category:
                enriched_site_data['category'] = detected_category
            
            # Add location details
            if location_details.get('state'):
                enriched_site_data['state'] = location_details['state']
            if location_details.get('district'):
                enriched_site_data['district'] = location_details['district']
            
            enriched_data.append(enriched_site_data)
        
        # Use the enriched data for filtering
        data_to_filter = enriched_data
    else:
        # Use the original data for filtering
        data_to_filter = crawled_data
    
    # Now apply all the filters
    filtered_data = []
    
    for site_data in data_to_filter:
        # Check if the item passes all filters
        include_item = True
        
        # Filter by keywords
        if keywords and include_item:
            keyword_match = False
            for keyword in keywords.split(','):
                keyword = keyword.strip().lower()
                if keyword in site_data.get('title', '').lower() or keyword in site_data.get('description', '').lower():
                    keyword_match = True
                    break
            include_item = keyword_match
        
        # Filter by geo-location
        if geo_location and include_item:
            geo_match = geo_location.lower() in site_data.get('description', '').lower()
            if 'country' in site_data:
                geo_match = geo_match or geo_location.lower() in site_data['country'].lower()
            include_item = geo_match
        
        # Filter by date range
        if date_range and include_item and 'date_detected' in site_data:
            from datetime import datetime
            start_date, end_date = date_range
            item_date = datetime.strptime(site_data['date_detected'], '%Y-%m-%d')
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            include_item = start <= item_date <= end
        
        # Filter by risk threshold
        if risk_threshold is not None and include_item and 'risk_score' in site_data:
            include_item = site_data['risk_score'] >= risk_threshold
        
        # Filter by seller only
        if seller_only and include_item and 'is_seller' in site_data:
            include_item = site_data['is_seller']
        
        # Filter by country
        if country and include_item and 'country' in site_data:
            include_item = country.lower() in site_data['country'].lower()
        
        # Filter by state
        if state and include_item and 'state' in site_data:
            include_item = state.lower() in site_data['state'].lower()
        
        # Filter by district
        if district and include_item and 'district' in site_data:
            include_item = district.lower() in site_data['district'].lower()
        
        # Filter by category
        if category and include_item and 'category' in site_data:
            include_item = category.lower() == site_data['category'].lower()
        
        # If the item passes all filters, include it
        if include_item:
            filtered_data.append(site_data)
    
    return filtered_data if filtered_data else data_to_filter  # Return all data if no filters match

def detect_category(text):
    """Detect the category of content based on text"""
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Define category keywords
    categories = {
        'drugs': ['drug', 'cocaine', 'heroin', 'mdma', 'ecstasy', 'lsd', 'marijuana', 'cannabis', 'weed', 'pills', 'pharmacy'],
        'weapons': ['weapon', 'gun', 'rifle', 'pistol', 'ammunition', 'firearm', 'explosive', 'knife', 'tactical'],
        'hacking': ['hack', 'exploit', 'vulnerability', 'malware', 'ransomware', 'ddos', 'phishing', 'botnet'],
        'counterfeit': ['counterfeit', 'fake', 'replica', 'clone', 'copy', 'forgery', 'document', 'passport', 'id card'],
        'financial': ['credit card', 'bank account', 'paypal', 'bitcoin', 'cryptocurrency', 'money laundering', 'finance'],
        'data': ['data', 'database', 'breach', 'leak', 'personal information', 'identity', 'account', 'password'],
        'services': ['service', 'hire', 'rent', 'contract', 'hitman', 'hacker', 'escort']
    }
    
    # Check each category
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in text_lower:
                return category
    
    return 'other'

def extract_location_details(text, country=None):
    """Extract state and district information from text"""
    if not text:
        return {}
    
    # This is a simplified implementation
    # In a real app, you would use NLP or a location database
    
    # Define some common states/regions and districts/cities
    location_data = {
        'USA': {
            'states': {
                'California': ['Los Angeles', 'San Francisco', 'San Diego', 'Sacramento'],
                'New York': ['New York City', 'Buffalo', 'Albany', 'Rochester'],
                'Texas': ['Austin', 'Houston', 'Dallas', 'San Antonio'],
                'Florida': ['Miami', 'Orlando', 'Tampa', 'Jacksonville']
            }
        },
        'Russia': {
            'states': {
                'Moscow Oblast': ['Moscow', 'Khimki', 'Podolsk'],
                'Saint Petersburg': ['Saint Petersburg', 'Pushkin', 'Peterhof']
            }
        },
        'Germany': {
            'states': {
                'Bavaria': ['Munich', 'Nuremberg', 'Augsburg'],
                'Berlin': ['Berlin'],
                'North Rhine-Westphalia': ['Cologne', 'Düsseldorf', 'Dortmund']
            }
        }
    }
    
    result = {}
    text_lower = text.lower()
    
    # If country is provided, only check that country's locations
    if country and country in location_data:
        for state, cities in location_data[country]['states'].items():
            if state.lower() in text_lower:
                result['state'] = state
                
                # Check for cities in this state
                for city in cities:
                    if city.lower() in text_lower:
                        result['district'] = city
                        break
    else:
        # Check all countries
        for country_name, country_info in location_data.items():
            for state, cities in country_info['states'].items():
                if state.lower() in text_lower:
                    result['state'] = state
                    result['country'] = country_name
                    
                    # Check for cities in this state
                    for city in cities:
                        if city.lower() in text_lower:
                            result['district'] = city
                            break
                    
                    if 'district' in result:
                        break
            
            if 'state' in result:
                break
    
    return result
