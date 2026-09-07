@echo off
title AIESEC Event Radar - Export GitHub Actions Secret
cd /d "%~dp0"
echo ======================================================================
echo   AIESEC EVENT RADAR - EXPORT GITHUB ACTIONS SECRET
echo ======================================================================
echo.
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe scripts\export_gh_secret.py
) else (
    python scripts\export_gh_secret.py
)
echo.
echo Opening GitHub Secrets page in your browser...
start https://github.com/abdelrahmanmotazz/aiesec-event-radar/settings/secrets/actions/new
echo.
echo ----------------------------------------------------------------------
echo  Secret has been copied to your clipboard!
echo  On GitHub:
echo    1. Name: FB_STORAGE_STATE
echo    2. Secret: Press Ctrl+V
echo    3. Click "Add secret"
echo ----------------------------------------------------------------------
echo.
pause
