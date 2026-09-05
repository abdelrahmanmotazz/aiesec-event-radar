"""Enhanced Social Media Event Scraper targeting Facebook Events Pages & Instagram Feeds."""

import json
import logging
import re
from datetime import datetime, timedelta
from typing import List, Optional
from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import EventRecord
from ..analyzers.caption_analyzer import CaptionAnalyzer

logger = logging.getLogger(__name__)

# Key Egyptian student and event hubs on Facebook
FACEBOOK_EVENT_TARGETS = [
    {"type": "explore", "slug": "cairo-egypt", "city": "Cairo"},
    {"type": "explore", "slug": "alexandria-egypt", "city": "Alexandria"},
    {"type": "search", "query": "career+fair+cairo", "city": "Cairo"},
    {"type": "search", "query": "career+fair+alexandria", "city": "Alexandria"},
    {"type": "search", "query": "hackathon+egypt", "city": "Cairo"},
    {"type": "search", "query": "youth+summit+egypt", "city": "Cairo"},
    {"type": "search", "query": "ieee+egypt+conference", "city": "Cairo"},
    {"type": "search", "query": "enactus+egypt+competition", "city": "Cairo"},
]

INSTAGRAM_HASHTAGS = [
    {"tag": "eventsincairo", "city": "Cairo"},
    {"tag": "egypt_events", "city": "Cairo"},
    {"tag": "alexevents", "city": "Alexandria"},
    {"tag": "cairo_events", "city": "Cairo"},
]


