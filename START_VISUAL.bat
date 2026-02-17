@echo off
REM JARVIS Three.js Launcher - Starts both backend and HTTP server

echo ============================================================
echo JARVIS Three.js Visual System Launcher
echo ============================================================
echo.

REM Start WebSocket backend in new window
echo [1/2] Starting WebSocket backend server...
start "JARVIS Backend" cmd /k ".\jarvis_env\Scripts\python.exe -u backend\websocket_server.py"

REM Wait for backend to initialize
timeout /t 2 /nobreak >nul

REM Start HTTP server for frontend in new window
echo [2/2] Starting HTTP server for visualization...
start "JARVIS Visual Server" cmd /k "cd visual && ..\jarvis_env\Scripts\python.exe -m http.server 8000"

REM Wait for HTTP server to start
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo JARVIS System Ready!
echo ============================================================
echo.
echo WebSocket Backend: ws://localhost:8765
echo Visual Frontend:   http://localhost:8000
echo.
echo Opening visualization in browser...
start http://localhost:8000
echo.
echo Press any key to STOP all servers and exit...
pause >nul

REM Kill both server windows
taskkill /FI "WindowTitle eq JARVIS Backend*" >nul 2>&1
taskkill /FI "WindowTitle eq JARVIS Visual Server*" >nul 2>&1

echo.
echo JARVIS offline. Goodbye.
