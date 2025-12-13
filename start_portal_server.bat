@echo off
REM TallyConnect Portal Server - One-Click Start
REM No manual generation needed - reports generated on-demand!

echo.
echo ========================================
echo  TallyConnect Portal Server
echo ========================================
echo.
echo Starting server...
echo Reports will be generated automatically when you click them!
echo.
echo Portal will open in your browser automatically.
echo.
echo Press Ctrl+C to stop the server.
echo.

cd /d "%~dp0"
python portal_server.py

pause

