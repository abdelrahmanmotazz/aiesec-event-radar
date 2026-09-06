@echo off
title AIESEC Event Radar - Full Scraper
cd /d "%~dp0"
echo ======================================================================
echo   AIESEC EVENT RADAR - FULL PIPELINE SCRAPER
echo ======================================================================
echo.
echo Scraping Facebook, Instagram, TicketsMarche, Summits, and University portals...
call .venv\Scripts\python.exe scripts\daily_scrape.py
echo.
echo Scrape complete! Press any key to exit...
pause >nul
