"""מקור-אמת לכל ה-enums וקטגוריות סוג-הפרויקט של המרקטפלייס.

הקודים באנגלית (כמקובל); התוויות והתיאורים בעברית לתצוגה בפרונט.
"""

from __future__ import annotations

# --- 10 קטגוריות סוג-פרויקט (Spec §1) ---
# הסדר משמש גם ל-sort_order בטבלת ה-lookup ובתשובת GET /meta/project-types.
# התיאורים חשובים: אין חפיפה חלקית בין קטגוריות, אז הלקוח חייב לבחור נכון (Spec §1).
PROJECT_TYPES: list[dict[str, str]] = [
    {
        "code": "landing",
        "label_he": "אתר תדמית",
        "description_he": "אתר תדמית / דף נחיתה — נוכחות דיגיטלית, ללא משתמשים או התחברות.",
    },
    {
        "code": "store",
        "label_he": "חנות אונליין",
        "description_he": "חנות אונליין — קטלוג מוצרים, עגלת קניות ותשלום.",
    },
    {
        "code": "mobile",
        "label_he": "אפליקציית מובייל",
        "description_he": "אפליקציה טבעית לאנדרואיד / iOS.",
    },
    {
        "code": "webapp",
        "label_he": "Web App",
        "description_he": "מערכת web עם משתמשים והתחברות — בלי מנוי חוזר.",
    },
    {
        "code": "saas",
        "label_he": "מערכת SaaS",
        "description_he": "מערכת SaaS — עם מנוי ותשלום חוזר.",
    },
    {
        "code": "automation",
        "label_he": "אוטומציה ואינטגרציות",
        "description_he": "אוטומציות, חיבור בין מערכות ו-APIs.",
    },
    {
        "code": "bot_chat",
        "label_he": "בוט צ'אט",
        "description_he": "בוט טקסט ל-WhatsApp / Telegram.",
    },
    {
        "code": "bot_voice",
        "label_he": "בוט קולי",
        "description_he": "בוט קולי / מענה טלפוני אוטומטי.",
    },
    {
        "code": "ai_agents",
        "label_he": "AI ואייג'נטים",
        "description_he": "פתרונות מבוססי AI ואייג'נטים חכמים.",
    },
    {
        "code": "other",
        "label_he": "אחר",
        "description_he": "משהו אחר שלא נכנס לקטגוריות שלמעלה.",
    },
]

# קבוצת הקודים החוקיים — לוולידציה מהירה.
PROJECT_TYPE_CODES: frozenset[str] = frozenset(pt["code"] for pt in PROJECT_TYPES)

# --- מודלי תמחור (Spec §2.1 / §4.2) ---
PRICING_MODELS: frozenset[str] = frozenset({"hourly", "after_scoping", "budget_friendly"})

# תיוג budget_friendly — משותף ללקוח ולמפתח. הגורם היחיד מ-pricing שנכנס למנוע (Spec §3.2).
BUDGET_FRIENDLY = "budget_friendly"

# מודל hourly — רק כשהוא מסומן מותר (ורלוונטי) שדה hourly_rate.
HOURLY = "hourly"

# --- זמינות (Spec §2.1) ---
AVAILABILITY_VALUES: frozenset[str] = frozenset({"available", "limited", "unavailable"})
AVAILABILITY_AVAILABLE = "available"
AVAILABILITY_LIMITED = "limited"
AVAILABILITY_UNAVAILABLE = "unavailable"

# --- לו"ז מבוקש (Spec §2.2 / §4.2) ---
TIMELINE_VALUES: frozenset[str] = frozenset({"urgent", "weeks", "flexible"})

# --- רמת מעורבות (Spec §2.2) — מטא-דאטה לפנייה, לא נכנס למנוע ---
INVOLVEMENT_VALUES: frozenset[str] = frozenset({"full_handoff", "collaborative"})

# ניסוח עברי של רמת המעורבות — משמש לבניית הודעת הוואטסאפ המוכנה.
INVOLVEMENT_LABELS_HE: dict[str, str] = {
    "full_handoff": "מעדיף/ה למסור את הפרויקט מקצה לקצה",
    "collaborative": "מעדיף/ה עבודה משותפת ומעורבות בתהליך",
}
