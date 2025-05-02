@echo off
echo Setting up OpenVPN for Dark Web Monitoring Tool...
echo.

REM Set the paths
set BACKEND_DIR=p:\Dark-Web-Monitering\backend
set VPN_CONFIG_DIR=p:\Dark-Web-Monitering\backend\vpn_configs
set VPN_CONFIG=p:\Dark-Web-Monitering\backend\vpn_configs\vpn_config.ovpn
set OPENVPN_PATH="C:\Program Files\Proton\VPN\v3.5.3\Resources\openvpn.exe"
set OPENVPN_PATH_ALT="C:\Program Files\Proton\VPN\v3.5.2\Resources\openvpn.exe"

REM Check if OpenVPN exists at the expected path
if exist %OPENVPN_PATH% (
    echo Found OpenVPN at %OPENVPN_PATH%
) else (
    if exist %OPENVPN_PATH_ALT% (
        echo Found OpenVPN at %OPENVPN_PATH_ALT%
        set OPENVPN_PATH=%OPENVPN_PATH_ALT%
    ) else (
        echo OpenVPN executable not found at expected locations.
        echo Please provide the full path to your OpenVPN executable:
        set /p OPENVPN_PATH=
        
        if not exist "!OPENVPN_PATH!" (
            echo The specified path does not exist.
            pause
            exit /b 1
        )
    )
)

REM Update the .env file with the OpenVPN path
echo Updating .env file with OpenVPN path...
powershell -Command "(Get-Content '%BACKEND_DIR%\.env') -replace '^VPN_PROVIDER=.*', 'VPN_PROVIDER=OpenVPN' | Set-Content '%BACKEND_DIR%\.env'"
powershell -Command "(Get-Content '%BACKEND_DIR%\.env') -replace '^VPN_CONFIG_FILE=.*', 'VPN_CONFIG_FILE=vpn_config.ovpn' | Set-Content '%BACKEND_DIR%\.env'"

REM Add the OpenVPN path to the .env file if it doesn't exist
findstr /c:"OPENVPN_PATH" "%BACKEND_DIR%\.env" >nul
if %ERRORLEVEL% neq 0 (
    echo.>> "%BACKEND_DIR%\.env"
    echo # Path to OpenVPN executable>> "%BACKEND_DIR%\.env"
    echo OPENVPN_PATH=%OPENVPN_PATH%>> "%BACKEND_DIR%\.env"
) else (
    powershell -Command "(Get-Content '%BACKEND_DIR%\.env') -replace '^OPENVPN_PATH=.*', 'OPENVPN_PATH=%OPENVPN_PATH%' | Set-Content '%BACKEND_DIR%\.env'"
)

echo .env file updated successfully.

