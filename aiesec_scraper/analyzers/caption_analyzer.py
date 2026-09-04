"""Caption and Content Intelligence Analyzer for Social Media Event Announcements."""

import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

ARABIC_MONTHS = {
    "يناير": 1, "فبراير": 2, "مارس": 3, "أبريل": 4, "مايو": 5, "يونيو": 6,
    "يوليو": 7, "أغسطس": 8, "سبتمبر": 9, "أكتوبر": 10, "نوفمبر": 11, "ديسمبر": 12
}

EVENT_TRIGGERS = [
    # English
    r"\bmeet\s+us\b", r"\bregister\s+now\b", r"\blink\s+in\s+bio\b", r"\bjoin\s+us\b",
    r"\bcareer\s+fair\b", r"\bhackathon\b", r"\bconference\b", r"\bworkshop\b",
    r"\bsummit\b", r"\bevent\b", r"\bbootcamp\b", r"\bwebinar\b", r"\bspeaker\b",
    # Arabic
    r"سجل\s+الآن", r"اللينك\s+في\s+البايو", r"معرض\s+التوظيف", r"ملتقى", r"مؤتمر",
    r"ورشة\s+عمل", r"هاكاثون", r"يوم\s+التوظيف", r"حضور\s+مجاني", r"ندوة", r"فعالية"
]


class CaptionAnalyzer:
    """Extracts structured event data from social media captions and flyer text."""

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")

    def is_event_post(self, caption: str) -> bool:
        """Determines if the social post caption represents an actual event."""
        if not caption:
            return False
        caption_lower = caption.lower()
        for pattern in EVENT_TRIGGERS:
            if re.search(pattern, caption_lower, re.IGNORECASE):
                return True
        return False

    def analyze(self, caption: str, flyer_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyzes a caption using Gemini AI if configured, or the resilient rule engine.
        Returns a structured dictionary of event entities.
        """
        if not caption and not flyer_url:
            return {"is_event": False}

        # Use Gemini AI if API key is present
        if self.api_key:
            ai_result = self._analyze_with_gemini(caption, flyer_url)
            if ai_result and ai_result.get("is_event"):
                return ai_result

        # Fallback to local NLP rule engine
        return self._analyze_with_rules(caption)

    def _analyze_with_rules(self, caption: str) -> Dict[str, Any]:
        """Rule-based extractor for Arabic and English event announcements."""
        is_event = self.is_event_post(caption)
        if not is_event:
            return {"is_event": False}

        lines = [line.strip() for line in caption.split("\n") if line.strip()]
        title = lines[0] if lines else "Social Media Event Announcement"
        if len(title) > 80:
            title = title[:77] + "..."

        # Venue detection
        venue = "TBA"
        for v_kw in ["Greek Campus", "AUC", "GUC", "Cairo University", "Alexandria University", "الجامعة الأمريكية", "جامعة القاهرة", "المقر", "MQR", "Online / Zoom"]:
            if v_kw.lower() in caption.lower():
                venue = v_kw
                break

        # City detection
        city = "Cairo"
        for c in ["Alexandria", "Giza", "Mansoura", "Assiut", "Hurghada", "الإسكندرية", "الجيزة", "المنصورة"]:
            if c.lower() in caption.lower():
                city = c
                break

        # Pricing detection
        ticket_type = "Free" if any(w in caption.lower() for w in ["free", "مجانا", "مجاني", "بدون رسوم"]) else "Registration Required"

        # Date extraction attempt
        extracted_date = None
        # Match standard numeric dates like 15/10/2026 or 15-10-2026
        num_date_match = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b", caption)
        if num_date_match:
            try:
                day, month, year = int(num_date_match.group(1)), int(num_date_match.group(2)), int(num_date_match.group(3))
                if year < 100:
                    year += 2000
                extracted_date = datetime(year, month, day)
            except Exception:
                pass

        return {
            "is_event": True,
            "title": title,
            "start_date": extracted_date,
            "venue": venue,
            "city": city,
            "ticket_type": ticket_type,
            "summary": caption[:200]
        }

    def _analyze_with_gemini(self, caption: str, flyer_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Call Gemini API via google-genai to extract structured event data."""
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)

            prompt = (
                "You are an event extraction intelligence tool for AIESEC youth leadership organization in Egypt.\n"
                "Analyze this social media announcement and extract structured details in JSON.\n"
                "JSON format:\n"
                "{\n"
                '  "is_event": true,\n'
                '  "title": "Clear concise event title",\n'
                '  "start_date_iso": "YYYY-MM-DDTHH:MM:SS or null",\n'
                '  "venue": "Venue name or TBA",\n'
                '  "city": "Egyptian city (e.g. Cairo, Alexandria)",\n'
                '  "ticket_type": "Free or Paid",\n'
                '  "organizer": "Hosting entity or club",\n'
                '  "youth_relevance_score": 8.5,\n'
                '  "summary": "1-2 sentence summary"\n'
                "}\n"
                f"Post Text:\n{caption}"
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

            text_resp = response.text
            # Extract JSON block
            json_match = re.search(r"\{.*\}", text_resp, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                if data.get("is_event"):
                    start_dt = None
                    if data.get("start_date_iso"):
                        try:
                            start_dt = datetime.fromisoformat(data["start_date_iso"].replace("Z", ""))
                        except Exception:
                            pass
                    data["start_date"] = start_dt
                    return data
        except Exception as e:
            logger.debug(f"Gemini caption analysis notice: {e}")

        return None
