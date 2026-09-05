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


def test_api_events_social_filter():
    response = client.get("/api/events?source=social")
    assert response.status_code == 200
    data = response.json()
    assert len(data["events"]) > 0
    social_sources = ["facebook", "linkedin", "instagram", "telegram", "social media", "social"]
    for ev in data["events"]:
        assert any(s in ev["source"].lower() for s in social_sources)
        assert len(ev["description"]) >= 100
        assert ev["b2c_score"] > 0


def test_api_events_summits_filter():
    response = client.get("/api/events?source=summits")
    assert response.status_code == 200
    data = response.json()
    assert len(data["events"]) >= 5
    for ev in data["events"]:
        assert ev["category"] == "Flagship Summits"
        assert len(ev["description"]) >= 100
        assert ev["b2c_score"] >= 9.0

