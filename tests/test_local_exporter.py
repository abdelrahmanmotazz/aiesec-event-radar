"""Tests for local Excel and CSV exporters."""

import os
from datetime import datetime
from aiesec_scraper.models import EventRecord
from aiesec_scraper.exporters.local import LocalExporter


def test_excel_and_csv_generation(tmp_path):
    exporter = LocalExporter(output_dir=str(tmp_path))
    events = [
        EventRecord(
            event_id="test_1",
            title="Alexandria Leadership Bootcamp",
            source="Meetup",
            start_date=datetime(2026, 11, 15, 10, 0),
            date_display="Nov 15, 2026 · 10:00 AM",
            location="Alexandria Bibliotheca",
            city="Alexandria",
            country="Egypt",
            url="https://meetup.com/alex-leadership",
            ticket_type="Free",
            organizer="Alexandria Youth Club",
            description="Intensive leadership skills workshop for university students.",
            category="Leadership & Skills Workshops",
            aiesec_tags=["leadership", "skills", "student"],
            b2c_score=9.2,
            b2c_priority="HIGH",
            recommended_action="Speaker Outreach & Presentation"
        )
    ]

    res = exporter.export(events, base_filename="test_run")
    assert os.path.exists(res["excel_latest"])
    assert os.path.exists(res["csv_latest"])
    assert res["total_records"] == 1
