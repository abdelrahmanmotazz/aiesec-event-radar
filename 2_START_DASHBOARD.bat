@echo off
title AIESEC Event Radar - Web Dashboard
cd /d "%~dp0"
echo ======================================================================
echo   AIESEC EVENT RADAR - DASHBOARD SERVER
echo ======================================================================
echo.
echo Starting dashboard server at http://localhost:8000 ...
echo Opening your browser in 2 seconds...
echo Press Ctrl+C in this window to stop the server.
echo.
timeout /t 2 /nobreak >nul
start http://localhost:8000
call .venv\Scripts\python.exe -m aiesec_scraper.web
pause
