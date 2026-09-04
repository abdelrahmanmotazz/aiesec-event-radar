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

    def parse_datetime(self, val: Optional[str]) -> Optional[datetime]:
        """Safely parse various datetime formats into a naive or UTC datetime."""
        if not val:
            return None
        try:
            # Clean common formatting artifacts
            cleaned = val.strip()
            # Handle ISO formats
            dt = date_parser.parse(cleaned)
            # Normalize to naive UTC for consistent comparison
            if dt.tzinfo:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
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
