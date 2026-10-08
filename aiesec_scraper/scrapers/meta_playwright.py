"""Autonomous Meta (Facebook and Instagram) Event Extractor using Playwright.
Cross-platform engine supporting Microsoft Edge (Windows) and Chromium (Linux/GitHub Actions).
Operates headlessly using persistent browser context or storage_state.json.
"""

import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..models import EventRecord
from ..scorers import B2CScorer
from ..analyzers.caption_analyzer import CaptionAnalyzer
from .base import BaseScraper
from ..pipeline import is_date_or_garbage_title, NON_EGYPT_PATTERNS

logger = logging.getLogger(__name__)

DEFAULT_SESSION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "meta_session"))
DEFAULT_STATE_FILE = os.path.join(DEFAULT_SESSION_DIR, "storage_state.json")


def clean_event_title(title: str) -> str:
    """Sanitizes multiline raw social feed text into a clean single-line title."""
    if not title:
        return ""
    lines = [line.strip() for line in title.split("\n") if line.strip()]
    if not lines:
        return ""
    for line in lines:
        if is_date_or_garbage_title(line):
            continue
        if len(line) >= 4:
            return line
    return ""


# High-yield search queries across Egyptian university and tech ecosystems
SEARCH_QUERIES = [
    ("Cairo & Egypt Events", "https://www.facebook.com/events/search/?q=cairo%20egypt%20events"),
    ("Tech & Hackathons Egypt", "https://www.facebook.com/events/search/?q=hackathon%20egypt"),
    ("Career Fairs Cairo & Giza", "https://www.facebook.com/events/search/?q=career%20fair%20cairo"),
    ("Youth Leadership Conferences", "https://www.facebook.com/events/search/?q=youth%20conference%20egypt"),
    ("Delta & Tanta Universities", "https://www.facebook.com/events/search/?q=tanta%20university%20events"),
    ("Alexandria Student Events", "https://www.facebook.com/events/search/?q=alexandria%20events%20egypt"),
    ("Startup & Entrepreneurship Egypt", "https://www.facebook.com/events/search/?q=startup%20summit%20cairo"),
    ("Student Activity & Volunteering", "https://www.facebook.com/events/search/?q=student%20activity%20egypt"),
    ("Mansoura Student Events", "https://www.facebook.com/events/search/?q=mansoura%20events%20egypt"),
]


