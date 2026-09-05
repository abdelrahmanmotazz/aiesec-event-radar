"""Scraper modules for event discovery platforms."""

from .base import BaseScraper
from .eventbrite import EventbriteScraper
from .allevents import AllEventsScraper
from .meetup import MeetupScraper
from .tentimes import TenTimesScraper
from .social import SocialMediaScraper
from .ticketsmarche import TicketsMarcheScraper
from .summits import EgyptSummitsScraper

__all__ = [
    "BaseScraper",
    "EventbriteScraper",
    "AllEventsScraper",
    "MeetupScraper",
    "TenTimesScraper",
    "SocialMediaScraper",
    "TicketsMarcheScraper",
    "EgyptSummitsScraper",
]

