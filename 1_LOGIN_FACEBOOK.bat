@echo off
title AIESEC Event Radar - Facebook Login Setup (Arkose-Safe)
cd /d "%~dp0"
echo ======================================================================
echo   AIESEC EVENT RADAR - GENUINE EDGE FACEBOOK LOGIN (ARKOSE-SAFE)
echo ======================================================================
echo.
echo Launching genuine Microsoft Edge natively (No automation flags)...
echo 1. Complete your Facebook login and 2FA in the Edge window that opens.
echo 2. Once your Facebook Events feed loads, return here and press ENTER.
echo.
call .venv\Scripts\python.exe scripts\login_meta.py
echo.
echo Done! Session saved. Press any key to exit...
pause >nul
