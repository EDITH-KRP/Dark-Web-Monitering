def filter_data(crawled_data, keywords=None, geo_location=None):
    """Filter crawled data based on given criteria"""
    filtered_data = []

    for site_data in crawled_data:
      
        if keywords and any(keyword.lower() in site_data['description'].lower() for keyword in keywords.split(',')):
            filtered_data.append(site_data)

        
        if geo_location and geo_location.lower() in site_data['description'].lower():
            filtered_data.append(site_data)

    return filtered_data
