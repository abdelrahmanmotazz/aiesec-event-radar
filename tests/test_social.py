"""Tests for Social Media Scraper Suite."""

import time
from aiesec_scraper.scrapers.social import SocialMediaScraper


def test_social_media_scraper_scraping():
    scraper = SocialMediaScraper()
    start = time.time()
    events = scraper.scrape(city=None)
    elapsed = time.time() - start

    # Concurrency check: 4 network probes should resolve rapidly (< 15 seconds)
    assert elapsed < 15.0
    assert len(events) >= 10

    # Ensure all multi-network feeds are represented
    sources = {e.source for e in events}
    assert any("Facebook" in s for s in sources)
    assert any("LinkedIn" in s for s in sources)
    assert any("Instagram" in s for s in sources)
    assert any("Telegram" in s for s in sources)

    # Specificity check: descriptions must be detailed (> 100 chars) and contain concrete briefing info
    for ev in events:
        assert len(ev.description) >= 100
        assert ev.city in ["Cairo", "Alexandria", "Tanta", "Mansoura"]
        assert ev.url.startswith("http")


def test_social_media_scraper_city_filter():
    scraper = SocialMediaScraper()
    tanta_events = scraper.scrape(city="Tanta")
    assert len(tanta_events) > 0
    for ev in tanta_events:
        assert ev.city == "Tanta"
