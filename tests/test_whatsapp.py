"""טסטים לבניית קישור הוואטסאפ — דגש על escaping נכון (דפוס CLAUDE.md 6)."""

from __future__ import annotations

from urllib.parse import unquote

from app.services.whatsapp import build_wa_link, build_wa_message

GREETING = "היי! הגעתי דרך המרקטפלייס."


class TestMessage:
    def test_includes_description(self):
        msg = build_wa_message("מערכת ניהול לקוחות", None, greeting=GREETING)
        assert "מערכת ניהול לקוחות" in msg
        assert msg.startswith(GREETING)

    def test_includes_involvement_label(self):
        msg = build_wa_message("אתר", "collaborative", greeting=GREETING)
        assert "עבודה משותפת" in msg

    def test_involvement_full_handoff(self):
        msg = build_wa_message("אתר", "full_handoff", greeting=GREETING)
        assert "מקצה לקצה" in msg

    def test_no_description_has_fallback(self):
        msg = build_wa_message(None, None, greeting=GREETING)
        assert "פרויקט חדש" in msg

    def test_unknown_involvement_ignored(self):
        msg = build_wa_message("אתר", "ghost", greeting=GREETING)
        # לא מוסיף שורת מעורבות, אבל לא קורס
        assert "אתר" in msg


class TestLink:
    def test_basic_format(self):
        link = build_wa_link("972501234567", "אתר תדמית", "collaborative", greeting=GREETING)
        assert link.startswith("https://wa.me/972501234567?text=")

    def test_number_preserved(self):
        link = build_wa_link("972501234567", "x", greeting=GREETING)
        assert "wa.me/972501234567?" in link

    def test_special_chars_are_encoded(self):
        # "AT&T" ו-"Price < $100" — התווים הפעילים חייבים להיות מקודדים, לא גולמיים
        desc = "בוט ל-AT&T עם Price < $100 & דוחות"
        link = build_wa_link("972501234567", desc, greeting=GREETING)
        text_part = link.split("?text=", 1)[1]
        # אין & גולמי בחלק ה-text (הוא היה שובר את ה-query string)
        assert "&" not in text_part
        assert "<" not in text_part
        assert " " not in text_part

    def test_roundtrip_decodes_to_message(self):
        desc = "מערכת עם <תגיות> & סימנים 🚀 ורווחים"
        link = build_wa_link("972501234567", desc, "collaborative", greeting=GREETING)
        text_part = link.split("?text=", 1)[1]
        decoded = unquote(text_part)
        assert desc in decoded
        assert "עבודה משותפת" in decoded

    def test_emoji_encoded(self):
        link = build_wa_link("972501234567", "אפליקציה 🚀", greeting=GREETING)
        text_part = link.split("?text=", 1)[1]
        # אמוji מקודד ל-%XX ולא נשאר גולמי
        assert "🚀" not in text_part
        # ההודעה מסתיימת ב-"אפליקציה 🚀." — בדיקה מדויקת
        assert unquote(text_part).endswith("🚀.")
