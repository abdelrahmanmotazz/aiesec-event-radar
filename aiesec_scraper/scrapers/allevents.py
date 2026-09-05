"""AllEvents.in Scraper for Egyptian cities and hubs."""

import logging
from typing import List, Optional
from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import EventRecord

logger = logging.getLogger(__name__)


class AllEventsScraper(BaseScraper):
    """Scrapes AllEvents.in city event listings."""

    name: str = "AllEvents"

    def scrape(self, city: Optional[str] = None, country: str = "egypt", max_pages: int = 2) -> List[EventRecord]:
        """Scrape upcoming events from AllEvents.in."""
        results: List[EventRecord] = []
        seen_ids = set()

        # AllEvents organizes by city
        target_cities = [city.lower()] if city and city.lower() not in ["all", "egypt", "nationwide", "country"] else ["cairo", "alexandria", "giza"]

        for c in target_cities:
            for page in range(1, max_pages + 1):
                url = f"https://allevents.in/{c}/all?page={page}"
                try:
                    resp = self.client.get(url)
                    if resp.status_code != 200:
                        logger.warning(f"[AllEvents] Status {resp.status_code} for {url}")
                        break

                    soup = BeautifulSoup(resp.text, "lxml")
                    cards = soup.select("li.event-card, div.event-card")
                    if not cards:
                        break

                    page_count = 0
                    for card in cards:
                        eid = card.get("data-eid") or card.get("data-id")
                        title = card.get("data-name")
                        link = card.get("data-link")

                        # Fallback parsing within card elements
                        if not title:
                            title_el = card.select_one("h3, .title, .event-item__title")
                            title = title_el.get_text(strip=True) if title_el else None

                        if not link:
                            a_el = card.select_one("a.event-card-link, a[href*='allevents.in/']")
                            link = a_el.get("href") if a_el else None

                        if not title or not isinstance(title, str) or len(title.strip()) < 3 or title.strip().lower() in ["null", "none", "event"]:
                            continue
                        if not link:
                            continue

                        event_id = f"ae_{eid or hash(link) & 0xffffffff}"
                        if event_id in seen_ids:
                            continue
                        seen_ids.add(event_id)

                        # Extract date
                        date_el = card.select_one(".date, .meta-top-info .date, .datetime")
                        date_str = date_el.get_text(strip=True) if date_el else ""
                        start_dt = self.parse_datetime(date_str)

                        # Extract venue/location
                        loc_el = card.select_one(".subtitle, .location, .venue")
                        location = loc_el.get_text(strip=True) if loc_el else "Venue TBA"

                        # Pricing indicator
                        is_free = "free" in card.get_text(strip=True).lower() or "free" in title.lower()
                        ticket_type = "Free" if is_free else "Registration / Tickets"

                        record = EventRecord(
                            event_id=event_id,
                            title=title.strip(),
                            source=self.name,
                            start_date=start_dt,
                            end_date=None,
                            date_display=date_str or "Date TBA",
                            location=location.strip() or "TBA",
                            city=c.capitalize(),
                            country=country.capitalize(),
                            url=link,
                            ticket_type=ticket_type,
                            organizer="AllEvents Organizer",
                            description=""
                        )
                        results.append(record)
                        page_count += 1

                    if page_count == 0:
                        break

                except Exception as e:
                    logger.error(f"[AllEvents] Error scraping {url}: {e}")
                    break

        return results
