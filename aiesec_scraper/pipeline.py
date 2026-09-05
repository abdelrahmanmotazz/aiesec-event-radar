"""Event Pipeline: Orchestration, Date Filtering (6 Months), Clash Detection, and Deduplication."""

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


class EventPipeline:
    """End-to-end ingestion, scoring, clash detection, and deduplication pipeline."""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.scorer = B2CScorer(self.config.get("keywords"))
        self.window_months = self.config.get("date_window_months", 6)
        self.default_cities = self.config.get("default_cities", ["tanta", "cairo", "alexandria", "giza", "mansoura"])

    def run(self, city: Optional[str] = None, country: str = "egypt") -> List[EventRecord]:
        """
        Executes the scraping run across all platforms, enriches records with AIESEC B2C
        scoring, filters to the 6-month window, applies clash detection, and deduplicates.
        """
        raw_events: List[EventRecord] = []

        logger.info(f"Starting scraping pipeline for {city or 'Egypt Nationwide'}...")

        # If nationwide, scrape country-wide feeds + key hubs
        if not city or city.lower() in ["all", "egypt", "nationwide", "country"]:
            # 1. Egypt Flagship Summits (Techne Summit Alexandria/Cairo, RiseUp, IEEE Congress)
            try:
                summits_scraper = EgyptSummitsScraper()
                raw_events.extend(summits_scraper.scrape(city=None, country=country))
            except Exception as e:
                logger.error(f"Error in Egypt Summits scrape: {e}")

            # 2. TicketsMarche Nationwide Feed
            try:
                tm_scraper = TicketsMarcheScraper()
                raw_events.extend(tm_scraper.scrape(city=None, country=country))
            except Exception as e:
                logger.error(f"Error in TicketsMarche scrape: {e}")

            # 3. Nationwide Eventbrite search
            try:
                eb = EventbriteScraper()
                raw_events.extend(eb.scrape(city=None, country=country))
            except Exception as e:
                logger.error(f"Error in nationwide Eventbrite scrape: {e}")

            # 4. Hub-by-hub scrape for AllEvents, Meetup, 10times, Social
            hub_scrapers = [
                AllEventsScraper(),
                MeetupScraper(),
                TenTimesScraper(),
                SocialMediaScraper(),
            ]
            for hub in self.default_cities:
                for scraper in hub_scrapers:
                    try:
                        events = scraper.scrape(city=hub, country=country)
                        raw_events.extend(events)
                    except Exception as e:
                        logger.error(f"Error in {scraper.name} scrape for {hub}: {e}")
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
                try:
                    events = scraper.scrape(city=city, country=country)
                    raw_events.extend(events)
                except Exception as e:
                    logger.error(f"Error in {scraper.name} scrape for {city}: {e}")

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
        """Merge identical events appearing across multiple platforms."""
        unique: List[EventRecord] = []
        seen_signatures: Dict[str, EventRecord] = {}

        for ev in events:
            clean_title = clean_title_for_comparison(ev.title)
            date_part = ev.start_date.strftime("%Y-%m-%d") if ev.start_date else "tba"
            sig = f"{clean_title}_{date_part}"

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
