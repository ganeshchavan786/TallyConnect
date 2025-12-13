@echo off
REM TallyConnect Portal - Quick Start Script

echo.
echo ========================================
echo  TallyConnect Portal - Quick Start
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Generating portal...
python generate_portal.py

if errorlevel 1 (
    echo.
    echo [ERROR] Portal generation failed!
    echo Please check Python is installed and database exists.
    pause
    exit /b 1
)

echo.
echo [2/2] Opening portal in browser...
start "" "reports\portal\index.html"

echo.
echo ========================================
echo  Portal opened in browser!
echo ========================================
echo.
echo Usage:
echo  1. Click on Company
echo  2. Select Report Type
echo  3. (For Ledger) Select Ledger
echo  4. View Report!
echo.
echo Tip: You can also create desktop shortcut:
echo  create_desktop_shortcut.bat
echo.
pause

