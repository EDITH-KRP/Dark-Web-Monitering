import requests
import socket
import dns.resolver
import ssl
import OpenSSL
import os
import json
import time
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
import ipwhois
import geoip2.database
import geoip2.errors
import shodan
import tldextract
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ip_reveal')

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', '.env'))

# API keys from environment variables
SHODAN_API_KEY = os.getenv('SHODAN_API_KEY')
IPINFO_API_KEY = os.getenv('IPINFO_API_KEY')
IP2LOCATION_API_KEY = os.getenv('IP2LOCATION_API_KEY')
ABUSEIPDB_API_KEY = os.getenv('ABUSEIPDB_API_KEY')

def get_ip_direct(domain):
    """Attempt to get IP directly through DNS resolution"""
    try:
        # Remove .onion TLD for direct resolution attempts
        extracted = tldextract.extract(domain)
        if extracted.suffix == 'onion':
            # This shouldn't work for properly configured .onion sites
            # If it does, it's a misconfiguration
            domain_without_onion = extracted.domain
        else:
            domain_without_onion = domain
            
        ip_address = socket.gethostbyname(domain_without_onion)
        return {"ip": ip_address, "method": "direct_dns", "confidence": "high"}
    except socket.gaierror:
        logger.info(f"Could not resolve {domain} directly")
        return None

def get_ip_dns_leak(domain):
    """Check for DNS leaks by querying different record types"""
    try:
        results = []
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA']
        
        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                for rdata in answers:
                    if record_type == 'MX':
                        # Extract the mail server domain
                        mail_domain = str(rdata.exchange)
                        try:
                            mail_ip = socket.gethostbyname(mail_domain)
                            results.append({
                                "ip": mail_ip,
                                "method": f"dns_leak_mx",
                                "confidence": "medium",
                                "related_domain": mail_domain
                            })
                        except:
                            pass
                    elif record_type == 'NS':
                        # Extract the nameserver domain
                        ns_domain = str(rdata)
                        try:
                            ns_ip = socket.gethostbyname(ns_domain)
                            results.append({
                                "ip": ns_ip,
                                "method": f"dns_leak_ns",
                                "confidence": "medium",
                                "related_domain": ns_domain
                            })
                        except:
                            pass
                    elif record_type in ['A', 'AAAA']:
                        results.append({
                            "ip": str(rdata),
                            "method": f"dns_leak_{record_type.lower()}",
                            "confidence": "high"
                        })
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
                continue
                
        return results if results else None
    except Exception as e:
        logger.error(f"Error in DNS leak check for {domain}: {e}")
        return None

def get_ip_ssl_cert(domain):
    """Extract IP from SSL certificate information"""
    try:
        # Try to connect with SSL and extract certificate info
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # Add port 443 if not specified
        if ':' not in domain:
            connect_domain = f"{domain}:443"
        else:
            connect_domain = domain
            
        with socket.create_connection((connect_domain.split(':')[0], 
                                      int(connect_domain.split(':')[1])), 
                                      timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain.split(':')[0]) as ssock:
                cert = ssock.getpeercert(binary_form=True)
                x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert)
                
                # Extract all domains from the certificate
                cert_domains = []
                
                # Subject Common Name
                subject = x509.get_subject()
                common_name = subject.commonName
                if common_name:
                    cert_domains.append(common_name)
                
                # Subject Alternative Names
                for i in range(x509.get_extension_count()):
                    ext = x509.get_extension(i)
                    if ext.get_short_name().decode('utf-8') == 'subjectAltName':
                        alt_names = ext.get_data()
                        # Parse the ASN.1 data to extract domain names
                        san_text = OpenSSL.crypto.dump_extension(
                            ext.get_short_name(), ext.get_data(), 0, 0
                        ).decode('utf-8')
                        
                        # Extract domains using regex
                        domains = re.findall(r'DNS:([\w\.-]+)', san_text)
                        cert_domains.extend(domains)
                
                # Try to resolve each domain
                results = []
                for cert_domain in cert_domains:
                    try:
                        cert_ip = socket.gethostbyname(cert_domain)
                        results.append({
                            "ip": cert_ip,
                            "method": "ssl_cert",
                            "confidence": "medium",
                            "related_domain": cert_domain
                        })
                    except:
                        continue
                        
                return results if results else None
    except Exception as e:
        logger.error(f"Error in SSL certificate check for {domain}: {e}")
        return None

