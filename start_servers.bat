@echo off
echo === Starting Dark Web Monitoring Tool ===
echo.

REM Start the backend server
start cmd /k "cd backend && python app.py"

REM Wait for backend to start
echo Waiting for backend server to start...
timeout /t 5 /nobreak > nul

REM Start the frontend server
start cmd /k "cd frontend && python -m http.server 8000"

REM Open the browser
echo Opening browser...
timeout /t 2 /nobreak > nul
start http://localhost:8000

echo.
echo Servers started successfully!
echo - Backend: http://localhost:5000
echo - Frontend: http://localhost:8000
echo.
echo Press any key to exit this window (servers will continue running)
pause > nul