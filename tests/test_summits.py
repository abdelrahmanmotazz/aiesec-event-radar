"""Unit tests for EgyptSummitsScraper."""

import pytest
from aiesec_scraper.scrapers.summits import EgyptSummitsScraper
from aiesec_scraper.scorers import B2CScorer

def test_summits_scraper_nationwide():
    scraper = EgyptSummitsScraper()
    events = scraper.scrape(city=None)
    
    assert len(events) >= 6
    
    # Assert Techne Summit Alexandria is present
    techne_alex = next((e for e in events if "techne summit alexandria" in e.title.lower()), None)
    assert techne_alex is not None
    assert techne_alex.city == "Alexandria"
    assert "Bibliotheca Alexandrina" in techne_alex.location
    assert techne_alex.start_date.month == 10
    
    # Assert Techne Summit Cairo is present
    techne_cairo = next((e for e in events if "techne summit cairo" in e.title.lower()), None)
    assert techne_cairo is not None
    assert techne_cairo.city == "Cairo"
    assert techne_cairo.start_date.month == 9

    # Assert RiseUp is present
    riseup = next((e for e in events if "riseup" in e.title.lower()), None)
    assert riseup is not None
    assert riseup.city == "Giza"

    # Assert Delta/Tanta summit is present
    tanta_summit = next((e for e in events if "tanta" in e.city.lower()), None)
    assert tanta_summit is not None
    assert tanta_summit.city == "Tanta"

def test_summits_scoring_and_priority():
    scraper = EgyptSummitsScraper()
    scorer = B2CScorer()
    events = scraper.scrape(city=None)
    
    for ev in events:
        score, priority, category, tags, action, parallel = scorer.evaluate(
            title=ev.title,
            description=ev.description,
            location=ev.location
        )
        assert score >= 7.0, f"Summit {ev.title} scored too low: {score}"
        assert priority in ["HIGH", "MEDIUM"]
