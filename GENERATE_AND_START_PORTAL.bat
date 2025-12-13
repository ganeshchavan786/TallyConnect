@echo off
REM TallyConnect Portal - Generate Reports and Start Server
REM Use this if you need to regenerate portal reports first

echo.
echo ========================================
echo  TallyConnect Portal - Generate & Start
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.x
    pause
    exit /b 1
)

echo [1/2] Generating portal reports...
python generate_portal.py

if errorlevel 1 (
    echo.
    echo [ERROR] Portal generation failed!
    pause
    exit /b 1
)

echo.
echo [2/2] Starting portal server...
echo.
echo Portal will open automatically in your browser.
echo Press Ctrl+C in this window to stop the server.
echo.

REM Start portal server
python portal_server.py

REM If server exits, pause to show any errors
if errorlevel 1 (
    echo.
    echo [ERROR] Portal server failed to start.
    pause
)

