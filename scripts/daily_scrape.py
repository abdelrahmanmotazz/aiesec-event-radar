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

from aiesec_scraper.pipeline import EventPipeline, normalize_egypt_city
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

    logger.info(f"Scrape pass finished. Retrieved {len(events)} newly scraped events.")

    # Load existing database to accumulate events across runs
    existing_events = []
    root_events_json = os.path.join(PROJECT_ROOT, "events.json")
    if os.path.exists(root_events_json):
        try:
            with open(root_events_json, "r", encoding="utf-8") as f:
                raw_existing = json.load(f)
                for item in raw_existing:
                    try:
                        existing_events.append(EventRecord(**item))
                    except Exception:
                        pass
            logger.info(f"Loaded {len(existing_events)} existing events from local database.")
        except Exception as read_err:
            logger.warning(f"Could not read existing events.json: {read_err}")

    # Combine fresh live scraped events with existing accumulated events
    combined_events = events + existing_events
    if not combined_events:
        logger.warning("Zero events available! Preserving existing database.")
        sys.exit(0)

    # Re-apply calibrated B2C scoring to all combined records
    for ev in combined_events:
        score, priority, category, tags, action, parallel_org = pipeline.scorer.evaluate(
            title=ev.title,
            description=ev.description,
            location=ev.location
        )
        is_summit = (ev.source == "Egypt Flagship Summits" or "summit" in ev.source.lower())
        ev.b2c_score = max(score, 9.2) if is_summit else score
        ev.b2c_priority = "HIGH" if is_summit else priority
        ev.category = "Flagship Summits" if is_summit else category
        ev.aiesec_tags = tags
        if not ev.recommended_action or not is_summit:
            ev.recommended_action = action
        ev.city = normalize_egypt_city(ev.city, ev.title, ev.location)
        if parallel_org and not ev.parallel_org:
            ev.parallel_org = parallel_org

    # Re-apply date window filtering, quality filtering, and fuzzy deduplication
    valid_events = pipeline._filter_date_window(combined_events)
    deduped_events = pipeline._deduplicate(valid_events)
    pipeline._apply_clash_detection(deduped_events)
    pipeline._enrich_organizer_contacts(deduped_events)

    deduped_events.sort(key=lambda x: (
        x.start_date is None,
        x.start_date or datetime.max,
        -x.b2c_score
    ))
    events = deduped_events
    logger.info(f"Combined & deduplicated database contains {len(events)} verified Egyptian events.")

    # 1. Export Excel and CSV to data/ directory
    data_dir = os.path.join(PROJECT_ROOT, "data")
    local_exporter = LocalExporter(output_dir=data_dir)
    export_res = local_exporter.export(events)
    logger.info(f"Updated Excel & CSV in {data_dir}: {export_res.get('total_records')} records.")

    # 2. Synchronize events.json and events-data.js across all deploy targets
    # Mode 'json' ensures datetimes and Pydantic models serialize cleanly
    json_payload = [e.model_dump(mode="json") for e in events]
    json_data = json.dumps(json_payload, indent=2, ensure_ascii=False)
    js_data = (
        f"// Auto-generated AIESEC Radar Events Data\n"
        f"window.RADAR_DATASET_VERSION = '{datetime.now().strftime('%Y-%m-%d_%H%M')}';\n"
        f"window.AIESEC_INITIAL_EVENTS = {json_data};\n"
        f"window.RADAR_STATIC_EVENTS = window.AIESEC_INITIAL_EVENTS;\n"
        f"window.__AIESEC_EVENTS__ = window.AIESEC_INITIAL_EVENTS;\n"
    )

    target_json_paths = [
        os.path.join(PROJECT_ROOT, "events.json"),
        os.path.join(PROJECT_ROOT, "aiesec_scraper", "web", "static", "events.json"),
        os.path.join(PROJECT_ROOT, "docs", "events.json"),
    ]
    target_js_paths = [
        os.path.join(PROJECT_ROOT, "events-data.js"),
        os.path.join(PROJECT_ROOT, "aiesec_scraper", "web", "static", "events-data.js"),
        os.path.join(PROJECT_ROOT, "docs", "events-data.js"),
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

    for path in target_js_paths:
        parent = os.path.dirname(path)
        if os.path.exists(parent):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(js_data)
                logger.info(f"✓ Synchronized: {os.path.relpath(path, PROJECT_ROOT)}")
            except Exception as write_err:
                logger.error(f"Failed writing to {path}: {write_err}")

    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(f"=== Daily Scrape Finished Successfully in {elapsed:.1f}s ===")
    logger.info(f"Total Unique Events in Radar: {len(events)}")


if __name__ == "__main__":
    run_daily_scrape()
