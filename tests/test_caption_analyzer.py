"""Unit tests for Caption and Social Announcement Intelligence."""

from aiesec_scraper.analyzers.caption_analyzer import CaptionAnalyzer


def test_arabic_event_caption():
    analyzer = CaptionAnalyzer()
    arabic_caption = (
        "مستنيينكم في ملتقى التوظيف السنوي بجامعة القاهرة يوم 15-10-2026\n"
        "حضور مجاني لجميع الطلاب وحديثي التخرج. اللينك في البايو للتسجيل!"
    )
    assert analyzer.is_event_post(arabic_caption) is True

    analysis = analyzer.analyze(arabic_caption)
    assert analysis["is_event"] is True
    assert "Cairo University" in analysis["venue"] or "جامعة القاهرة" in analysis["venue"]
    assert analysis["ticket_type"] == "Free"


def test_english_event_caption():
    analyzer = CaptionAnalyzer()
    english_caption = (
        "Join us at The Greek Campus for the Cairo AI Hackathon 2026!\n"
        "Register now via link in bio. Over 500 developers competing."
    )
    assert analyzer.is_event_post(english_caption) is True

    analysis = analyzer.analyze(english_caption)
    assert analysis["is_event"] is True
    assert "Greek Campus" in analysis["venue"]


def test_negative_control_casual_post():
    analyzer = CaptionAnalyzer()
    casual_post = "Had a great cup of coffee this morning with friends in Zamalek. Weather is lovely today!"
    assert analyzer.is_event_post(casual_post) is False
    assert analyzer.analyze(casual_post)["is_event"] is False


def test_registration_link_extraction():
    analyzer = CaptionAnalyzer()
    post_with_form = (
        "IEEE CUSB Annual Robotics Challenge 2026! Applications are open now.\n"
        "Fill the form to register your team: https://forms.gle/xYz987AbCdEf\n"
        "Venue: Cairo University Engineering Quad."
    )
    assert analyzer.is_event_post(post_with_form) is True
    analysis = analyzer.analyze(post_with_form)
    assert analysis["is_event"] is True
    assert analysis["registration_url"] == "https://forms.gle/xYz987AbCdEf"


def test_franco_and_student_union_caption():
    analyzer = CaptionAnalyzer()
    franco_caption = "Tanta University Student Union bootcamp! segel now el link fel bio for free admission."
    assert analyzer.is_event_post(franco_caption) is True
    analysis = analyzer.analyze(franco_caption)
    assert analysis["is_event"] is True
    assert analysis["city"] == "Tanta"


def test_bilingual_caption_date_and_contact_extraction():
    analyzer = CaptionAnalyzer()
    post = (
        "🔥 جاهزين؟ 🔥\n"
        "ملتقى التوظيف وريادة الأعمال بجامعة طنطا 2026 - Tanta Career Summit\n"
        "يوم السبت ٢١ نوفمبر ٢٠٢٦ في مجمع سبرباي جامعة طنطا\n"
        "سجل الآن: https://forms.gle/TantaCareerSummit2026\n"
        "للتواصل: 01012345678 | info@tantasummit.org.eg | @tanta_youth_summit"
    )
    analysis = analyzer.analyze(post)
    assert analysis["is_event"] is True
    assert "ملتقى التوظيف" in analysis["title"]
    assert analysis["city"] == "Tanta"
    assert "Tanta University" in analysis["venue"]
    assert analysis["start_date"] is not None
    assert analysis["start_date"].year == 2026
    assert analysis["start_date"].month == 11
    assert analysis["start_date"].day == 21
    assert analysis["registration_url"] == "https://forms.gle/TantaCareerSummit2026"
    assert analysis["organizer_phone"] == "01012345678"
    assert analysis["organizer_email"] == "info@tantasummit.org.eg"
    assert analysis["organizer_instagram"] == "tanta_youth_summit"


def test_poster_vision_ocr_extraction():
    from urllib.parse import quote
    analyzer = CaptionAnalyzer()
    svg_poster = (
        '<svg xmlns="http://www.w3.org/2000/svg">'
        "<text>IEEE Cairo University &amp; Enactus Egypt — AI &amp; Career Expo 2026</text>"
        "<text>يوم السبت ٢٨ نوفمبر ٢٠٢٦ - هندسة القاهرة (CUFE)</text>"
        "<text>Scan QR to Register: https://forms.gle/IEEECairoAIExpo2026</text>"
        "<text>Contact: 01098765432 | ieee@cu.edu.eg | @ieeecusb</text>"
        "</svg>"
    )
    data_uri = "data:image/svg+xml;utf8," + quote(svg_poster)
    result = analyzer.analyze_poster_image(image_source=data_uri, caption="Wait for us tomorrow! 🔥")
    assert result["is_event"] is True
    assert "IEEE Cairo University" in result["title"]
    assert "Cairo University" in result["venue"]
    assert result["registration_url"] == "https://forms.gle/IEEECairoAIExpo2026"
    assert result["organizer_phone"] == "01098765432"
    assert result["organizer_instagram"] == "ieeecusb"


def test_registration_link_inspector_open_and_closed():
    analyzer = CaptionAnalyzer()
    open_html = """
    <html>
      <head><title>IEEE CUFE AI Summit 2026 Registration</title></head>
      <body>
        <div role="heading">Full Name</div>
        <div role="heading">University & Faculty</div>
        <div role="heading">WhatsApp Phone Number</div>
      </body>
    </html>
    """
    open_res = analyzer.inspect_registration_link("https://forms.gle/OpenForm123", html_override=open_html)
    assert open_res["is_open"] is True
    assert open_res["status"] == "OPEN"
    assert open_res["was_shortened"] is True
    assert "Full Name" in open_res["questions"]

    closed_html = """
    <html>
      <head><title>AUC Career Fair Registration</title></head>
      <body>
        <div>This form is no longer accepting responses. لم يعد هذا النموذج يقبل الردود</div>
      </body>
    </html>
    """
    closed_res = analyzer.inspect_registration_link("https://forms.gle/ClosedForm999", html_override=closed_html)
    assert closed_res["is_open"] is False
    assert closed_res["status"] == "CLOSED"


def test_campus_watchlist_52_pages():
    from aiesec_scraper.scrapers.campus_watchlist import (
        EGYPT_CAMPUS_WATCHLIST,
        get_campus_watchlist,
        get_priority_watchlist_queries,
    )
    assert len(EGYPT_CAMPUS_WATCHLIST) >= 45
    tanta_pages = get_campus_watchlist(city="tanta")
    assert len(tanta_pages) >= 4
    ieee_pages = get_campus_watchlist(category="ieee")
    assert len(ieee_pages) >= 8
    priority_queries = get_priority_watchlist_queries(limit=6)
    assert len(priority_queries) == 6
    assert all(url.startswith("https://www.facebook.com/") for _, url in priority_queries)


