import geoip2.database
import random
import os
import csv
import pandas as pd
import uuid
import time
import json

# Simulated GeoIP database path
GEOIP2_DATABASE = '/path/to/GeoLite2-City.mmdb'

def get_ip_details(site_url):
    """Fetch the IP details of a Dark Web site using real tools"""
    import socket
    import subprocess
    import re
    import json
    import requests
    import platform
    import os
    import time
    from urllib.parse import urlparse
    
    # Extract domain from URL
    parsed_url = urlparse(site_url)
    domain = parsed_url.netloc
    
    # If no domain was extracted, try to parse the URL differently
    if not domain:
        if '://' not in site_url:
            # Add http:// if missing
            site_url = 'http://' + site_url
            parsed_url = urlparse(site_url)
            domain = parsed_url.netloc
        else:
            # Try to extract domain from the full URL
            domain = site_url.split('://', 1)[1].split('/', 1)[0]
    
    print(f"Resolving domain: {domain}")
    
    # If it's an onion address, we need to use Tor to resolve it
    if domain.endswith('.onion'):
        print("Detected .onion address, using Tor for resolution")
        
        # Method 1: Use torsocks to resolve the onion address
        try:
            system = platform.system()
            
            if system == "Windows":
                # On Windows, check if torsocks is available
                torsocks_check = subprocess.run(["where", "torsocks"], 
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.PIPE,
                                              text=True)
                torsocks_available = torsocks_check.returncode == 0
            else:
                # On Linux/macOS, check if torsocks is available
                torsocks_check = subprocess.run(["which", "torsocks"], 
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.PIPE,
                                              text=True)
                torsocks_available = torsocks_check.returncode == 0
            
            if torsocks_available:
                print("Using torsocks to resolve onion address")
                cmd = ["torsocks", "host", domain]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                # Extract IP from the output
                ip_match = re.search(r'has address (\d+\.\d+\.\d+\.\d+)', result.stdout)
                
                if ip_match:
                    ip_address = ip_match.group(1)
                    print(f"Resolved to IP: {ip_address}")
                else:
                    print("Could not resolve onion address using torsocks")
                    raise Exception("No IP address found in torsocks output")
            else:
                print("torsocks not available, trying alternative methods")
                raise Exception("torsocks not available")
                
        except Exception as e:
            print(f"torsocks method failed: {e}")
            
            # Method 2: Try to use Tor's control port to get info about the hidden service
            try:
                from stem.control import Controller
                
                print("Trying to use Tor control port to get hidden service info")
                
                # Try different control ports
                control_ports = [9051, 9151]
                controller = None
                
                for port in control_ports:
                    try:
                        controller = Controller.from_port(port=port)
                        break
                    except:
                        continue
                
                if controller:
                    try:
                        # Try to authenticate with empty password
                        controller.authenticate()
                    except:
                        try:
                            # Try cookie authentication
                            controller.authenticate(cookie_auth=True)
                        except:
                            # If all else fails, we can't use the controller
                            controller = None
                
                if controller:
                    # Try to get info about the hidden service
                    try:
                        # This might not work depending on Tor configuration
                        hs_desc = controller.get_hidden_service_descriptor(domain.replace('.onion', ''))
                        introduction_points = hs_desc.introduction_points()
                        
                        # Return information about the hidden service
                        return {
                            'domain': domain,
                            'status': 'hidden_service_info',
                            'message': 'Retrieved hidden service information',
                            'is_tor': True,
                            'is_proxy': True,
                            'is_datacenter': False,
                            'introduction_points': len(introduction_points),
                            'hidden_service_version': hs_desc.version,
                            'last_modified': hs_desc.published.strftime('%Y-%m-%d %H:%M:%S') if hs_desc.published else 'Unknown'
                        }
                    except Exception as hs_e:
                        print(f"Could not get hidden service info: {hs_e}")
                        # Continue to next method
                else:
                    print("Could not connect to Tor control port")
            except Exception as stem_e:
                print(f"Tor control port method failed: {stem_e}")
            
            # Method 3: Use Tor to connect to the site and get the exit node IP
            try:
                print("Trying to get Tor exit node IP")
                from crawler import get_tor_session
                session = get_tor_session()
                
                if not session:
                    print("Could not establish Tor session")
                    raise Exception("Failed to create Tor session")
                
                # First try to connect to the onion site to see if it's reachable
                try:
                    print(f"Attempting to connect to {site_url}")
                    site_response = session.get(site_url, timeout=60)
                    site_reachable = site_response.status_code < 400
                except Exception as site_e:
                    print(f"Could not connect to onion site: {site_e}")
                    site_reachable = False
                
                # Get the exit node IP
                print("Getting Tor exit node IP")
                ip_services = [
                    'https://api.ipify.org?format=json',
                    'https://ipinfo.io/json',
                    'https://ipapi.co/json/',
                    'https://api.myip.com'
                ]
                
                for service in ip_services:
                    try:
                        response = session.get(service, timeout=30)
                        if response.status_code == 200:
                            ip_data = response.json()
                            ip_address = ip_data.get('ip') or ip_data.get('query') or ip_data.get('ipAddress')
                            if ip_address:
                                print(f"Got Tor exit node IP: {ip_address}")
                                break
                    except:
                        continue
                
                if not ip_address:
                    print("Could not determine Tor exit node IP")
                    raise Exception("Failed to get Tor exit node IP")
                
                return {
                    'domain': domain,
                    'ip_address': ip_address,
                    'status': 'tor_exit_node',
                    'message': 'This is a Tor exit node IP, not the actual server IP',
                    'is_tor': True,
                    'is_proxy': True,
                    'is_datacenter': True,
                    'site_reachable': site_reachable
                }
            except Exception as tor_e:
                print(f"Tor exit node method failed: {tor_e}")
                
                # If all methods fail, return an error
                return {
                    'domain': domain,
                    'status': 'error',
                    'message': 'Could not resolve onion address using any available method',
                    'is_tor': True,
                    'is_proxy': True,
                    'is_datacenter': False
                }
    else:
        # For regular domains, use standard DNS resolution
        try:
            print(f"Using standard DNS resolution for {domain}")
            ip_address = socket.gethostbyname(domain)
            print(f"Resolved to IP: {ip_address}")
        except socket.gaierror as e:
            print(f"DNS resolution failed: {e}")
            return {
                'domain': domain,
                'status': 'error',
                'message': f'Error resolving domain: {str(e)}'
            }
    
    # Now that we have an IP, get more details about it
    try:
        # Use multiple IP information services for redundancy
        ip_info_services = [
            {'url': f'https://ipinfo.io/{ip_address}/json', 'name': 'ipinfo.io'},
            {'url': f'https://ipapi.co/{ip_address}/json/', 'name': 'ipapi.co'},
            {'url': f'https://api.ip2location.io/?key=demo&ip={ip_address}', 'name': 'ip2location.io'},
            {'url': f'https://freegeoip.app/json/{ip_address}', 'name': 'freegeoip.app'}
        ]
        
        ip_data = None
        service_used = None
        
        for service in ip_info_services:
            try:
                print(f"Trying IP info service: {service['name']}")
                response = requests.get(service['url'], timeout=10)
                
                if response.status_code == 200:
                    ip_data = response.json()
                    service_used = service['name']
                    print(f"Successfully got IP data from {service['name']}")
                    break
            except Exception as service_e:
                print(f"Error with {service['name']}: {service_e}")
                continue
        
        if not ip_data:
            print("All IP info services failed")
            return {
                'domain': domain,
                'ip_address': ip_address,
                'status': 'partial',
                'message': 'Could not get detailed IP information from any service'
            }
        
        # Extract location information (different services use different field names)
        country = ip_data.get('country') or ip_data.get('country_name') or ip_data.get('countryName') or 'Unknown'
        city = ip_data.get('city') or 'Unknown'
        region = ip_data.get('region') or ip_data.get('region_name') or ip_data.get('regionName') or 'Unknown'
        
        # Extract coordinates (different services use different field names)
        latitude = None
        longitude = None
        
        if 'loc' in ip_data and ',' in ip_data['loc']:
            lat, lon = ip_data['loc'].split(',')
            latitude = float(lat)
            longitude = float(lon)
        elif 'latitude' in ip_data and 'longitude' in ip_data:
            latitude = float(ip_data['latitude'])
            longitude = float(ip_data['longitude'])
        elif 'lat' in ip_data and 'lon' in ip_data:
            latitude = float(ip_data['lat'])
            longitude = float(ip_data['lon'])
        
        # Extract organization/ISP information
        org = ip_data.get('org') or ip_data.get('isp') or ip_data.get('as') or ip_data.get('asn') or 'Unknown'
        
        # Check if it's a Tor exit node
        is_tor = False
        try:
            print("Checking if IP is a Tor exit node")
            tor_exit_response = requests.get('https://check.torproject.org/torbulkexitlist', timeout=10)
            if tor_exit_response.status_code == 200:
                is_tor = ip_address in tor_exit_response.text.split('\n')
                print(f"Is Tor exit node: {is_tor}")
        except Exception as tor_e:
            print(f"Error checking Tor exit node status: {tor_e}")
            # If we can't check, use a secondary method
            try:
                tor_exit_response = requests.get('https://www.dan.me.uk/torlist/', timeout=10)
                if tor_exit_response.status_code == 200:
                    is_tor = ip_address in tor_exit_response.text.split('\n')
                    print(f"Is Tor exit node (secondary check): {is_tor}")
            except:
                print("Secondary Tor exit node check also failed")
                # If we can't check, assume it's not a Tor exit node
                pass
        
        # Check if it's a proxy or VPN
        is_proxy = False
        is_datacenter = False
        
        # Look for keywords in the organization name
        proxy_keywords = [
            'proxy', 'vpn', 'hosting', 'cloud', 'server', 'data center', 'datacenter',
            'anonymous', 'tor', 'exit', 'relay', 'node', 'aws', 'azure', 'google', 
            'digital ocean', 'linode', 'ovh', 'vultr', 'hetzner'
        ]
        
        if org:
            org_lower = org.lower()
            is_proxy = any(keyword in org_lower for keyword in proxy_keywords)
            is_datacenter = ('host' in org_lower or 'data' in org_lower or 
                            'cloud' in org_lower or 'server' in org_lower)
            
            print(f"Organization: {org}")
            print(f"Is proxy: {is_proxy}")
            print(f"Is datacenter: {is_datacenter}")
        
        # Try to get additional threat intelligence about the IP
        threat_info = {}
        try:
            print("Getting threat intelligence data")
            # AbuseIPDB (free tier, limited requests)
            abuse_response = requests.get(
                f'https://api.abuseipdb.com/api/v2/check?ipAddress={ip_address}',
                headers={'Key': 'YOUR_API_KEY', 'Accept': 'application/json'},
                timeout=10
            )
            
            if abuse_response.status_code == 200:
                abuse_data = abuse_response.json()
                if 'data' in abuse_data:
                    threat_info['abuse_score'] = abuse_data['data'].get('abuseConfidenceScore')
                    threat_info['abuse_reports'] = abuse_data['data'].get('totalReports')
                    print(f"AbuseIPDB score: {threat_info.get('abuse_score')}")
        except Exception as threat_e:
            print(f"Error getting threat intelligence: {threat_e}")
            # Continue without threat intelligence
        
        # Compile all the information
        result = {
            'domain': domain,
            'ip_address': ip_address,
            'country': country,
            'city': city,
            'region': region,
            'latitude': latitude,
            'longitude': longitude,
            'isp': org,
            'is_tor': is_tor,
            'is_proxy': is_proxy,
            'is_datacenter': is_datacenter,
            'status': 'resolved',
            'service_used': service_used
        }
        
        # Add threat intelligence if available
        if threat_info:
            result['threat_intelligence'] = threat_info
        
        return result
    
    except Exception as e:
        print(f"Error getting IP details: {e}")
        # If there's an error getting IP details, return what we have
        return {
            'domain': domain,
            'ip_address': ip_address,
            'status': 'error',
            'message': f'Error getting IP details: {str(e)}'
        }