def get_ip_http_headers(domain):
    """Check for IP leaks in HTTP headers"""
    try:
        # Setup proxies for .onion domains
        proxies = None
        if domain.endswith('.onion'):
            proxies = {
                'http': 'socks5h://127.0.0.1:9050',
                'https': 'socks5h://127.0.0.1:9050'
            }
            
        # Try both HTTP and HTTPS
        protocols = ['http', 'https'] if not domain.endswith('.onion') else ['http']
        
        results = []
        for protocol in protocols:
            try:
                url = f"{protocol}://{domain}"
                response = requests.get(url, 
                                       headers={'User-Agent': 'Mozilla/5.0 DarkWebMonitor'},
                                       proxies=proxies,
                                       timeout=15,
                                       allow_redirects=True)
                
                # Check headers for potential IP leaks
                headers_to_check = ['Server', 'X-Powered-By', 'Via', 'X-Forwarded-For', 
                                   'X-Real-IP', 'X-Server-IP', 'X-Host', 'X-Forwarded-Host']
                
                for header in headers_to_check:
                    if header in response.headers:
                        # Look for IP patterns in header values
                        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
                        ips = re.findall(ip_pattern, response.headers[header])
                        
                        for ip in ips:
                            results.append({
                                "ip": ip,
                                "method": f"http_header_{header.lower()}",
                                "confidence": "medium",
                                "header": header,
                                "header_value": response.headers[header]
                            })
                
                # Check for IPs in response body
                ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
                ips = re.findall(ip_pattern, response.text)
                
                for ip in ips:
                    # Validate that it's a real IP (not something like 0.0.0.0 or 127.0.0.1)
                    if not ip.startswith(('0.', '127.', '192.168.', '10.', '172.16.', '172.17.', '172.18.')):
                        results.append({
                            "ip": ip,
                            "method": "http_body",
                            "confidence": "low"
                        })
                        
            except Exception as e:
                logger.error(f"Error fetching {protocol}://{domain}: {e}")
                continue
                
        return results if results else None
    except Exception as e:
        logger.error(f"Error in HTTP headers check for {domain}: {e}")
        return None

def get_ip_shodan(domain):
    """Query Shodan for information about the domain"""
    if not SHODAN_API_KEY:
        return None
        
    try:
        api = shodan.Shodan(SHODAN_API_KEY)
        
        # First try direct domain search
        try:
            results = api.search(f"hostname:{domain}")
            if results['total'] > 0:
                shodan_results = []
                for result in results['matches']:
                    shodan_results.append({
                        "ip": result['ip_str'],
                        "method": "shodan_hostname",
                        "confidence": "high",
                        "ports": result.get('port'),
                        "shodan_data": {
                            "org": result.get('org'),
                            "isp": result.get('isp'),
                            "os": result.get('os'),
                            "product": result.get('product')
                        }
                    })
                return shodan_results
        except:
            pass
            
        # If no results, try to search for SSL certificate
        try:
            results = api.search(f"ssl.cert.subject.cn:{domain}")
            if results['total'] > 0:
                shodan_results = []
                for result in results['matches']:
                    shodan_results.append({
                        "ip": result['ip_str'],
                        "method": "shodan_ssl",
                        "confidence": "medium",
                        "ports": result.get('port'),
                        "shodan_data": {
                            "org": result.get('org'),
                            "isp": result.get('isp'),
                            "os": result.get('os'),
                            "product": result.get('product')
                        }
                    })
                return shodan_results
        except:
            pass
            
        return None
    except Exception as e:
        logger.error(f"Error in Shodan check for {domain}: {e}")
        return None

