# מרקטפלייס להתאמת מפתחים — Backend

התאמת מפתחים ישראלים ללקוחות שרוצים לבנות פרויקט **מאפס** (אתר, אפליקציה, אוטומציה,
בוט, SaaS). הלקוח עונה על 5 שאלות ומקבל רשימה קצרה וממוקדת של מפתחים מתאימים — כל אחד
עם ציון התאמה, מודל תמחור, ופנייה ישירה בוואטסאפ. **אין צ'אט פנימי, אין תיווך.**

ההתאמה כולה **rule-based ודטרמיניסטית** — אותה פנייה מחזירה תמיד אותה תוצאה. בלי LLM
בליבה. הכל רץ ב-query אחד ל-DB + חישוב בזיכרון.

> המימוש נאמן ל-[`docs/Spec.md`](docs/Spec.md). מומלץ לקרוא אותו להקשר המלא.

---

## Stack

- **FastAPI** (async) — שכבת ה-API
- **SQLAlchemy 2.0 async** + **asyncpg** — גישה ל-Postgres של Supabase
- **Alembic** — מיגרציות סכמה
- **Pydantic v2** — ולידציה
- **Supabase Storage** — תמונות פרופיל
- **pytest** — טסטים

---

## מבנה הפרויקט

```
app/
  main.py          # אפליקציית FastAPI, CORS, טיפול שגיאות גנרי
  config.py        # הגדרות ממשתני סביבה
  database.py      # engine + session אסינכרוני
  constants.py     # 10 קטגוריות + כל ה-enums (מקור אמת)
  models.py        # מודלים: Developer, Request, Referral, ProjectType
  schemas.py       # סכמות Pydantic + ולידציה (E.164, hourly_rate, enums, NaN/Inf)
  engine.py        # ★ מנוע ההתאמה — פונקציות טהורות, דטרמיניסטיות
  mappers.py       # מיפוי ORM ↔ מנוע/פלט
  services/
    whatsapp.py    # בניית קישור wa.me עם URL-encoding
    storage.py     # העלאת תמונת פרופיל (זיהוי לפי magic bytes)
  routers/         # 7 ה-endpoints
alembic/           # מיגרציות (0001 = סכמה מלאה + seed)
supabase/
  policies.sql     # RLS + view ציבורי + bucket תמונות
tests/             # ★ 93 טסטים ללא DB + טסטי אינטגרציה (מדולגים בלי DB)
```

---

## התקנה והרצה מקומית

```bash
# 1. תלויות
pip install -r requirements.txt

# 2. הגדרות — העתק והשלם ערכים
cp .env.example .env
#   ערוך את DATABASE_URL, SUPABASE_URL, SUPABASE_SERVICE_KEY

# 3. הרצת מיגרציות (יוצר טבלאות + אינדקסים + trigger + זריעת קטגוריות)
alembic upgrade head

# 4. (אופציונלי) זריעת מפתחי דמו — כדי ש-/match יחזיר תוצאות
python scripts/seed_developers.py            # --force לזריעה מחדש

# 5. החלת RLS ומדיניות פרטיות (חד-פעמי, ב-Supabase SQL Editor או psql)
#    מריצים את התוכן של supabase/policies.sql

# 6. הרצת השרת
uvicorn app.main:app --reload
```

השרת יעלה על `http://localhost:8000`. תיעוד אינטראקטיבי: `http://localhost:8000/docs`.

### חיבור הפרונט לבקאנד

הפרונט (`frontend/`) רץ כברירת מחדל ב-mock mode. לחיבור לבקאנד האמיתי, צור
`frontend/.env` עם `VITE_USE_MOCK=false` ו-`VITE_API_BASE_URL=http://localhost:8000`,
ואז `npm run dev`. ה-CORS נשלט דרך `ALLOWED_ORIGINS`. פרטים ב-`frontend/README.md`.

---

## API — סיכום Endpoints

