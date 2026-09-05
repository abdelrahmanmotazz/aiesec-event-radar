import concurrent.futures
import hashlib
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .models import EventRecord
from .scorers import B2CScorer
from .scrapers import (
    AllEventsScraper,
    EgyptSummitsScraper,
    EventbriteScraper,
    MeetupScraper,
    SocialMediaScraper,
    TenTimesScraper,
    TicketsMarcheScraper,
)

logger = logging.getLogger(__name__)


def clean_title_for_comparison(title: str) -> str:
    """Normalize event title for deduplication comparison."""
    cleaned = re.sub(r"[^\w\s]", "", title.lower())
    tokens = [w for w in cleaned.split() if w not in ["the", "a", "an", "in", "at", "and", "of", "to", "for", "tickets"]]
    return " ".join(tokens)


def compute_event_fingerprint(title: str, city: str, date_str: str) -> str:
    """Compute SHA-256 fingerprint for O(1) instant deduplication across platforms."""
    clean_title = clean_title_for_comparison(title)
    clean_city = (city or "egypt").strip().lower()
    raw = f"{clean_title}|{clean_city}|{date_str}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _safe_scrape_task(scraper, city: Optional[str], country: str) -> List[EventRecord]:
    """Worker task for multithreaded parallel scraper execution."""
    try:
        return scraper.scrape(city=city, country=country)
    except Exception as e:
        logger.error(f"Error in concurrent {scraper.name} scrape for {city or 'nationwide'}: {e}")
        return []


class EventPipeline:
    """End-to-end ingestion, scoring, clash detection, and deduplication pipeline."""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.scorer = B2CScorer(self.config.get("keywords"))
        self.window_months = self.config.get("date_window_months", 6)
        self.default_cities = self.config.get("default_cities", ["tanta", "cairo", "alexandria", "giza", "mansoura"])

    def run(self, city: Optional[str] = None, country: str = "egypt") -> List[EventRecord]:
        """
        Executes high-throughput concurrent scraping across all discovery engines,
        enriches records with AIESEC B2C scoring, applies 6-month filtering,
        clash detection, and cryptographic deduplication.
        """
        raw_events: List[EventRecord] = []
        logger.info(f"Starting concurrent scraping pipeline for {city or 'Egypt Nationwide'}...")

        # Multithreaded concurrent scraping
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            tasks = []

            # Nationwide Scrapes
            if not city or city.lower() in ["all", "egypt", "nationwide", "country"]:
                tasks.append(executor.submit(_safe_scrape_task, EgyptSummitsScraper(), None, country))
                tasks.append(executor.submit(_safe_scrape_task, TicketsMarcheScraper(), None, country))
                tasks.append(executor.submit(_safe_scrape_task, EventbriteScraper(), None, country))

                hub_scrapers_classes = [AllEventsScraper, MeetupScraper, TenTimesScraper, SocialMediaScraper]
                for hub in self.default_cities:
                    for cls in hub_scrapers_classes:
                        tasks.append(executor.submit(_safe_scrape_task, cls(), hub, country))
            else:
                # Single city targeted
                city_scrapers = [
                    EgyptSummitsScraper(),
                    TicketsMarcheScraper(),
                    EventbriteScraper(),
                    AllEventsScraper(),
                    MeetupScraper(),
                    TenTimesScraper(),
                    SocialMediaScraper(),
                ]
                for scraper in city_scrapers:
                    tasks.append(executor.submit(_safe_scrape_task, scraper, city, country))

            for future in concurrent.futures.as_completed(tasks):
                try:
                    results = future.result()
                    if results:
                        raw_events.extend(results)
                except Exception as e:
                    logger.error(f"Error retrieving worker scrape result: {e}")

        logger.info(f"Collected {len(raw_events)} raw events. Applying 6-month filter & B2C scoring...")

        # Apply AIESEC B2C Scoring & Parallel Org Detection
        scored_events = []
        for ev in raw_events:
            score, priority, category, tags, action, parallel_org = self.scorer.evaluate(
                title=ev.title,
                description=ev.description,
                location=ev.location
            )
            ev.b2c_score = score
            ev.b2c_priority = priority
            ev.category = category
            ev.aiesec_tags = tags
            ev.recommended_action = action
            ev.parallel_org = parallel_org
            scored_events.append(ev)

        # Apply 6-Month Date Filter
        filtered_events = self._filter_date_window(scored_events)

        # Deduplicate cross-platform postings
        deduped_events = self._deduplicate(filtered_events)

        # Apply Clash Detection (Events competing on the same weekend in the same city)
        self._apply_clash_detection(deduped_events)

        # Sort: Primary by Date, with High Priority events clearly positioned
        deduped_events.sort(key=lambda x: (
            x.start_date is None,
            x.start_date or datetime.max,
            -x.b2c_score
        ))

        logger.info(f"Pipeline complete. Returning {len(deduped_events)} unique upcoming events.")
        return deduped_events

    def _filter_date_window(self, events: List[EventRecord]) -> List[EventRecord]:
        """Keep events within the next 6 months (~180 days)."""
        now = datetime.now()
        max_date = now + timedelta(days=self.window_months * 30)

        valid = []
        for ev in events:
            if ev.start_date:
                if ev.start_date < (now - timedelta(days=1)):
                    continue
                if ev.start_date > max_date:
                    continue
            valid.append(ev)

        return valid

    def _deduplicate(self, events: List[EventRecord]) -> List[EventRecord]:
        """Merge identical events appearing across multiple platforms using cryptographic fingerprinting."""
        unique: List[EventRecord] = []
        seen_signatures: Dict[str, EventRecord] = {}

        for ev in events:
            date_part = ev.start_date.strftime("%Y-%m-%d") if ev.start_date else "tba"
            sig = compute_event_fingerprint(ev.title, ev.city, date_part)

            if sig in seen_signatures:
                existing = seen_signatures[sig]
                if ev.source not in existing.source:
                    existing.source = f"{existing.source}, {ev.source}"
                if len(ev.description) > len(existing.description):
                    existing.description = ev.description
                if ev.parallel_org and not existing.parallel_org:
                    existing.parallel_org = ev.parallel_org
            else:
                seen_signatures[sig] = ev
                unique.append(ev)

        return unique

    def _apply_clash_detection(self, events: List[EventRecord]):
        """
        Flags events happening on the same weekend/date within the same city
        where multiple high/medium-impact student events compete for attendee footfall.
        """
        # Group by (city, date_window)
        date_city_map: Dict[str, List[EventRecord]] = {}

        for ev in events:
            if not ev.start_date:
                continue
            # Round date to year-week for weekend clash grouping
            week_key = f"{ev.city.lower()}_{ev.start_date.strftime('%Y-W%W')}"
            if week_key not in date_city_map:
                date_city_map[week_key] = []
            date_city_map[week_key].append(ev)

        for week_key, group in date_city_map.items():
            if len(group) >= 2:
                # 2 or more events in the same city in the same week
                for ev in group:
                    ev.clash_warning = True
                    ev.clash_count = len(group)
                    ev.clash_details = [other.title for other in group if other.event_id != ev.event_id][:3]
