# Dark Web Monitoring System - Usage Guide

This guide provides instructions on how to use the Dark Web Monitoring System to crawl and analyze Dark Web sites, reveal hidden IP addresses, track seller profiles, and visualize the data.

## Prerequisites

Before using the system, make sure you have:

1. **Tor Browser** installed on your system
2. **Python 3.7+** installed
3. Required Python packages (install with `pip install -r backend/requirements.txt`)
4. API keys for various services (configured in `backend/.env`)

## Starting the System

There are two ways to start the system:

### Option 1: Using the Interactive Batch Script (Windows)

1. Double-click on `start_dark_web_monitor.bat`
2. From the menu, select your desired option:
   - Option 1: Start the complete system (backend + frontend)
   - Option 2: Start backend only
   - Option 3: Run system tests
   - Option 4: Install required packages
   - Option 5: Check system status
   - Option 6: Exit

The batch script will:
- Check if Tor is running and start it if needed
- Create necessary directories if they don't exist
- Start the backend server when requested
- Open the frontend in your default browser when requested

### Option 2: Using the Python Script (Cross-platform)

1. Open a terminal/command prompt
2. Navigate to the project directory
3. Run: `python start_monitoring.py`
4. The script will:
   - Check if Tor is running and start it if needed
   - Start the backend server
   - Open the frontend in your default browser

## Using the System

### Crawling the Dark Web

1. In the frontend, go to the "Crawl the Dark Web" section
2. Enter keywords to search for (e.g., "drugs, weapons, hacking")
3. Optionally enter a geo-location to focus on
4. Use the advanced filters if needed:
   - Date range
   - Minimum risk score
   - Seller profiles only
   - Country/region/city filters
   - Content category
5. Click "Start Crawling"
6. The system will:
   - Connect to the Tor network
   - Crawl .onion sites starting from seed URLs
   - Filter results based on your criteria
   - Display the results in the interface

### Revealing IP Addresses

1. Go to the "Reveal IP Details" section
2. Enter a Dark Web URL (.onion site)
3. Click "Reveal IP"
4. The system will:
   - Attempt multiple methods to reveal the IP (DNS leaks, SSL certificates, HTTP headers, etc.)
   - Show the IP address if found
   - Display geolocation information for the IP

### Tracking Seller Profiles

1. Go to the "Track Seller" section (accessible from the main dashboard)
2. Enter the URL of a seller profile on a Dark Web marketplace
3. Click "Track Seller"
4. The system will:
   - Extract seller information (name, rating, products, feedback)
   - Save the profile for historical tracking
   - Display the information in the interface

### Viewing Historical Data

1. Use the "Timeline View" section to see historical data
2. Filter by date detected
3. The system will show how sites and sellers have changed over time

### Exporting Data

1. After crawling or tracking, use the export buttons:
   - "Export CSV" for spreadsheet format
   - "Export Excel" for Microsoft Excel format
2. The exported files will contain all the data collected

### Uploading to Decentralized Storage

1. Use the "Upload to Filebase" button to store data in decentralized storage
2. This ensures the data is preserved even if your local system is compromised

## Advanced Features

### VPN Integration

The system can connect through a VPN for additional anonymity:

1. Configure your VPN settings in `backend/.env`
2. Use the VPN toggle in the interface to connect/disconnect

### Alternative Browsers

Besides Tor, the system supports other Dark Web browsers if installed:

1. I2P
2. Freenet
3. TAILS

Select the browser from the dropdown in the crawl interface.

## Troubleshooting

### Tor Connection Issues

If you see "Could not connect to Tor" errors:

1. Make sure Tor Browser is installed
2. Verify the Tor path in `backend/.env` is correct
3. Try starting Tor Browser manually before using the system

### API Key Errors

If you see errors related to API services:

1. Check that all API keys in `backend/.env` are valid
2. Some features may be limited without valid API keys

### Performance Issues

If the system is running slowly:

1. Reduce the maximum number of pages to crawl
2. Focus your search with more specific keywords
3. Use the risk threshold to filter out low-risk content

## Security Considerations

1. **Legal Compliance**: Ensure you're using this tool in compliance with all applicable laws.
2. **VPN Usage**: Always use a VPN when accessing the Dark Web to protect your identity.
3. **API Keys**: Keep your API keys secure and never share them.
4. **Data Handling**: Be careful with the data you collect and how you store it.
5. **System Isolation**: Consider running this tool in an isolated environment.

## Disclaimer

This tool is provided for educational and research purposes only. The developers are not responsible for any misuse or illegal activities conducted with this tool.