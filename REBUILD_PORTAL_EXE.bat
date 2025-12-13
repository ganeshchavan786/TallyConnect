@echo off
REM Quick rebuild script for Portal EXE only
REM Use this after making changes to portal_server.py

echo.
echo ========================================
echo  Rebuilding TallyConnectPortal.exe
echo ========================================
echo.

REM Clean previous build
if exist "build\TallyConnectPortal" rmdir /s /q "build\TallyConnectPortal"
if exist "dist\TallyConnectPortal.exe" del /q "dist\TallyConnectPortal.exe"

echo [1/2] Building TallyConnectPortal.exe...
python -m PyInstaller --clean --noconfirm TallyConnectPortal.spec

if not exist "dist\TallyConnectPortal.exe" (
    echo [ERROR] Build failed! TallyConnectPortal.exe not created
    pause
    exit /b 1
)

echo.
echo [SUCCESS] TallyConnectPortal.exe rebuilt successfully!
echo Location: dist\TallyConnectPortal.exe
echo.
echo [2/2] Testing EXE...
echo.
echo Running EXE to verify portal directory is found...
echo.

REM Test run (will exit quickly if portal found)
timeout /t 2 /nobreak >nul
start "" "dist\TallyConnectPortal.exe"

echo.
echo ========================================
echo  Rebuild Complete!
echo ========================================
echo.
echo If portal directory error appears, check:
echo 1. Reports directory exists in project root
echo 2. TallyConnectPortal.spec includes reports in datas
echo.
pause

