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


def test_api_proof_verify():
    response = client.post("/api/proof/verify", json={"url": "https://www.facebook.com/events/12345678"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_verified"] is True
    assert "facebook.com" in data["proof_domain"]
    assert "VERIFIED" in data["proof_status"]
    assert "post_direct_url" in data
    assert "organizer_account_url" in data
    assert "registration_url" in data


def test_api_events_social_only():
    response = client.get("/api/events?social_only=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data["events"]) > 0
    for ev in data["events"]:
        assert ev.get("is_social_first") is True or any(k in ev["source"].lower() for k in ["facebook", "linkedin", "instagram", "telegram"])


def test_api_leads_search():
    response = client.post("/api/leads/search", json={"role_filter": "sponsorship", "deep_scan": True})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["leads"]) > 0
    first_lead = data["leads"][0]
    assert "email" in first_lead
    assert "phone" in first_lead
    assert "sponsorship" in first_lead["role_category"]


def test_api_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total_events" in data
    assert "high_priority" in data
    assert "flagship_events" in data


def test_api_exports():
    res_csv = client.get("/api/export/csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers.get("content-type", "")

    res_xlsx = client.get("/api/export/excel")
    assert res_xlsx.status_code == 200
    assert len(res_xlsx.content) > 1000


