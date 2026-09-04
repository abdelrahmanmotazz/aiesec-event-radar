"""Social Media Event Scraper for Instagram & Facebook Public Announcements."""

import logging
import re
from datetime import datetime, timedelta
from typing import List, Optional
from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import EventRecord
from ..analyzers.caption_analyzer import CaptionAnalyzer

logger = logging.getLogger(__name__)

# Sample public discovery feeds and hashtag feeds for Egyptian youth events
POPULAR_SOCIAL_FEEDS = [
    {"platform": "Instagram", "tag": "eventsincairo", "city": "Cairo"},
    {"platform": "Instagram", "tag": "egypt_events", "city": "Cairo"},
    {"platform": "Instagram", "tag": "alexevents", "city": "Alexandria"},
    {"platform": "Facebook", "tag": "egypt-career-fairs", "city": "Cairo"},
]


class SocialMediaScraper(BaseScraper):
    """Scrapes public social media event announcement feeds with caption intelligence."""

    name: str = "Social Media"

    def __init__(self, timeout: float = 15.0):
        super().__init__(timeout=timeout)
        self.analyzer = CaptionAnalyzer()

    def scrape(self, city: Optional[str] = None, country: str = "egypt") -> List[EventRecord]:
        """Scrape upcoming event announcements from public social posts."""
        results: List[EventRecord] = []
        seen_ids = set()

        # Ingest public social event feeds
        for feed in POPULAR_SOCIAL_FEEDS:
            if city and city.lower() not in ["all", "egypt", "nationwide", "country"]:
                if feed["city"].lower() != city.lower():
                    continue

            platform = feed["platform"]
            tag = feed["tag"]

            # Query public aggregator mirrors for the hashtag/feed
            url = f"https://dumpoir.com/tag/{tag}" if platform == "Instagram" else f"https://mbasic.facebook.com/search/posts/?q={tag}"

            try:
                resp = self.client.get(url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "lxml")
                    posts = soup.select(".post, .item, div.post-container, article, .story")
                    for p in posts[:10]:
                        text = p.get_text(separator="\n", strip=True)
                        if not self.analyzer.is_event_post(text):
                            continue

                        analysis = self.analyzer.analyze(text)
                        if not analysis.get("is_event"):
                            continue

                        ev_id = f"sm_{hash(text[:50]) & 0xffffffff}"
                        if ev_id in seen_ids:
                            continue
                        seen_ids.add(ev_id)

                        start_dt = analysis.get("start_date") or (datetime.now() + timedelta(days=14))
                        rec = EventRecord(
                            event_id=ev_id,
                            title=analysis.get("title", f"{feed['city']} Youth Event"),
                            source=platform,
                            start_date=start_dt,
                            date_display=start_dt.strftime("%b %d, %Y · %I:%M %p") if start_dt else "Upcoming (Date in Bio)",
                            location=analysis.get("venue", "Cairo"),
                            city=analysis.get("city", feed["city"]),
                            country=country.capitalize(),
                            url=f"https://instagram.com/explore/tags/{tag}" if platform == "Instagram" else "https://facebook.com",
                            ticket_type=analysis.get("ticket_type", "Registration Required"),
                            organizer="Social Media Page Organizer",
                            description=analysis.get("summary", text[:250]),
                            raw_caption=text[:400]
                        )
                        results.append(rec)

            except Exception as e:
                logger.debug(f"[SocialMedia] Notice querying {feed['tag']}: {e}")

        return results
