@echo off
setlocal enabledelayedexpansion

echo.
echo ===================================================
echo       DARK WEB MONITORING SYSTEM LAUNCHER
echo ===================================================
echo.

REM Set colors for better readability
color 0B

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.7+ and try again.
    goto :exit
)

REM Get the Tor executable path from .env file
set TOR_PATH=
for /f "tokens=1,* delims==" %%a in ('type "backend\.env" ^| findstr "TOR_EXECUTABLE_PATH"') do (
    set TOR_PATH=%%b
    REM Remove quotes if present
    set TOR_PATH=!TOR_PATH:"=!
)

echo [INFO] Checking system requirements...

REM Check if Tor is installed
if not defined TOR_PATH (
    echo [WARNING] Tor executable path not found in .env file.
    echo You may need to set TOR_EXECUTABLE_PATH in backend\.env
) else (
    echo [INFO] Tor executable found at: !TOR_PATH!
)

REM Check if required directories exist, create if not
if not exist "backend\data" mkdir "backend\data"
if not exist "backend\data\crawled" mkdir "backend\data\crawled"
if not exist "backend\data\sellers" mkdir "backend\data\sellers"
if not exist "backend\logs" mkdir "backend\logs"

echo [INFO] Required directories created/verified.

REM Check if Tor is running
echo [INFO] Checking Tor status...
powershell -Command "Test-NetConnection -ComputerName localhost -Port 9050 -InformationLevel Quiet" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Tor is already running.
) else (
    echo [INFO] Tor is not running.
    if defined TOR_PATH (
        echo [INFO] Starting Tor...
        start "" "!TOR_PATH!"
        echo [INFO] Waiting for Tor to initialize...
        timeout /t 10 /nobreak >nul
    ) else (
        echo [WARNING] Cannot start Tor automatically. Please start Tor Browser manually.
        pause
    )
)

:menu
cls
echo.
echo ===================================================
echo       DARK WEB MONITORING SYSTEM MENU
echo ===================================================
echo.
echo  1. Start the complete system (backend + frontend)
echo  2. Start backend only
echo  3. Run system tests
echo  4. Install required packages
echo  5. Check system status
echo  6. Exit
echo.
echo ===================================================
echo.

set /p choice=Enter your choice (1-6): 

if "%choice%"=="1" goto start_system
if "%choice%"=="2" goto start_backend
if "%choice%"=="3" goto run_tests
if "%choice%"=="4" goto install_packages
if "%choice%"=="5" goto check_status
if "%choice%"=="6" goto exit

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto menu

:start_system
echo.
echo [INFO] Starting Dark Web Monitoring System...
echo.

REM Start the backend server
start "Dark Web Monitoring Backend" cmd /c "python backend\app.py"

REM Wait for backend to start
echo [INFO] Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Open the frontend in the default browser
echo [INFO] Opening frontend...
start "" "frontend\index.html"

echo.
echo [SUCCESS] Dark Web Monitoring System started successfully!
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:start_backend
echo.
echo [INFO] Starting backend server only...
echo.

REM Start the backend server
start "Dark Web Monitoring Backend" cmd /c "python backend\app.py"

echo.
echo [SUCCESS] Backend server started successfully!
echo The API is available at http://localhost:5000/
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:run_tests
echo.
echo [INFO] Running system tests...
echo.

python test_system.py

echo.
echo Press any key to return to menu...
pause >nul
goto menu

:install_packages
echo.
echo [INFO] Installing required packages...
echo.

pip install -r backend\requirements.txt

echo.
echo [INFO] Package installation completed.
echo Press any key to return to menu...
pause >nul
goto menu

:check_status
echo.
echo [INFO] Checking system status...
echo.

echo Checking Tor connection...
powershell -Command "Test-NetConnection -ComputerName localhost -Port 9050 -InformationLevel Quiet" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Tor is running.
) else (
    echo [FAIL] Tor is not running.
)

echo Checking backend server...
powershell -Command "Test-NetConnection -ComputerName localhost -Port 5000 -InformationLevel Quiet" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend server is running.
) else (
    echo [FAIL] Backend server is not running.
)

echo.
echo Press any key to return to menu...
pause >nul
goto menu

:exit
echo.
echo [INFO] Exiting Dark Web Monitoring System...
echo.
color 07
endlocal
exit /b 0