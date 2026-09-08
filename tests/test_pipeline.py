"""Unit tests for Pipeline date window filtering and deduplication."""

from datetime import datetime, timedelta
from aiesec_scraper.models import EventRecord
from aiesec_scraper.pipeline import EventPipeline, clean_title_for_comparison


def test_clean_title():
    assert clean_title_for_comparison("The Annual Cairo Career Fair 2026!") == "annual cairo career fair 2026"


def test_date_window_filtering():
    pipeline = EventPipeline({"date_window_months": 6})
    now = datetime.now()

    ev_past = EventRecord(
        event_id="1",
        title="Old Event",
        source="Test",
        start_date=now - timedelta(days=10),
        url="http://test.com/1"
    )
    ev_upcoming = EventRecord(
        event_id="2",
        title="Upcoming Conference",
        source="Test",
        start_date=now + timedelta(days=45),
        url="http://test.com/2"
    )
    ev_too_far = EventRecord(
        event_id="3",
        title="Next Year Event",
        source="Test",
        start_date=now + timedelta(days=250),
        url="http://test.com/3"
    )

    filtered = pipeline._filter_date_window([ev_past, ev_upcoming, ev_too_far])
    assert len(filtered) == 1
    assert filtered[0].title == "Upcoming Conference"


def test_deduplication():
    pipeline = EventPipeline()
    now = datetime.now() + timedelta(days=30)

    ev1 = EventRecord(
        event_id="eb_1",
        title="Egypt Tech Summit 2026",
        source="Eventbrite",
        start_date=now,
        url="http://eventbrite.com/1",
        description="Short description"
    )
    ev2 = EventRecord(
        event_id="ae_2",
        title="Egypt Tech Summit 2026 Tickets",
        source="AllEvents",
        start_date=now,
        url="http://allevents.in/2",
        description="Much longer and detailed description of Egypt Tech Summit"
    )

    deduped = pipeline._deduplicate([ev1, ev2])
    assert len(deduped) == 1
    # Check that platforms got merged
    assert "Eventbrite" in deduped[0].source
    assert "AllEvents" in deduped[0].source
    # Richer description was preserved
    assert "detailed description" in deduped[0].description


def test_enrich_organizer_contacts():
    pipeline = EventPipeline()

    ev_techne = EventRecord(
        event_id="ts_1",
        title="Techne Summit Alexandria 2026",
        source="EgyptSummits",
        url="https://technesummit.com"
    )
    ev_regex = EventRecord(
        event_id="reg_2",
        title="Alex Youth Hackathon",
        source="Facebook",
        url="https://facebook.com/events/123",
        description="Join us! Contact organizers at alexhack@youth.org or call 01012345678 for details. Follow @alexhackathon on IG."
    )

    pipeline._enrich_organizer_contacts([ev_techne, ev_regex])

    # Techne Summit enriched from curated directory
    assert ev_techne.organizer_email == "info@technesummit.com"
    assert ev_techne.organizer_instagram == "technesummit"
    assert ev_techne.organizer_linkedin == "company/techne-summit"
    assert ev_techne.organizer_phone == "+20 120 000 8324"

    # Regex enriched from description
    assert ev_regex.organizer_email == "alexhack@youth.org"
    assert "01012345678" in ev_regex.organizer_phone
    assert ev_regex.organizer_instagram == "alexhackathon"