def get_geolocation(ip_address):
    """Get geolocation information for an IP address using multiple services"""
    results = {}
    
    # 1. Try GeoIP2 database if available
    try:
        # Check for GeoLite2 database
        geoip_db_path = os.path.join(os.path.dirname(__file__), 'GeoLite2-City.mmdb')
        if os.path.exists(geoip_db_path):
            with geoip2.database.Reader(geoip_db_path) as reader:
                response = reader.city(ip_address)
                results['geoip2'] = {
                    'country': response.country.name,
                    'country_code': response.country.iso_code,
                    'city': response.city.name,
                    'postal': response.postal.code,
                    'latitude': response.location.latitude,
                    'longitude': response.location.longitude,
                    'accuracy_radius': response.location.accuracy_radius
                }
    except Exception as e:
        logger.error(f"Error with GeoIP2 database: {e}")
    
    # 2. Try ipinfo.io
    if IPINFO_API_KEY:
        try:
            response = requests.get(f"https://ipinfo.io/{ip_address}?token={IPINFO_API_KEY}")
            if response.status_code == 200:
                data = response.json()
                results['ipinfo'] = {
                    'country': data.get('country'),
                    'region': data.get('region'),
                    'city': data.get('city'),
                    'location': data.get('loc'),
                    'org': data.get('org'),
                    'postal': data.get('postal'),
                    'timezone': data.get('timezone')
                }
        except Exception as e:
            logger.error(f"Error with ipinfo.io: {e}")
    
    # 3. Try IP2Location
    if IP2LOCATION_API_KEY:
        try:
            response = requests.get(
                f"https://api.ip2location.io/?key={IP2LOCATION_API_KEY}&ip={ip_address}"
            )
            if response.status_code == 200:
                data = response.json()
                results['ip2location'] = {
                    'country': data.get('country_name'),
                    'country_code': data.get('country_code'),
                    'region': data.get('region_name'),
                    'city': data.get('city_name'),
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'zip_code': data.get('zip_code'),
                    'isp': data.get('isp')
                }
        except Exception as e:
            logger.error(f"Error with IP2Location: {e}")
    
    # 4. Try AbuseIPDB for additional information
    if ABUSEIPDB_API_KEY:
        try:
            headers = {
                'Key': ABUSEIPDB_API_KEY,
                'Accept': 'application/json',
            }
            response = requests.get(
                f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip_address}",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json().get('data', {})
                results['abuseipdb'] = {
                    'country': data.get('countryName'),
                    'country_code': data.get('countryCode'),
                    'isp': data.get('isp'),
                    'domain': data.get('domain'),
                    'usage_type': data.get('usageType'),
                    'is_tor': data.get('isTor'),
                    'abuse_score': data.get('abuseConfidenceScore')
                }
        except Exception as e:
            logger.error(f"Error with AbuseIPDB: {e}")
    
    # 5. Try WHOIS information
    try:
        obj = ipwhois.IPWhois(ip_address)
        whois_data = obj.lookup_rdap(depth=1)
        results['whois'] = {
            'asn': whois_data.get('asn'),
            'asn_description': whois_data.get('asn_description'),
            'network': whois_data.get('network', {}).get('name'),
            'country': whois_data.get('asn_country_code'),
            'cidr': whois_data.get('network', {}).get('cidr'),
            'abuse_emails': whois_data.get('network', {}).get('abuse_emails'),
            'admin_emails': whois_data.get('network', {}).get('admin_emails')
        }
    except Exception as e:
        logger.error(f"Error with WHOIS lookup: {e}")
    
    # 6. Try Nominatim as a fallback
    if 'geoip2' not in results and 'ipinfo' not in results and 'ip2location' not in results:
        try:
            geolocator = Nominatim(user_agent="dark-web-ip-reveal")
            location = geolocator.geocode(ip_address)
            if location:
                results['nominatim'] = {
                    'address': location.address,
                    'latitude': location.latitude,
                    'longitude': location.longitude
                }
        except Exception as e:
            logger.error(f"Error with Nominatim: {e}")
    
    # Return consolidated results
    if results:
        # Get the most reliable source
        source_priority = ['geoip2', 'ipinfo', 'ip2location', 'abuseipdb', 'whois', 'nominatim']
        best_source = next((s for s in source_priority if s in results), None)
        
        if best_source:
            consolidated = {
                'ip': ip_address,
                'source': best_source,
                'country': results[best_source].get('country'),
                'city': results[best_source].get('city'),
                'coordinates': None,
                'isp': None,
                'details': results
            }
            
            # Get coordinates
            if 'latitude' in results[best_source] and 'longitude' in results[best_source]:
                consolidated['coordinates'] = {
                    'latitude': results[best_source]['latitude'],
                    'longitude': results[best_source]['longitude']
                }
            elif best_source == 'ipinfo' and 'location' in results[best_source]:
                try:
                    lat, lon = results[best_source]['location'].split(',')
                    consolidated['coordinates'] = {
                        'latitude': float(lat),
                        'longitude': float(lon)
                    }
                except:
                    pass
            
            # Get ISP information
            for source in ['abuseipdb', 'ip2location', 'whois']:
                if source in results and 'isp' in results[source]:
                    consolidated['isp'] = results[source]['isp']
                    break
                elif source == 'whois' and 'asn_description' in results[source]:
                    consolidated['isp'] = results[source]['asn_description']
                    break
            
            return consolidated
        else:
            return {"error": "Could not determine geolocation", "ip": ip_address}
    else:
        return {"error": "No geolocation data available", "ip": ip_address}

