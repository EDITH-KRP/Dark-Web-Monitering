# Dark Web Monitoring Tool

This project is a comprehensive Dark Web monitoring solution designed to crawl .onion websites, attempt IP and geolocation reveals, filter dark web sites based on keywords and risk scores, and track seller profiles. The tool includes both backend (Python) and frontend (HTML5, CSS3, JavaScript) components.

## Features

- **Tor Crawling**: Crawl `.onion` websites on the Dark Web using the Tor network.
- **IP and Geolocation Reveal**: Attempt to reveal the true IP and geolocation of Dark Web sites.
- **Keyword and Risk Filtering**: Filter sites based on predefined keywords like "drugs", "murder", "arms", etc., and calculate a risk score.
- **Seller Tracking**: Track seller profiles and activities on Dark Web marketplaces.
- **VPN Support**: Mask IPs and prevent tracking using VPN connections.
- **Web Archive Proxy**: View old versions of websites using web archive proxies.
- **Multi-Browser Support**: Support for TOR, I2P, Freenet, and TAILS browsers.
- **Geolocation Identification**: Identify geographic locations associated with Dark Web sites.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Real Service Integration](#real-service-integration)
- [Usage](#usage)
- [Backend Structure](#backend-structure)
- [Frontend Structure](#frontend-structure)
- [Dark Web Scripts](#dark-web-scripts)
- [Dependencies](#dependencies)
- [Security Considerations](#security-considerations)
- [License](#license)

## Quick Start

For a quick setup with all dependencies and configurations:

```bash
# Clone the repository
git clone https://github.com/yourusername/dark-web-monitoring-tool.git
cd dark-web-monitoring-tool

# Run the setup script
python setup.py

# Start the backend server
python backend/app.py

# Open the frontend in your browser
# Simply open frontend/index.html in your web browser
```

## Installation

### Prerequisites

Before you begin, ensure that you have the following installed:

- Python 3.7 or higher
- Tor Browser (for crawling `.onion` sites)
- OpenVPN (for VPN connections)
- Virtual environment (recommended)

### Manual Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/dark-web-monitoring-tool.git
cd dark-web-monitoring-tool
```

2. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

4. Create required directories:

```bash
mkdir -p backend/vpn_configs
mkdir -p backend/cache/web_archive
mkdir -p backend/data
mkdir -p backend/logs
mkdir -p backend/data_storage
mkdir -p backend/exports
```

5. Configure the environment:

```bash
# Copy the example .env file
cp backend/.env.example backend/.env
# Edit the .env file with your settings
```

## Real Service Integration

This tool has been updated to use real services instead of simulations. Here's how to set up each component:

### 1. VPN Integration

The tool uses OpenVPN for secure connections. To set up:

1. Place your OpenVPN configuration file in `backend/vpn_configs/vpn_config.ovpn`
2. Place any required certificate files (ca.crt, client.crt, client.key) in the same directory
3. Update the VPN settings in `backend/.env`:

```
VPN_PROVIDER=OpenVPN
VPN_CONFIG_FILE=vpn_config.ovpn
```

### 2. TOR Network Integration

For real TOR network integration:

1. Install Tor Browser or the Tor service
2. Ensure Tor is running on the default ports (9050 for SOCKS, 9051 for control)
3. For Tor control port access, add these lines to your torrc file:

```
ControlPort 9051
CookieAuthentication 1
```

4. Update Tor settings in `backend/.env`:

```
TOR_CONTROL_PORT=9051
TOR_SOCKS_PORT=9050
```

### 3. IP Details Revelation

For accurate IP information:

1. Sign up for free API keys from services like:
   - ipinfo.io
   - ip2location.io
   - abuseipdb.com
   - shodan.io

2. Add your API keys to `backend/.env`:

```
IPINFO_API_KEY=your_ipinfo_api_key
IP2LOCATION_API_KEY=your_ip2location_api_key
ABUSEIPDB_API_KEY=your_abuseipdb_api_key
SHODAN_API_KEY=your_shodan_api_key
```

### 4. Web Archive Access

The tool now uses real archive.org access:

1. No API key is required for basic access
2. The tool implements caching to avoid rate limits
3. Configure cache settings in `backend/.env`:

```
WEB_ARCHIVE_CACHE_TTL=86400  # 24 hours in seconds
```

### 5. Filebase Decentralized Storage

The tool now integrates with Filebase for decentralized storage:

1. Sign up for a Filebase account at [filebase.com](https://filebase.com/)
2. Create a bucket for your data
3. Generate access keys
4. Update your `.env` file:

```
FILEBASE_BUCKET=your-bucket-name
FILEBASE_ACCESS_KEY=your-access-key
FILEBASE_SECRET_KEY=your-secret-key
FILEBASE_ENDPOINT=https://s3.filebase.com
STORAGE_TYPE=filebase
```

For detailed setup instructions, see [FILEBASE_SETUP.md](docs/FILEBASE_SETUP.md).

### 6. Alternative Browsers (I2P, Freenet, TAILS)

For additional dark web browsers:

1. **I2P**: Install I2P from https://geti2p.net/
2. **Freenet**: Install Freenet from https://freenetproject.org/
3. **TAILS**: Use TAILS OS from https://tails.boum.org/

The tool will automatically detect and use these browsers if available.

## Usage

### Running the Backend

1. Navigate to the project root directory
2. Start the Flask server:

```bash
python backend/app.py
```

This will start the backend API on `http://localhost:5000`.

### Running the Frontend

1. Open the `frontend/index.html` file in a browser to view the monitoring dashboard.
2. The frontend will communicate with the backend API to display the crawled data, filtered results, IP details, and seller profiles.

### Example Usage:

1. **Crawling Dark Web Sites**:
   - Select a browser (TOR, I2P, Freenet, TAILS)
   - Enter keywords (e.g., "drugs, arms")
   - Enter geo-location (e.g., "Russia")
   - Click "Start Crawling"

2. **Revealing IP Details**:
   - Enter a Dark Web URL (e.g., "example.onion")
   - Click "Reveal IP"

3. **Checking Web Archives**:
   - Enter a URL to check archives
   - Click "Check Archives"

4. **Exporting Data**:
   - After crawling, use the export buttons to save data as CSV or Excel

## Backend Structure

The backend is built with Flask and Python. Here's a brief overview of the structure:

```
backend/
├── app.py                # Main entry point for Flask app
├── config.py             # Configuration loader
├── logger.py             # Logging configuration
├── crawler.py            # Handles crawling and scraping of .onion sites
├── vpn_connect.py        # Manages VPN connection for IP masking
├── utils.py              # Helper functions like IP reveal, geolocation, etc.
├── web_archive.py        # Web archive access functionality
├── dark_web_filters.py   # Filtering and risk assessment
├── i2p_connect.py        # I2P browser integration
├── freenet_connect.py    # Freenet browser integration
├── tails_connect.py      # TAILS browser integration
├── data_storage/         # Folder for storing crawled data
├── cache/                # Cache for web archive and other data
├── vpn_configs/          # VPN configuration files
├── logs/                 # Log files
└── requirements.txt      # Backend dependencies
```

## Frontend Structure

The frontend consists of HTML, CSS, and JavaScript files that handle the UI and interact with the backend API.

```
frontend/
├── index.html                    # Main HTML page
├── styles.css                    # CSS file for styling the UI
├── script.js                     # JavaScript file for core functionality
├── browser-selector.js           # Browser selection functionality
├── dark-mode-toggle.js           # Dark/Light mode toggle
├── filter.js                     # Data filtering functionality
├── ip-details.js                 # IP reveal functionality
├── web-archive.js                # Web archive functionality
├── export.js                     # Data export functionality
├── vpn-status.js                 # VPN status monitoring
└── assets/                       # Images and other assets
```

## Dark Web Scripts

The `dark-web-scripts/` folder contains specialized scripts for dark web operations:

```
dark-web-scripts/
├── tor_crawler.py                # Specialized TOR crawler
├── ip_reveal.py                  # Advanced IP revelation techniques
├── dark_web_filters.py           # Content filtering and categorization
└── seller_tracking.py            # Seller profile tracking
```

## Dependencies

The tool requires several Python packages. The main dependencies are:

- **Core**: Flask, Requests, BeautifulSoup4, lxml
- **Tor**: Stem, PySocks
- **VPN**: psutil, pycryptodome, cryptography
- **IP Analysis**: geoip2, maxminddb, ipwhois, dnspython
- **Data Processing**: pandas, openpyxl
- **Web Archive**: waybackpy
- **Configuration**: python-dotenv

All dependencies are listed in `backend/requirements.txt` and can be installed with:

```bash
pip install -r backend/requirements.txt
```

## Security Considerations

When using this tool, please be aware of the following security considerations:

1. **Legal Compliance**: Ensure you're using this tool in compliance with all applicable laws and regulations.

2. **VPN Usage**: Always use a VPN when accessing the Dark Web to protect your identity.

3. **API Keys**: Keep your API keys secure and never commit them to public repositories.

4. **Tor Configuration**: Properly configure Tor to prevent identity leaks.

5. **Data Handling**: Be careful with the data you collect and how you store it.

6. **System Isolation**: Consider running this tool in an isolated environment.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is provided for educational and research purposes only. The developers are not responsible for any misuse or illegal activities conducted with this tool.