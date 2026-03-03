@echo off
setlocal
title JARVIS

REM ============================================================
REM   JARVIS — Silent Professional Launcher
REM   Backend runs hidden (pythonw.exe), only Electron UI visible
REM ============================================================

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

REM === Prevent Multiple Instances ===
tasklist /FI "IMAGENAME eq pythonw.exe" 2>nul | findstr /i "pythonw.exe" >nul
if %errorlevel%==0 (
    echo [!] JARVIS backend already running. Launching UI only...
    goto :launch_ui
)

REM === Install desktop dependencies on first run ===
if not exist "%PROJECT_DIR%desktop\node_modules" (
    echo [1/3] Installing dependencies...
    cd /d "%PROJECT_DIR%desktop"
    npm install
    cd /d "%PROJECT_DIR%"
) else (
    echo [1/3] Dependencies OK
)

REM === Start Backend Silently (No Console Window) ===
echo [2/3] Starting JARVIS Brain (silent)...
start "" /B "%PROJECT_DIR%.venv_gpu\Scripts\pythonw.exe" "%PROJECT_DIR%run_brain.py"

REM === Wait for Backend + WebSocket to Initialize ===
echo      Waiting for neural core...
timeout /t 4 /nobreak >nul

:launch_ui
REM === Launch Electron Desktop ===
echo [3/3] Launching JARVIS Desktop...
cd /d "%PROJECT_DIR%desktop"
node launch.js --dev

REM === Electron closed — Clean up backend ===
echo.
echo [SHUTDOWN] Cleaning up...
taskkill /F /IM pythonw.exe 2>nul
echo [OK] JARVIS shutdown complete.
timeout /t 2 /nobreak >nul
exit
