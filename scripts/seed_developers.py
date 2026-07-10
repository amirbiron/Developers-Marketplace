"""Seed — מזריק מפתחי דמו ל-DB לצורכי פיתוח והדגמה.

הרצה (מתיקיית השורש של הריפו):
    DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/marketplace \\
        python scripts/seed_developers.py           # מדלג אם כבר יש מפתחים
    ... python scripts/seed_developers.py --force    # מנקה קודם וזורע מחדש

הנתונים תואמים לפיקסצ'רים של הפרונט (frontend/src/lib/mock.ts) כדי שההתנהגות
תהיה עקבית בין mock mode לבקאנד האמיתי.
"""

from __future__ import annotations

import asyncio
import os
import sys

# מאפשר הרצה כקובץ עצמאי (מוסיף את שורש הריפו ל-sys.path)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import delete, func, select  # noqa: E402

from app.database import AsyncSessionLocal  # noqa: E402
from app.models import Developer  # noqa: E402

DEVELOPERS: list[dict] = [
    {
        "full_name": "יעל אברהמי",
        "title": "Full-stack · SaaS",
        "highlight": "מקימה SaaS עם billing ותשתית תשלומים מהיום הראשון",
        "bio": "מפתחת פוֹל-סטאק עם 7 שנות ניסיון בבניית מוצרי SaaS מאפס — אימות, מנויים, דשבורדים.",
        "whatsapp_e164": "972501112233",
        "project_types": ["saas", "webapp"],
        "stack": ["React", "Next.js", "FastAPI", "Supabase", "Stripe"],
        "ai_tools": ["Claude Code", "Cursor"],
        "pricing_models": ["hourly", "budget_friendly"],
        "hourly_rate": 380,
        "availability": "available",
        "portfolio_url": "https://yael.dev",
        "links": {"github": "https://github.com/yael", "linkedin": "https://linkedin.com/in/yael"},
        "is_verified": True,
    },
    {
        "full_name": "איתי לוי",
        "title": "Mobile Engineer",
        "highlight": "אפליקציות מובייל חלקות ומהירות ב-React Native",
        "bio": "מתמחה באפליקציות מובייל חוצות-פלטפורמה עם ביצועים גבוהים וחוויית משתמש מוקפדת.",
        "whatsapp_e164": "972502223344",
        "project_types": ["mobile", "webapp"],
        "stack": ["React Native", "Expo", "TypeScript", "Firebase"],
        "ai_tools": ["Cursor"],
        "pricing_models": ["after_scoping"],
        "hourly_rate": None,
        "availability": "available",
        "portfolio_url": "https://itai.app",
        "links": {"github": "https://github.com/itai"},
        "is_verified": True,
    },
    {
        "full_name": "נועה שרון",
        "title": "E-commerce Developer",
        "highlight": "חנויות Shopify שממירות — עיצוב שמוכר",
        "bio": "בונה חנויות אונליין מהירות וממירות, כולל אינטגרציות תשלום ומשלוח לשוק הישראלי.",
        "whatsapp_e164": "972503334455",
        "project_types": ["store", "landing"],
        "stack": ["Shopify", "Liquid", "React", "Tailwind"],
        "ai_tools": [],
        "pricing_models": ["hourly"],
        "hourly_rate": 300,
        "availability": "limited",
        "portfolio_url": "https://noa-store.co.il",
        "links": {"linkedin": "https://linkedin.com/in/noa"},
        "is_verified": False,
    },
    {
        "full_name": "דניאל כ׳ץ",
        "title": "Automation & AI",
        "highlight": "אוטומציות ו-AI agents שחוסכות לצוות שעות בשבוע",
        "bio": "מחבר מערכות, בונה אוטומציות ו-agents חכמים שמייתרים עבודה ידנית ומאיצים תהליכים.",
        "whatsapp_e164": "972504445566",
        "project_types": ["automation", "ai_agents"],
        "stack": ["Python", "LangChain", "n8n", "OpenAI", "Supabase"],
        "ai_tools": ["Claude Code", "Claude", "Cursor"],
        "pricing_models": ["after_scoping", "budget_friendly"],
        "hourly_rate": None,
        "availability": "available",
        "portfolio_url": "https://daniel-ai.dev",
        "links": {"github": "https://github.com/danielk"},
        "is_verified": True,
    },
    {
        "full_name": "מור פרידמן",
        "title": "Bot Developer",
        "highlight": "בוטים ל-WhatsApp ו-Telegram שמוכרים ומשרתים",
        "bio": "בונה בוטים חכמים לשירות ומכירות עם אינטגרציות CRM ותשלומים.",
        "whatsapp_e164": "972505556677",
        "project_types": ["bot_chat", "automation"],
        "stack": ["Node.js", "Baileys", "Telegraf", "Supabase"],
        "ai_tools": ["Claude"],
        "pricing_models": ["budget_friendly"],
        "hourly_rate": None,
        "availability": "available",
        "portfolio_url": None,
        "links": {"github": "https://github.com/morf"},
        "is_verified": False,
    },
    {
        "full_name": "רון ביטון",
        "title": "Senior Web Engineer",
        "highlight": "מערכות web מורכבות עם קוד נקי וארכיטקטורה יציבה",
        "bio": "מהנדס בכיר לבניית מערכות web בקנה מידה, עם דגש על אמינות, בדיקות ותחזוקתיות.",
        "whatsapp_e164": "972506667788",
        "project_types": ["webapp", "saas"],
        "stack": ["Vue", "Nuxt", "Node.js", "PostgreSQL"],
        "ai_tools": ["Cursor"],
        "pricing_models": ["hourly"],
        "hourly_rate": 450,
        "availability": "limited",
        "portfolio_url": "https://ron.codes",
        "links": {"github": "https://github.com/ronb", "linkedin": "https://linkedin.com/in/ronb"},
        "is_verified": True,
    },
    {
        "full_name": "שירה גולן",
        "title": "AI Engineer",
        "highlight": "AI agents ו-RAG שמבינים את הביזנס שלך",
        "bio": "בונה מערכות AI מבוססות agents ו-RAG, מחיבור מקורות מידע ועד ממשק משתמש.",
        "whatsapp_e164": "972507778899",
        "project_types": ["ai_agents", "automation"],
        "stack": ["Python", "LlamaIndex", "Claude", "Pinecone", "FastAPI"],
        "ai_tools": ["Claude Code", "Claude"],
        "pricing_models": ["after_scoping"],
        "hourly_rate": None,
        "availability": "available",
        "portfolio_url": "https://shira.ai",
        "links": {"linkedin": "https://linkedin.com/in/shira"},
        "is_verified": True,
    },
    {
        "full_name": "עידו רוזן",
        "title": "Voice & Bots",
        "highlight": "בוט קולי ומענה טלפוני חכם בעברית",
        "bio": "מפתח מערכות קוליות ומענה טלפוני אוטומטי עם זיהוי דיבור והבנת שפה בעברית.",
        "whatsapp_e164": "972508889900",
        "project_types": ["bot_voice", "bot_chat"],
        "stack": ["Python", "Twilio", "LiveKit", "Whisper"],
        "ai_tools": ["Claude"],
        "pricing_models": ["budget_friendly", "after_scoping"],
        "hourly_rate": None,
        "availability": "available",
        "portfolio_url": "https://ido-voice.dev",
        "links": {"github": "https://github.com/idor"},
        "is_verified": False,
    },
]


async def seed(force: bool) -> None:
    async with AsyncSessionLocal() as db:
        existing = (await db.execute(select(func.count()).select_from(Developer))).scalar_one()
        if existing and not force:
            print(f"כבר קיימים {existing} מפתחים — מדלג. הרץ עם --force לזריעה מחדש.")
            return
        if force and existing:
            await db.execute(delete(Developer))
            await db.commit()
            print(f"נמחקו {existing} מפתחים קיימים.")
        db.add_all([Developer(**data) for data in DEVELOPERS])
        await db.commit()
        print(f"✓ נזרעו {len(DEVELOPERS)} מפתחי דמו.")


if __name__ == "__main__":
    asyncio.run(seed(force="--force" in sys.argv))
