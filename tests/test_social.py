"""Tests for Social Media Scraper Suite (Facebook Events & Instagram Feeds)."""

import time
from aiesec_scraper.scrapers.social import SocialMediaScraper


def test_social_media_scraper_scraping():
    scraper = SocialMediaScraper()
    start = time.time()
    events = scraper.scrape(city=None)
    elapsed = time.time() - start

    # Concurrency check: should resolve rapidly (< 10 seconds)
    assert elapsed < 10.0
    assert len(events) >= 10

    # Ensure Facebook and Instagram are represented, while Telegram and LinkedIn are completely excluded
    sources = {e.source for e in events}
    assert any("Facebook" in s for s in sources)
    assert any("Instagram" in s for s in sources)
    assert not any("Telegram" in s for s in sources)
    assert not any("LinkedIn" in s for s in sources)

    # Specificity check: descriptions must be detailed (> 100 chars) and contain concrete briefing info
    for ev in events:
        assert len(ev.description) >= 100
        assert ev.city in ["Cairo", "Alexandria", "Tanta", "Mansoura", "Assiut"]
        assert ev.url.startswith("http")
        assert ev.is_social_first is True
        assert ev.post_direct_url.startswith("http")
        assert ev.organizer_profile_url.startswith("http")
        assert ev.proof_url.startswith("http")
        # Direct post URL must be the proof URL
        assert ev.proof_url == ev.post_direct_url


def test_social_media_scraper_city_filter():
    scraper = SocialMediaScraper()
    tanta_events = scraper.scrape(city="Tanta")
    assert len(tanta_events) > 0
    for ev in tanta_events:
        assert ev.city == "Tanta"
        assert ev.is_social_first is True
        assert ev.post_direct_url.startswith("http")


def test_social_media_registration_urls():
    scraper = SocialMediaScraper()
    events = scraper.scrape(city=None)
    events_with_forms = [e for e in events if e.registration_url]
    assert len(events_with_forms) > 0
    for ev in events_with_forms:
        assert "http" in ev.registration_url
