# DevMatch — Frontend

פרונט **React + Vite + TypeScript + Tailwind** למרקטפלייס התאמת המפתחים.
עיצוב כהה מודרני עם וייב של מפתחים (אקסנט **ירוק טרמינל**), RTL עברית מלא, מעברים חלקים.

## הרצה

```bash
npm install
npm run dev        # פיתוח — ברירת מחדל: mock mode (עובד בלי בקאנד)
npm run build      # בנייה לפרודקשן (typecheck + bundle)
npm run preview    # תצוגה מקדימה של ה-build
```

## חיבור לבקאנד

כברירת מחדל האפליקציה רצה ב-**mock mode** עם נתוני דמו — כדי לראות הכול בלי בקאנד חי.
לחיבור ל-FastAPI האמיתי, צור `.env` מתוך `.env.example`:

```
VITE_USE_MOCK=false
VITE_API_BASE_URL=http://localhost:8000
```

(ה-CORS בבקאנד נשלט דרך `ALLOWED_ORIGINS`.)

## מבנה

```
src/
  lib/          # טיפוסים תואמי בקאנד, לקוח API, mock (מנוע ניקוד נאמן), תוויות
  components/   # layout (Header/Footer/BackgroundFX) + ספריית UI
  features/
    match/      # אשף 5 שאלות → תוצאות (ScoreRing + כרטיסי מפתח)
    developer/  # טופס הרשמה מחולק לקטעים
  pages/        # HomePage, MatchPage, JoinPage
```

## Flows

- **`/`** — דף בית עם hero בסגנון טרמינל ושתי CTA.
- **`/match`** — אשף 5 שאלות (מה בונים · תמחור · לו"ז · מעורבות · פרטים) → מסך תוצאות
  עם ציון התאמה ופנייה בוואטסאפ.
- **`/join`** — הרשמת מפתח (auto-publish), כולל העלאת תמונת פרופיל.