class SocialMediaScraper(BaseScraper):
    """
    Scrapes Facebook Events pages, public event discovery feeds,
    and Instagram event announcement channels with deep caption analysis.
    """

    name: str = "Facebook & Social Media"

    def __init__(self, timeout: float = 15.0):
        super().__init__(timeout=timeout)
        self.analyzer = CaptionAnalyzer()

    def scrape(self, city: Optional[str] = None, country: str = "egypt") -> List[EventRecord]:
        """Scrape upcoming events from Facebook Events pages and Instagram feeds."""
        results: List[EventRecord] = []
        seen_urls = set()

        # 1. Scrape Facebook Events Pages
        fb_events = self._scrape_facebook_events(city=city, country=country, seen_urls=seen_urls)
        results.extend(fb_events)

        # 2. Scrape Instagram Public Feeds
        ig_events = self._scrape_instagram_feeds(city=city, country=country, seen_urls=seen_urls)
        results.extend(ig_events)

        return results

    def _scrape_facebook_events(self, city: Optional[str], country: str, seen_urls: set) -> List[EventRecord]:
        """Navigates directly to Facebook Events exploration and search pages."""
        events: List[EventRecord] = []

        for target in FACEBOOK_EVENT_TARGETS:
            target_city = target["city"]
            if city and city.lower() not in ["all", "egypt", "nationwide", "country"]:
                if target_city.lower() != city.lower():
                    continue

            if target["type"] == "explore":
                url = f"https://www.facebook.com/events/explore/{target['slug']}/"
            else:
                url = f"https://www.facebook.com/events/search/?q={target['query']}"

            try:
                resp = self.client.get(url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "lxml")

                    # Extract JSON-LD / schema.org if rendered
                    scripts = soup.find_all("script", type="application/ld+json")
                    for s in scripts:
                        if not s.string:
                            continue
                        try:
                            data = json.loads(s.string)
                            items = data if isinstance(data, list) else [data]
                            for item in items:
                                if item.get("@type") == "Event":
                                    ev_url = item.get("url") or url
                                    if ev_url in seen_urls:
                                        continue
                                    seen_urls.add(ev_url)
                                    start_dt = self.parse_datetime(item.get("startDate"))
                                    record = EventRecord(
                                        event_id=f"fb_{hash(ev_url) & 0xffffffff}",
                                        title=item.get("name", "Facebook Event").strip(),
                                        source="Facebook Events",
                                        start_date=start_dt,
                                        date_display=start_dt.strftime("%b %d, %Y · %I:%M %p") if start_dt else "Date on Facebook",
                                        location=item.get("location", {}).get("name", target_city),
                                        city=target_city,
                                        country=country.capitalize(),
                                        url=ev_url,
                                        ticket_type="Free / Registration",
                                        organizer=item.get("organizer", {}).get("name", "Facebook Event Organizer"),
                                        description=item.get("description", "")[:300]
                                    )
                                    events.append(record)
                        except Exception:
                            pass

                    # Extract event links and text blocks
                    event_links = soup.select("a[href*='/events/']")
                    for a in event_links:
                        href = a.get("href", "")
                        match = re.search(r"/events/(\d+)", href)
                        if not match:
                            continue
                        event_id_str = match.group(1)
                        full_event_url = f"https://www.facebook.com/events/{event_id_str}/"
                        if full_event_url in seen_urls:
                            continue
                        seen_urls.add(full_event_url)

                        text = a.get_text(separator=" ", strip=True)
                        if not text or len(text) < 4:
                            continue

                        # Check caption relevance
                        analysis = self.analyzer.analyze(text)
                        title = analysis.get("title") or text.split("·")[0].strip()
                        if len(title) < 3 or "facebook" in title.lower():
                            continue

                        start_dt = analysis.get("start_date") or (datetime.now() + timedelta(days=21))
                        rec = EventRecord(
                            event_id=f"fb_{event_id_str}",
                            title=title,
                            source="Facebook Events",
                            start_date=start_dt,
                            date_display=start_dt.strftime("%b %d, %Y · %I:%M %p") if start_dt else "Check Facebook Event",
                            location=analysis.get("venue", target_city),
                            city=target_city,
                            country=country.capitalize(),
                            url=full_event_url,
                            ticket_type=analysis.get("ticket_type", "Registration"),
                            organizer="Facebook Event Host",
                            description=analysis.get("summary", text[:250]),
                            raw_caption=text[:400]
                        )
                        events.append(rec)

            except Exception as e:
                logger.debug(f"[Facebook Events] Scraping notice for {url}: {e}")

        return events

    def _scrape_instagram_feeds(self, city: Optional[str], country: str, seen_urls: set) -> List[EventRecord]:
        """Scrapes public Instagram event discovery channels."""
        events: List[EventRecord] = []

        for feed in INSTAGRAM_HASHTAGS:
            if city and city.lower() not in ["all", "egypt", "nationwide", "country"]:
                if feed["city"].lower() != city.lower():
                    continue

            tag = feed["tag"]
            url = f"https://dumpoir.com/tag/{tag}"

            try:
                resp = self.client.get(url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "lxml")
                    posts = soup.select(".post, .item, div.post-container, article, .story")
                    for p in posts[:8]:
                        text = p.get_text(separator="\n", strip=True)
                        if not self.analyzer.is_event_post(text):
                            continue

                        analysis = self.analyzer.analyze(text)
                        if not analysis.get("is_event"):
                            continue

                        post_id = f"ig_{hash(text[:40]) & 0xffffffff}"
                        post_url = f"https://instagram.com/explore/tags/{tag}"
                        if post_id in seen_urls:
                            continue
                        seen_urls.add(post_id)

                        start_dt = analysis.get("start_date") or (datetime.now() + timedelta(days=14))
                        rec = EventRecord(
                            event_id=post_id,
                            title=analysis.get("title", f"{feed['city']} Youth Event"),
                            source="Instagram",
                            start_date=start_dt,
                            date_display=start_dt.strftime("%b %d, %Y · %I:%M %p") if start_dt else "Upcoming (Check Bio)",
                            location=analysis.get("venue", feed["city"]),
                            city=analysis.get("city", feed["city"]),
                            country=country.capitalize(),
                            url=post_url,
                            ticket_type=analysis.get("ticket_type", "Free / Registration"),
                            organizer="Instagram Curator",
                            description=analysis.get("summary", text[:250]),
                            raw_caption=text[:400]
                        )
                        events.append(rec)

            except Exception as e:
                logger.debug(f"[Instagram] Notice for {tag}: {e}")

        return events
