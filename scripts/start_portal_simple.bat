@echo off
REM Simple Portal Starter - Can be run from anywhere
REM This script automatically navigates to project root

echo.
echo ========================================
echo  TallyConnect Portal - Starting...
echo ========================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Navigate to project root (parent of scripts folder)
cd /d "%SCRIPT_DIR%.."

REM Check if we're in the right place
if not exist "backend\portal_launcher.py" (
    echo [ERROR] Could not find backend\portal_launcher.py
    echo Current directory: %CD%
    echo.
    echo Please ensure this script is in the scripts folder.
    pause
    exit /b 1
)

echo [INFO] Project root: %CD%
echo [INFO] Starting portal server...
echo.
echo Portal will open automatically in your browser.
echo Press Ctrl+C in this window to stop the server.
echo.

REM Start portal server
python -m backend.portal_launcher

REM If server exits, pause to show any errors
if errorlevel 1 (
    echo.
    echo [ERROR] Portal server failed to start.
    pause
)

