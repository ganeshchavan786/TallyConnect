@echo off
REM Create Desktop Shortcut for TallyConnect Portal

echo.
echo ========================================
echo  TallyConnect - Desktop Shortcut Creator
echo ========================================
echo.

set "PROJECT_DIR=%~dp0"
set "PORTAL_HTML=%PROJECT_DIR%reports\portal\index.html"
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\TallyConnect Portal.lnk"

echo Creating desktop shortcut...
echo Portal: %PORTAL_HTML%
echo.

REM Create VBScript to create shortcut
set "VBS=%TEMP%\create_shortcut.vbs"
(
echo Set oWS = WScript.CreateObject("WScript.Shell"^)
echo sLinkFile = "%SHORTCUT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile^)
echo oLink.TargetPath = "%PORTAL_HTML%"
echo oLink.IconLocation = "shell32.dll,13"
echo oLink.Description = "TallyConnect Report Portal"
echo oLink.WorkingDirectory = "%PROJECT_DIR%"
echo oLink.Save
) > "%VBS%"

cscript //nologo "%VBS%"
del "%VBS%"

if exist "%SHORTCUT%" (
    echo.
    echo [SUCCESS] Desktop shortcut created!
    echo Location: %SHORTCUT%
    echo.
    echo You can now double-click "TallyConnect Portal" on your desktop
    echo to open the report portal.
) else (
    echo.
    echo [ERROR] Failed to create shortcut.
    echo.
    echo Manual method:
    echo 1. Right-click on Desktop
    echo 2. New ^> Shortcut
    echo 3. Browse to: %PORTAL_HTML%
    echo 4. Name it: TallyConnect Portal
)

echo.
pause