def test_deduplication_preserves_social_fields():
    pipeline = EventPipeline()
    now = datetime.now() + timedelta(days=20)

    ev_web = EventRecord(
        event_id="web_1",
        title="Cairo AI Bootcamp 2026",
        source="Eventbrite",
        start_date=now,
        url="https://eventbrite.com/ai-bootcamp"
    )
    ev_social = EventRecord(
        event_id="soc_1",
        title="Cairo AI Bootcamp 2026",
        source="Facebook",
        start_date=now,
        url="https://facebook.com/events/ai-bootcamp",
        post_direct_url="https://www.facebook.com/events/987654321012345",
        organizer_profile_url="https://www.facebook.com/cufe.official",
        registration_url="https://forms.gle/aiBootcampCairo2026",
        is_social_first=True
    )

    deduped = pipeline._deduplicate([ev_web, ev_social])
    assert len(deduped) == 1
    record = deduped[0]
    assert record.is_social_first is True
    assert record.post_direct_url == "https://www.facebook.com/events/987654321012345"
    assert record.organizer_profile_url == "https://www.facebook.com/cufe.official"
    assert record.registration_url == "https://forms.gle/aiBootcampCairo2026"

    pipeline._enrich_organizer_contacts(deduped)
    assert record.proof_url == "https://www.facebook.com/events/987654321012345"
    assert record.proof_type == "Direct Social Announcement Post"


def test_clean_event_title():
    from aiesec_scraper.pipeline import clean_event_title

    raw_noisy = "Thu, Jun 11 · 10:00 AM\nCairo Tech Meetup\n1.4K interested · 51 went\nInterested"
    assert clean_event_title(raw_noisy) == "Cairo Tech Meetup"

    single_line = "RiseUp Summit 2026"
    assert clean_event_title(single_line) == "RiseUp Summit 2026"

    # Attendee counts and action buttons must never be treated as valid titles
    assert clean_event_title("Interested") == ""
    assert clean_event_title("328 interested · 44 going") == ""
    assert clean_event_title("104 interested · 9 going") == ""
    assert clean_event_title("63 interested · 13 going") == ""


def test_bad_link_and_non_egypt_filter():
    from aiesec_scraper.pipeline import is_bad_or_non_egypt

    # Generic Facebook root without specific event
    bad_root = EventRecord(
        event_id="bad_1",
        title="Valid Title",
        source="Facebook",
        url="https://www.facebook.com/events/"
    )
    assert is_bad_or_non_egypt(bad_root) is True

    # Invalid protocol
    bad_url = EventRecord(
        event_id="bad_2",
        title="Valid Title",
        source="Web",
        url="#"
    )
    assert is_bad_or_non_egypt(bad_url) is True

    # Foreign US Virginia bleed
    us_event = EventRecord(
        event_id="us_1",
        title="Oktoberfest 5k",
        source="AllEvents",
        location="3950 Wheeler Ave, Alexandria, VA 22304, United States",
        url="https://allevents.in/alexandria/oktoberfest-5k/123"
    )
    assert is_bad_or_non_egypt(us_event) is True

    # Valid Egyptian event
    egypt_event = EventRecord(
        event_id="eg_1",
        title="Bibliotheca Alexandrina Youth Tech Forum",
        source="AllEvents",
        location="Chatby, Alexandria, Egypt",
        url="https://allevents.in/alexandria-eg/youth-tech-forum/456"
    )
    assert is_bad_or_non_egypt(egypt_event) is False


def test_fuzzy_token_deduplication():
    pipeline = EventPipeline()
    now = datetime.now() + timedelta(days=15)

    ev1 = EventRecord(
        event_id="ev_a",
        title="27th Connected Banking Summit - Innovation & AI",
        source="Eventbrite",
        start_date=now,
        url="https://eventbrite.com/cbs-27",
        aiesec_tags=["Banking", "Fintech"],
        description="Short description"
    )
    ev2 = EventRecord(
        event_id="ev_b",
        title="27th Edition Connected Banking Summit Innovation AI",
        source="AllEvents",
        start_date=now,
        url="https://allevents.in/cairo/cbs-27/999",
        aiesec_tags=["AI", "Career"],
        description="Much more detailed description of the connected banking summit"
    )

    deduped = pipeline._deduplicate([ev1, ev2])
    assert len(deduped) == 1
    assert "Eventbrite" in deduped[0].source
    assert "AllEvents" in deduped[0].source
    assert "Banking" in deduped[0].aiesec_tags
    assert "AI" in deduped[0].aiesec_tags
    assert "detailed description" in deduped[0].description



