"""Unit tests for FastAPI Web Dashboard Endpoints."""

from fastapi.testclient import TestClient
from aiesec_scraper.web.app import app
from aiesec_scraper.models import EventRecord

client = TestClient(app)


def test_dashboard_root_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "AIESEC in Tanta" in response.text
    assert "B2C RADAR" in response.text


def test_api_events_filtering():
    response = client.get("/api/events?sort=score_desc")
    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert "metrics" in data
    assert "total_events" in data["metrics"]


def test_api_pitch_generation():
    payload = {
        "event_id": "test_1",
        "member_name": "Karim Mostafa",
        "member_email": "karim.mostafa@aiesec.net",
        "member_phone": "+201098765432",
        "purpose": "event_collaboration"
    }
    response = client.post("/api/pitch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "subject" in data
    assert "body" in data
    assert "Karim Mostafa" in data["body"]
    assert "mailto:" in data["mailto_url"]
