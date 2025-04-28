import requests
import socket
from geopy.geocoders import Nominatim


def get_ip(domain):
    try:
        ip_address = socket.gethostbyname(domain)
        return ip_address
    except socket.gaierror as e:
        return {"error": f"Error resolving domain {domain}: {e}"}


def get_geolocation(ip_address):
    geolocator = Nominatim(user_agent="dark-web-ip-reveal")
    try:
        location = geolocator.geocode(ip_address)
        if location:
            return {"ip": ip_address, "location": location.address}
        else:
            return {"error": "Location not found for the given IP address."}
    except Exception as e:
        return {"error": f"Error getting geolocation for IP {ip_address}: {e}"}


def reveal_ip_and_geo(domain):
    ip = get_ip(domain)
    if isinstance(ip, dict) and ip.get("error"):
        return ip
    
    geo_info = get_geolocation(ip)
    return geo_info

if __name__ == "__main__":
   
    domain = "example.onion" 
    result = reveal_ip_and_geo(domain)
    print(result)
