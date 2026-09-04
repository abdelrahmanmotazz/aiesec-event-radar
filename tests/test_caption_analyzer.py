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
