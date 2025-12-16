@echo off
REM TallyConnect Portal - One-Click Start for Developers
REM Double-click this file to start the portal server

echo.
echo ========================================
echo  TallyConnect Portal - Starting...
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.x
    pause
    exit /b 1
)

REM Change to project root directory
cd /d "%~dp0\.."

REM Check if backend/portal_launcher.py exists
if not exist "backend\portal_launcher.py" (
    echo [ERROR] backend\portal_launcher.py not found!
    echo Please run this from the project root directory.
    pause
    exit /b 1
)

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

