@echo off
echo ========================================
echo Virtual Partner - Render Deployment Setup
echo ========================================
echo.

echo Step 1: Initializing Git repository...
git init
if %errorlevel% neq 0 (
    echo ERROR: Git not found. Please install Git first.
    pause
    exit /b 1
)

echo.
echo Step 2: Adding files to Git...
git add .
if %errorlevel% neq 0 (
    echo ERROR: Failed to add files.
    pause
    exit /b 1
)

echo.
echo Step 3: Creating initial commit...
git commit -m "Initial commit - Ready for Render deployment"
if %errorlevel% neq 0 (
    echo ERROR: Failed to create commit.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Git repository initialized successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Create a repository on GitHub.com
echo 2. Run these commands (replace YOUR_USERNAME with your GitHub username):
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/virtual-partner.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 3. Then follow the instructions in RENDER_DEPLOYMENT.md
echo.
pause

