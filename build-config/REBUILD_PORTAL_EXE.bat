@echo off
REM Quick rebuild script for Portal EXE only
REM Use this after making changes to portal_server.py

echo.
echo ========================================
echo  Rebuilding TallyConnectPortal.exe
echo ========================================
echo.

REM Kill running EXE if it exists
echo [0/2] Checking for running EXE...
tasklist /FI "IMAGENAME eq TallyConnectPortal.exe" 2>NUL | find /I /N "TallyConnectPortal.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [INFO] TallyConnectPortal.exe is running. Closing it...
    taskkill /F /IM TallyConnectPortal.exe /T >NUL 2>&1
    timeout /t 2 /nobreak >NUL
)

REM Clean previous build
echo [INFO] Cleaning previous build...
if exist "build\TallyConnectPortal" rmdir /s /q "build\TallyConnectPortal"
if exist "dist\TallyConnectPortal.exe" (
    REM Try to delete, if fails, file is locked
    del /q "dist\TallyConnectPortal.exe" 2>NUL
    if exist "dist\TallyConnectPortal.exe" (
        echo [WARNING] Cannot delete TallyConnectPortal.exe - file may be locked
        echo [INFO] Please close any running instances and try again
        pause
        exit /b 1
    )
)

echo [1/2] Building TallyConnectPortal.exe...
cd /d "%~dp0\.."
python scripts\generate_windows_icons.py --input Logo.png --out build-config\TallyConnect.ico >nul 2>&1
python -m PyInstaller --clean --noconfirm build-config/TallyConnectPortal.spec

if not exist "dist\TallyConnectPortal.exe" (
    echo [ERROR] Build failed! TallyConnectPortal.exe not created
    pause
    exit /b 1
)

echo.
echo [SUCCESS] TallyConnectPortal.exe rebuilt successfully!
echo Location: dist\TallyConnectPortal.exe
if exist "build-config\TallyConnect.ico" (
    copy /y "build-config\TallyConnect.ico" "dist\TallyConnect.ico" >nul
)
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
echo 1. Frontend directory exists in project root
echo 2. TallyConnectPortal.spec includes frontend in datas
echo.
pause

