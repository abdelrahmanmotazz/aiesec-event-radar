"""Abstract Base Scraper with resilient HTTP client and date parsing."""

import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List, Optional
import httpx
from dateutil import parser as date_parser

from ..models import EventRecord


DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


class BaseScraper(ABC):
    """Base class for all platform scrapers."""

    name: str = "Base"

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout
        self.client = httpx.Client(
            headers=DEFAULT_HEADERS,
            follow_redirects=True,
            timeout=self.timeout
        )

    @abstractmethod
    def scrape(self, city: Optional[str] = None, country: str = "egypt") -> List[EventRecord]:
        """Fetch and extract events for a given city/country."""
        pass

    @classmethod
    def parse_datetime(cls, val: Optional[str], ref_now: Optional[datetime] = None) -> Optional[datetime]:
        """Safely parse various datetime formats (including bullets •/·, ranges, and yearless strings) into a naive datetime."""
        if not val or not isinstance(val, str):
            return None
        cleaned = val.strip()
        if not cleaned or cleaned.lower() in ["upcoming", "tba", "tbd", "date tba", "null", "none"]:
            return None

        now = ref_now or datetime.now()

        # 0. Relative dates
        lower = cleaned.lower()
        if lower in ["today", "happening now", "live now"]:
            return now.replace(hour=10, minute=0, second=0, microsecond=0)
        if lower == "tomorrow":
            from datetime import timedelta
            return (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)

        # 1. Fast path for standard ISO date/datetime strings
        if re.match(r"^\d{4}-\d{2}-\d{2}", cleaned):
            try:
                dt = date_parser.parse(cleaned)
                if dt.tzinfo:
                    dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
                return dt
            except Exception:
                pass

        # 2. Extract explicit 4-digit year and time if present anywhere in the string
        has_explicit_year = bool(re.search(r"\b(202[0-9])\b", cleaned))
        explicit_year = int(re.search(r"\b(202[0-9])\b", cleaned).group(1)) if has_explicit_year else now.year

        time_match = re.search(r"\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\b", cleaned)
        time_str = time_match.group(1) if time_match else ""

        # Remove time_str from norm BEFORE matching day/month so '25 Oct • 07:00 PM' never matches 'Oct 07'
        norm = cleaned
        if time_match:
            norm = norm[:time_match.start()] + " " + norm[time_match.end():]

        # 3. Strip bullets, '+ N more', and timezone abbreviations
        norm = re.sub(r"[•·|]+", " ", norm)
        norm = re.sub(r"\+\s*\d+\s*more\b", " ", norm, flags=re.IGNORECASE)
        norm = re.sub(r"\b(EET|EEST|EDT|EST|CDT|CST|MDT|MST|PDT|PST|BST|CEST|CET|GMT|UTC)\b", " ", norm, flags=re.IGNORECASE)
        norm = re.sub(r"\b(from|starting|on|at)\b", " ", norm, flags=re.IGNORECASE)
        norm = re.sub(r"\s+", " ", norm).strip()

        # 4. Handle date ranges, multi-day lists, and single dates:
        # Case A: Day-first range or single date: "15 - 17 Nov 2026", "8 and 9 Oct", "25 Oct", "06 Oct to 20 Dec"
        m_day_first = re.search(
            r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(?:(?:-|–|to|&|and|,)\s*(?:\d{1,2}(?:st|nd|rd|th)?\s*(?:-|–|to|&|and|,)\s*)?\d{1,2}(?:st|nd|rd|th)?\s+)?(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\b",
            norm,
            re.IGNORECASE,
        )
        # Case B: Month-first range or single date: "Oct 03 - 05, 2026", "Mon, Jan 18, 2027 - Jan 29, 2027", "Oct 16, 17", "Nov 12,13 & 14"
        m_month_first = re.search(
            r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+(\d{1,2})(?:st|nd|rd|th)?(?!:)\b",
            norm,
            re.IGNORECASE,
        )

        if m_day_first and (not m_month_first or m_day_first.start() <= m_month_first.start()):
            candidate = f"{m_day_first.group(1)} {m_day_first.group(2)} {explicit_year} {time_str}".strip()
        elif m_month_first:
            candidate = f"{m_month_first.group(1)} {m_month_first.group(2)} {explicit_year} {time_str}".strip()
        else:
            candidate = f"{norm} {explicit_year} {time_str}".strip() if not has_explicit_year else f"{norm} {time_str}".strip()

        try:
            default_dt = datetime(explicit_year, now.month, now.day, 9, 0)
            dt = date_parser.parse(candidate, default=default_dt, fuzzy=True)
            if dt.tzinfo:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
            # If no explicit year was provided and the parsed date is >60 days in the past, roll to next year
            if not has_explicit_year and (now - dt).days > 60:
                dt = dt.replace(year=dt.year + 1)
            return dt
        except Exception:
            return None

    def close(self):
        """Close the underlying HTTP client."""
        try:
            self.client.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
