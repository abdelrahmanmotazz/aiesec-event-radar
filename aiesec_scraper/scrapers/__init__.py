"""Scraper modules for event discovery platforms."""

from .base import BaseScraper
from .eventbrite import EventbriteScraper
from .allevents import AllEventsScraper
from .meetup import MeetupScraper
from .tentimes import TenTimesScraper
from .social import SocialMediaScraper

__all__ = [
    "BaseScraper",
    "EventbriteScraper",
    "AllEventsScraper",
    "MeetupScraper",
    "TenTimesScraper",
    "SocialMediaScraper",
]
