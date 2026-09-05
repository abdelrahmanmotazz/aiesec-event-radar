"""Automated Daily Event Scraper & Multi-Target Synchronizer.

Executed by GitHub Actions on a daily cron schedule to update the live
AIESEC Radar database without requiring any paid server infrastructure.
"""

import json
import logging
import os
import sys
from datetime import datetime

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from aiesec_scraper.pipeline import EventPipeline
from aiesec_scraper.exporters.local import LocalExporter
from aiesec_scraper.models import EventRecord

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("daily_scraper")


def run_daily_scrape():
    logger.info("=== Starting Automated Daily AIESEC Event Scrape ===")
    start_time = datetime.now()

    # Load configuration if available
    config = {}
    config_path = os.path.join(PROJECT_ROOT, "config.yaml")
    if os.path.exists(config_path):
        try:
            import yaml
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Could not load config.yaml: {e}")

    pipeline = EventPipeline(config)
    logger.info("Running concurrent multi-source scraper (Egypt nationwide & Delta/Tanta hubs)...")
    
    try:
        events = pipeline.run(city=None, country="egypt")
    except Exception as e:
        logger.error(f"Critical error during pipeline execution: {e}")
        events = []

    logger.info(f"Pipeline finished. Retrieved {len(events)} processed & scored events.")

    # Safeguard: If live scraping produced zero events (e.g. rate limit), do not wipe existing data
    root_events_json = os.path.join(PROJECT_ROOT, "events.json")
    if not events and os.path.exists(root_events_json):
        logger.warning("Zero events returned by live scrapers! Preserving existing database.")
        sys.exit(0)

    # 1. Export Excel and CSV to data/ directory
    data_dir = os.path.join(PROJECT_ROOT, "data")
    local_exporter = LocalExporter(output_dir=data_dir)
    export_res = local_exporter.export(events)
    logger.info(f"Updated Excel & CSV in {data_dir}: {export_res.get('total_records')} records.")

    # 2. Synchronize events.json across all deploy targets
    # Mode 'json' ensures datetimes and Pydantic models serialize cleanly
    json_payload = [e.model_dump(mode="json") for e in events]
    json_data = json.dumps(json_payload, indent=2, ensure_ascii=False)

    target_json_paths = [
        os.path.join(PROJECT_ROOT, "events.json"),
        os.path.join(PROJECT_ROOT, "aiesec_scraper", "web", "static", "events.json"),
        os.path.join(PROJECT_ROOT, "docs", "events.json"),
    ]

    for path in target_json_paths:
        parent = os.path.dirname(path)
        if os.path.exists(parent):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(json_data)
                logger.info(f"✓ Synchronized: {os.path.relpath(path, PROJECT_ROOT)}")
            except Exception as write_err:
                logger.error(f"Failed writing to {path}: {write_err}")

    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(f"=== Daily Scrape Finished Successfully in {elapsed:.1f}s ===")
    logger.info(f"Total Unique Events in Radar: {len(events)}")


if __name__ == "__main__":
    run_daily_scrape()