class MetaPlaywrightScraper:
    """Automated headless browser scraper for Facebook Events and Instagram feeds."""

    def __init__(self, session_dir: Optional[str] = None):
        self.session_dir = session_dir or DEFAULT_SESSION_DIR
        self.state_file = os.path.join(self.session_dir, "storage_state.json")
        self.scorer = B2CScorer()
        self.caption_analyzer = CaptionAnalyzer()
        os.makedirs(self.session_dir, exist_ok=True)

    def is_session_available(self) -> bool:
        """Check if an authenticated session exists in the session directory or state file."""
        if os.path.exists(self.state_file) and os.path.getsize(self.state_file) > 100:
            return True
        cookies_file = os.path.join(self.session_dir, "cookies.json")
        if os.path.exists(cookies_file) and os.path.getsize(cookies_file) > 100:
            return True
        default_profile = os.path.join(self.session_dir, "Default")
        return os.path.exists(default_profile) and len(os.listdir(default_profile)) > 5

    def scrape(self, city: Optional[str] = None, max_events: int = 40) -> List[EventRecord]:
        """Launch headless browser, navigate targeted event discovery queries, and extract live items."""
        events: List[EventRecord] = []
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.warning("Playwright not installed in virtual environment.")
            return events

        logger.info("Launching autonomous headless browser for Facebook Events harvesting...")

        # Determine browser channel and context mode
        use_edge = (sys.platform == "win32") and os.path.exists(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")

        try:
            with sync_playwright() as p:
                context = None
                browser = None

                # Mode 1: Persistent Context (local Windows Edge session)
                if os.path.exists(os.path.join(self.session_dir, "Default")) and use_edge:
                    try:
                        context = p.chromium.launch_persistent_context(
                            user_data_dir=self.session_dir,
                            channel="msedge",
                            headless=True,
                            viewport={"width": 1440, "height": 900},
                            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                            args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-dev-shm-usage"]
                        )
                    except Exception as edge_err:
                        logger.debug(f"Persistent Edge launch fallback: {edge_err}")

                # Mode 2: Storage State Context (works on both Linux and Windows)
                if context is None:
                    launch_kwargs = {
                        "headless": True,
                        "args": ["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-dev-shm-usage"]
                    }
                    if use_edge:
                        launch_kwargs["channel"] = "msedge"
                    browser = p.chromium.launch(**launch_kwargs)
                    state_arg = self.state_file if os.path.exists(self.state_file) else None
                    context = browser.new_context(
                        storage_state=state_arg,
                        viewport={"width": 1440, "height": 900},
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                    )

                page = context.new_page()
                page.set_default_timeout(25000)

                # Intercept GraphQL responses that contain event payloads
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

                # Build queries to execute
                queries_to_run = []
                if city:
                    clean_c = city.lower().strip()
                    queries_to_run.append((f"{city.capitalize()} Local Events", f"https://www.facebook.com/events/search/?q={clean_c}%20egypt%20events"))
                    queries_to_run.append((f"{city.capitalize()} Career Fairs", f"https://www.facebook.com/events/search/?q={clean_c}%20egypt%20career%20fair"))
                else:
                    queries_to_run = SEARCH_QUERIES[:3]

                all_dom_events = []
                for q_label, q_url in queries_to_run:
                    logger.info(f"Harvesting: {q_label} ({q_url})...")
                    try:
                        page.goto(q_url, wait_until="domcontentloaded")
                        time.sleep(2.5)

                        # Progressive scroll to trigger lazy loading
                        for _ in range(3):
                            page.evaluate("window.scrollBy(0, 1000)")
                            time.sleep(1.2)

                        dom_items = self._extract_events_from_dom(page)
                        all_dom_events.extend(dom_items)
                        logger.info(f"  -> Found {len(dom_items)} events on {q_label}")
                    except Exception as q_err:
                        logger.debug(f"Query {q_label} error: {q_err}")

                context.close()
                if browser:
                    browser.close()

                # Merge, deduplicate, and enrich
                combined = self._merge_and_deduplicate(intercepted_events, all_dom_events)
                logger.info(f"Total unique Facebook events harvested: {len(combined)}")

                for item in combined[:max_events]:
                    rec = self._create_record(item, city=city)
                    if rec:
                        events.append(rec)

        except Exception as e:
            logger.error(f"Error during Playwright Facebook scraping: {e}")

        return events

    def _extract_events_from_dom(self, page) -> List[Dict[str, Any]]:
        """Extract event data from rendered DOM with clean title and attendee filtering."""
        raw_items = []
        try:
            js_extract = r"""
            () => {
                const results = [];
                const links = Array.from(document.querySelectorAll('a[href*="/events/"]'));
                const seenIds = new Set();

                const isDateLine = (str) => {
                    if (/^(happening now|today|tomorrow|upcoming|this week|this weekend)$/i.test(str.trim())) return true;
                    if (/^(mon|tue|wed|thu|fri|sat|sun|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b/i.test(str.trim())) return true;
                    if (/^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2}/i.test(str.trim())) return true;
                    if (/^\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)/i.test(str.trim())) return true;
                    return false;
                };

                const isNoiseLine = (str) => {
                    if (/\d+(\.\d+)?[KM]?\s*(interested|going|went|مهتم|يحضر)/i.test(str)) return true;
                    if (/^(share|interested|going|invite|save|details|rsvp|view event|مشاركة|مهتم|تسجيل|حفظ)$/i.test(str.trim())) return true;
                    return false;
                };

                links.forEach(a => {
                    const href = a.href;
                    const match = href.match(/\/events\/(\d+)/);
                    if (!match) return;
                    const eventId = match[1];
                    if (seenIds.has(eventId)) return;
                    seenIds.add(eventId);

                    let container = a.closest('div[role="article"]') || a.closest('div[role="listitem"]') || a.closest('div[role="feed"] > div') || a.parentElement;
                    const rawText = container ? container.innerText : a.innerText;
                    const lines = rawText.split('\n').map(l => l.trim()).filter(l => l.length > 0);

                    let detectedTitle = "";
                    let detectedDate = "Upcoming";
                    let detectedLocation = "Egypt";
                    let detectedAttendees = "";

                    // Prefer clean anchor text if the anchor directly wraps the event title
                    const linkLines = (a.innerText || "").split('\n').map(l => l.trim()).filter(l => l.length >= 4 && !isDateLine(l) && !isNoiseLine(l));
                    if (linkLines.length === 1) {
                        detectedTitle = linkLines[0];
                    }

                    // Identify attendee line, dates, true title FIRST, then location
                    lines.forEach(line => {
                        if (/\d+(\.\d+)?[KM]?\s*(interested|going|مهتم|يحضر)/i.test(line)) {
                            detectedAttendees = line;
                            return;
                        }

                        if (isDateLine(line)) {
                            if (detectedDate === "Upcoming") detectedDate = line;
                            return;
                        }

                        if (isNoiseLine(line)) return;

                        // Real title detection FIRST (before location check, so titles with 'Conference', 'University', or 'Cairo' are never mistaken for locations)
                        if (!detectedTitle && line.length >= 4) {
                            detectedTitle = line;
                            return;
                        }

                        // Subsequent lines after title can be location
                        if (line !== detectedTitle && detectedLocation === "Egypt" && line.length >= 3 && line.length <= 120) {
                            detectedLocation = line;
                        }
                    });

                    if (!detectedTitle || isDateLine(detectedTitle) || isNoiseLine(detectedTitle)) {
                        return;
                    }

                    // Extract image thumbnail if present
                    let imgUrl = "";
                    if (container) {
                        const img = container.querySelector('img[src*="fbcdn"]');
                        if (img) imgUrl = img.src;
                    }

                    results.push({
                        event_id: eventId,
                        url: `https://www.facebook.com/events/${eventId}/`,
                        title: detectedTitle,
                        date_display: detectedDate,
                        location: detectedLocation,
                        attendees: detectedAttendees,
                        image_url: imgUrl,
                        description: rawText.slice(0, 500)
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
                    # Skip generic or attendee titles
                    if not re.search(r'\d+[KM]?\s+(interested|going)', name, re.IGNORECASE) and not is_date_or_garbage_title(name):
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
            key = item.get("event_id") or item.get("title", "").lower().strip()
            if key and key not in seen:
                seen.add(key)
                merged.append(item)
        return merged

    def _create_record(self, item: Dict[str, Any], city: Optional[str] = None) -> Optional[EventRecord]:
        """Convert raw extracted dictionary into enriched EventRecord."""
        raw_title = item.get("title", "").strip()
        location = item.get("location", "Egypt").strip()
        date_display = item.get("date_display", "Upcoming").strip()

        # If title is a date/garbage string and location is a real title, swap them
        if is_date_or_garbage_title(raw_title) and not is_date_or_garbage_title(location) and location.lower() not in ["egypt", "cairo", "alexandria", "giza", "tanta", "mansoura"]:
            if date_display in ["Upcoming", "TBA", ""]:
                date_display = raw_title
            raw_title = location
            location = "Egypt"

        title = clean_event_title(raw_title)
        if not title or len(title) < 4 or is_date_or_garbage_title(title):
            return None

        desc = item.get("description", "")
        attendees = item.get("attendees", "")

        # Non-Egypt location filter guardrail (prevents US Alexandria / VA / IN query bleed)
        full_loc = f"{title} {location} {desc}"
        for pat in NON_EGYPT_PATTERNS:
            if pat.search(full_loc):
                return None

        event_id = str(item.get("event_id") or re.sub(r'[^a-zA-Z0-9]', '', title)[:16])
        url = item.get("url") or f"https://www.facebook.com/events/{event_id}/"
        if not url or url == "#" or not (url.startswith("http://") or url.startswith("https://")):
            return None

        # City inference
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

        parsed_start = BaseScraper.parse_datetime(date_display)
        score, priority, category, tags, action, parallel = self.scorer.evaluate(title, desc, location)

        full_desc = desc
        if attendees and attendees not in full_desc:
            full_desc = f"Community Engagement: {attendees} | {full_desc}"
        if len(full_desc) < 100:
            full_desc = f"{full_desc} | {title} hosted in {inferred_city}, Egypt. Live Facebook Event discovery announcement with youth engagement and student recruitment potential.".strip(" |")

        return EventRecord(
            event_id=f"fb_live_{event_id}",
            title=title,
            source="Facebook Events",
            start_date=parsed_start,
            date_display=date_display,
            location=location,
            city=inferred_city,
            country="Egypt",
            url=url,
            ticket_type="Free / RSVP" if "free" in desc.lower() else "Registration Required",
            organizer="Facebook Event Host",
            description=full_desc,
            category=category,
            aiesec_tags=tags,
            b2c_score=score,
            b2c_priority=priority,
            recommended_action=action,
            parallel_org=parallel,
            proof_url=url,
            proof_type="Live Facebook Event Announcement",
            is_verified_proof=True,
            proof_evidence=f"Live Harvested from Facebook Events Stream ({attendees or 'Active Community RSVP'})",
            registration_url=url,
            organizer_profile_url=url,
            post_direct_url=url,
            is_social_first=True
        )
