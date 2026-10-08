"""Caption and Content Intelligence Analyzer for Social Media Event Announcements."""

import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

ARABIC_DIGITS_MAP = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

ARABIC_MONTHS = {
    "يناير": 1, "فبراير": 2, "مارس": 3, "أبريل": 4, "ابريل": 4, "مايو": 5, "يونيو": 6,
    "يوليو": 7, "أغسطس": 8, "اغسطس": 8, "سبتمبر": 9, "أكتوبر": 10, "اكتوبر": 10,
    "نوفمبر": 11, "ديسمبر": 12
}

MONTH_ABBR = [
    "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

EVENT_TRIGGERS = [
    # English Action & Registration Triggers
    r"\bmeet\s+us\b", r"\bregister\s+now\b", r"\blink\s+in\s+bio\b", r"\bjoin\s+us\b",
    r"\bapply\s+now\b", r"\bfill\s+the\s+form\b", r"\bforms?\.gle\b", r"\bgoogle\s+form\b",
    r"\bfree\s+(admission|entry|ticket|attendance)\b", r"\bopen\s+for\s+all\b",
    r"\bsave\s+the\s+date\b", r"\bcall\s+for\s+(speakers|delegates|applicants|sponsors)\b",
    r"\bapplications?\s+(are\s+)?open\b", r"\brecruitment\s+(is\s+)?open\b", r"\brsvp\b",
    # English Event Formats
    r"\bcareer\s+fair\b", r"\bemployment\s+fair\b", r"\bjob\s+fair\b", r"\binternship\s+(day|fair)\b",
    r"\bhackathon\b", r"\bdatathon\b", r"\bideathon\b", r"\bconference\b", r"\bworkshop\b",
    r"\bsummit\b", r"\bevent\b", r"\bbootcamp\b", r"\bwebinar\b", r"\bspeaker\b",
    r"\bsymposium\b", r"\bconclave\b", r"\bcongress\b", r"\bforum\b", r"\bexpo\b",
    r"\bcase\s+competition\b", r"\brobotics\s+(competition|challenge)\b", r"\bmasterclass\b",
    r"\binfo\s+session\b", r"\binduction\b", r"\borientation\s+day\b", r"\bwelcome\s+party\b",
    r"\bcampus\s+activation\b", r"\bgeneral\s+assembly\b", r"\bopen\s+day\b",
    # Student Orgs & Campus Bodies
    r"\bstudent\s+union\b", r"\bstudent\s+activity\b", r"\bieee\b", r"\benactus\b",
    r"\bgdsc\b", r"\bgdg\b", r"\bgoogle\s+developer\b", r"\bmsp\b", r"\bmicrosoft\s+student\b",
    r"\bhult\s+prize\b", r"\bmodel\s+un\b", r"\bmun\b", r"\bmep\b",
    r"\bspe\b", r"\baapg\b", r"\basme\b", r"\bformula\s+student\b", r"\bscci\b", r"\bepsf\b", r"\bifmsa\b",
    # Arabic Action & Registration Triggers
    r"سجل\s+(الآن|الان)", r"(اللينك|الرابط)\s+في\s+(البايو|البيو)", r"(اللينك|الرابط)\s+في\s+أول\s+(كومنت|تعليق)",
    r"(استمارة|فورم)\s+(التقديم|التسجيل)", r"فتح\s+باب\s+(التقديم|التسجيل|الانضمام)", r"انضم\s+إلينا", r"مستنيينكم",
    r"حضور\s+مجاني", r"التسجيل\s+مجاناً?", r"الدخول\s+بالبطاقة\s+الجامعية", r"(مفتوح|متاح)\s+لجميع\s+الطلاب",
    r"بدون\s+أي\s+رسوم", r"دعوة\s+عامة", r"احجز\s+مكانك", r"احجز\s+تذكرتك",
    # Arabic Event Formats
    r"معرض\s+التوظيف", r"ملتقى\s+التوظيف", r"يوم\s+التوظيف", r"ملتقى\s+توظيف", r"فرص\s+تدريب", r"تدريب\s+صيفي",
    r"مؤتمر", r"قمة", r"منتدى", r"فعالية", r"فعاليات", r"إيفنت", r"ايفنت", r"ندوة", r"جلسة\s+حوارية", r"سيشن",
    r"ورشة\s+عمل", r"وورك\s+شوب", r"هاكاثون", r"مسابقة", r"تحدي\s+البرمجة", r"معسكر\s+تدريبي", r"بوت\s+كامب",
    r"ريادة\s+أعمال", r"حاضنة\s+أعمال", r"معرض\s+علمي", r"يوم\s+هندسي", r"ملتقى\s+سنوي",
    # Arabic Student Bodies
    r"اتحاد\s+طلاب", r"الأنشطة\s+الطلابية", r"نشاط\s+طلابي", r"أسرة\s+طلابية", r"نموذج\s+محاكاة", r"هالت\s+برايز",
    # Franco / Egyptian Social Media Slang
    r"\bsegel\s+now\b", r"\bel\s+link\s+fel\s+bio\b", r"\blink\s+fel\s+comment\b", r"\bopen\s+for\s+applicants\b"
]

FORM_URL_REGEX = re.compile(
    r"https?://(?:forms\.gle/[\w\-]+|docs\.google\.com/forms/d/e/[\w\-]+/viewform[^\s\"']*|bit\.ly/[\w\-]+|linktr\.ee/[\w\-_.]+|lu\.ma/[\w\-]+|eventbrite\.com/e/[\w\-]+|ticketsmarche\.com/[\w\-_/]+|collardtickets\.com/[\w\-_/]+|t\.me/[\w\-]+(?:/\d+)?|chat\.whatsapp\.com/[\w\-]+)",
    re.IGNORECASE
)

HYPE_LINE_REGEX = re.compile(
    r"^(?:[\W_]|are you ready|stay tuned|big news|announcement|save the date|breaking|جاهزين|مستعدين|مفاجأة|قريبا|قريباً|تنبيه|إعلان هام|اعلان هام)+$",
    re.IGNORECASE
)


def normalize_arabic_digits(text: str) -> str:
    """Convert Eastern Arabic numerals (٠-٩) to standard ASCII digits (0-9)."""
    return text.translate(ARABIC_DIGITS_MAP) if text else ""


class CaptionAnalyzer:
    """Extracts structured event data from social media captions, URLs, and flyer text."""

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")

    def is_event_post(self, caption: str) -> bool:
        """Determines if the social post caption represents an actual event."""
        if not caption:
            return False
        caption_lower = normalize_arabic_digits(caption).lower()
        for pattern in EVENT_TRIGGERS:
            if re.search(pattern, caption_lower, re.IGNORECASE):
                return True
        return False

    def extract_registration_url(self, caption: str) -> Optional[str]:
        """Extracts direct Google Form, Bitly, Linktree, Luma, or ticketing links from caption text."""
        if not caption:
            return None
        match = FORM_URL_REGEX.search(caption)
        return match.group(0) if match else None

    def extract_contacts(self, caption: str) -> Dict[str, Optional[str]]:
        """Extracts organizer email, Egyptian mobile/WhatsApp number, and Instagram handle from caption."""
        norm = normalize_arabic_digits(caption or "")
        email = None
        phone = None
        instagram = None

        email_m = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", norm)
        if email_m and not email_m.group(0).lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            email = email_m.group(0)

        phone_m = re.search(r"(?:\+?20[\s\-]?|0)1[0125][\s\-]?\d{4}[\s\-]?\d{4}\b|\b1[5679]\d{3}\b", norm)
        if phone_m:
            phone = re.sub(r"[\s\-]+", "", phone_m.group(0))

        clean_no_emails = re.sub(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", " ", norm)
        ig_m = re.search(r"(?:instagram\.com/|(?<![\w.-])@)([a-zA-Z0-9_.]{3,30})", clean_no_emails)
        if ig_m:
            handle = ig_m.group(1)
            if handle.lower() not in ("gmail", "yahoo", "hotmail", "outlook", "share", "reel", "explore", "events"):
                instagram = handle

        return {
            "email": email,
            "phone": phone,
            "instagram": instagram
        }

    def extract_datetime_from_caption(self, caption: str, ref_now: Optional[datetime] = None) -> tuple[Optional[datetime], Optional[str]]:
        """Extracts start_date and human-readable date_display from Arabic, English, or numeric dates."""
        if not caption:
            return None, None
        if ref_now is None:
            ref_now = datetime.now()

        norm = normalize_arabic_digits(caption)

        # 1. Check Arabic date patterns: e.g. "15 نوفمبر 2026" or "يوم الجمعة 20 أكتوبر"
        for ar_month, m_num in ARABIC_MONTHS.items():
            pattern = rf"\b(\d{{1,2}})(?:\s*(?:-|إلى|الى|و)\s*\d{{1,2}})?\s+(?:من\s+)?(?:شهر\s+)?{ar_month}(?:\s+(\d{{4}}))?"
            m_ar = re.search(pattern, norm)
            if m_ar:
                day = int(m_ar.group(1))
                year = int(m_ar.group(2)) if m_ar.group(2) else ref_now.year
                try:
                    dt = datetime(year, m_num, day, 10, 0)
                    if not m_ar.group(2) and dt.date() < ref_now.date():
                        dt = datetime(year + 1, m_num, day, 10, 0)
                    return dt, f"{MONTH_ABBR[m_num]} {day:02d}, {dt.year}"
                except ValueError:
                    pass

        # 2. Check numeric date patterns: DD/MM/YYYY or YYYY-MM-DD
        m_iso = re.search(r"\b(202[6-9])[/-](\d{1,2})[/-](\d{1,2})\b", norm)
        if m_iso:
            try:
                y, m, d = int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3))
                dt = datetime(y, m, d, 10, 0)
                return dt, f"{MONTH_ABBR[m]} {d:02d}, {y}"
            except ValueError:
                pass

        m_dmy = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](202[6-9]|\d{2})\b", norm)
        if m_dmy:
            try:
                d, m, y = int(m_dmy.group(1)), int(m_dmy.group(2)), int(m_dmy.group(3))
                if y < 100:
                    y += 2000
                dt = datetime(y, m, d, 10, 0)
                return dt, f"{MONTH_ABBR[m]} {d:02d}, {y}"
            except ValueError:
                pass

        # 3. Check English date patterns across lines via BaseScraper.parse_datetime
        from ..scrapers.base import BaseScraper
        for line in norm.split("\n"):
            line_clean = line.strip()
            if not line_clean:
                continue
            if re.search(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b", line_clean, re.IGNORECASE) and re.search(r"\b\d{1,2}\b", line_clean):
                parsed = BaseScraper.parse_datetime(line_clean, ref_now=ref_now)
                if parsed:
                    return parsed, parsed.strftime("%b %d, %Y")

        return None, None

    def analyze(self, caption: str, flyer_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyzes a caption using Gemini AI if configured, or the resilient bilingual NLP rule engine.
        Returns a structured dictionary of event entities.
        """
        if not caption and not flyer_url:
            return {"is_event": False}

        # Use Gemini AI if API key is present
        if self.api_key:
            ai_result = self._analyze_with_gemini(caption, flyer_url)
            if ai_result and ai_result.get("is_event"):
                if not ai_result.get("registration_url"):
                    ai_result["registration_url"] = self.extract_registration_url(caption)
                contacts = self.extract_contacts(caption)
                ai_result.setdefault("organizer_email", contacts["email"])
                ai_result.setdefault("organizer_phone", contacts["phone"])
                ai_result.setdefault("organizer_instagram", contacts["instagram"])
                return ai_result

        # Fallback to local bilingual NLP rule engine
        return self._analyze_with_rules(caption)

    def _select_best_title(self, lines: list[str]) -> str:
        """Selects the cleanest headline from multi-line social post text."""
        if not lines:
            return "Social Media Event Announcement"

        for line in lines:
            # Strip leading/trailing emojis and bullets
            cleaned = re.sub(r"^[\s🔥🚨📢✨⚡🌟🎉🎊📌📍🗓️📅⏰⏳🔗👉👇•·\-–—:|]+|[\s🔥🚨📢✨⚡🌟🎉🎊📌📍🔗•·\-–—:|]+$", "", line).strip()
            if len(cleaned) < 5:
                continue
            if cleaned.startswith(("http://", "https://", "#")):
                continue
            if HYPE_LINE_REGEX.match(cleaned):
                continue
            if re.match(r"^(?:date|time|location|venue|where|when|link|register|التاريخ|الموعد|المكان|العنوان|للتسجيل)\s*[:\-]", cleaned, re.IGNORECASE):
                continue
            if len(cleaned) > 95:
                return cleaned[:92].rstrip() + "..."
            return cleaned

        fallback = lines[0]
        return fallback[:92] + "..." if len(fallback) > 95 else fallback

    def _analyze_with_rules(self, caption: str) -> Dict[str, Any]:
        """Rule-based extractor for Arabic, English, and Franco-Arabic event announcements."""
        is_event = self.is_event_post(caption)
        if not is_event:
            return {"is_event": False}

        lines = [line.strip() for line in caption.split("\n") if line.strip()]
        title = self._select_best_title(lines)

        # Venue detection with expanded Egyptian campus & innovation hub catalog
        venue = "Campus Auditorium / TBA"
        venue_catalogs = [
            ("The Greek Campus", ["greek campus", "الجريك كامبس", "مقر الجريك"]),
            ("Cairo University Engineering Quad (CUFE)", ["cufe", "faculty of engineering cairo", "هندسة القاهرة", "جامعة القاهرة", "cairo university"]),
            ("Ain Shams University Al-Zaafaran Hall", ["ain shams", "عين شمس", "قصر الزعفران", "الزعفران"]),
            ("Alexandria University Conference Center", ["alexandria university", "جامعة الإسكندرية", "جامعة الاسكندرية", "شاطبي"]),
            ("Tanta University Sebor Campus (Hall 3)", ["tanta university", "جامعة طنطا", "مجمع سبرباي", "سبرباي", "طنطا"]),
            ("Mansoura University Convention Center", ["mansoura university", "جامعة المنصورة", "حاسبات المنصورة"]),
            ("Zagazig University Grand Hall", ["zagazig university", "جامعة الزقازيق"]),
            ("Assiut University Conference Center", ["assiut university", "جامعة أسيوط", "جامعة اسيوط"]),
            ("Creativa Innovation Hub", ["creativa", "كرياتيفا", "itida", "ايتيدا", "tiec"]),
            ("AUC New Cairo Campus & Venture Lab", ["auc", "الجامعة الأمريكية", "american university in cairo"]),
            ("GUC Main Campus Complex", ["guc", "الجامعة الألمانية", "german university in cairo"]),
            ("BUE Campus El Shorouk", ["bue", "الجامعة البريطانية", "british university in egypt"]),
            ("Nile University Smart Village Campus", ["nile university", "جامعة النيل", "smart village", "القرية الذكية"]),
            ("Zewail City of Science and Technology", ["zewail", "مدينة زويل", "جامعة زويل"]),
            ("Bibliotheca Alexandrina Conference Center", ["bibliotheca alexandrina", "مكتبة الإسكندرية", "مكتبة الاسكندرية"]),
            ("Egypt International Exhibition Center (EIEC)", ["eiec", "مركز مصر للمعارض", "المنارة", "al manara"]),
            ("Jesuit Cultural Center Alexandria", ["jesuit", "الجزويت", "مركز الجزويت"]),
            ("Rawabet Art Space Downtown Cairo", ["rawabet", "روابط"]),
            ("Consoleya Coworking Space Downtown Cairo", ["consoleya", "القنصلية"]),
            ("Online / Live Stream", ["online", "zoom", "teams", "بث مباشر", "أونلاين", "اونلاين", "webinar"])
        ]
        caption_lower = normalize_arabic_digits(caption).lower()
        for v_name, v_triggers in venue_catalogs:
            if any(vt in caption_lower for vt in v_triggers):
                venue = v_name
                break

        # City detection with expanded Egyptian governorates
        city = "Cairo"
        city_triggers = [
            ("Alexandria", ["alexandria", "إسكندرية", "اسكندرية", "الإسكندرية", "الاسكندرية", "شاطبي", "سموحة", "gleem", "san stefano"]),
            ("Tanta", ["tanta", "طنطا", "الغربية", "gharbia", "سبرباي"]),
            ("Mansoura", ["mansoura", "المنصورة", "الدقهلية", "dakahlia"]),
            ("Assiut", ["assiut", "أسيوط", "اسيوط"]),
            ("Giza", ["giza", "الجيزة", "جيزة", "أكتوبر", "6th of october", "sheikh zayed", "زايد", "الدقي", "المهندسين", "smart village"]),
            ("Sharkia", ["zagazig", "الزقازيق", "الشرقية", "sharkia"]),
            ("Port Said", ["port said", "بورسعيد"]),
            ("Suez", ["suez", "السويس", "ismailia", "الإسماعيلية"]),
            ("New Cairo", ["new cairo", "القاهرة الجديدة", "التجمع", "fifth settlement", "el shorouk", "الشروق"]),
            ("Cairo", ["cairo", "القاهرة", "مدينة نصر", "العباسية", "المعادي", "التحرير", "وسط البلد", "مصر الجديدة", "heliopolis", "maadi", "nasr city", "zamalek"])
        ]
        for c_name, c_keywords in city_triggers:
            if any(ck in caption_lower for ck in c_keywords):
                city = c_name
                break

        # Pricing detection
        ticket_type = "Free" if any(w in caption_lower for w in [
            "free", "مجانا", "مجاني", "بدون رسوم", "حضور مجاني", "الدخول مجاني", "مجاناً", "open for all"
        ]) else "Registration Required"

        # Registration Form URL
        registration_url = self.extract_registration_url(caption)

        # Date extraction
        extracted_date, date_display = self.extract_datetime_from_caption(caption)

        # Organizer & Contacts extraction
        contacts = self.extract_contacts(caption)
        organizer = "Social Event Host"
        org_m = re.search(r"(?:organized by|hosted by|presented by|powered by|تنظيم|برعاية)\s*[:\-]?\s*([^\n,.|]{3,50})", caption, re.IGNORECASE)
        if org_m:
            organizer = org_m.group(1).strip()

        return {
            "is_event": True,
            "title": title,
            "start_date": extracted_date,
            "date_display": date_display or "Upcoming / Live",
            "venue": venue,
            "city": city,
            "ticket_type": ticket_type,
            "registration_url": registration_url,
            "organizer": organizer,
            "organizer_email": contacts["email"],
            "organizer_phone": contacts["phone"],
            "organizer_instagram": contacts["instagram"],
            "summary": caption[:280]
        }

    def _analyze_with_gemini(self, caption: str, flyer_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Call Gemini API via google-genai to extract structured event data."""
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)

            prompt = (
                "You are an event extraction intelligence tool for Youth Event Radar in Egypt.\n"
                "Analyze this social media announcement and extract structured details in JSON.\n"
                "JSON format:\n"
                "{\n"
                '  "is_event": true,\n'
                '  "title": "Clear concise event title",\n'
                '  "start_date_iso": "YYYY-MM-DDTHH:MM:SS or null",\n'
                '  "venue": "Venue name or TBA",\n'
                '  "city": "Egyptian city (e.g. Cairo, Alexandria, Tanta, Mansoura, Giza, Assiut)",\n'
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
