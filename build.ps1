# TallyConnect Build Script - PowerShell Wrapper
# This script calls the batch file build script
# Usage: .\build.ps1 or just build (if in PATH)

param()

Write-Host ""
Write-Host "========================================"
Write-Host " TallyConnect Build Script"
Write-Host "========================================"
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Verify build.bat exists
if (-not (Test-Path "build.bat")) {
    Write-Host "[ERROR] build.bat not found in: $scriptDir" -ForegroundColor Red
    exit 1
}

# Run the batch file
Write-Host "Running build.bat..." -ForegroundColor Cyan
& cmd /c "`"$scriptDir\build.bat`""
