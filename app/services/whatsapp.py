"""בניית קישור wa.me עם הודעה מוכנה (Spec §4.2 / §5.2).

זה הכלי היחיד שמייצר את הפנייה. הודעת הטקסט נכנסת ל-URL, שהוא סינטקס פעיל,
אז כל נתון מהמשתמש (description) חייב URL-encoding (דפוס CLAUDE.md 6).
"""

from __future__ import annotations

from urllib.parse import quote

from app.config import get_settings
from app.constants import INVOLVEMENT_LABELS_HE


def build_wa_message(
    description: str | None = None,
    involvement: str | None = None,
    greeting: str | None = None,
) -> str:
    """מרכיב את גוף הודעת הפתיחה בעברית מתוך תיאור הפרויקט ורמת המעורבות."""
    settings = get_settings()
    greeting_text = greeting if greeting is not None else settings.wa_greeting

    parts: list[str] = []
    if (greeting_text or "").strip():
        parts.append(greeting_text.strip())

    desc = (description or "").strip()
    if desc:
        parts.append(f"אני מחפש/ת מפתח/ת ל: {desc}.")
    else:
        parts.append("אני מחפש/ת מפתח/ת לפרויקט חדש.")

    involvement_text = INVOLVEMENT_LABELS_HE.get((involvement or "").strip().lower())
    if involvement_text:
        parts.append(involvement_text + ".")

    return " ".join(parts)


def build_wa_link(
    whatsapp_e164: str,
    description: str | None = None,
    involvement: str | None = None,
    greeting: str | None = None,
) -> str:
    """בונה קישור wa.me מלא עם ההודעה מקודדת ל-URL."""
    message = build_wa_message(description, involvement, greeting)
    # safe="" → מקודד גם & < > / וכו', כדי ש"AT&T" או "Price < $100" לא ישברו את ה-URL
    encoded = quote(message, safe="")
    return f"https://wa.me/{whatsapp_e164}?text={encoded}"
