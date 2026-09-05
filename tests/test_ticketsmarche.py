"""Unit tests for TicketsMarcheScraper."""

import pytest
from bs4 import BeautifulSoup
from aiesec_scraper.scrapers.ticketsmarche import TicketsMarcheScraper

SAMPLE_TM_HTML = """
<html>
<body>
<div class="card">
    <a href="/event/Tech_Conference_9999#ticketsbuy" onclick='window.dataLayer = window.dataLayer || [];window.dataLayer.push({"event":"select_item","ecommerce":{"items":[{"item_name":"Egypt Tech Innovation Fest","item_id":"Tech_Conference_9999","price":"250.00","item_brand":"TicketsMarche","item_category":"Conferences"}],"vendor_name":"Egypt Tech Council"}});'>
        Book Now
    </a>
    <p>Oct 15 | 07:00 PM | Greek Campus Downtown Cairo | Organized by Egypt Tech Council</p>
</div>
<div class="card">
    <a href="/event/Alex_Youth_Fest_8888#ticketsbuy" onclick='window.dataLayer = window.dataLayer || [];window.dataLayer.push({"event":"select_item","ecommerce":{"items":[{"item_name":"Alexandria Youth Leadership Forum","item_id":"Alex_Youth_Fest_8888","price":"0.00","item_brand":"TicketsMarche","item_category":"Youth"}],"vendor_name":"Alexandria Youth Association"}});'>
        Book Now
    </a>
    <p>Nov 20 | 06:00 PM | Bibliotheca Alexandrina | Organized by Alexandria Youth Association</p>
</div>
</body>
</html>
"""

def test_ticketsmarche_parse_soup():
    scraper = TicketsMarcheScraper()
    soup = BeautifulSoup(SAMPLE_TM_HTML, "lxml")
    events = scraper._parse_soup(soup, seen_ids=set(), city=None)
    
    assert len(events) == 2
    
    e1 = next(e for e in events if e.event_id == "tm_Tech_Conference_9999")
    assert e1.title == "Egypt Tech Innovation Fest"
    assert e1.source == "TicketsMarche"
    assert e1.organizer == "Egypt Tech Council"
    assert "250.00 EGP" in e1.ticket_type
    assert e1.city == "Cairo"
    assert e1.start_date is not None
    assert e1.start_date.month == 10
    assert e1.start_date.day == 15

    e2 = next(e for e in events if e.event_id == "tm_Alex_Youth_Fest_8888")
    assert e2.title == "Alexandria Youth Leadership Forum"
    assert e2.city == "Alexandria"
    assert e2.start_date.month == 11
    assert e2.start_date.day == 20

def test_ticketsmarche_city_filter():
    scraper = TicketsMarcheScraper()
    soup = BeautifulSoup(SAMPLE_TM_HTML, "lxml")
    
    alex_events = scraper._parse_soup(soup, seen_ids=set(), city="alexandria")
    assert len(alex_events) == 1
    assert alex_events[0].city == "Alexandria"
