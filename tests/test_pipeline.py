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


