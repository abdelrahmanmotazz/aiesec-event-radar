"""Unit tests for EventSearchIndex FTS5 engine."""

from aiesec_scraper.models import EventRecord
from aiesec_scraper.search_index import EventSearchIndex


def test_fts5_indexing_and_search():
    events = [
        EventRecord(
            event_id="ev_riseup_1",
            title="RiseUp Summit 2026",
            source="Manual",
            url="https://riseupsummit.com",
            description="The premier startup and entrepreneurship summit in Cairo.",
            city="Cairo",
            location="The Grand Museum",
            category="Startup Competition",
            organizer="RiseUp"
        ),
        EventRecord(
            event_id="ev_techne_2",
            title="Techne Summit Alexandria",
            source="Manual",
            url="https://technesummit.com",
            description="International technology conference for founders and youth.",
            city="Alexandria",
            location="Bibliotheca Alexandrina",
            category="Tech and Innovation",
            organizer="Techne"
        ),
        EventRecord(
            event_id="ev_tanta_job_3",
            title="Delta Career Fair Tanta",
            source="Manual",
            url="https://deltacareer.com",
            description="Annual job fair connecting students with global companies.",
            city="Tanta",
            location="Tanta University",
            category="Career and Employment",
            organizer="Delta Hub"
        )
    ]

    index = EventSearchIndex(events)

    # Search for startup
    results = index.search("startup")
    assert "ev_riseup_1" in results

    # Search for alexandria
    alex_results = index.search("Alexandria")
    assert "ev_techne_2" in alex_results

    # Search for tanta
    tanta_results = index.search("Tanta")
    assert "ev_tanta_job_3" in tanta_results

    # Search empty string returns empty
    assert index.search("") == []