def export_to_csv(data):
    """Export data to CSV file"""
    if not data:
        raise ValueError("No data to export")
    
    # Create export directory if it doesn't exist
    export_dir = os.path.join(os.path.dirname(__file__), 'exports')
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    # Generate a unique filename
    filename = f"dark_web_export_{int(time.time())}.csv"
    filepath = os.path.join(export_dir, filename)
    
    # Write data to CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        # Get all possible field names from the data
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        
        writer = csv.DictWriter(csvfile, fieldnames=sorted(fieldnames))
        writer.writeheader()
        writer.writerows(data)
    
    return filepath

def export_to_excel(data):
    """Export data to Excel file"""
    if not data:
        raise ValueError("No data to export")
    
    # Create export directory if it doesn't exist
    export_dir = os.path.join(os.path.dirname(__file__), 'exports')
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    # Generate a unique filename
    filename = f"dark_web_export_{int(time.time())}.xlsx"
    filepath = os.path.join(export_dir, filename)
    
    # Convert to DataFrame and export to Excel
    df = pd.DataFrame(data)
    df.to_excel(filepath, index=False)
    
    return filepath

def save_to_filebase(data, data_type='crawl_results'):
    """
    Save data to Filebase (decentralized storage) or local storage
    
    This function integrates with Filebase, a decentralized storage platform
    that uses IPFS, Sia, or Filecoin as the underlying storage layer.
    
    Args:
        data: The data to save (will be converted to JSON)
        data_type: Type of data (used for organizing storage)
        
    Returns:
        dict: Information about the saved data including CID if using Filebase
    """
    import os
    
    # Check if we should use Filebase or local storage
    storage_type = os.getenv('STORAGE_TYPE', 'local').lower()
    
    if storage_type == 'filebase':
        # Use the Filebase storage module
        try:
            from filebase_storage import save_to_filebase as filebase_save
            return filebase_save(data, data_type)
        except ImportError:
            print("Filebase storage module not available, falling back to local storage")
            return _save_to_local_storage(data, data_type)
    else:
        # Use the legacy local storage implementation
        return _save_to_local_storage(data, data_type)

