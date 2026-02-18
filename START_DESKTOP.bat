@echo off
REM JARVIS Desktop Widget Launcher
REM Uses launch.js to clear ELECTRON_RUN_AS_NODE before spawning Electron

echo.
echo ============================================================
echo    JARVIS Desktop AI Presence v3.0
echo ============================================================
echo.

REM ── Install dependencies on first run ──
if not exist "%~dp0desktop\node_modules" (
    echo [1/3] Installing dependencies...
    cd /d "%~dp0desktop"
    npm install
    cd /d "%~dp0"
) else (
    echo [1/3] Dependencies OK
)

REM ── Start WebSocket backend ──
echo [2/3] Starting WebSocket backend...
start "JARVIS Backend" /min cmd /k "cd /d "%~dp0" && python run_brain.py"
timeout /t 2 /nobreak >nul

REM ── Launch Electron via clean-env launcher ──
echo [3/3] Launching JARVIS Desktop...
cd /d "%~dp0desktop"
node launch.js --dev

echo.
echo ============================================================
echo    JARVIS Desktop closed.
echo ============================================================

REM ── Cleanup backend ──
taskkill /FI "WindowTitle eq JARVIS Backend*" >nul 2>&1

echo Goodbye.
pause
