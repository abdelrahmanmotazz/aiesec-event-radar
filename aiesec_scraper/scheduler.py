"""Scheduler Module: Supports both continuous loop runs and Windows Task Scheduler scripts."""

import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, Optional

from .pipeline import EventPipeline
from .exporters import GoogleSheetsExporter, LocalExporter

logger = logging.getLogger(__name__)


class ScraperScheduler:
    """Handles recurring 3-day scraping and synchronization jobs."""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.interval_days = self.config.get("schedule_interval_days", 3)
        self.pipeline = EventPipeline(self.config)
        self.local_exporter = LocalExporter(output_dir=self.config.get("output", {}).get("output_dir", "data"))
        self.sheets_exporter = GoogleSheetsExporter(
            service_account_file=self.config.get("output", {}).get("google_sheets", {}).get("service_account_file", "service_account.json"),
            sheet_name=self.config.get("output", {}).get("google_sheets", {}).get("sheet_name", "AIESEC Egypt B2C Event Radar")
        )

    def execute_job(self, city: Optional[str] = None, country: str = "egypt") -> dict:
        """Runs a single pass of the pipeline and synchronizes outputs."""
        start_time = datetime.now()
        logger.info(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] Starting scheduled scrape job...")

        events = self.pipeline.run(city=city, country=country)
        local_res = self.local_exporter.export(events)
        sheets_res = self.sheets_exporter.sync(events)

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Job completed in {duration:.1f}s. Total events: {len(events)}")

        return {
            "timestamp": start_time.isoformat(),
            "total_events": len(events),
            "local_export": local_res,
            "sheets_sync": sheets_res,
            "duration_seconds": duration
        }

    def run_loop(self, interval_days: Optional[int] = None, city: Optional[str] = None, country: str = "egypt"):
        """Continuous background loop running every N days."""
        days = interval_days or self.interval_days
        seconds = days * 24 * 60 * 60

        logger.info(f"Starting recurring scheduler: Running every {days} days. Press Ctrl+C to stop.")
        while True:
            try:
                self.execute_job(city=city, country=country)
                next_run = datetime.now() + timedelta(days=days)
                logger.info(f"Sleeping until next run at {next_run.strftime('%Y-%m-%d %H:%M:%S')}...")
                time.sleep(seconds)
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user.")
                break
            except Exception as e:
                logger.error(f"Error during scheduled execution: {e}")
                logger.info("Retrying in 1 hour...")
                time.sleep(3600)

    @staticmethod
    def generate_windows_task_script(target_dir: str = ".") -> str:
        """
        Creates a Windows .bat script that can be added to Windows Task Scheduler
        to run automatically in the background every 3 days.
        """
        abs_target_dir = os.path.abspath(target_dir)
        python_exe = sys.executable
        bat_content = f"""@echo off
REM AIESEC Egypt B2C Event Scraper Auto-Runner
cd /d "{abs_target_dir}"
"{python_exe}" -m aiesec_scraper.cli run --country egypt
"""
        bat_path = os.path.join(abs_target_dir, "run_scheduled_scrape.bat")
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)

        return os.path.abspath(bat_path)