def _save_to_local_storage(data, data_type='crawl_results'):
    """Legacy implementation of local storage"""
    import os
    import json
    import time
    import uuid
    from pathlib import Path
    
    # Generate a unique ID for this data
    data_id = str(uuid.uuid4())
    timestamp = int(time.time())
    
    # Add metadata
    metadata = {
        'id': data_id,
        'timestamp': timestamp,
        'timestamp_readable': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)),
        'data_type': data_type,
        'record_count': len(data) if isinstance(data, list) else 1
    }
    
    # Prepare the full data object
    full_data = {
        'metadata': metadata,
        'data': data
    }
    
    # Create the directory if it doesn't exist
    storage_dir = Path(os.path.dirname(__file__)) / 'data_storage' / data_type
    os.makedirs(storage_dir, exist_ok=True)
    
    # Create the filename
    filename = f"{data_type}_{data_id}.json"
    file_path = storage_dir / filename
    
    # Write the data
    with open(file_path, 'w') as f:
        json.dump(full_data, f, indent=2)
    
    # Generate a simulated CID for compatibility
    cid = f"Qm{uuid.uuid4().hex[:38]}"
    
    return {
        'success': True,
        'storage': 'local',
        'id': data_id,
        'filename': filename,
        'file_path': str(file_path),
        'timestamp': timestamp,
        'cid': cid,
        'url': f"file://{file_path}"
    }
