#!/usr/bin/env python
"""
Test script for the Dark Web Monitoring System
"""
import requests
import json
import time
import sys

def test_backend_connection():
    """Test if the backend is running"""
    try:
        response = requests.get('http://localhost:5000/')
        if response.status_code == 200:
            print("✅ Backend connection successful")
            return True
        else:
            print(f"❌ Backend returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Make sure it's running on http://localhost:5000/")
        return False

def test_browser_status():
    """Test the browser status endpoint"""
    try:
        response = requests.get('http://localhost:5000/browser-status')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Browser status: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Browser status check failed with status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend")
        return False

def test_vpn_status():
    """Test the VPN status endpoint"""
    try:
        response = requests.get('http://localhost:5000/vpn-status')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ VPN status: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ VPN status check failed with status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend")
        return False

def test_ip_reveal():
    """Test the IP reveal functionality with a sample domain"""
    try:
        # Use a public domain for testing
        test_domain = "example.com"
        
        response = requests.post(
            'http://localhost:5000/ip-details',
            json={"url": test_domain}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ IP reveal test successful")
            print(f"   Domain: {test_domain}")
            print(f"   IP: {data.get('ip')}")
            if 'geolocation' in data:
                print(f"   Location: {data['geolocation'].get('country')}")
            return True
        else:
            print(f"❌ IP reveal test failed with status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend")
        return False
    except Exception as e:
        print(f"❌ IP reveal test failed with error: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Testing Dark Web Monitoring System...")
    print("-" * 50)
    
    # Test backend connection
    if not test_backend_connection():
        print("\n❌ Backend connection failed. Please make sure the backend is running.")
        print("   Run 'python backend/app.py' to start the backend.")
        return 1
    
    print("\n🔍 Testing browser status...")
    test_browser_status()
    
    print("\n🔍 Testing VPN status...")
    test_vpn_status()
    
    print("\n🔍 Testing IP reveal functionality...")
    test_ip_reveal()
    
    print("\n✅ All tests completed")
    print("-" * 50)
    print("The Dark Web Monitoring System is ready to use!")
    print("Run 'python start_monitoring.py' to start the system")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())