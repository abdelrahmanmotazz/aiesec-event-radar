@echo off
title AIESEC Event Radar - Facebook Login Setup
cd /d "%~dp0"
echo ======================================================================
echo   AIESEC EVENT RADAR - ONE-TIME FACEBOOK SESSION LOGIN
echo ======================================================================
echo.
echo Launching Microsoft Edge...
echo 1. Log in to your Facebook account in the Edge window that opens.
echo 2. Once logged in, return to this black window and press ENTER.
echo.
call .venv\Scripts\python.exe scripts\login_meta.py
echo.
echo Done! Press any key to exit...
pause >nul
