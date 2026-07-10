# DevMatch — Frontend

פרונט **React + Vite + TypeScript + Tailwind** למרקטפלייס התאמת המפתחים.
עיצוב כהה מודרני עם וייב של מפתחים (אקסנט **ירוק טרמינל**), RTL עברית מלא, מעברים חלקים.

## הרצה

```bash
npm install
npm run dev        # פיתוח (ראה "חיבור לבקאנד" — בקאנד אמיתי או mock)
npm run build      # בנייה לפרודקשן (typecheck + bundle)
npm run preview    # תצוגה מקדימה של ה-build
```

## חיבור לבקאנד

כברירת מחדל האפליקציה פונה ל-**בקאנד אמיתי** (`VITE_API_BASE_URL`, ברירת מחדל
`http://localhost:8000`). כך פריסה לפרודקשן לא משרתת בטעות נתוני דמו.

להרצה עצמאית בלי בקאנד (נתוני דמו) — העתק `.env.example` ל-`.env`; הוא כבר מגדיר
`VITE_USE_MOCK=true`:

```
VITE_USE_MOCK=true                       # מצב דמו — בלי בקאנד חי
VITE_API_BASE_URL=http://localhost:8000  # כתובת ה-FastAPI (כשלא במצב דמו)
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
- **`/dev/:id`** — פרופיל מפתח בודד (מקושר מכרטיסי התוצאה). פנייה בוואטסאפ זמינה
  כשמגיעים מהתוצאות (עם `request_id`); בגישה ישירה מוצג CTA למצוא התאמה — נאמן למודל הפרטיות.
