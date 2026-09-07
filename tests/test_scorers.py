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


def test_medical_congress_penalties():
    scorer = B2CScorer()
    # Clinical oncology congress
    s1, p1, c1, _, a1, _ = scorer.evaluate(
        title="6th ONCOAZHAR Conference",
        description="Latest clinical oncology updates and surgical management.",
        location="Al Azhar Conference Center"
    )
    assert p1 == "LOW"
    assert s1 <= 4.0
    assert "Medical" in c1

    # Dental / TMJ surgery workshop
    s2, p2, c2, _, a2, _ = scorer.evaluate(
        title="2nd Cairo International TMJ Workshop 2026",
        description="Advanced surgical techniques in temporomandibular joint reconstruction.",
        location="Hilton Cairo Grand Nile"
    )
    assert p2 == "LOW"
    assert s2 <= 4.0
    assert "Medical" in c2


def test_industrial_b2b_penalties():
    scorer = B2CScorer()
    # Banking summit
    s1, p1, c1, _, _, _ = scorer.evaluate(
        title="27th Connected Banking Summit North Africa",
        description="Fintech banking executives discussing enterprise banking solutions.",
        location="Nile Ritz-Carlton"
    )
    assert p1 == "LOW"
    assert s1 <= 4.0
    assert "B2B" in c1 or "Industrial" in c1

    # Textile machinery
    s2, p2, c2, _, _, _ = scorer.evaluate(
        title="The 24th Egypt International Textile Machinery Exhibition",
        description="Heavy spinning, weaving, and textile factory equipment.",
        location="Cairo International Convention Centre"
    )
    assert p2 == "LOW"
    assert s2 <= 4.0
    assert "B2B" in c2 or "Industrial" in c2


def test_social_entertainment_penalties():
    scorer = B2CScorer()
    # Coffee chat
    s1, p1, c1, _, _, _ = scorer.evaluate(
        title="Caribou Coffee Morning Cairo East Walk Mall",
        description="Casual morning coffee chat and socializing.",
        location="Near AUC"
    )
    assert p1 == "LOW"
    assert s1 <= 4.0
    assert "Social" in c1 or "Entertainment" in c1

    # Wedding
    s2, p2, c2, _, _, _ = scorer.evaluate(
        title="Michael and Madonnas Wedding",
        description="Wedding reception and private evening celebration.",
        location="Four Seasons Nile Plaza"
    )
    assert p2 == "LOW"
    assert s2 <= 4.0


def test_calibrated_summits():
    scorer = B2CScorer()
    s1, p1, c1, _, _, _ = scorer.evaluate(
        title="RiseUp Summit 2026",
        description="The MENA region's flagship entrepreneurship and youth innovation gathering.",
        location="Grand Egyptian Museum"
    )
    assert p1 == "HIGH"
    assert s1 >= 9.5
    assert c1 == "Flagship Summits"

