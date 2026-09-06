"""Tests for the /api/social/import and /api/social/auto-scrape endpoints."""

import pytest
from fastapi.testclient import TestClient
from aiesec_scraper.web.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_import_social_events_success(client):
    payload = {
        "events": [
            {
                "event_id": "test_fb_live_12345",
                "title": "Cairo AI and Robotics Youth Summit 2026",
                "url": "https://www.facebook.com/events/123456789012345/",
                "date_display": "March 28, 2026",
                "location": "Greek Campus, Downtown Cairo",
                "city": "Cairo",
                "source": "Facebook Events",
                "description": "Annual student robotics and artificial intelligence exhibition and hackathon bringing together youth engineers and students across Egypt for hands-on technical workshops.",
                "ticket_type": "Free Student Pass"
            }
        ]
    }
    response = client.post("/api/social/import", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["imported"] >= 1
    assert data["total_events"] > 0


def test_import_social_events_empty(client):
    payload = {"events": []}
    response = client.post("/api/social/import", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["imported"] == 0
