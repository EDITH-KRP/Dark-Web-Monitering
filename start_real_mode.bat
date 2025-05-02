@echo off
echo Starting Dark Web Monitoring Tool in TEST REAL MODE...
echo.

REM Set the paths
set BACKEND_DIR=d:\Dark-Web-Monitering\backend
set FRONTEND_DIR=d:\Dark-Web-Monitering\frontend
set VPN_CONFIG=d:\Dark-Web-Monitering\backend\vpn_configs\vpn_config.ovpn
set OPENVPN_PATH="C:\Program Files\Proton\VPN\v3.5.3\Resources\openvpn.exe"

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Skip Tor Browser in test mode
echo Skipping Tor Browser in test mode...
echo This is a test run without Tor Browser.

REM Skip OpenVPN check in test mode
echo Skipping OpenVPN check in test mode...

REM Create VPN config directory if it doesn't exist
if not exist "d:\Dark-Web-Monitering\backend\vpn_configs" (
    mkdir "d:\Dark-Web-Monitering\backend\vpn_configs"
)

REM Create a dummy VPN config file for testing
echo # This is a dummy VPN config file for testing > "%VPN_CONFIG%"
echo client >> "%VPN_CONFIG%"
echo dev tun >> "%VPN_CONFIG%"
echo proto udp >> "%VPN_CONFIG%"
echo remote test-server.com 1194 >> "%VPN_CONFIG%"
echo resolv-retry infinite >> "%VPN_CONFIG%"
echo nobind >> "%VPN_CONFIG%"
echo persist-key >> "%VPN_CONFIG%"
echo persist-tun >> "%VPN_CONFIG%"
echo ^<ca^> >> "%VPN_CONFIG%"
echo # Dummy CA certificate >> "%VPN_CONFIG%"
echo ^</ca^> >> "%VPN_CONFIG%"
echo ^<cert^> >> "%VPN_CONFIG%"
echo # Dummy certificate >> "%VPN_CONFIG%"
echo ^</cert^> >> "%VPN_CONFIG%"
echo ^<key^> >> "%VPN_CONFIG%"
echo # Dummy key >> "%VPN_CONFIG%"
echo ^</key^> >> "%VPN_CONFIG%"

echo Skipping OpenVPN connection in test mode...
echo Using simulated VPN connection for testing.

REM Create a .env file if it doesn't exist
if not exist "d:\Dark-Web-Monitering\backend\.env" (
    echo Creating .env file for testing...
    echo # Dark Web Monitoring Tool Configuration > "d:\Dark-Web-Monitering\backend\.env"
    echo DARK_WEB_DEV_MODE=0 >> "d:\Dark-Web-Monitering\backend\.env"
    echo SHODAN_API_KEY=test_key >> "d:\Dark-Web-Monitering\backend\.env"
    echo ABUSEIPDB_API_KEY=test_key >> "d:\Dark-Web-Monitering\backend\.env"
    echo IPINFO_API_KEY=test_key >> "d:\Dark-Web-Monitering\backend\.env"
    echo IP2LOCATION_API_KEY=test_key >> "d:\Dark-Web-Monitering\backend\.env"
    echo TOR_CONTROL_PORT=9051 >> "d:\Dark-Web-Monitering\backend\.env"
    echo TOR_SOCKS_PORT=9050 >> "d:\Dark-Web-Monitering\backend\.env"
    echo VPN_PROVIDER=OpenVPN >> "d:\Dark-Web-Monitering\backend\.env"
    echo VPN_CONFIG_FILE=vpn_config.ovpn >> "d:\Dark-Web-Monitering\backend\.env"
    echo FILEBASE_BUCKET=test-bucket >> "d:\Dark-Web-Monitering\backend\.env"
    echo FILEBASE_ACCESS_KEY=test_key >> "d:\Dark-Web-Monitering\backend\.env"
    echo FILEBASE_SECRET_KEY=test_key >> "d:\Dark-Web-Monitering\backend\.env"
)

REM Check if pip is installed
where pip >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Pip is not installed or not in PATH.
    echo Skipping package installation.
) else (
    REM Install required Python packages
    echo Installing required Python packages...
    pip install -r %BACKEND_DIR%\requirements.txt
)

REM Start the backend server
echo Starting backend server in TEST REAL MODE...
start "Dark Web Monitoring Backend (TEST REAL MODE)" cmd /c "cd /d %BACKEND_DIR% && set DARK_WEB_DEV_MODE=0 && python app.py"

REM Wait for backend to initialize
echo Waiting for backend to initialize...
timeout /t 10 /nobreak >nul

REM Start the frontend server
echo Starting frontend server...
start "Dark Web Monitoring Frontend" cmd /c "cd /d %FRONTEND_DIR% && python -m http.server 8000"

REM Wait a moment for the frontend server to start
timeout /t 2 /nobreak >nul

REM Open the frontend in the default browser
echo Opening frontend in your default browser...
start http://localhost:8000/

echo.
echo Dark Web Monitoring Tool is now running in TEST REAL MODE!
echo.
echo Backend API: http://localhost:5000/
echo Frontend Interface: http://localhost:8000/
echo.
echo Press any key to stop the servers and exit...
pause >nul

REM Kill the servers when the user presses a key
echo Stopping servers...
taskkill /FI "WINDOWTITLE eq Dark Web Monitoring Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Dark Web Monitoring Frontend*" /F >nul 2>&1

echo Application stopped.
pause