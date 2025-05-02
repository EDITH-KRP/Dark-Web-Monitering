@echo off
echo === Dark Web Monitoring Tool Real Mode Test ===
echo.

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Run the test script
python test_real_mode.py

pause