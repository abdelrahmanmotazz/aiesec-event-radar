"""AIESEC B2C Relevance Scoring, Parallel Org Detection, and Opportunity Engine."""

import re
from typing import Dict, List, Optional, Tuple


PARALLEL_ORG_PATTERNS = {
    "IEEE": [r"\bieee\b", r"ieee\s+student\s+branch", r"ieee\s+egypt"],
    "Enactus": [r"\benactus\b"],
    "Hult Prize": [r"\bhult\s+prize\b", r"\bhult\b"],
    "Toastmasters": [r"\btoastmasters\b", r"toastmasters\s+club"],
    "Google Developer Group (GDG)": [r"\bgdg\b", r"google\s+developer\s+groups?", r"\bgdsc\b"],
    "TEDx": [r"\btedx\b", r"tedx[a-z]+"],
    "Rotaract": [r"\brotaract\b", r"rotary\s+youth"],
    "Model United Nations (MUN)": [r"\bmun\b", r"model\s+united\s+nations", r"\bcairo\s+mun\b"],
}

DEFAULT_KEYWORD_RULES = {
    "Flagship Summits": {
        "weight": 10,
        "action": "Major National Activation: Deploy LC Delegation, Booth Presence & Global Volunteer Recruitment",
        "terms": [
            "techne", "techne summit", "riseup", "riseup summit", "career summit",
            "egypt career summit", "youth summit", "national congress", "she can",
            "she can summit", "national exposition", "delta youth", "innovation week",
            "cairo ict", "seamless"
        ]
    },
    "Career & Recruitment Fairs": {
        "weight": 10,
        "action": "Booth Booking & Direct Lead Generation for Global Talent / Teacher",
        "terms": [
            "career", "job fair", "employment", "recruitment", "internship",
            "career day", "hiring", "cv", "resume", "fresh graduate", "linkedin",
            "job seekers", "career expo"
        ]
    },
    "University & Student Summits": {
        "weight": 10,
        "action": "Campus Activation, Flyering & Physical Presence",
        "terms": [
            "student", "university", "campus", "youth", "undergraduate",
            "auc", "guc", "cairo university", "ain shams", "alexandria university",
            "bue", "msa", "giu", "must", "aast", "youth summit", "student union"
        ]
    },
    "Parallel Student Org / Youth Initiative": {
        "weight": 10,
        "action": "Partner Outreach: Co-marketing, Joint Booth, or Workshop Collaboration",
        "terms": [
            "ieee", "enactus", "hult prize", "toastmasters", "gdg", "google developer",
            "tedx", "rotaract", "lions club", "youth speak", "mun", "model united nations"
        ]
    },
    "Tech & Hackathons": {
        "weight": 10,
        "action": "Promote Global Talent IT & Tech Internship Opportunities",
        "terms": [
            "hackathon", "developer", "coding", "software", "artificial intelligence",
            "ai summit", "machine learning", "data science", "web development",
            "robotics", "cybersecurity", "tech expo"
        ]
    },
    "Leadership & Skills Workshops": {
        "weight": 9,
        "action": "Speaker Outreach, Workshop Co-hosting & AIESEC Presentation",
        "terms": [
            "leadership", "soft skills", "public speaking", "entrepreneurship",
            "startup", "incubator", "accelerator", "pitch", "bootcamp",
            "empowerment", "management", "business case"
        ]
    },
    "Volunteering & Social Impact / SDGs": {
        "weight": 9,
        "action": "Promote Global Volunteer Projects & SDG Alignment",
        "terms": [
            "volunteer", "volunteering", "ngo", "sdg", "sustainable development",
            "social impact", "climate", "charity", "community service",
            "un", "united nations", "environment", "green"
        ]
    },
    "Intercultural & Language Exchanges": {
        "weight": 7,
        "action": "Cultural Stand / Intercultural Experience Promotion",
        "terms": [
            "cultural", "language exchange", "cross-cultural", "embassy",
            "study abroad", "international students", "erasmus", "festival",
            "expo", "heritage"
        ]
    },
    "Arts & Entertainment": {
        "weight": 4,
        "action": "Youth Crowd Presence / Brand Awareness",
        "terms": [
            "concert", "music festival", "comedy", "theatre", "art exhibition",
            "film screening", "standup"
        ]
    }
}


class B2CScorer:
    """Evaluates events against AIESEC youth recruitment and partnership criteria."""

    def __init__(self, custom_rules: Dict = None):
        self.rules = custom_rules or DEFAULT_KEYWORD_RULES

    def detect_parallel_org(self, text: str) -> Optional[str]:
        """Detects if an event is organized by or partnered with a known student/youth org."""
        lower_text = text.lower()
        for org_name, patterns in PARALLEL_ORG_PATTERNS.items():
            for p in patterns:
                if re.search(p, lower_text, re.IGNORECASE):
                    return org_name
        return None

    def evaluate(self, title: str, description: str = "", location: str = "") -> Tuple[float, str, str, List[str], str, Optional[str]]:
        """
        Calculates the B2C opportunity score and determines relevant tags.
        
        Returns:
            (b2c_score, b2c_priority, primary_category, tags, recommended_action, parallel_org)
        """
        combined_text = f"{title} {description} {location}".lower()

        # Check for parallel youth organization
        detected_org = self.detect_parallel_org(combined_text)

        matched_categories = []
        all_matched_tags = []
        max_weight = 0
        score_sum = 0
        total_matches = 0

        for category, rule in self.rules.items():
            weight = rule.get("weight", 5)
            terms = rule.get("terms", [])
            action = rule.get("action", "General Monitoring")

            cat_matches = []
            for term in terms:
                if len(term.split()) == 1 and len(term) <= 4:
                    pattern = rf"\b{re.escape(term)}\b"
                else:
                    pattern = re.escape(term)

                if re.search(pattern, combined_text, re.IGNORECASE):
                    cat_matches.append(term)

            if cat_matches:
                matched_categories.append((category, weight, action, cat_matches))
                all_matched_tags.extend(cat_matches)
                score_sum += weight * len(cat_matches)
                total_matches += len(cat_matches)
                if weight > max_weight:
                    max_weight = weight

        if not matched_categories:
            return (
                3.0,
                "LOW",
                "General Event",
                ["general"],
                "Monitor for potential youth presence",
                detected_org
            )

        # Sort by rule weight descending, then by number of matching terms
        matched_categories.sort(key=lambda x: (x[1], len(x[3])), reverse=True)
        primary_category, primary_weight, primary_action, _ = matched_categories[0]

        # If a parallel student org is detected, prioritize collaboration action
        if detected_org:
            all_matched_tags = [t for t in all_matched_tags if t.lower() != detected_org.lower()]
            all_matched_tags.insert(0, detected_org)
            if primary_category not in ["Flagship Summits", "Career & Recruitment Fairs"]:
                primary_category = "Parallel Student Org / Youth Initiative"
                primary_action = f"Partner Outreach with {detected_org}: Joint Activation / PR Collaboration"

        # Calculate normalized score out of 10
        raw_score = primary_weight + min(total_matches * 0.4, 2.0)
        final_score = round(min(raw_score, 10.0), 1)

        # Priority banding
        if final_score >= 8.5:
            priority = "HIGH"
        elif final_score >= 6.0:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        unique_tags = list(dict.fromkeys(all_matched_tags))[:6]

        return (
            final_score,
            priority,
            primary_category,
            unique_tags,
            primary_action,
            detected_org
        )
