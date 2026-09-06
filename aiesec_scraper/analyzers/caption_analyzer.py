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
    # English Action & Registration Triggers
    r"\bmeet\s+us\b", r"\bregister\s+now\b", r"\blink\s+in\s+bio\b", r"\bjoin\s+us\b",
    r"\bapply\s+now\b", r"\bfill\s+the\s+form\b", r"\bforms?\.gle\b", r"\bgoogle\s+form\b",
    r"\bfree\s+(admission|entry|ticket|attendance)\b", r"\bopen\s+for\s+all\b",
    r"\bsave\s+the\s+date\b", r"\bcall\s+for\s+(speakers|delegates|applicants)\b",
    r"\bapplications?\s+(are\s+)?open\b", r"\brecruitment\s+(is\s+)?open\b",
    # English Event Formats
    r"\bcareer\s+fair\b", r"\bemployment\s+fair\b", r"\bjob\s+fair\b", r"\binternship\s+(day|fair)\b",
    r"\bhackathon\b", r"\bdatathon\b", r"\bideathon\b", r"\bconference\b", r"\bworkshop\b",
    r"\bsummit\b", r"\bevent\b", r"\bbootcamp\b", r"\bwebinar\b", r"\bspeaker\b",
    r"\bsymposium\b", r"\bconclave\b", r"\bcongress\b", r"\bforum\b", r"\bexpo\b",
    r"\bcase\s+competition\b", r"\brobotics\s+(competition|challenge)\b", r"\bmasterclass\b",
    r"\binfo\s+session\b", r"\binduction\b", r"\borientation\s+day\b", r"\bwelcome\s+party\b",
    r"\bcampus\s+activation\b", r"\bgeneral\s+assembly\b",
    # Student Orgs & Campus Bodies
    r"\bstudent\s+union\b", r"\bstudent\s+activity\b", r"\bieee\b", r"\benactus\b",
    r"\bgdsc\b", r"\bgoogle\s+developer\s+student\b", r"\bmsp\b", r"\bmicrosoft\s+student\b",
    r"\bhult\s+prize\b", r"\baiesec\b", r"\bmodel\s+un\b", r"\bmun\b", r"\bmep\b",
    r"\bspe\b", r"\baapg\b", r"\basme\b", r"\bformula\s+student\b", r"\bscci\b", r"\bepsf\b",
    # Arabic Action & Registration Triggers
    r"سجل\s+(الآن|الان)", r"(اللينك|الرابط)\s+في\s+(البايو|البيو)", r"(اللينك|الرابط)\s+في\s+أول\s+(كومنت|تعليق)",
    r"(استمارة|فورم)\s+(التقديم|التسجيل)", r"فتح\s+باب\s+(التقديم|التسجيل|الانضمام)", r"انضم\s+إلينا", r"مستنيينكم",
    r"حضور\s+مجاني", r"التسجيل\s+مجاناً?", r"الدخول\s+بالبطاقة\s+الجامعية", r"(مفتوح|متاح)\s+لجميع\s+الطلاب",
    r"بدون\s+أي\s+رسوم", r"دعوة\s+عامة", r"احجز\s+مكانك",
    # Arabic Event Formats
    r"معرض\s+التوظيف", r"ملتقى\s+التوظيف", r"يوم\s+التوظيف", r"ملتقى\s+توظيف", r"فرص\s+تدريب", r"تدريب\s+صيفي",
    r"مؤتمر", r"قمة", r"منتدى", r"فعالية", r"فعاليات", r"إيفنت", r"ندوة", r"جلسة\s+حوارية", r"سيشن",
    r"ورشة\s+عمل", r"وورك\s+شوب", r"هاكاثون", r"مسابقة", r"تحدي\s+البرمجة", r"معسكر\s+تدريبي", r"بوت\s+كامب",
    r"ريادة\s+أعمال", r"حاضنة\s+أعمال", r"معرض\s+علمي", r"يوم\s+هندسي", r"ملتقى\s+سنوي",
    # Arabic Student Bodies
    r"اتحاد\s+طلاب", r"الأنشطة\s+الطلابية", r"نشاط\s+طلابي", r"أسرة\s+طلابية", r"نموذج\s+محاكاة", r"هالت\s+برايز",
    # Franco / Egyptian Social Media Slang
    r"\bsegel\s+now\b", r"\bel\s+link\s+fel\s+bio\b", r"\blink\s+fel\s+comment\b", r"\bopen\s+for\s+applicants\b"
]

