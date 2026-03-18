@echo off
chcp 65001 > nul
echo ================================================
echo  AI News Digest - Starting server...
echo ================================================
echo.
echo Open browser: http://localhost:8080
echo Press Ctrl+C to stop
echo.
python app.py
pause
