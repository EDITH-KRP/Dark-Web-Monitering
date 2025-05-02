@echo off
echo === Starting Dark Web Monitoring Tool ===
echo.

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Run the application starter script
python start_app.py

pause