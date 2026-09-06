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