| Method | Path | תיאור |
|---|---|---|
| `POST` | `/developers` | הרשמת מפתח (auto-publish). מחזיר `edit_token` חד-פעמי |
| `GET` | `/developers/{id}` | פרופיל ציבורי — **בלי** `whatsapp_e164` |
| `PATCH` | `/developers/{id}` | עדכון + השהיה עצמית. דורש `X-Edit-Token` (בעלוּת) |
| `POST` | `/avatars` | העלאת תמונת פרופיל → מחזיר URL |
| `GET` | `/meta/project-types` | 10 סוגי הפרויקט + תיאורים |
| `POST` | `/match` | **הלב** — שומר פנייה, מריץ מנוע, מחזיר top-N (בלי מספרים) |
| `POST` | `/referrals` | רושם פנייה, **מחזיר מספר וואטסאפ** — הנקודה היחידה שהמספר יוצא |

דוגמה ל-`POST /match`:

```json
{
  "project_type": "saas",
  "pricing_prefs": ["hourly", "budget_friendly"],
  "timeline": "weeks",
  "involvement": "collaborative",
  "portfolio_only": true,
  "description": "מערכת ניהול לקוחות עם דשבורד",
  "stack_pref": ["React", "Supabase"]
}
```

---

## מנוע ההתאמה (engine.py)

דטרמיניסטי, זול, ניתן לדיבוג. שלושה שלבים:

1. **סינון מקדים** — `is_active` + זמינות ≠ `unavailable` + התאמת סוג פרויקט **מדויקת**
   (אין חפיפה חלקית) + פילטר תיק-עבודות אם ביקשו.
2. **ניקוד** — סוג פרויקט (50) + stack (0–30) + זמינות×לו"ז (5–20) + בונוס `budget_friendly` (+10).
   כשהלקוח לא ציין stack, הגורם לא פעיל והציון מנורמל חזרה ל-0–100 (הלקוח הלא-טכני לא נענש).
3. **מיון ושבירת שוויון** — ציון ↓, אחר כך `is_verified` → `available` → `updated_at` → `id`.
   מחזיר עד 8 תוצאות. אם אף אחד לא עבר — רשימה ריקה (לא תוצאות מזויפות).

---

## אבטחה ופרטיות

- **`whatsapp_e164` לעולם לא יוצא ל-client** חוץ מ-`POST /referrals`, שגם רושם את הפנייה.
  נאכף בקוד (סכמות פלט בלי המספר) וגם ב-RLS + view ציבורי (`supabase/policies.sql`).
- **`is_verified` לא ניתן להגדרה ע"י הלקוח** — רק דרך גישת admin ישירה ל-DB.
- **ולידציה** — E.164, טווחי מספרים כולל NaN/Inf, escaping מלא של נתוני משתמש בקישור wa.me.
- **שגיאות** — תשובות שגיאה גנריות בעברית, בלי stack traces / מזהים פנימיים.

### אימות בעלוּת (edit-token)

`POST /developers` מחזיר **`edit_token` חד-פעמי**; ב-DB נשמר רק ה-hash שלו
(`edit_token_hash`, לעולם לא נחשף). `PATCH /developers/{id}` דורש את האסימון ב-header
`X-Edit-Token` ומאמת אותו בזמן קבוע — כך רק מי שיצר את הפרופיל יכול לערוך אותו
(כולל שינוי מספר הוואטסאפ). `is_verified` נשאר admin-only (לא נכלל בסכמות הקלט).

> הרחבה עתידית: מעבר ל-Supabase Auth (חשבונות אמיתיים + `owner_id`) כשיהיה פרויקט
> Supabase חי — הסכמה תומכת בכך בלי migration כואב.

---

## טסטים

```bash
# כל הטסטים שלא דורשים DB (מנוע, סכמות, whatsapp, storage) — רצים תמיד
pytest -q

# כולל טסטי אינטגרציה מול Postgres — הגדר תחילה:
export TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/marketplace_test"
pytest -q
```

מנוע ההתאמה מכוסה במלואו בטסטי יחידה טהורים (בלי DB) — כל שורות טבלת הזמינות, חפיפת
stack, נורמליזציה, בונוס, שבירת שוויון, ודטרמיניזם.

---

## פריסה (Render)

`render.yaml` מגדיר web service עם:
- `preDeployCommand: alembic upgrade head` — מיגרציות רצות אוטומטית לפני כל deploy.
- משתני סביבה נדרשים: `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `ALLOWED_ORIGINS`.

לאחר הפריסה הראשונה — יש להריץ פעם אחת את `supabase/policies.sql` ב-Supabase.
