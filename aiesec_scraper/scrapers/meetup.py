"""Meetup.com Scraper for Egyptian youth, tech, and networking events."""

import json
import logging
from typing import List, Optional
from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import EventRecord

logger = logging.getLogger(__name__)


class MeetupScraper(BaseScraper):
    """Scrapes Meetup events using structured JSON-LD and Apollo state."""

    name: str = "Meetup"

    def scrape(self, city: Optional[str] = None, country: str = "egypt") -> List[EventRecord]:
        """Scrape upcoming events from Meetup."""
        results: List[EventRecord] = []
        seen_urls = set()

        target_cities = [city.capitalize()] if city and city.lower() not in ["all", "egypt", "nationwide", "country"] else ["Cairo", "Alexandria"]

        for c in target_cities:
            url = f"https://www.meetup.com/find/?location=eg--{c}"
            try:
                resp = self.client.get(url)
                if resp.status_code != 200:
                    logger.warning(f"[Meetup] Status {resp.status_code} for {url}")
                    continue

                soup = BeautifulSoup(resp.text, "lxml")
                scripts = soup.find_all("script", type="application/ld+json")

                for script in scripts:
                    if not script.string:
                        continue
                    try:
                        data = json.loads(script.string)
                        items = []
                        if isinstance(data, list):
                            items = data
                        elif isinstance(data, dict):
                            if data.get("@type") == "Event":
                                items = [data]
                            elif "itemListElement" in data:
                                items = [x.get("item", x) for x in data["itemListElement"]]

                        for ev in items:
                            if not isinstance(ev, dict) or ev.get("@type") != "Event":
                                continue

                            title = ev.get("name")
                            event_url = ev.get("url")
                            if not title or not event_url or event_url in seen_urls:
                                continue
                            seen_urls.add(event_url)

                            start_dt = self.parse_datetime(ev.get("startDate"))
                            end_dt = self.parse_datetime(ev.get("endDate"))

                            loc_info = ev.get("location", {})
                            venue = "TBA"
                            if isinstance(loc_info, dict):
                                venue = loc_info.get("name") or loc_info.get("address", {}).get("streetAddress", "TBA")
                            elif isinstance(loc_info, str):
                                venue = loc_info

                            organizer_info = ev.get("organizer", {})
                            org_name = "Meetup Group"
                            if isinstance(organizer_info, dict):
                                org_name = organizer_info.get("name", org_name)

                            desc = ev.get("description", "") or ""

                            # Check ticket offers
                            offers = ev.get("offers", {})
                            ticket_type = "Free"
                            if isinstance(offers, dict):
                                price = offers.get("price")
                                if price and price not in [0, "0", 0.0, "0.0"]:
                                    ticket_type = f"Paid ({price} {offers.get('priceCurrency', '')})".strip()

                            record = EventRecord(
                                event_id=f"mu_{hash(event_url) & 0xffffffff}",
                                title=title.strip(),
                                source=self.name,
                                start_date=start_dt,
                                end_date=end_dt,
                                date_display=start_dt.strftime("%b %d, %Y · %I:%M %p") if start_dt else "Date TBA",
                                location=venue.strip() or "TBA",
                                city=c,
                                country=country.capitalize(),
                                url=event_url,
                                ticket_type=ticket_type,
                                organizer=org_name.strip(),
                                description=desc.strip()[:300]
                            )
                            results.append(record)

                    except Exception:
                        continue

            except Exception as e:
                logger.error(f"[Meetup] Error scraping {url}: {e}")
                continue

        return results
