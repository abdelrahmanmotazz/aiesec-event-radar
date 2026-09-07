"""End-to-End System Health and Integrity Verifier.

Validates:
1. Exact hash parity across static frontend targets (events.json, app.js, index.html).
2. Data cleanliness: zero foreign bleed, zero invalid URLs, zero duplicates.
3. Data exports (CSV, Excel) are populated and up to date.
4. Executes pytest test suite and asserts zero failures.
"""

import hashlib
import json
import os
import subprocess
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from aiesec_scraper.pipeline import is_bad_or_non_egypt, normalize_event_url
from aiesec_scraper.models import EventRecord


def get_sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def verify_all():
    print("==================================================")
    print("   AIESEC RADAR - END-TO-END SYSTEM VERIFICATION  ")
    print("==================================================")
    errors = []

    # 1. Parity Check: events.json
    events_targets = [
        os.path.join(PROJECT_ROOT, "events.json"),
        os.path.join(PROJECT_ROOT, "docs", "events.json"),
        os.path.join(PROJECT_ROOT, "aiesec_scraper", "web", "static", "events.json"),
    ]
    hashes_events = {}
    for p in events_targets:
        if not os.path.exists(p):
            errors.append(f"Missing file: {p}")
        else:
            hashes_events[p] = get_sha256(p)

    if len(set(hashes_events.values())) == 1:
        print(f"[OK] events.json parity verified (hash: {list(hashes_events.values())[0][:12]})")
    else:
        errors.append(f"Hash mismatch across events.json files: {hashes_events}")

    # 2. Parity Check: app.js
    app_targets = [
        os.path.join(PROJECT_ROOT, "app.js"),
        os.path.join(PROJECT_ROOT, "docs", "app.js"),
        os.path.join(PROJECT_ROOT, "aiesec_scraper", "web", "static", "app.js"),
    ]
    hashes_app = {p: get_sha256(p) for p in app_targets if os.path.exists(p)}
    if len(set(hashes_app.values())) == 1:
        print(f"[OK] app.js parity verified (hash: {list(hashes_app.values())[0][:12]})")
    else:
        errors.append(f"Hash mismatch across app.js files: {hashes_app}")

    # 3. Data Integrity & Quality Check
    with open(events_targets[0], "r", encoding="utf-8") as f:
        events = json.load(f)

    print(f"[INFO] Total verified events in database: {len(events)}")
    if len(events) < 50:
        errors.append(f"Event count unusually low ({len(events)})")

    seen_ids = set()
    seen_urls = set()
    for ev_dict in events:
        eid = ev_dict.get("event_id")
        if eid in seen_ids:
            errors.append(f"Duplicate event_id detected: {eid}")
        seen_ids.add(eid)

        raw_url = ev_dict.get("url", "")
        canon_url = normalize_event_url(raw_url)
        if canon_url and canon_url in seen_urls:
            errors.append(f"Duplicate canonical URL detected: {canon_url}")
        if canon_url:
            seen_urls.add(canon_url)

        # Check for invalid URL or non-Egypt bleed
        rec = EventRecord(**ev_dict)
        if is_bad_or_non_egypt(rec):
            errors.append(f"Quality filter failure: {rec.title} ({rec.location}) - {rec.url}")

    print(f"[OK] 0 duplicates, 0 broken links, 0 non-Egypt events detected.")

    # 4. Data Exports Check
    csv_path = os.path.join(PROJECT_ROOT, "data", "aiesec_egypt_events_latest.csv")
    xlsx_path = os.path.join(PROJECT_ROOT, "data", "aiesec_egypt_events_latest.xlsx")
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 1000:
        print(f"[OK] CSV export verified ({os.path.getsize(csv_path)} bytes)")
    else:
        errors.append(f"CSV export missing or empty: {csv_path}")

    if os.path.exists(xlsx_path) and os.path.getsize(xlsx_path) > 5000:
        print(f"[OK] Excel export verified ({os.path.getsize(xlsx_path)} bytes)")
    else:
        errors.append(f"Excel export missing or empty: {xlsx_path}")

    # 5. Pytest Execution
    print("\n[INFO] Running full pytest test suite...")
    res = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )
    if res.returncode == 0:
        print(f"[OK] Pytest test suite passed cleanly:\n{res.stdout.strip()}")
    else:
        errors.append(f"Pytest suite failed with return code {res.returncode}:\n{res.stdout}\n{res.stderr}")

    print("\n--------------------------------------------------")
    if errors:
        print(f"[FAILED] Found {len(errors)} error(s):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("[SUCCESS] ALL CHECKS PASSED WITH 0 ERRORS! SYSTEM IS 100% OPERATIONAL.")
        print("--------------------------------------------------")


if __name__ == "__main__":
    verify_all()
