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
if exist "%~dp0.jarvis_ready" del "%~dp0.jarvis_ready"

REM Start Python backend in a new window, piping output to the console but also touching a ready flag
start "JARVIS Backend" /min cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && cd /d "%~dp0" && call .venv_gpu\Scripts\activate && python run_brain.py"

echo    Waiting for AI Models to load into GPU (This prevents system stutter)...
:waitloop
if exist "%~dp0.jarvis_ready" goto :launch_electron
timeout /t 1 /nobreak >nul
goto :waitloop

:launch_electron

REM ── Launch Electron via clean-env launcher ──
echo [3/3] Launching JARVIS Desktop...
cd /d "%~dp0desktop"
node launch.js

echo.
echo ============================================================
echo    JARVIS Desktop closed.
echo ============================================================

REM ── Cleanup backend ──
taskkill /F /T /FI "WindowTitle eq JARVIS Backend*" >nul 2>&1

echo Goodbye.
pause
