@echo off
echo Starting Dark Web Monitoring Tool...
echo.

REM Set the paths
set BACKEND_DIR=p:\Dark-Web-Monitering\backend
set FRONTEND_DIR=p:\Dark-Web-Monitering\frontend

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Start the backend server
echo Starting backend server...
start "Dark Web Monitoring Backend" cmd /c "cd /d %BACKEND_DIR% && python app.py"

REM Wait for backend to initialize
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Start the frontend server
echo Starting frontend server...
start "Dark Web Monitoring Frontend" cmd /c "cd /d %FRONTEND_DIR% && python -m http.server 8000"

REM Wait a moment for the frontend server to start
timeout /t 2 /nobreak >nul

REM Open the frontend in the default browser
echo Opening frontend in your default browser...
start http://localhost:8000/

echo.
echo Dark Web Monitoring Tool is now running!
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