FORM_URL_REGEX = re.compile(
    r"https?://(?:forms\.gle/[\w\-]+|docs\.google\.com/forms/d/e/[\w\-]+/viewform[^\s\"']*|bit\.ly/[\w\-]+|linktr\.ee/[\w\-]+|t\.me/[\w\-]+/\d+|chat\.whatsapp\.com/[\w\-]+)",
    re.IGNORECASE
)


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

    def extract_registration_url(self, caption: str) -> Optional[str]:
        """Extracts direct Google Form, Bitly, Linktree, or registration links from caption text."""
        if not caption:
            return None
        match = FORM_URL_REGEX.search(caption)
        return match.group(0) if match else None

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
                # Also ensure registration link extracted if missing in AI response
                if not ai_result.get("registration_url"):
                    ai_result["registration_url"] = self.extract_registration_url(caption)
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
        if len(title) > 90:
            title = title[:87] + "..."

        # Venue detection with expanded Egyptian campus list
        venue = "Campus Auditorium / TBA"
        venue_catalogs = [
            ("The Greek Campus", ["greek campus", "الجريك كامبس", "مقر الجريك"]),
            ("Cairo University Engineering Quad (CUFE)", ["cufe", "faculty of engineering cairo", "هندسة القاهرة", "جامعة القاهرة"]),
            ("Ain Shams University Al-Zaafaran Hall", ["ain shams", "عين شمس", "قصر الزعفران", "الزعفران"]),
            ("Alexandria University Faculty of Commerce", ["alexandria university", "جامعة الإسكندرية", "شاطبي", "مكتبة الإسكندرية"]),
            ("Tanta University Sebor Campus (Hall 3)", ["tanta university", "جامعة طنطا", "مجمع سبرباي", "سبرباي", "طنطا"]),
            ("Mansoura University Convention Center", ["mansoura university", "جامعة المنصورة", "حاسبات المنصورة"]),
            ("Creativa Innovation Hub (Giza Hub)", ["creativa", "كرياتيفا", "itida", "ايتيدا", "tiec"]),
            ("AUC New Cairo Campus & Venture Lab", ["auc", "الجامعة الأمريكية", "new cairo"]),
            ("GUC Main Campus Complex", ["guc", "الجامعة الألمانية"]),
            ("Bibliotheca Alexandrina Conference Center", ["bibliotheca alexandrina", "مكتبة الإسكندرية"]),
            ("Jesuit Cultural Center Alexandria", ["jesuit", "الجزويت", "مركز الجزويت"]),
            ("Rawabet Art Space Downtown Cairo", ["rawabet", "روابط"]),
            ("Online / Telegram Live Stream", ["online", "zoom", "teams", "بث مباشر", "أونلاين", "اونلاين", "webinar"])
        ]
        caption_lower = caption.lower()
        for v_name, v_triggers in venue_catalogs:
            if any(vt in caption_lower for vt in v_triggers):
                venue = v_name
                break

        # City detection with expanded Egyptian governorates
        city = "Cairo"
        city_triggers = [
            ("Alexandria", ["alexandria", "إسكندرية", "اسكندرية", "الإسكندرية", "الاسكندرية", "شاطبي", "سموحة"]),
            ("Tanta", ["tanta", "طنطا", "الغربية", "gharbia", "سبرباي"]),
            ("Mansoura", ["mansoura", "المنصورة", "الدقهلية", "dakahlia"]),
            ("Assiut", ["assiut", "أسيوط", "اسيوط"]),
            ("Giza", ["giza", "الجيزة", "جيزة", "أكتوبر", "زايد", "الدقي", "المهندسين"]),
            ("Zagazig", ["zagazig", "الزقازيق", "الشرقية"]),
            ("Cairo", ["cairo", "القاهرة", "مدينة نصر", "العباسية", "المعادي", "التجمع", "التحرير"])
        ]
        for c_name, c_keywords in city_triggers:
            if any(ck in caption_lower for ck in c_keywords):
                city = c_name
                break

        # Pricing detection
        ticket_type = "Free" if any(w in caption_lower for w in [
            "free", "مجانا", "مجاني", "بدون رسوم", "حضور مجاني", "الدخول مجاني", "مجاناً"
        ]) else "Registration Required"

        # Registration Form URL
        registration_url = self.extract_registration_url(caption)

        # Date extraction attempt
        extracted_date = None
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
            "registration_url": registration_url,
            "summary": caption[:240]
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
