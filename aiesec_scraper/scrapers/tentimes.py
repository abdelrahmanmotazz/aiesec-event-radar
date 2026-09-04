"""10times Scraper for Egypt trade fairs, expos, and conferences."""

import logging
from typing import List, Optional
from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import EventRecord

logger = logging.getLogger(__name__)


class TenTimesScraper(BaseScraper):
    """Scrapes 10times for major exhibitions and conferences in Egypt."""

    name: str = "10times"

    def scrape(self, city: Optional[str] = None, country: str = "egypt") -> List[EventRecord]:
        """
        Attempts to scrape 10times event listings.
        Handles Cloudflare challenges gracefully without breaking the pipeline.
        """
        results: List[EventRecord] = []
        target = "egypt" if not city or city.lower() in ["all", "nationwide", "egypt"] else f"{city.lower()}-eg"
        url = f"https://10times.com/{target}"

        try:
            resp = self.client.get(url)
            if resp.status_code == 403 or "challenges.cloudflare.com" in resp.text:
                logger.info("[10times] Cloudflare challenge active; skipped in standard HTTP mode.")
                return results

            if resp.status_code != 200:
                logger.warning(f"[10times] Status {resp.status_code} for {url}")
                return results

            soup = BeautifulSoup(resp.text, "lxml")
            rows = soup.select("tr.event-card, tr[data-id], .event-card")

            for row in rows:
                title_el = row.select_one("h2, h3, a.event-name, strong")
                link_el = row.select_one("a[href*='10times.com/']")
                if not title_el or not link_el:
                    continue

                title = title_el.get_text(strip=True)
                link = link_el.get("href")
                date_el = row.select_one(".date, td.event-date, time")
                date_str = date_el.get_text(strip=True) if date_el else ""
                loc_el = row.select_one(".venue, td.event-venue, .city")
                loc_str = loc_el.get_text(strip=True) if loc_el else "Egypt"

                record = EventRecord(
                    event_id=f"10t_{hash(link) & 0xffffffff}",
                    title=title,
                    source=self.name,
                    start_date=self.parse_datetime(date_str),
                    end_date=None,
                    date_display=date_str or "Date TBA",
                    location=loc_str,
                    city=city.capitalize() if city else "Egypt",
                    country=country.capitalize(),
                    url=link,
                    ticket_type="Trade Fair / Conference Registration",
                    organizer="10times Listed Organizer",
                    description=""
                )
                results.append(record)

        except Exception as e:
            logger.debug(f"[10times] Scraping notice: {e}")

        return results
