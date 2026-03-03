@echo off
REM ===================================================
REM   JARVIS Auto-Start — REMOVE from Windows Startup
REM ===================================================

set SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\JARVIS.lnk

if not exist "%SHORTCUT%" (
    echo [!] JARVIS auto-start is not enabled.
    pause
    exit /b
)

del "%SHORTCUT%"
echo [OK] JARVIS auto-start disabled.
echo     It will no longer launch on boot.
pause
