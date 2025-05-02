@echo off
echo Starting Tor Browser in background mode...

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
timeout /t 5 /nobreak >nul

echo Tor should now be running in the background.
echo You can now start the Dark Web Monitoring Tool in production mode.
echo.
echo Press any key to exit...
pause >nul