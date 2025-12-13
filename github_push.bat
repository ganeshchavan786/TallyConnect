@echo off
REM TallyConnect - GitHub Push Script
REM Replace YOUR_USERNAME with your actual GitHub username

echo.
echo ========================================
echo  TallyConnect - GitHub Setup
echo ========================================
echo.

REM Set your GitHub username here
set GITHUB_USER=ganeshchavan786

echo [1/3] Setting up remote repository...
git remote remove origin 2>nul
git remote add origin https://github.com/%GITHUB_USER%/TallyConnect.git

echo.
echo [2/3] Verifying branch...
git branch -M main

echo.
echo [3/3] Pushing to GitHub...
echo.
echo You will be prompted for:
echo  - Username: Your GitHub username
echo  - Password: Your Personal Access Token (NOT your GitHub password!)
echo.
echo If you don't have a token, create one at:
echo https://github.com/settings/tokens/new
echo (Select scope: repo - Full control)
echo.
pause

git push -u origin main

if errorlevel 1 (
    echo.
    echo [ERROR] Push failed!
    echo.
    echo Common issues:
    echo  1. Wrong username in this script (line 9)
    echo  2. Need Personal Access Token (not password)
    echo  3. Repository not created on GitHub
    echo.
    echo Create token: https://github.com/settings/tokens/new
    pause
    exit /b 1
)

echo.
echo ========================================
echo  SUCCESS! Code pushed to GitHub
echo ========================================
echo.
echo Repository URL:
echo https://github.com/%GITHUB_USER%/TallyConnect
echo.
echo Next steps:
echo  1. Visit the URL above to see your code
echo  2. Share the repository with team
echo  3. Set up branch protection (optional)
echo.
pause