REM Create a test script to verify OpenVPN connection
echo Creating test script...
echo import os > "%BACKEND_DIR%\test_vpn.py"
echo import subprocess >> "%BACKEND_DIR%\test_vpn.py"
echo import time >> "%BACKEND_DIR%\test_vpn.py"
echo. >> "%BACKEND_DIR%\test_vpn.py"
echo print("Testing OpenVPN connection...") >> "%BACKEND_DIR%\test_vpn.py"
echo. >> "%BACKEND_DIR%\test_vpn.py"
echo # Get OpenVPN path from .env file or use default >> "%BACKEND_DIR%\test_vpn.py"
echo openvpn_path = %OPENVPN_PATH% >> "%BACKEND_DIR%\test_vpn.py"
echo config_path = os.path.join(os.path.dirname(__file__), 'vpn_configs', 'vpn_config.ovpn') >> "%BACKEND_DIR%\test_vpn.py"
echo. >> "%BACKEND_DIR%\test_vpn.py"
echo print(f"OpenVPN path: {openvpn_path}") >> "%BACKEND_DIR%\test_vpn.py"
echo print(f"Config path: {config_path}") >> "%BACKEND_DIR%\test_vpn.py"
echo. >> "%BACKEND_DIR%\test_vpn.py"
echo # Command to connect to VPN >> "%BACKEND_DIR%\test_vpn.py"
echo cmd = [openvpn_path, "--config", config_path] >> "%BACKEND_DIR%\test_vpn.py"
echo. >> "%BACKEND_DIR%\test_vpn.py"
echo try: >> "%BACKEND_DIR%\test_vpn.py"
echo     # Start OpenVPN in a separate process >> "%BACKEND_DIR%\test_vpn.py"
echo     print("Starting OpenVPN process...") >> "%BACKEND_DIR%\test_vpn.py"
echo     vpn_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True) >> "%BACKEND_DIR%\test_vpn.py"
echo. >> "%BACKEND_DIR%\test_vpn.py"
echo     # Wait for connection to establish (look for "Initialization Sequence Completed") >> "%BACKEND_DIR%\test_vpn.py"
echo     print("Waiting for connection to establish...") >> "%BACKEND_DIR%\test_vpn.py"
echo     connection_established = False >> "%BACKEND_DIR%\test_vpn.py"
echo     for i in range(30):  # Wait up to 30 seconds >> "%BACKEND_DIR%\test_vpn.py"
echo         if vpn_process.poll() is not None: >> "%BACKEND_DIR%\test_vpn.py"
echo             # Process exited >> "%BACKEND_DIR%\test_vpn.py"
echo             stdout, stderr = vpn_process.communicate() >> "%BACKEND_DIR%\test_vpn.py"
echo             print(f"OpenVPN process exited with code {vpn_process.returncode}") >> "%BACKEND_DIR%\test_vpn.py"
echo             print(f"Output: {stdout}") >> "%BACKEND_DIR%\test_vpn.py"
echo             print(f"Error: {stderr}") >> "%BACKEND_DIR%\test_vpn.py"
echo             break >> "%BACKEND_DIR%\test_vpn.py"
echo. >> "%BACKEND_DIR%\test_vpn.py"
echo         line = vpn_process.stdout.readline() >> "%BACKEND_DIR%\test_vpn.py"
echo         print(f"OpenVPN output: {line.strip()}") >> "%BACKEND_DIR%\test_vpn.py"
echo         if "Initialization Sequence Completed" in line: >> "%BACKEND_DIR%\test_vpn.py"
echo             connection_established = True >> "%BACKEND_DIR%\test_vpn.py"
echo             print("VPN connection established successfully!") >> "%BACKEND_DIR%\test_vpn.py"
echo             break >> "%BACKEND_DIR%\test_vpn.py"
echo         time.sleep(1) >> "%BACKEND_DIR%\test_vpn.py"
echo. >> "%BACKEND_DIR%\test_vpn.py"
echo     if not connection_established: >> "%BACKEND_DIR%\test_vpn.py"
echo         print("Failed to establish VPN connection within timeout period.") >> "%BACKEND_DIR%\test_vpn.py"
echo. >> "%BACKEND_DIR%\test_vpn.py"
echo     # Clean up >> "%BACKEND_DIR%\test_vpn.py"
echo     if vpn_process and vpn_process.poll() is None: >> "%BACKEND_DIR%\test_vpn.py"
echo         print("Terminating VPN process...") >> "%BACKEND_DIR%\test_vpn.py"
echo         vpn_process.terminate() >> "%BACKEND_DIR%\test_vpn.py"
echo. >> "%BACKEND_DIR%\test_vpn.py"
echo except Exception as e: >> "%BACKEND_DIR%\test_vpn.py"
echo     print(f"Error testing VPN connection: {e}") >> "%BACKEND_DIR%\test_vpn.py"
echo. >> "%BACKEND_DIR%\test_vpn.py"
echo input("Press Enter to exit...") >> "%BACKEND_DIR%\test_vpn.py"

echo Test script created successfully.

echo.
echo Setup complete. You can now:
echo 1. Run the test script to verify OpenVPN connection: python %BACKEND_DIR%\test_vpn.py
echo 2. Start the application with VPN support: start_with_vpn.bat
echo.
echo Note: You may need to run these scripts as administrator for OpenVPN to work properly.
echo.
pause