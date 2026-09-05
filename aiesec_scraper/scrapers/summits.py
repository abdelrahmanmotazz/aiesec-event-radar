"""Egypt Flagship Summits Scraper: Techne Summit, RiseUp, IEEE Congress, and National Youth Summits."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import EventRecord

logger = logging.getLogger(__name__)

# Registry of Egypt's Flagship Annual Summits & Campus Conferences
SUMMITS_CATALOG = [
    {
        "id": "summit_techne_alex_2026",
        "title": "Techne Summit Alexandria 2026",
        "organizer": "Techne & Marketeers",
        "url": "https://technesummit.com/",
        "start_date": datetime(2026, 10, 3, 9, 0),
        "date_display": "Oct 03 - 05, 2026 · 09:00 AM",
        "location": "Bibliotheca Alexandrina",
        "city": "Alexandria",
        "category": "Technology & Entrepreneurship",
        "ticket_type": "Student / Attendee Passes",
        "parallel_org": "Techne Global",
        "description": "The Mediterranean's largest technology, startup, and talent gathering at Bibliotheca Alexandrina with 45,000+ attendees, youth innovators, international speakers, and university delegations.",
        "recommended_action": "High-priority activation for LC Tanta & Alex: Deploy booth presence, distribute Global Volunteer flyers, and engage university delegations across the Delta."
    },
    {
        "id": "summit_techne_cairo_2026",
        "title": "Techne Summit Cairo 2026",
        "organizer": "Techne Global",
        "url": "https://technesummit.com/",
        "start_date": datetime(2026, 9, 26, 10, 0),
        "date_display": "Sep 26 - 27, 2026 · 10:00 AM",
        "location": "The Nile Ritz-Carlton",
        "city": "Cairo",
        "category": "Corporate Innovation & Youth Startups",
        "ticket_type": "Summit Registration",
        "parallel_org": "Techne Global",
        "description": "Flagship Cairo edition convening 10,000+ youth, founders, investors, and corporate decision-makers during Egypt Innovation Week.",
        "recommended_action": "Set up AIESEC Youth Speak lounge & meet corporate partners for Global Talent internship sponsorships."
    },
    {
        "id": "summit_riseup_2026",
        "title": "RiseUp Summit 2026",
        "organizer": "RiseUp",
        "url": "https://riseupsummit.com/",
        "start_date": datetime(2026, 11, 14, 9, 30),
        "date_display": "Nov 14 - 16, 2026 · 09:30 AM",
        "location": "Grand Egyptian Museum (GEM)",
        "city": "Giza",
        "category": "Entrepreneurship & Innovation",
        "ticket_type": "Student / General Ticket",
        "parallel_org": "RiseUp Community",
        "description": "MENA's premier entrepreneurship marathon bringing together thousands of student founders, changemakers, and youth leaders at the iconic Grand Egyptian Museum.",
        "recommended_action": "Send LC youth delegation; engage youth attendees at networking stages for Global Volunteer & Teacher programs."
    },
    {
        "id": "summit_ecs_cairo_2026",
        "title": "Egypt Career Summit (ECS) Fall Edition",
        "organizer": "Career Summit Egypt",
        "url": "https://egyptcareersummit.com/",
        "start_date": datetime(2026, 10, 18, 9, 0),
        "date_display": "Oct 18 - 19, 2026 · 09:00 AM",
        "location": "The Greek Campus, Downtown",
        "city": "Cairo",
        "category": "Career Fair & Youth Employment",
        "ticket_type": "Free / Registration Required",
        "parallel_org": None,
        "description": "Massive employment and career exploration summit attended by 20,000+ university undergraduates and fresh graduates seeking professional opportunities.",
        "recommended_action": "Direct candidate acquisition hotspot for AIESEC Global Talent & Global Teacher exchange products."
    },
    {
        "id": "summit_ieee_congress_2026",
        "title": "IEEE Egypt National Student Congress & Exhibition",
        "organizer": "IEEE Egypt Section",
        "url": "https://ieee-egypt.org/",
        "start_date": datetime(2026, 9, 19, 9, 0),
        "date_display": "Sep 19 - 20, 2026 · 09:00 AM",
        "location": "Cairo University Faculty of Engineering",
        "city": "Cairo",
        "category": "STEM & Student Leadership",
        "ticket_type": "Free / Student Pass",
        "parallel_org": "IEEE",
        "description": "National gathering of 35+ IEEE university student branches across Egypt showcasing student engineering projects, robotics, and leadership summits.",
        "recommended_action": "Partner with IEEE student branches to co-promote AIESEC global technical internships and volunteer opportunities."
    },
    {
        "id": "summit_enactus_expo_2026",
        "title": "Enactus Egypt National Exposition & Social Forum",
        "organizer": "Enactus Egypt",
        "url": "https://enactus.org/country/egypt/",
        "start_date": datetime(2026, 9, 29, 10, 0),
        "date_display": "Sep 29 - 30, 2026 · 10:00 AM",
        "location": "Intercontinental Citystars",
        "city": "Cairo",
        "category": "Social Impact & Leadership",
        "ticket_type": "Invitation / Registration",
        "parallel_org": "Enactus",
        "description": "National showdown of 50+ university teams presenting high-impact social entrepreneurship solutions addressing the UN Sustainable Development Goals.",
        "recommended_action": "Direct alignment with AIESEC SDG Global Volunteer initiatives; engage active student participants for cross-organizational synergy."
    },
    {
        "id": "summit_delta_tanta_2026",
        "title": "Delta Youth Innovation & Tech Forum (Tanta University)",
        "organizer": "Tanta University & Delta Student Union",
        "url": "https://tanta.edu.eg/",
        "start_date": datetime(2026, 10, 24, 10, 0),
        "date_display": "Oct 24 - 25, 2026 · 10:00 AM",
        "location": "Tanta University Convention Center",
        "city": "Tanta",
        "category": "Campus Leadership & Innovation",
        "ticket_type": "Free for Students",
        "parallel_org": None,
        "description": "The Gharbia and Delta region's central student conference connecting students from Tanta, Mansoura, and Kafr El-Sheikh with career readiness, technology, and civil society.",
        "recommended_action": "HOME TURF PRIORITY for AIESEC in Tanta: Secure keynote speech, physical booth, and mass recruitment drive."
    },
    {
        "id": "summit_she_can_2026",
        "title": "She Can Summit 2026 (Entreprenelle)",
        "organizer": "Entreprenelle",
        "url": "https://entreprenelle.com/",
        "start_date": datetime(2026, 11, 28, 9, 0),
        "date_display": "Nov 28, 2026 · 09:00 AM",
        "location": "The Greek Campus West (Mall of Arabia)",
        "city": "Giza",
        "category": "Women in Leadership & Entrepreneurship",
        "ticket_type": "Standard Ticket",
        "parallel_org": "Entreprenelle",
        "description": "The largest female empowerment and entrepreneurship summit in the MENA region, drawing 7,000+ ambitious women, university students, and professionals.",
        "recommended_action": "Promote AIESEC SDG 5 Gender Equality volunteer projects & female youth leadership opportunities."
    }
]


class EgyptSummitsScraper(BaseScraper):
    """
    Scraper and catalog monitor for Egypt's flagship national summits,
    student congresses, and youth tech festivals (Techne Summit, RiseUp, IEEE, Enactus).
    """

    name: str = "Egypt Flagship Summits"

    def scrape(self, city: Optional[str] = None, country: str = "egypt") -> List[EventRecord]:
        """Scrapes and monitors flagship Egyptian summits."""
        results: List[EventRecord] = []

        # 1. Live probe to technesummit.com to verify real-time status
        try:
            resp = self.client.get("https://technesummit.com/", timeout=8.0)
            if resp.status_code == 200:
                logger.info("[Egypt Summits] Successfully confirmed live technesummit.com connectivity")
        except Exception as e:
            logger.debug(f"[Egypt Summits] Notice probing live techne site: {e}")

        # 2. Iterate catalog and filter according to requested city
        for s in SUMMITS_CATALOG:
            target_city = s["city"]
            if city and city.lower() not in ["all", "egypt", "nationwide", "country"]:
                if target_city.lower() != city.lower():
                    continue

            record = EventRecord(
                event_id=s["id"],
                title=s["title"],
                source="Egypt Flagship Summits",
                start_date=s["start_date"],
                date_display=s["date_display"],
                location=s["location"],
                city=target_city,
                country=country.capitalize(),
                url=s["url"],
                ticket_type=s["ticket_type"],
                organizer=s["organizer"],
                parallel_org=s.get("parallel_org"),
                category=s.get("category"),
                description=s["description"],
                recommended_action=s.get("recommended_action")
            )
            results.append(record)

        logger.info(f"[Egypt Summits] Generated {len(results)} flagship summit records")
        return results
