@echo off
REM ===================================================
REM   JARVIS Auto-Start — ADD to Windows Startup
REM ===================================================
REM Creates a shortcut in the Startup folder so JARVIS
REM launches automatically when Windows boots.

set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT=%STARTUP%\JARVIS.lnk

if exist "%SHORTCUT%" (
    echo [!] JARVIS auto-start is already enabled.
    echo     Location: %SHORTCUT%
    pause
    exit /b
)

REM Create shortcut via PowerShell
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%~dp0START_DESKTOP.bat'; $s.WorkingDirectory = '%~dp0'; $s.Description = 'JARVIS AI Desktop'; $s.Save()"

echo [OK] JARVIS will now auto-start on boot!
echo     Shortcut: %SHORTCUT%
echo.
echo     To disable: run AUTOSTART_OFF.bat
pause
