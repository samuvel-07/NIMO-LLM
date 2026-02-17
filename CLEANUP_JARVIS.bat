@echo off
REM JARVIS Complete Cleanup Script
REM Gracefully terminates all processes and removes build artifacts

echo.
echo ============================================================
echo      JARVIS GRACEFUL SHUTDOWN ^& CLEANUP
echo ============================================================
echo.
echo This will:
echo  - Terminate all JARVIS processes gracefully
echo  - Release GPU resources and WebSocket connections  
echo  - Delete virtual environment (jarvis_env)
echo  - Delete Python cache (__pycache__)
echo  - Delete temporary files and speech models
echo  - Preserve all source code and configuration
echo.
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please ensure Python is installed and accessible
    pause
    exit /b 1
)

echo WARNING: This will delete approximately 200+ MB of data
echo.
set /p CONFIRM="Type 'YES' to confirm cleanup (or anything else to cancel): "

if /i not "%CONFIRM%"=="YES" (
    echo.
    echo Cleanup cancelled by user.
    echo.
    pause
    exit /b 0
)

echo.
echo ============================================================
echo Starting cleanup...
echo ============================================================
echo.

REM Run the Python cleanup script
python cleanup_jarvis.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo Cleanup completed with warnings
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo Cleanup completed successfully
    echo ============================================================
)

echo.
echo Press any key to exit...
pause >nul
