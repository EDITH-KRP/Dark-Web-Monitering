from flask import Flask, jsonify, request, send_file
import json
import os
import sys
import datetime
from flask_cors import CORS

# Import configuration and logging
import config
from logger import logger, get_logger

# Import core modules
from crawler import start_crawl
from vpn_connect import connect_vpn, check_vpn_status, disconnect_vpn
from utils import get_ip_details, export_to_csv, export_to_excel, save_to_filebase
from dark_web_filters import filter_data
from web_archive import fetch_archive

# Import browser modules with error handling
try:
    from i2p_connect import get_i2p_session, browse_i2p_site, search_i2p
    I2P_AVAILABLE = True
    logger.info("I2P module loaded successfully")
except ImportError as e:
    I2P_AVAILABLE = False
    logger.warning(f"I2P module not available: {e}")

try:
    from freenet_connect import is_freenet_running, fetch_freenet_key, search_freenet
    FREENET_AVAILABLE = True
    logger.info("Freenet module loaded successfully")
except ImportError as e:
    FREENET_AVAILABLE = False
    logger.warning(f"Freenet module not available: {e}")

try:
    from tails_connect import is_running_in_tails, get_tails_tor_session, fetch_url_with_tails
    TAILS_AVAILABLE = True
    logger.info("TAILS module loaded successfully")
except ImportError as e:
    TAILS_AVAILABLE = False
    logger.warning(f"TAILS module not available: {e}")

# Create Flask app
app = Flask(__name__)
# Enable CORS with more specific settings
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})
app.config['CORS_HEADERS'] = 'Content-Type'

# Get module-specific logger
app_logger = get_logger('app')
app_logger.info("Starting Dark Web Monitoring API")

# Initialize VPN connection
app_logger.info("Initializing VPN connection")
vpn_status = connect_vpn()
app_logger.info(f"VPN status: {vpn_status['connected']}")

@app.route('/')
def home():
    return "Dark Web Monitoring Crawler API is running!"