def reveal_ip_and_geo(domain):
    """Main function to reveal IP and geolocation of a domain"""
    logger.info(f"Starting IP reveal for {domain}")
    
    # Clean the domain (remove http/https and trailing slash)
    if domain.startswith(('http://', 'https://')):
        domain = domain.split('://', 1)[1]
    
    if '/' in domain:
        domain = domain.split('/', 1)[0]
    
    # Skip if it's an IP address already
    if re.match(r'^(?:\d{1,3}\.){3}\d{1,3}$', domain):
        logger.info(f"{domain} is already an IP address")
        geo_info = get_geolocation(domain)
        return {
            "success": True,
            "ip_found": True,
            "domain": domain,
            "ip": domain,
            "method": "direct_ip",
            "geolocation": geo_info
        }
    
    # Try all methods to find IP
    all_results = []
    
    # 1. Direct DNS resolution
    direct_result = get_ip_direct(domain)
    if direct_result:
        all_results.append(direct_result)
    
    # 2. DNS leak check
    dns_results = get_ip_dns_leak(domain)
    if dns_results:
        all_results.extend(dns_results)
    
    # 3. SSL certificate check
    ssl_results = get_ip_ssl_cert(domain)
    if ssl_results:
        all_results.extend(ssl_results)
    
    # 4. HTTP headers check
    http_results = get_ip_http_headers(domain)
    if http_results:
        all_results.extend(http_results)
    
    # 5. Shodan check
    shodan_results = get_ip_shodan(domain)
    if shodan_results:
        all_results.extend(shodan_results)
    
    # Process results
    if all_results:
        # Sort by confidence
        confidence_levels = {"high": 3, "medium": 2, "low": 1}
        all_results.sort(key=lambda x: confidence_levels.get(x.get("confidence", "low"), 0), reverse=True)
        
        # Get the best result
        best_result = all_results[0]
        ip = best_result["ip"]
        
        # Get geolocation for the IP
        geo_info = get_geolocation(ip)
        
        return {
            "success": True,
            "ip_found": True,
            "domain": domain,
            "ip": ip,
            "method": best_result["method"],
            "confidence": best_result.get("confidence", "unknown"),
            "all_detected_ips": [r["ip"] for r in all_results],
            "geolocation": geo_info,
            "detailed_results": all_results
        }
    else:
        return {
            "success": False,
            "ip_found": False,
            "domain": domain,
            "error": "Could not reveal IP address for this domain"
        }

if __name__ == "__main__":
    # Example usage
    domain = "example.onion"  # Replace with actual domain to test
    result = reveal_ip_and_geo(domain)
    print(json.dumps(result, indent=2))
