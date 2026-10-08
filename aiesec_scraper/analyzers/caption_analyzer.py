"""Caption and Content Intelligence Analyzer for Social Media Event Announcements."""

import base64
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

    def _analyze_with_gemini(
        self,
        caption: str,
        flyer_url: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        mime_type: str = "image/png",
        api_key_override: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Call Gemini 2.5 Flash (Text + Multimodal Vision) via google-genai to extract structured event data."""
        active_key = api_key_override or self.api_key
        if not active_key:
            return None
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=active_key)

            if not image_bytes and flyer_url and flyer_url.startswith(("http://", "https://")):
                try:
                    import httpx
                    with httpx.Client(timeout=6.0, follow_redirects=True) as http_client:
                        img_resp = http_client.get(flyer_url)
                        if img_resp.status_code == 200 and len(img_resp.content) > 100:
                            image_bytes = img_resp.content
                            ct = img_resp.headers.get("content-type", "")
                            if "image/" in ct:
                                mime_type = ct.split(";")[0].strip()
                except Exception as img_err:
                    logger.debug(f"Flyer fetch notice for {flyer_url}: {img_err}")

            prompt = (
                "You are an event extraction & poster OCR intelligence engine for Youth Event Radar in Egypt.\n"
                "Analyze this social media announcement and/or event flyer image (Arabic & English) and extract structured details in JSON.\n"
                "Read all visible text on the flyer image including event title, Arabic/English dates, university campus/hall, QR/registration URL, and contacts.\n"
                "JSON format:\n"
                "{\n"
                '  "is_event": true,\n'
                '  "title": "Clear concise event title",\n'
                '  "start_date_iso": "YYYY-MM-DDTHH:MM:SS or null",\n'
                '  "date_display": "Human readable date e.g. Nov 21, 2026",\n'
                '  "venue": "Venue/University hall name or TBA",\n'
                '  "city": "Egyptian city (e.g. Cairo, Alexandria, Tanta, Mansoura, Giza, Assiut, New Cairo)",\n'
                '  "ticket_type": "Free or Paid",\n'
                '  "organizer": "Hosting student club, university, or entity",\n'
                '  "registration_url": "Direct registration form URL if visible or null",\n'
                '  "ocr_text": "All key text transcribed from the poster image",\n'
                '  "youth_relevance_score": 8.5,\n'
                '  "summary": "1-2 sentence summary"\n'
                "}\n"
                f"Post Caption:\n{caption or '(Poster image only)'}"
            )

            contents_payload: list[Any] = [prompt]
            if image_bytes:
                contents_payload.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents_payload,
            )

            text_resp = response.text or ""
            json_match = re.search(r"\{.*\}", text_resp, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                if data.get("is_event"):
                    start_dt = None
                    if data.get("start_date_iso"):
                        try:
                            start_dt = datetime.fromisoformat(str(data["start_date_iso"]).replace("Z", ""))
                        except Exception:
                            pass
                    data["start_date"] = start_dt
                    return data
        except Exception as e:
            logger.debug(f"Gemini caption/vision analysis notice: {e}")

        return None

    @staticmethod
    def _extract_embedded_poster_text(image_bytes: Optional[bytes], image_source: Optional[str] = None) -> str:
        """Extract embedded text chunks from SVG posters, PNG tEXt/iTXt chunks, or ASCII/UTF-8 flyer comments."""
        extracted_chunks: list[str] = []
        if image_source and image_source.startswith("data:image/svg+xml"):
            try:
                from urllib.parse import unquote
                if ";base64," in image_source:
                    b64_part = image_source.split(";base64,", 1)[1]
                    raw_svg = base64.b64decode(b64_part).decode("utf-8", errors="ignore")
                else:
                    raw_svg = unquote(image_source.split(",", 1)[1])
                text_nodes = re.findall(r">([^<>]{2,200})<", raw_svg)
                if text_nodes:
                    extracted_chunks.append("\n".join(t.strip() for t in text_nodes if t.strip()))
            except Exception:
                pass

        if not image_bytes:
            return "\n".join(extracted_chunks).strip()

        # Check if raw bytes are SVG/XML
        if b"<svg" in image_bytes[:500].lower():
            try:
                raw_svg = image_bytes.decode("utf-8", errors="ignore")
                text_nodes = re.findall(r">([^<>]{2,200})<", raw_svg)
                if text_nodes:
                    extracted_chunks.append("\n".join(t.strip() for t in text_nodes if t.strip()))
            except Exception:
                pass

        # Check PNG tEXt / iTXt metadata chunks
        if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
            pos = 8
            while pos + 8 <= len(image_bytes):
                try:
                    length = int.from_bytes(image_bytes[pos:pos + 4], "big")
                    chunk_type = image_bytes[pos + 4:pos + 8]
                    chunk_data = image_bytes[pos + 8:pos + 8 + length]
                    if chunk_type in (b"tEXt", b"iTXt"):
                        decoded = chunk_data.replace(b"\x00", b" ").decode("utf-8", errors="ignore").strip()
                        if len(decoded) >= 5:
                            extracted_chunks.append(decoded)
                    pos += 12 + length
                except Exception:
                    break

        return "\n".join(extracted_chunks).strip()

    def analyze_poster_image(
        self,
        image_source: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        mime_type: str = "image/png",
        caption: str = "",
        gemini_api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze an event flyer/poster image using Gemini 2.5 Flash Vision + embedded text/NLP fallback."""
        import base64

        if not image_bytes and image_source:
            src = image_source.strip()
            if src.startswith("data:"):
                try:
                    header, encoded = src.split(",", 1)
                    if "image/" in header:
                        mime_type = header.split("data:")[1].split(";")[0]
                    if ";base64" in header:
                        image_bytes = base64.b64decode(encoded)
                    else:
                        from urllib.parse import unquote
                        image_bytes = unquote(encoded).encode("utf-8")
                except Exception as dec_err:
                    logger.debug(f"Data URI decode notice: {dec_err}")
            elif src.startswith(("http://", "https://")):
                try:
                    import httpx
                    with httpx.Client(timeout=7.0, follow_redirects=True) as client:
                        resp = client.get(src)
                        if resp.status_code == 200:
                            image_bytes = resp.content
                            ct = resp.headers.get("content-type", "")
                            if "image/" in ct:
                                mime_type = ct.split(";")[0].strip()
                except Exception as fetch_err:
                    logger.debug(f"Image URL fetch notice: {fetch_err}")

        embedded_text = self._extract_embedded_poster_text(image_bytes, image_source)
        combined_caption = "\n".join(part for part in [embedded_text, caption] if part).strip()

        active_key = gemini_api_key or self.api_key
        if active_key and (image_bytes or image_source):
            ai_res = self._analyze_with_gemini(
                combined_caption,
                flyer_url=image_source if (image_source and image_source.startswith("http")) else None,
                image_bytes=image_bytes,
                mime_type=mime_type,
                api_key_override=active_key,
            )
            if ai_res and ai_res.get("is_event"):
                ocr_text = ai_res.get("ocr_text") or combined_caption
                full_text = f"{ocr_text}\n{combined_caption}".strip()
                if not ai_res.get("registration_url"):
                    ai_res["registration_url"] = self.extract_registration_url(full_text)
                contacts = self.extract_contacts(full_text)
                ai_res.setdefault("organizer_email", contacts["email"])
                ai_res.setdefault("organizer_phone", contacts["phone"])
                ai_res.setdefault("organizer_instagram", contacts["instagram"])
                ai_res["ocr_text"] = ocr_text
                ai_res["vision_engine"] = "gemini-2.5-flash-vision"
                return ai_res

        # Fallback: Bilingual NLP analysis over extracted poster text + caption
        if combined_caption:
            rule_res = self._analyze_with_rules(combined_caption)
            if rule_res.get("is_event"):
                rule_res["ocr_text"] = combined_caption
                rule_res["vision_engine"] = "hybrid-poster-nlp"
                return rule_res

        return {"is_event": False, "ocr_text": combined_caption, "vision_engine": "none"}

    def inspect_registration_link(
        self,
        url: str,
        html_override: Optional[str] = None,
        timeout: float = 7.0,
    ) -> Dict[str, Any]:
        """Unshorten bit.ly / linktr.ee / forms.gle links and inspect whether a registration form is OPEN or CLOSED."""
        clean_url = (url or "").strip()
        if not clean_url or not clean_url.startswith(("http://", "https://")):
            return {"valid": False, "original_url": clean_url, "status": "INVALID"}

        resolved_url = clean_url
        was_shortened = any(d in clean_url.lower() for d in ("bit.ly/", "linktr.ee/", "forms.gle/", "t.co/", "tinyurl.com/"))
        html_text = html_override or ""
        http_status = 200 if html_override is not None else 0

        if html_override is None:
            try:
                import httpx
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
                }
                with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
                    resp = client.get(clean_url)
                    http_status = resp.status_code
                    resolved_url = str(resp.url)
                    html_text = resp.text or ""

                    # If Linktree, look for embedded Google Form / Luma / Eventbrite registration link
                    if "linktr.ee" in resolved_url.lower() and html_text:
                        deep_m = FORM_URL_REGEX.search(html_text)
                        if deep_m and "linktr.ee" not in deep_m.group(0).lower():
                            deep_url = deep_m.group(0)
                            resolved_url = deep_url
                            was_shortened = True
                            resp2 = client.get(deep_url)
                            http_status = resp2.status_code
                            resolved_url = str(resp2.url)
                            html_text = resp2.text or ""
            except Exception as exc:
                logger.debug(f"Registration link inspection fallback for {clean_url}: {exc}")
                return {
                    "valid": True,
                    "original_url": clean_url,
                    "resolved_url": resolved_url,
                    "was_shortened": was_shortened,
                    "is_open": True,
                    "status": "UNVERIFIED_OFFLINE",
                    "status_label": "Link Captured (Live Check Offline)",
                    "form_title": None,
                    "questions": [],
                }

        if resolved_url != clean_url:
            was_shortened = True

        # Parse HTML for form status, title, and questions
        html_lower = html_text.lower()
        closed_phrases = [
            "this form is no longer accepting responses",
            "no longer accepting responses",
            "لم يعد هذا النموذج يقبل الردود",
            "تم إغلاق باب التسجيل",
            "انتهى التسجيل",
            "registration is closed",
            "registration closed",
            "event has ended",
            "sales have ended",
            "sold out",
        ]
        is_closed = any(phrase in html_lower for phrase in closed_phrases)
        if http_status in (404, 410):
            is_closed = True

        form_title = None
        form_desc = None
        questions: list[str] = []

        if html_text:
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_text, "html.parser")
                og_title = soup.find("meta", property="og:title") or soup.find("title")
                if og_title:
                    form_title = (og_title.get("content") if og_title.has_attr("content") else og_title.get_text() or "").strip()
                og_desc = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
                if og_desc and og_desc.has_attr("content"):
                    form_desc = (og_desc.get("content") or "").strip()

                # Extract Google Form / Registration field labels
                for heading in soup.select('[role="heading"], .M7eMe, label'):
                    q_txt = heading.get_text(" ", strip=True).rstrip(" *")
                    if 3 <= len(q_txt) <= 85 and q_txt != form_title and q_txt not in questions:
                        questions.append(q_txt)
                        if len(questions) >= 8:
                            break
            except Exception:
                pass

        deadline_dt, deadline_display = self.extract_datetime_from_caption(f"{form_title or ''}\n{form_desc or ''}")

        return {
            "valid": True,
            "original_url": clean_url,
            "resolved_url": resolved_url,
            "was_shortened": was_shortened,
            "is_open": not is_closed,
            "status": "CLOSED" if is_closed else "OPEN",
            "status_label": "CLOSED — No Longer Accepting Responses" if is_closed else "OPEN — Accepting Responses",
            "form_title": form_title,
            "form_description": form_desc,
            "questions": questions[:6],
            "deadline_display": deadline_display,
        }