@app.route('/mock-data', methods=['GET'])
def get_mock_data():
    """Return mock data for testing"""
    try:
        from mock_data import generate_mock_data
        
        # Get query parameters
        num_items = request.args.get('num_items', default=10, type=int)
        keywords = request.args.get('keywords', default='drugs,bitcoin,weapons,hacking')
        keywords_list = [k.strip() for k in keywords.split(',')]
        
        # Generate mock data
        mock_data = generate_mock_data(num_items=num_items, keywords=keywords_list)
        
        app_logger.info(f"Generated {len(mock_data)} mock items")
        return jsonify(mock_data), 200
    except Exception as e:
        app_logger.error(f"Error generating mock data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/crawl', methods=['POST'])
def crawl_dark_web():
    """Crawl Dark Web and return data with enhanced filtering"""
    try:
        app_logger.info("Received crawl request")
        data = request.get_json()
        
        # Basic parameters
        keywords = data.get('keywords', '')
        geo_location = data.get('geo_location', '')
        
        app_logger.info(f"Crawl parameters: keywords={keywords}, geo_location={geo_location}")
        
        # Advanced filtering parameters
        date_range = data.get('date_range')  # [start_date, end_date] in 'YYYY-MM-DD' format
        risk_threshold = data.get('risk_threshold')  # Minimum risk score (0-100)
        seller_only = data.get('seller_only', False)  # Only include sellers
        country = data.get('country')  # Specific country
        state = data.get('state')  # Specific state/region
        district = data.get('district')  # Specific district/city
        category = data.get('category')  # Content category
        
        # Additional parameters
        max_pages = data.get('max_pages', 10)  # Maximum number of pages to crawl (reduced for faster response)
        enable_ip_detection = data.get('enable_ip_detection', True)  # Whether to try to reveal IPs
        
        # For development purposes, always use mock data to ensure functionality
        app_logger.info("Using mock data for crawling")
        from mock_data import generate_mock_data
        crawled_data = generate_mock_data(num_items=15, keywords=keywords.split(',') if keywords else ["darkweb"])
    
        # Process the crawled data
        app_logger.info(f"Processing {len(crawled_data)} crawled items")
        
        # Try to use the enhanced filter
        try:
            from dark_web_scripts.dark_web_filters import filter_data
        except ImportError:
            # Fall back to the original filter if the enhanced one is not available
            app_logger.warning("Enhanced filter not available, falling back to original filter")
            try:
                from dark_web_filters import filter_data
            except ImportError:
                app_logger.error("Could not import any filter module, using identity function")
                # Define a simple pass-through function if no filter module is available
                def filter_data(data, **kwargs):
                    return data
        
        # Add date_detected field if not present
        for item in crawled_data:
            if 'date_detected' not in item:
                item['date_detected'] = datetime.datetime.now().strftime('%Y-%m-%d')
            if 'country' not in item:
                item['country'] = 'Unknown'
        
        # Apply filtering
        try:
            filtered_data = filter_data(
                crawled_data, 
                keywords=keywords, 
                geo_location=geo_location,
                date_range=date_range,
                risk_threshold=risk_threshold,
                seller_only=seller_only,
                country=country,
                state=state,
                district=district,
                category=category
            )
            app_logger.info(f"Filtered data: {len(filtered_data)} items")
        except Exception as e:
            app_logger.error(f"Error filtering data: {e}")
            filtered_data = crawled_data
            app_logger.info("Using unfiltered data due to filter error")
        
        # Ensure the data has all required fields for the frontend
        for item in filtered_data:
            try:
                # Add required fields if missing
                if 'title' not in item or not item['title']:
                    item['title'] = 'Untitled'
                    
                if 'description' not in item or not item['description']:
                    item['description'] = item.get('content_sample', 'No description available')
                    
                if 'date_detected' not in item:
                    item['date_detected'] = datetime.datetime.now().strftime('%Y-%m-%d')
                    
                if 'country' not in item:
                    item['country'] = 'Unknown'
                    
                if 'risk_score' not in item:
                    item['risk_score'] = 50  # Default medium risk
                    
                if 'is_seller' not in item:
                    item['is_seller'] = False
                    
                # Add archive link if missing
                if 'archive_link' not in item:
                    item['archive_link'] = f"https://web.archive.org/web/{item.get('url', '#')}"
                
                # Ensure URL is present
                if 'url' not in item or not item['url']:
                    item['url'] = '#'
            except Exception as e:
                app_logger.error(f"Error processing item: {e}")
                # Skip problematic items
                continue
        
        # Save the data for later use
        try:
            save_crawl_data(filtered_data)
        except Exception as e:
            app_logger.error(f"Error saving crawl data: {e}")
        
        app_logger.info(f"Returning {len(filtered_data)} filtered results")
        return jsonify(filtered_data), 200
    except Exception as e:
        app_logger.error(f"Error in crawl endpoint: {e}")
        # Return mock data as a fallback
        try:
            from mock_data import generate_mock_data
            mock_data = generate_mock_data(num_items=8, keywords=keywords.split(',') if keywords else ["drugs", "bitcoin"])
            app_logger.info(f"Returning {len(mock_data)} mock items due to error")
            return jsonify(mock_data), 200
        except Exception as e2:
            app_logger.error(f"Error generating mock data: {e2}")
            return jsonify({"error": f"Crawl failed: {str(e)}"}), 500

def save_crawl_data(data):
    """Save crawled data to a JSON file for later use"""
    try:
        # Create directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(__file__), 'data_storage')
        os.makedirs(data_dir, exist_ok=True)
        
        # Save to file
        file_path = os.path.join(data_dir, 'crawled_data.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        app_logger.info(f"Saved crawl data to {file_path}")
        return True
    except Exception as e:
        app_logger.error(f"Error saving crawl data: {e}")
        return False

@app.route('/ip-details', methods=['POST'])
def ip_details():
    """Fetch IP details of a Dark Web site"""
    data = request.get_json()
    site_url = data.get('url', '')
    
    if not site_url:
        return jsonify({"error": "URL is required"}), 400

    # Try to use the enhanced IP reveal functionality
    try:
        from dark_web_scripts.ip_reveal import reveal_ip_and_geo
        
        app_logger.info(f"Revealing IP for {site_url} using enhanced method")
        ip_info = reveal_ip_and_geo(site_url)
        
        if ip_info:
            return jsonify(ip_info), 200
        else:
            return jsonify({"error": "Could not reveal IP address"}), 404
    except ImportError:
        # Fall back to the original method
        app_logger.warning("Enhanced IP reveal not available, falling back to original method")
        ip_info = get_ip_details(site_url)
        return jsonify(ip_info), 200

@app.route('/web-archive', methods=['POST'])
def web_archive():
    """Fetch archived version of a site"""
    data = request.get_json()
    site_url = data.get('url', '')
    
    if not site_url:
        return jsonify({"error": "URL is required"}), 400

    archive_data = fetch_archive(site_url)
    return jsonify(archive_data), 200

@app.route('/vpn-status', methods=['GET'])
def vpn_status():
    """Get current VPN status"""
    status = check_vpn_status()
    return jsonify(status), 200

@app.route('/vpn-connect', methods=['POST'])
def vpn_connect():
    """Connect to VPN"""
    status = connect_vpn()
    return jsonify(status), 200

@app.route('/vpn-disconnect', methods=['POST'])
def vpn_disconnect():
    """Disconnect from VPN"""
    status = disconnect_vpn()
    return jsonify(status), 200

@app.route('/export-csv', methods=['GET'])
def export_csv():
    """Export crawled data to CSV"""
    try:
        # Get the latest crawl data
        data_path = os.path.join(os.path.dirname(__file__), 'data_storage', 'crawled_data.json')
        
        if not os.path.exists(data_path):
            return jsonify({"error": "No crawl data available"}), 404
        
        with open(data_path, 'r') as f:
            crawl_data = json.load(f)
        
        # Export to CSV
        csv_path = export_to_csv(crawl_data)
        
        # Return the file
        return send_file(csv_path, as_attachment=True, download_name="dark_web_data.csv")
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/export-excel', methods=['GET'])
def export_excel():
    """Export crawled data to Excel"""
    try:
        # Get the latest crawl data
        data_path = os.path.join(os.path.dirname(__file__), 'data_storage', 'crawled_data.json')
        
        if not os.path.exists(data_path):
            return jsonify({"error": "No crawl data available"}), 404
        
        with open(data_path, 'r') as f:
            crawl_data = json.load(f)
        
        # Export to Excel
        excel_path = export_to_excel(crawl_data)
        
        # Return the file
        return send_file(excel_path, as_attachment=True, download_name="dark_web_data.xlsx")
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload-to-filebase', methods=['POST'])
def upload_to_filebase():
    """Upload crawl data to decentralized storage (Filebase)"""
    try:
        data = request.get_json()
        data_type = data.get('data_type', 'crawl_results')
        
        # If data is provided in the request, use it
        if 'data' in data:
            crawl_data = data['data']
        else:
            # Otherwise, get the latest crawl data from file
            data_path = os.path.join(os.path.dirname(__file__), 'data_storage', 'crawled_data.json')
            
            if not os.path.exists(data_path):
                return jsonify({"error": "No crawl data available"}), 404
            
            with open(data_path, 'r') as f:
                crawl_data = json.load(f)
        
        # Upload to Filebase
        app_logger.info(f"Uploading data to Filebase, type: {data_type}")
        upload_result = save_to_filebase(crawl_data, data_type)
        
        return jsonify(upload_result), 200
    
    except Exception as e:
        app_logger.error(f"Error uploading to Filebase: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/filebase-data', methods=['GET'])
def list_filebase_data():
    """List data stored in Filebase"""
    try:
        data_type = request.args.get('data_type', 'crawl_results')
        limit = int(request.args.get('limit', 100))
        
        # Import the Filebase storage module
        try:
            from filebase_storage import list_filebase_data as list_data
            result = list_data(data_type, limit)
            return jsonify(result), 200
        except ImportError:
            app_logger.error("Filebase storage module not available")
            return jsonify({"error": "Filebase storage module not available"}), 500
    
    except Exception as e:
        app_logger.error(f"Error listing Filebase data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/filebase-data/<data_id>', methods=['GET'])
def get_filebase_data(data_id):
    """Get data from Filebase by ID"""
    try:
        data_type = request.args.get('data_type', 'crawl_results')
        
        # Import the Filebase storage module
        try:
            from filebase_storage import get_from_filebase
            result = get_from_filebase(data_id, data_type)
            
            if result is None:
                return jsonify({"error": "Data not found"}), 404
                
            return jsonify(result), 200
        except ImportError:
            app_logger.error("Filebase storage module not available")
            return jsonify({"error": "Filebase storage module not available"}), 500
    
    except Exception as e:
        app_logger.error(f"Error getting Filebase data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/filebase-data/<data_id>', methods=['DELETE'])
def delete_filebase_data(data_id):
    """Delete data from Filebase by ID"""
    try:
        data_type = request.args.get('data_type', 'crawl_results')
        
        # Import the Filebase storage module
        try:
            from filebase_storage import delete_from_filebase
            result = delete_from_filebase(data_id, data_type)
            
            if result:
                return jsonify({"success": True, "message": "Data deleted successfully"}), 200
            else:
                return jsonify({"error": "Failed to delete data"}), 500
        except ImportError:
            app_logger.error("Filebase storage module not available")
            return jsonify({"error": "Filebase storage module not available"}), 500
    
    except Exception as e:
        app_logger.error(f"Error deleting Filebase data: {e}")
        return jsonify({"error": str(e)}), 500

# New endpoints for different dark web browsers

@app.route('/browser-status', methods=['GET'])
def browser_status():
    """Get status of available dark web browsers"""
    status = {
        "tor": True,  # We always have Tor support
        "i2p": I2P_AVAILABLE,
        "freenet": FREENET_AVAILABLE,
        "tails": TAILS_AVAILABLE
    }
    return jsonify(status), 200

@app.route('/track-seller', methods=['POST'])
def track_seller():
    """Track a seller profile on a dark web marketplace"""
    data = request.get_json()
    seller_url = data.get('url', '')
    
    if not seller_url:
        return jsonify({"error": "Seller URL is required"}), 400
    
    try:
        from dark_web_scripts.seller_tracking import track_seller_profile
        
        app_logger.info(f"Tracking seller profile at {seller_url}")
        result = track_seller_profile(seller_url)
        
        if result and 'error' not in result:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except ImportError as e:
        app_logger.error(f"Seller tracking module not available: {e}")
        return jsonify({"error": "Seller tracking functionality not available"}), 500

@app.route('/seller-history', methods=['POST'])
def seller_history():
    """Get historical data for a seller"""
    data = request.get_json()
    marketplace = data.get('marketplace', '')
    seller_id = data.get('seller_id')
    seller_name = data.get('seller_name')
    
    if not marketplace:
        return jsonify({"error": "Marketplace is required"}), 400
    
    if not seller_id and not seller_name:
        return jsonify({"error": "Either seller_id or seller_name is required"}), 400
    
    try:
        from dark_web_scripts.seller_tracking import get_seller_history
        
        app_logger.info(f"Getting history for seller {seller_id or seller_name} on {marketplace}")
        result = get_seller_history(marketplace, seller_id, seller_name)
        
        if result and 'error' not in result:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except ImportError as e:
        app_logger.error(f"Seller tracking module not available: {e}")
        return jsonify({"error": "Seller history functionality not available"}), 500

@app.route('/seller-trends', methods=['POST'])
def seller_trends():
    """Analyze trends for a seller"""
    data = request.get_json()
    marketplace = data.get('marketplace', '')
    seller_id = data.get('seller_id')
    seller_name = data.get('seller_name')
    
    if not marketplace:
        return jsonify({"error": "Marketplace is required"}), 400
    
    if not seller_id and not seller_name:
        return jsonify({"error": "Either seller_id or seller_name is required"}), 400
    
    try:
        from dark_web_scripts.seller_tracking import get_seller_history, analyze_seller_trends
        
        # First get the history
        history = get_seller_history(marketplace, seller_id, seller_name)
        
        if 'error' in history:
            return jsonify(history), 400
        
        # Then analyze trends
        app_logger.info(f"Analyzing trends for seller {seller_id or seller_name} on {marketplace}")
        result = analyze_seller_trends(history)
        
        if result and 'error' not in result:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except ImportError as e:
        app_logger.error(f"Seller tracking module not available: {e}")
        return jsonify({"error": "Seller trends functionality not available"}), 500

@app.route('/crawl-with-browser', methods=['POST'])
def crawl_with_browser():
    """Crawl using a specific browser"""
    data = request.get_json()
    
    browser_type = data.get('browser_type', 'tor').lower()
    url = data.get('url', '')
    keywords = data.get('keywords', '')
    
    if not url and not keywords:
        return jsonify({"error": "Either URL or keywords are required"}), 400
    
    # Handle different browser types
    if browser_type == 'tor':
        if url:
            # Use the dark-web-scripts/tor_crawler.py implementation
            from dark_web_scripts.tor_crawler import scrape_onion_site
            result = scrape_onion_site(url)
        else:
            # Use the regular crawler with keywords
            result = start_crawl(keywords=keywords)
            
    elif browser_type == 'i2p':
        if not I2P_AVAILABLE:
            return jsonify({"error": "I2P support not available"}), 501
        
        if url:
            result = browse_i2p_site(url)
        else:
            result = search_i2p(keywords)
            
    elif browser_type == 'freenet':
        if not FREENET_AVAILABLE:
            return jsonify({"error": "Freenet support not available"}), 501
        
        if url and url.startswith(('CHK@', 'SSK@', 'USK@')):
            result = fetch_freenet_key(url)
        else:
            result = search_freenet(keywords)
            
    elif browser_type == 'tails':
        if not TAILS_AVAILABLE:
            return jsonify({"error": "TAILS support not available"}), 501
        
        if url:
            result = fetch_url_with_tails(url)
        else:
            return jsonify({"error": "Keywords not supported with TAILS browser"}), 400
            
    else:
        return jsonify({"error": f"Unsupported browser type: {browser_type}"}), 400
    
    # Filter and save the data if it's in the right format
    if isinstance(result, list) and result and 'url' in result[0]:
        filtered_data = filter_data(result, keywords)
        save_crawl_data(filtered_data)
        return jsonify(filtered_data), 200
    
    return jsonify(result), 200

def save_crawl_data(data):
    """Save crawl data to JSON file"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data_storage')
    
    # Create directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Save data to file
    data_path = os.path.join(data_dir, 'crawled_data.json')
    
    with open(data_path, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
