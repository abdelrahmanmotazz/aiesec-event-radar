"""Eventbrite Scraper for Egypt nationwide and specific Egyptian cities."""

import json
import logging
from typing import List, Optional
from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import EventRecord

logger = logging.getLogger(__name__)


class EventbriteScraper(BaseScraper):
    """Scrapes Eventbrite using Schema.org JSON-LD and HTML fallback."""

    name: str = "Eventbrite"

    def _build_url(self, city: Optional[str], country: str, page: int = 1) -> str:
        if city and city.lower() not in ["all", "egypt", "nationwide", "country"]:
            city_clean = city.lower().strip().replace(" ", "-")
            url = f"https://www.eventbrite.com/d/egypt--{city_clean}/all-events/?page={page}"
        else:
            country_clean = country.lower().strip().replace(" ", "-")
            url = f"https://www.eventbrite.com/d/{country_clean}/all-events/?page={page}"
        return url

    def scrape(self, city: Optional[str] = None, country: str = "egypt", max_pages: int = 3) -> List[EventRecord]:
        """Scrape upcoming events from Eventbrite."""
        results: List[EventRecord] = []
        seen_urls = set()

        for page in range(1, max_pages + 1):
            url = self._build_url(city, country, page)
            try:
                resp = self.client.get(url)
                if resp.status_code != 200:
                    logger.warning(f"[Eventbrite] Status {resp.status_code} for {url}")
                    break

                soup = BeautifulSoup(resp.text, "lxml")
                extracted_this_page = self._parse_json_ld(soup, city, country, seen_urls)
                
                # If JSON-LD didn't yield events, fallback to HTML parsing
                if not extracted_this_page:
                    extracted_this_page = self._parse_html_cards(soup, city, country, seen_urls)

                if not extracted_this_page:
                    break

                results.extend(extracted_this_page)

            except Exception as e:
                logger.error(f"[Eventbrite] Error scraping {url}: {e}")
                break

        return results

    def _parse_json_ld(self, soup: BeautifulSoup, city: Optional[str], country: str, seen_urls: set) -> List[EventRecord]:
        events: List[EventRecord] = []
        scripts = soup.find_all("script", type="application/ld+json")

        for script in scripts:
            if not script.string:
                continue
            try:
                data = json.loads(script.string)
                items = []
                if isinstance(data, dict):
                    if "itemListElement" in data:
                        items = data["itemListElement"]
                    elif data.get("@type") == "Event":
                        items = [{"item": data}]
                elif isinstance(data, list):
                    for d in data:
                        if isinstance(d, dict) and "itemListElement" in d:
                            items.extend(d["itemListElement"])
                        elif isinstance(d, dict) and d.get("@type") == "Event":
                            items.append({"item": d})

                for item in items:
                    ev = item.get("item", item)
                    if not isinstance(ev, dict):
                        continue
                    if ev.get("@type") != "Event" and "startDate" not in ev:
                        continue

                    title = ev.get("name")
                    event_url = ev.get("url")
                    if not title or not event_url or event_url in seen_urls:
                        continue
                    seen_urls.add(event_url)

                    start_dt = self.parse_datetime(ev.get("startDate"))
                    end_dt = self.parse_datetime(ev.get("endDate"))

                    # Extract location
                    loc_data = ev.get("location", {})
                    venue_name = "TBA"
                    detected_city = city.capitalize() if city else "Egypt"
                    if isinstance(loc_data, dict):
                        venue_name = loc_data.get("name", "TBA")
                        addr = loc_data.get("address", {})
                        if isinstance(addr, dict):
                            detected_city = addr.get("addressLocality") or detected_city
                    elif isinstance(loc_data, str):
                        venue_name = loc_data

                    # Extract ticket pricing
                    offers = ev.get("offers", {})
                    ticket_type = "Paid / Registration"
                    if isinstance(offers, dict):
                        is_free = offers.get("isAccessibleForFree")
                        low_price = offers.get("lowPrice", offers.get("price"))
                        if is_free is True or low_price in [0, "0", 0.0, "0.0"]:
                            ticket_type = "Free"
                    elif isinstance(offers, list):
                        for o in offers:
                            if isinstance(o, dict) and (o.get("isAccessibleForFree") or o.get("price") in [0, "0", 0.0]):
                                ticket_type = "Free"
                                break

                    # Organizer
                    organizer_name = "Eventbrite Organizer"
                    org_data = ev.get("organizer", {})
                    if isinstance(org_data, dict):
                        organizer_name = org_data.get("name", organizer_name)
                    elif isinstance(org_data, str):
                        organizer_name = org_data

                    desc = ev.get("description", "") or ""

                    record = EventRecord(
                        event_id=f"eb_{hash(event_url) & 0xffffffff}",
                        title=title.strip(),
                        source=self.name,
                        start_date=start_dt,
                        end_date=end_dt,
                        date_display=start_dt.strftime("%b %d, %Y · %I:%M %p") if start_dt else "Date TBA",
                        location=venue_name.strip() or "TBA",
                        city=detected_city,
                        country=country.capitalize(),
                        url=event_url,
                        ticket_type=ticket_type,
                        organizer=organizer_name.strip(),
                        description=desc.strip()[:300]
                    )
                    events.append(record)

            except Exception:
                continue

        return events

    def _parse_html_cards(self, soup: BeautifulSoup, city: Optional[str], country: str, seen_urls: set) -> List[EventRecord]:
        events: List[EventRecord] = []
        cards = soup.select("section.event-card-details, div.event-card, [data-testid='event-card']")

        for card in cards:
            link_el = card.select_one("a[href*='/e/']")
            title_el = card.select_one("h2, h3, .event-card__title, [data-testid='event-card-title']")
            if not link_el or not title_el:
                continue

            event_url = link_el.get("href", "").split("?")[0]
            if not event_url or event_url in seen_urls:
                continue
            seen_urls.add(event_url)

            title = title_el.get_text(strip=True)
            date_el = card.select_one("p.event-card__date, div.event-card__date, time")
            date_str = date_el.get_text(strip=True) if date_el else ""
            start_dt = self.parse_datetime(date_str)

            loc_el = card.select_one("p.event-card__location, div.event-card__location")
            location = loc_el.get_text(strip=True) if loc_el else "TBA"

            record = EventRecord(
                event_id=f"eb_{hash(event_url) & 0xffffffff}",
                title=title,
                source=self.name,
                start_date=start_dt,
                end_date=None,
                date_display=date_str or "Date TBA",
                location=location,
                city=city.capitalize() if city else "Egypt",
                country=country.capitalize(),
                url=event_url,
                ticket_type="Registration",
                organizer="Eventbrite Organizer",
                description=""
            )
            events.append(record)

        return events
