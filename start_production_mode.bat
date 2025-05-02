@echo off
echo Starting Dark Web Monitoring Tool in PRODUCTION MODE...
echo.

REM Set the paths
set BACKEND_DIR=p:\Dark-Web-Monitering\backend
set FRONTEND_DIR=p:\Dark-Web-Monitering\frontend
set VPN_CONFIG=p:\Dark-Web-Monitering\backend\vpn_configs\vpn_config.ovpn
set OPENVPN_PATH="C:\Program Files\Proton\VPN\v3.5.3\Resources\openvpn.exe"
set OPENVPN_PATH_ALT="C:\Program Files\Proton\VPN\v3.5.2\Resources\openvpn.exe"

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Start Tor Browser in the background
echo Starting Tor Browser in the background...
set TOR_PATH="C:\Users\prajw\OneDrive\Desktop\Tor Browser\Browser\TorBrowser\Tor\tor.exe"

if not exist %TOR_PATH% (
    echo Tor executable not found at %TOR_PATH%
    echo Please install Tor Browser or update the path in this script.
    pause
    exit /b 1
)

echo Starting Tor...
start "" /B %TOR_PATH%

echo Waiting for Tor to initialize...
timeout /t 10 /nobreak >nul

REM Run the production mode check script
echo Running production mode check...
python check_prod.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo Production mode check failed. Please fix the issues before continuing.
    pause
    exit /b 1
)

REM Check if OpenVPN exists at the expected path
if exist %OPENVPN_PATH% (
    echo Found OpenVPN at %OPENVPN_PATH%
) else (
    if exist %OPENVPN_PATH_ALT% (
        echo Found OpenVPN at %OPENVPN_PATH_ALT%
        set OPENVPN_PATH=%OPENVPN_PATH_ALT%
    ) else (
        echo OpenVPN executable not found at expected locations.
        echo The application cannot run in production mode without OpenVPN.
        pause
        exit /b 1
    )
)

REM Check if VPN config file exists
if not exist "%VPN_CONFIG%" (
    echo VPN configuration file not found at %VPN_CONFIG%
    echo The application cannot run in production mode without a VPN configuration.
    pause
    exit /b 1
)

REM Create a temporary batch file to run OpenVPN with admin privileges
echo @echo off > "%TEMP%\run_openvpn.bat"
echo echo Starting OpenVPN in PRODUCTION MODE... >> "%TEMP%\run_openvpn.bat"
echo %OPENVPN_PATH% --config "%VPN_CONFIG%" >> "%TEMP%\run_openvpn.bat"
echo pause >> "%TEMP%\run_openvpn.bat"

REM Start OpenVPN with admin privileges
echo Starting OpenVPN connection...
echo Please accept the UAC prompt if it appears.
powershell -Command "Start-Process -FilePath '%TEMP%\run_openvpn.bat' -Verb RunAs"

REM Wait for VPN to initialize
echo Waiting for VPN to initialize...
timeout /t 15 /nobreak >nul

REM Start the backend server
echo Starting backend server in PRODUCTION MODE...
start "Dark Web Monitoring Backend (PRODUCTION)" cmd /c "cd /d %BACKEND_DIR% && set DARK_WEB_DEV_MODE=0 && python app.py"

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
echo Dark Web Monitoring Tool is now running in PRODUCTION MODE!
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

REM Try to close OpenVPN
echo Stopping OpenVPN...
taskkill /F /IM openvpn.exe >nul 2>&1

echo Application stopped.
pause