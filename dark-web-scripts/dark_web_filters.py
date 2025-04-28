import json


def filter_sites(sites, keywords, risk_threshold=5):
    filtered_sites = []
    
    for site in sites:
        
        if any(keyword.lower() in site["description"].lower() for keyword in keywords):
            
            risk_score = sum(1 for keyword in keywords if keyword.lower() in site["description"].lower())
            
            if risk_score >= risk_threshold:
                site["risk_score"] = risk_score
                filtered_sites.append(site)

    return filtered_sites


def load_and_filter_sites():
    
    with open('sample_sites.json', 'r') as f:
        sites = json.load(f)

    keywords = ["drugs", "murder", "arms", "illicit"]
    risk_threshold = 3

    filtered_sites = filter_sites(sites, keywords, risk_threshold)
    return filtered_sites

if __name__ == "__main__":
    filtered_sites = load_and_filter_sites()
    print("Filtered Sites:")
    for site in filtered_sites:
        print(f"URL: {site['url']}, Risk Score: {site['risk_score']}")
