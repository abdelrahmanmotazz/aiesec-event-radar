"""TicketsMarche Event Scraper for Egyptian cultural, business, and campus events."""

import json
import logging
import re
from datetime import datetime, timedelta
from typing import List, Optional
from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import EventRecord

logger = logging.getLogger(__name__)

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12
}


class TicketsMarcheScraper(BaseScraper):
    """
    Scraper for TicketsMarche (ticketsmarche.com), Egypt's premier ticketing platform.
    Extracts events from ecommerce dataLayer payloads and card metadata.
    """

    name: str = "TicketsMarche"
    base_url: str = "https://www.ticketsmarche.com"

    def scrape(self, city: Optional[str] = None, country: str = "egypt") -> List[EventRecord]:
        """Scrape active events from TicketsMarche."""
        results: List[EventRecord] = []
        seen_ids = set()

        endpoints = ["/", "/events", "/conferences"]
        
        for ep in endpoints:
            url = f"{self.base_url}{ep}"
            try:
                resp = self.client.get(url)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "lxml")
                events = self._parse_soup(soup, seen_ids, city=city, country=country)
                results.extend(events)
            except Exception as e:
                logger.warning(f"[TicketsMarche] Failed to scrape {url}: {e}")

        logger.info(f"[TicketsMarche] Discovered {len(results)} events")
        return results

    def _parse_soup(self, soup: BeautifulSoup, seen_ids: set, city: Optional[str] = None, country: str = "egypt") -> List[EventRecord]:
        """Extract event records from soup."""
        events: List[EventRecord] = []

        for a in soup.find_all("a", onclick=True):
            onclick = a.get("onclick", "")
            if '"items":' not in onclick:
                continue

            match = re.search(r'"items":(\[.*?\])', onclick)
            if not match:
                continue

            try:
                items = json.loads(match.group(1))
                vendor_match = re.search(r'"vendor_name":"(.*?)"', onclick)
                vendor = vendor_match.group(1) if vendor_match else "TicketsMarche Organizer"

                for item in items:
                    raw_id = item.get("item_id")
                    if not raw_id or raw_id in seen_ids:
                        continue
                    seen_ids.add(raw_id)

                    title = item.get("item_name") or raw_id
                    price = item.get("price")
                    ticket_type = f"{price} EGP" if price and str(price) != "0" and str(price) != "0.00" else "Free / Paid Tickets"
                    event_url = f"{self.base_url}/event/{raw_id}"

                    # Ascend DOM to discover date, time, and venue
                    date_dt, date_disp, venue, detected_city = self._extract_date_and_venue(a, title)

                    # Filter by city if requested
                    if city and city.lower() not in ["all", "egypt", "nationwide", "country"]:
                        if detected_city.lower() != city.lower():
                            continue

                    rec = EventRecord(
                        event_id=f"tm_{raw_id}",
                        title=title.strip(),
                        source="TicketsMarche",
                        start_date=date_dt,
                        date_display=date_disp,
                        location=venue,
                        city=detected_city,
                        country=country.capitalize(),
                        url=event_url,
                        ticket_type=ticket_type,
                        organizer=vendor,
                        description=f"{title} organized by {vendor}. Tickets available on TicketsMarche ({ticket_type}). Venue: {venue}."
                    )
                    events.append(rec)
            except Exception as err:
                logger.debug(f"[TicketsMarche] Error parsing item: {err}")

        return events

    def _extract_date_and_venue(self, anchor_tag, title: str):
        """Climb ancestor DOM to find text containing date, time, and venue."""
        curr = anchor_tag
        ancestor_text = ""
        month_word_re = re.compile(
            r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december)\b",
            re.IGNORECASE,
        )
        date_part_re = re.compile(
            r"(?:\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december)\b[^|]*?\d|\d[^|]*?\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december)\b)",
            re.IGNORECASE,
        )
        time_part_re = re.compile(r"^(?:from\s+)?\d{1,2}(?::\d{2})?\s*(?:am|pm)(?:\s*to\s*\d{1,2}(?::\d{2})?\s*(?:am|pm))?$", re.IGNORECASE)

        for _ in range(7):
            if not curr:
                break
            text = curr.get_text(" | ", strip=True)
            if date_part_re.search(text):
                ancestor_text = text
                break
            curr = curr.parent

        venue = "Cairo Cultural Hub"
        detected_city = "Cairo"
        date_dt = None
        date_disp = "TBA"
        time_disp = ""

        if ancestor_text:
            parts = [p.strip() for p in ancestor_text.split("|") if p.strip()]
            title_norm = title.strip().lower()

            # 1. Find genuine date part (must contain month word + digit, and not be the event title)
            for part in parts:
                if part.lower() == title_norm:
                    continue
                if date_part_re.search(part):
                    date_disp = part
                    date_dt = self._parse_date_string(part) or self.parse_datetime(part)
                    break

            # 2. Find time part if separate
            for part in parts:
                if time_part_re.match(part):
                    time_disp = part
                    break

            if time_disp and date_disp != "TBA" and time_disp.lower() not in date_disp.lower():
                date_disp = f"{date_disp} · {time_disp}"

            # 3. Find venue (exclude title, date parts, time parts, prices, and button labels)
            venue_candidates = []
            for p in parts:
                p_low = p.lower()
                if p_low == title_norm or p == date_disp or p == time_disp:
                    continue
                if p in ["Organized by", "Book Now", "More Info", "Buy Tickets", "Tickets"]:
                    continue
                if date_part_re.search(p) or time_part_re.match(p):
                    continue
                if re.match(r"^(?:egp\s*)?\d+(?:[.,]\d+)?(?:\s*egp)?$", p_low):
                    continue
                if len(p) > 2:
                    venue_candidates.append(p)

            if venue_candidates:
                venue = venue_candidates[0]

        # City detection from venue or title
        combined_text = f"{title} {venue} {ancestor_text}".lower()
        if "alexandria" in combined_text or "alex" in combined_text or "bibliotheca" in combined_text:
            detected_city = "Alexandria"
        elif "giza" in combined_text or "610" in combined_text or "zayed" in combined_text or "arkan" in combined_text or "october" in combined_text:
            detected_city = "Giza"
        elif "tanta" in combined_text:
            detected_city = "Tanta"
        elif "mansoura" in combined_text:
            detected_city = "Mansoura"
        else:
            detected_city = "Cairo"

        return date_dt, date_disp, venue, detected_city

    def _parse_date_string(self, text: str) -> Optional[datetime]:
        """Parse TicketsMarche date strings e.g. 'Sep 12', 'From 11th to 14th SEPT', '6-8 September 2026'."""
        try:
            current_year = datetime.now().year
            # Check for standard 'Oct 16' or 'Nov 5 to Nov 7, 2026'
            m = re.search(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+(\d{1,2})\b", text, re.IGNORECASE)
            if m:
                month_str = m.group(1).lower()[:3]
                day = int(m.group(2))
                if month_str in MONTH_MAP:
                    month = MONTH_MAP[month_str]
                    hour = 20  # default 8:00 PM
                    time_m = re.search(r"(\d{1,2}):(\d{2})\s*(PM|AM)?", text, re.IGNORECASE)
                    if time_m:
                        h = int(time_m.group(1))
                        is_pm = time_m.group(3) and time_m.group(3).upper() == "PM"
                        if is_pm and h < 12:
                            h += 12
                        hour = h
                    return datetime(current_year, month, day, hour, 0)

            # Check for '11th to 14th SEPT' or 'From 24 Sep to 2 Oct'
            m2 = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)?\s*(?:to\s*\d{1,2}(?:st|nd|rd|th)?\s*)?(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\b", text, re.IGNORECASE)
            if m2:
                day = int(m2.group(1))
                month_str = m2.group(2).lower()[:3]
                if month_str in MONTH_MAP:
                    return datetime(current_year, MONTH_MAP[month_str], day, 18, 0)
        except Exception:
            pass
        return None
