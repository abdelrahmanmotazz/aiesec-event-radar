"""Unit tests for Pipeline date window filtering and deduplication."""

from datetime import datetime, timedelta
from aiesec_scraper.models import EventRecord
from aiesec_scraper.pipeline import EventPipeline, clean_title_for_comparison


def test_clean_title():
    assert clean_title_for_comparison("The Annual Cairo Career Fair 2026!") == "annual cairo career fair 2026"


def test_date_window_filtering():
    pipeline = EventPipeline({"date_window_months": 6})
    now = datetime.now()

    ev_past = EventRecord(
        event_id="1",
        title="Old Event",
        source="Test",
        start_date=now - timedelta(days=10),
        url="http://test.com/1"
    )
    ev_upcoming = EventRecord(
        event_id="2",
        title="Upcoming Conference",
        source="Test",
        start_date=now + timedelta(days=45),
        url="http://test.com/2"
    )
    ev_too_far = EventRecord(
        event_id="3",
        title="Next Year Event",
        source="Test",
        start_date=now + timedelta(days=250),
        url="http://test.com/3"
    )

    filtered = pipeline._filter_date_window([ev_past, ev_upcoming, ev_too_far])
    assert len(filtered) == 1
    assert filtered[0].title == "Upcoming Conference"


def test_deduplication():
    pipeline = EventPipeline()
    now = datetime.now() + timedelta(days=30)

    ev1 = EventRecord(
        event_id="eb_1",
        title="Egypt Tech Summit 2026",
        source="Eventbrite",
        start_date=now,
        url="http://eventbrite.com/1",
        description="Short description"
    )
    ev2 = EventRecord(
        event_id="ae_2",
        title="Egypt Tech Summit 2026 Tickets",
        source="AllEvents",
        start_date=now,
        url="http://allevents.in/2",
        description="Much longer and detailed description of Egypt Tech Summit"
    )

    deduped = pipeline._deduplicate([ev1, ev2])
    assert len(deduped) == 1
    # Check that platforms got merged
    assert "Eventbrite" in deduped[0].source
    assert "AllEvents" in deduped[0].source
    # Richer description was preserved
    assert "detailed description" in deduped[0].description
