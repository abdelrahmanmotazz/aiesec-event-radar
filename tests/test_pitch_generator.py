"""Unit tests for the AIESEC Partnership & PR Pitch Generator."""

from aiesec_scraper.models import EventRecord
from aiesec_scraper.analyzers.pitch_generator import PitchGenerator


def test_event_collaboration_pitch():
    ev = EventRecord(
        event_id="test_ev_1",
        title="Cairo University Tech Summit 2026",
        source="Eventbrite",
        date_display="Oct 20, 2026 · 10:00 AM",
        location="Grand Hall, Cairo University",
        city="Cairo",
        country="Egypt",
        url="https://eventbrite.com/e/cairo-tech-summit",
        organizer="Tech Club Committee"
    )

    pitch = PitchGenerator.generate_pitch(
        event=ev,
        member_name="Nour El-Din",
        member_email="nour.eldin@aiesec.net",
        member_phone="+201001122334",
        purpose="event_collaboration"
    )

    assert "Event Collaboration & Booth Partnership" in pitch["subject"]
    assert "Nour El-Din" in pitch["body"]
    assert "nour.eldin@aiesec.net" in pitch["body"]
    assert "+201001122334" in pitch["body"]
    assert "booth" in pitch["body"].lower()
    assert "mailto:" in pitch["mailto_url"]


def test_pr_collaboration_pitch():
    ev = EventRecord(
        event_id="test_ev_2",
        title="Alexandria Youth Leadership Conference",
        source="Meetup",
        date_display="Nov 12, 2026",
        location="Alexandria Center",
        city="Alexandria",
        country="Egypt",
        url="https://meetup.com/alex-youth",
        organizer="Alex Youth Foundation"
    )

    pitch = PitchGenerator.generate_pitch(
        event=ev,
        member_name="Salma Farouk",
        member_email="salma.farouk@aiesec.net",
        member_phone="+201223344556",
        purpose="pr_collaboration"
    )

    assert "PR & Media Partnership" in pitch["subject"]
    assert "Salma Farouk" in pitch["body"]
    assert "salma.farouk@aiesec.net" in pitch["body"]
    assert "social media" in pitch["body"].lower()
    assert "cross-promotion" in pitch["body"].lower()
