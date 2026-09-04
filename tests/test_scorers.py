"""Unit tests for the AIESEC B2C Relevance Scorer and Parallel Org Detection."""

import pytest
from aiesec_scraper.scorers import B2CScorer


def test_career_fair_scoring():
    scorer = B2CScorer()
    score, priority, category, tags, action, org = scorer.evaluate(
        title="Cairo University Annual Career & Job Fair 2026",
        description="Connect with top employers, submit CVs, and explore internships.",
        location="Cairo University Campus"
    )
    assert score >= 9.0
    assert priority == "HIGH"
    assert "Career" in category or "University" in category
    assert any(t in tags for t in ["career", "job fair", "student", "cv", "internship"])
    assert "Lead Generation" in action or "Booth" in action or "Flyering" in action


def test_tech_hackathon_scoring():
    scorer = B2CScorer()
    score, priority, category, tags, action, org = scorer.evaluate(
        title="AI Hackathon Egypt 2026",
        description="A 48-hour coding challenge for developers and computer science undergraduates.",
        location="The Greek Campus, Cairo"
    )
    assert score >= 8.5
    assert priority == "HIGH"
    assert "Tech" in category
    assert "hackathon" in tags or "coding" in tags
    assert "Global Talent" in action


def test_parallel_student_org_detection():
    scorer = B2CScorer()
    score, priority, category, tags, action, org = scorer.evaluate(
        title="IEEE Cairo University Student Branch Mega Annual Conference",
        description="Workshops on robotics, embedded systems, and tech careers for Egyptian engineering students.",
        location="Cairo University Hall"
    )
    assert org == "IEEE"
    assert priority == "HIGH"
    assert "IEEE" in tags
    assert "Partner Outreach" in action or "Joint" in action


def test_enactus_detection():
    scorer = B2CScorer()
    score, priority, category, tags, action, org = scorer.evaluate(
        title="Enactus Egypt National Innovation Expo 2026",
        description="Social entrepreneurship and sustainable community projects by university teams.",
        location="The Greek Campus"
    )
    assert org == "Enactus"
    assert priority == "HIGH"


def test_low_relevance_event():
    scorer = B2CScorer()
    score, priority, category, tags, action, org = scorer.evaluate(
        title="Local Neighborhood Flower Gardening Gathering",
        description="Sharing tips on watering indoor plants.",
        location="Maadi"
    )
    assert priority == "LOW"
    assert score <= 5.0
    assert org is None
