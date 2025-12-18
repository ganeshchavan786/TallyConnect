@echo off
REM TallyConnect Build Script
REM Builds executable and installer

echo.
echo ========================================
echo  TallyConnect v5.6 - Build Script
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.x
    pause
    exit /b 1
)

echo [1/4] Checking dependencies...
pip show pyodbc >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing pyodbc...
    pip install pyodbc
)

pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing PyInstaller...
    pip install pyinstaller
)

echo.
echo [2/5] Preparing branding (Logo.png -> .ico)...
cd /d "%~dp0\.."
python scripts\generate_windows_icons.py --input Logo.png --out build-config\TallyConnect.ico >nul 2>&1
python scripts\write_build_info.py >nul 2>&1

echo.
echo [3/5] Cleaning previous build...
cd /d "%~dp0\.."
if exist "build" rmdir /s /q "build"
if exist "dist\TallyConnect.exe" del /q "dist\TallyConnect.exe"

echo.
echo [4/5] Building TallyConnect.exe...
python -m PyInstaller --clean --noconfirm build-config/TallyConnect.spec

if not exist "dist\TallyConnect.exe" (
    echo [ERROR] Build failed! TallyConnect.exe not created
    pause
    exit /b 1
)

echo.
echo [SUCCESS] TallyConnect.exe created successfully!
echo Location: dist\TallyConnect.exe
if exist "build-config\TallyConnect.ico" (
    copy /y "build-config\TallyConnect.ico" "dist\TallyConnect.ico" >nul
)

echo.
echo [5/5] Building TallyConnectPortal.exe...
python -m PyInstaller --clean --noconfirm build-config/TallyConnectPortal.spec

if not exist "dist\TallyConnectPortal.exe" (
    echo [WARNING] Portal EXE build failed, but continuing...
) else (
    echo [SUCCESS] TallyConnectPortal.exe created successfully!
    echo Location: dist\TallyConnectPortal.exe
)

echo.
echo [OPTIONAL] Would you like to create installer? (Requires Inno Setup)
echo Press Y to create installer, or any other key to skip...
choice /c YN /n /m "Create installer? (Y/N): "

if errorlevel 2 goto :skip_installer
if errorlevel 1 goto :create_installer

:create_installer
echo.
echo Building installer with Inno Setup...

REM Check if Inno Setup is installed
set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%INNO_PATH%" (
    set "INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if not exist "%INNO_PATH%" (
    echo [WARNING] Inno Setup not found at default location
    echo Please install Inno Setup from: https://jrsoftware.org/isinfo.php
    echo Or compile TallyConnectInstaller.iss manually
    goto :skip_installer
)

"%INNO_PATH%" "%~dp0TallyConnectInstaller.iss"

if exist "dist\TallyConnectSetup_v5.6.exe" (
    echo.
    echo [SUCCESS] Installer created successfully!
    echo Location: dist\TallyConnectSetup_v5.6.exe
) else (
    echo [WARNING] Installer creation failed
)

:skip_installer
echo.
echo ========================================
echo  Build Complete!
echo ========================================
echo.
echo Files created:
if exist "dist\TallyConnect.exe" echo   - dist\TallyConnect.exe
if exist "dist\TallyConnectPortal.exe" echo   - dist\TallyConnectPortal.exe
if exist "dist\TallyConnectSetup_v5.6.exe" echo   - dist\TallyConnectSetup_v5.6.exe
echo.
echo You can now run TallyConnect.exe or distribute the installer
echo.
pause

