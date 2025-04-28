from flask import Flask, jsonify, request
from crawler import start_crawl
from vpn_connect import connect_vpn
from utils import get_ip_details
from dark_web_filters import filter_data
from web_archive import fetch_archive

app = Flask(__name__)


connect_vpn()

@app.route('/')
def home():
    return "Dark Web Monitoring Crawler API is running!"

@app.route('/crawl', methods=['GET'])
def crawl_dark_web():
    """Crawl Dark Web and return data"""
    
    keywords = request.args.get('keywords', '')
    geo_location = request.args.get('geo_location', '')

   
    crawled_data = start_crawl(keywords=keywords, geo_location=geo_location)

    
    filtered_data = filter_data(crawled_data, keywords, geo_location)

    return jsonify(filtered_data), 200

@app.route('/ip-details', methods=['GET'])
def ip_details():
    """Fetch IP details of a Dark Web site"""
    site_url = request.args.get('url', '')
    if not site_url:
        return jsonify({"error": "URL is required"}), 400

    ip_info = get_ip_details(site_url)
    return jsonify(ip_info), 200

@app.route('/web-archive', methods=['GET'])
def web_archive():
    """Fetch archived version of a site"""
    site_url = request.args.get('url', '')
    if not site_url:
        return jsonify({"error": "URL is required"}), 400

    archive_data = fetch_archive(site_url)
    return jsonify(archive_data), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
