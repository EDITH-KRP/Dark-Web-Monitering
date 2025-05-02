# Frontend-Backend Connection Guide

This document explains how the frontend and backend components of the Dark Web Monitoring Tool are connected and how to run them together.

## Architecture Overview

The Dark Web Monitoring Tool consists of two main components:

1. **Frontend**: A web-based user interface built with HTML, CSS, and JavaScript
2. **Backend**: A Flask-based API server that handles data processing, crawling, and storage

## Connection Method

The frontend connects to the backend via HTTP requests to the API endpoints. The connection is configured as follows:

- The backend API runs on `http://localhost:5000` by default
- The frontend automatically detects and connects to this API URL
- CORS (Cross-Origin Resource Sharing) is enabled on the backend to allow requests from the frontend

## Running the Application

### Option 1: Using the Integrated Starter (Recommended)

The easiest way to run both the frontend and backend together is to use the integrated starter script:

1. Open a command prompt or terminal
2. Navigate to the project root directory
3. Run the starter batch file:

```
start_app.bat
```

This will:
- Start the Flask backend server on port 5000
- Start a simple HTTP server for the frontend on port 8000
- Open your default web browser to the frontend URL

### Option 2: Running Components Separately

If you prefer to run the components separately:

#### Backend:

1. Open a command prompt or terminal
2. Navigate to the backend directory:
   ```
   cd backend
   ```
3. Install required packages (if not already installed):
   ```
   pip install -r requirements.txt
   ```
4. Start the Flask server:
   ```
   python app.py
   ```

#### Frontend:

1. Open another command prompt or terminal
2. Navigate to the frontend directory:
   ```
   cd frontend
   ```
3. Start a simple HTTP server:
   ```
   python -m http.server 8000
   ```
4. Open your web browser and navigate to:
   ```
   http://localhost:8000
   ```

## Troubleshooting Connection Issues

If you encounter connection issues between the frontend and backend:

1. **Check Backend Status**: Ensure the Flask server is running and accessible at http://localhost:5000
2. **Check Console Logs**: Open your browser's developer tools (F12) and check the console for error messages
3. **Check Network Requests**: In the browser's developer tools, go to the Network tab to see if API requests are being sent and what responses are received
4. **Check CORS**: If you see CORS errors, ensure the backend has CORS properly configured
5. **Check Firewall**: Ensure your firewall is not blocking connections to the local ports

## API Endpoints

The frontend communicates with the backend through the following main API endpoints:

- `/` - Home endpoint to check if the API is running
- `/crawl` - Start a Dark Web crawl with specified parameters
- `/ip-details` - Reveal IP details of a Dark Web site
- `/web-archive` - Fetch archived versions of a site
- `/vpn-status` - Check the current VPN status
- `/export-csv` - Export crawled data to CSV
- `/export-excel` - Export crawled data to Excel
- `/upload-to-filebase` - Upload crawl data to decentralized storage

## Customizing the Connection

If you need to run the backend on a different host or port:

1. Modify the `app.run()` parameters in `backend/app.py`
2. Update the `API_URL` constant in `frontend/script.js` accordingly

For production deployments, you may need to configure a proper web server (like Nginx or Apache) and WSGI server for the backend.