"""Autonomous Meta (Facebook and Instagram) Event Extractor using Playwright with Microsoft Edge.
Operates headlessly using persistent browser context to bypass anti-bot shields and extract live events.
"""

import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..models import EventRecord
from ..scorers import B2CScorer
from ..analyzers.caption_analyzer import CaptionAnalyzer

logger = logging.getLogger(__name__)

DEFAULT_SESSION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "meta_session"))


class MetaPlaywrightScraper:
    """Automated headless browser scraper for Facebook Events and Instagram feeds."""

    def __init__(self, session_dir: Optional[str] = None):
        self.session_dir = session_dir or DEFAULT_SESSION_DIR
        self.scorer = B2CScorer()
        self.caption_analyzer = CaptionAnalyzer()
        os.makedirs(self.session_dir, exist_ok=True)

    def is_session_available(self) -> bool:
        """Check if an authenticated session exists in the session directory."""
        cookies_file = os.path.join(self.session_dir, "cookies.json")
        state_file = os.path.join(self.session_dir, "storage_state.json")
        if os.path.exists(cookies_file) or os.path.exists(state_file):
            return True
        default_profile = os.path.join(self.session_dir, "Default")
        return os.path.exists(default_profile) and len(os.listdir(default_profile)) > 5

    def scrape(self, city: Optional[str] = None, max_events: int = 25) -> List[EventRecord]:
        """Launch headless Edge browser, navigate to Facebook Events, and extract live event items."""
        events: List[EventRecord] = []
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.warning("Playwright not installed in virtual environment.")
            return events

        logger.info("Launching headless Edge browser for autonomous Facebook Events extraction...")
        try:
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=self.session_dir,
                    channel="msedge",
                    headless=True,
                    viewport={"width": 1440, "height": 900},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                    ]
                )

                page = context.new_page()
                page.set_default_timeout(25000)

                # Intercept GraphQL responses that contain event queries
                intercepted_events: List[Dict[str, Any]] = []

                def handle_response(response):
                    try:
                        if "graphql" in response.url and response.status == 200:
                            content_type = response.headers.get("content-type", "")
                            if "json" in content_type:
                                text = response.text()
                                if "event" in text.lower() or "event_place" in text.lower():
                                    data = json.loads(text)
                                    self._extract_events_from_graphql(data, intercepted_events)
                    except Exception:
                        pass

                page.on("response", handle_response)

                # Navigate to Facebook Events discovery
                target_url = "https://www.facebook.com/events/"
                if city:
                    target_url = f"https://www.facebook.com/events/search/?q={city}%20egypt"

                logger.info(f"Navigating to {target_url}...")
                page.goto(target_url, wait_until="domcontentloaded")
                time.sleep(3)

                # Scroll to trigger dynamic GraphQL event loading
                for _ in range(4):
                    page.evaluate("window.scrollBy(0, 1000)")
                    time.sleep(1.5)

                # Extract events from DOM anchors
                dom_events = self._extract_events_from_dom(page)

                context.close()

                # Process intercepted & DOM events
                combined = self._merge_and_deduplicate(intercepted_events, dom_events)
                logger.info(f"Extracted {len(combined)} raw events from Facebook session.")

                for item in combined[:max_events]:
                    rec = self._create_record(item, city=city)
                    if rec:
                        events.append(rec)

        except Exception as e:
            logger.error(f"Error during Playwright Facebook scraping: {e}")

        return events

    def _extract_events_from_dom(self, page) -> List[Dict[str, Any]]:
        """Extract event data from rendered DOM anchors and card containers."""
        raw_items = []
        try:
            js_extract = r"""
            () => {
                const results = [];
                const links = Array.from(document.querySelectorAll('a[href*="/events/"]'));
                const seenIds = new Set();

                links.forEach(a => {
                    const href = a.href;
                    const match = href.match(/\/events\/(\d+)/);
                    if (!match) return;
                    const eventId = match[1];
                    if (seenIds.has(eventId)) return;
                    seenIds.add(eventId);

                    let container = a.closest('div[role="article"]') || a.closest('div[role="listitem"]') || a.parentElement;
                    let title = a.innerText.trim();
                    let fullText = container ? container.innerText : title;

                    const lines = fullText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
                    let detectedTitle = lines[0] || "Facebook Event";
                    let detectedDate = "Upcoming";
                    let detectedLocation = "Egypt";

                    lines.forEach(l => {
                        if (/\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|mon|tue|wed|thu|fri|sat|sun|today|tomorrow|am|pm)\b/i.test(l)) {
                            detectedDate = l;
                        } else if (/\b(cairo|alexandria|tanta|mansoura|giza|assiut|hall|centre|hotel|campus)\b/i.test(l)) {
                            detectedLocation = l;
                        } else if (l.length > 10 && detectedTitle === lines[0] && l !== lines[0]) {
                            detectedTitle = l;
                        }
                    });

                    results.push({
                        event_id: eventId,
                        url: `https://www.facebook.com/events/${eventId}/`,
                        title: detectedTitle,
                        date_display: detectedDate,
                        location: detectedLocation,
                        description: fullText.slice(0, 500)
                    });
                });
                return results;
            }
            """
            raw_items = page.evaluate(js_extract)
        except Exception as e:
            logger.debug(f"DOM extraction error: {e}")

        return raw_items

    def _extract_events_from_graphql(self, data: Any, accumulator: List[Dict[str, Any]]) -> None:
        """Recursively find event objects in nested GraphQL response JSON."""
        if isinstance(data, dict):
            if "id" in data and ("name" in data or "event_place" in data or "start_timestamp" in data):
                name = data.get("name") or data.get("title")
                if name and isinstance(name, str) and len(name) > 3:
                    event_id = str(data.get("id"))
                    start_ts = data.get("start_timestamp")
                    date_str = datetime.fromtimestamp(start_ts).strftime("%A, %B %d, %Y") if start_ts else "Upcoming"
                    place = data.get("event_place", {})
                    location = place.get("name", "Egypt") if isinstance(place, dict) else "Egypt"
                    desc = data.get("description", {}).get("text", "") if isinstance(data.get("description"), dict) else ""

                    accumulator.append({
                        "event_id": event_id,
                        "url": f"https://www.facebook.com/events/{event_id}/",
                        "title": name,
                        "date_display": date_str,
                        "location": location,
                        "description": desc or f"Live event extracted from Facebook: {name}"
                    })
            for v in data.values():
                self._extract_events_from_graphql(v, accumulator)
        elif isinstance(data, list):
            for item in data:
                self._extract_events_from_graphql(item, accumulator)

    def _merge_and_deduplicate(self, list_a: List[Dict[str, Any]], list_b: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate raw items by event_id or title."""
        seen = set()
        merged = []
        for item in list_a + list_b:
            key = item.get("event_id") or item.get("title", "").lower()
            if key and key not in seen:
                seen.add(key)
                merged.append(item)
        return merged

    def _create_record(self, item: Dict[str, Any], city: Optional[str] = None) -> Optional[EventRecord]:
        """Convert raw extracted dictionary into enriched EventRecord."""
        title = item.get("title", "").strip()
        if not title or len(title) < 4:
            return None

        event_id = str(item.get("event_id") or re.sub(r'[^a-zA-Z0-9]', '', title)[:16])
        url = item.get("url") or f"https://www.facebook.com/events/{event_id}/"
        location = item.get("location", "Egypt")
        desc = item.get("description", "")

        inferred_city = "Cairo"
        loc_lower = f"{title} {location} {desc}".lower()
        if "alex" in loc_lower:
            inferred_city = "Alexandria"
        elif "tanta" in loc_lower:
            inferred_city = "Tanta"
        elif "mansoura" in loc_lower:
            inferred_city = "Mansoura"
        elif "assiut" in loc_lower:
            inferred_city = "Assiut"
        elif "giza" in loc_lower or "smart village" in loc_lower:
            inferred_city = "Giza"
        elif city:
            inferred_city = city.capitalize()

        score, priority, category, tags, action, parallel = self.scorer.evaluate(title, desc, location)

        return EventRecord(
            event_id=f"fb_live_{event_id}",
            title=title,
            source="Facebook Events",
            date_display=item.get("date_display", "Upcoming"),
            location=location,
            city=inferred_city,
            country="Egypt",
            url=url,
            ticket_type="Free / RSVP" if "free" in desc.lower() else "Registration Required",
            organizer="Facebook Event Host",
            description=desc or f"{title} hosted in {inferred_city}, Egypt. Live event announcement from Facebook.",
            category=category,
            aiesec_tags=tags,
            b2c_score=score,
            b2c_priority=priority,
            recommended_action=action,
            parallel_org=parallel,
            proof_url=url,
            proof_type="Live Facebook Event Announcement",
            is_verified_proof=True,
            proof_evidence="Live Harvested from Facebook Events Discovery Stream",
            registration_url=url,
            post_direct_url=url,
            is_social_first=True
        )
