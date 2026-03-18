@echo off
chcp 65001 > nul
echo ================================================
echo  AI News Digest - Setup
echo ================================================
echo.

echo [1/3] Installing Python packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: pip install failed
    pause
    exit /b 1
)

echo.
echo [2/3] Installing Playwright browser (for Nikkei)...
playwright install chromium
if %errorlevel% neq 0 (
    echo WARNING: Playwright install failed. Nikkei scraping will be skipped.
)

echo.
echo [3/3] Checking .env file...
if not exist .env (
    copy .env.example .env
    echo Created .env file from .env.example
)

echo.
echo ================================================
echo  Setup complete!
echo  Edit .env file, then run run.bat
echo ================================================
pause
