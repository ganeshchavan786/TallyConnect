@echo off
REM TallyConnect Build Script - Wrapper
REM This script calls the main build script from build-config/
REM Kept in root for easy access

cd /d "%~dp0"
call build-config\build.bat

