@echo off
title AIESEC Event Radar - Sync Live Site
cd /d "%~dp0"
echo ======================================================================
echo   AIESEC EVENT RADAR - 1-CLICK LIVE SITE SYNCHRONIZER
echo ======================================================================
echo.
echo 1. Scraping Facebook, Instagram, TicketsMarche, Summits, and Universities...
echo    (Using your authenticated Facebook session in headless mode)
echo.
call .venv\Scripts\python.exe scripts\daily_scrape.py
echo.
echo 2. Pushing fresh events directly to your Live Website...
git add events.json docs/events.json aiesec_scraper/web/static/events.json data/
git commit -m "chore(live-sync): update radar events database [manual live sync]"
git push origin main
echo.
echo ======================================================================
echo   SUCCESS! Your live website is updated at:
echo   https://abdelrahmanmotazz.github.io/aiesec-event-radar/
echo ======================================================================
echo.
echo Press any key to exit...
pause >nul
