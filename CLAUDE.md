
## תהליך עבודה

1. **קודם מתכננים** – לפני כל מימוש, יש להציג תוכנית עבודה ברורה (עם הסברים בשפה פשוטה ומובנת לכל)
2. **אחר כך מממשים** – המימוש מתחיל רק לאחר אישור התוכנית.

## כלל חשוב: 

אם נמצאו באגים כלשהם בריפו - תמיד נחפש פיתרונות שורשיים לבעיה, ולא פיתרונות "טלאי".

## שפה

- סיכומי PR, תיאורי commit, והודעות סשן — **בעברית**
- הערות בקוד (comments) — **בעברית**
- שמות משתנים, פונקציות, וטבלאות — באנגלית (כמקובל)

---

### כלל 1: בדוק await על כל קריאה לפונקציה async
> לפני push, חפש בכל הקבצים שהשתנו קריאות לפונקציות async. ודא שכל קריאה עטופה ב-`await`. coroutine object ללא await הוא תמיד truthy — זה באג שקט שיכול לשבור הכול.

### כלל 2: Race conditions — check-then-act חייב להיות אטומי
> אל תפריד בין בדיקת תנאי לביצוע פעולה. אם יש lock/mutex, הבדיקה חייבת להיות בתוכו. במיוחד: daily limits, dedup checks, state transitions. השתמש ב-`UPDATE ... WHERE status = 'X'` + `rowcount` במקום SELECT+UPDATE.

### כלל 3: אל תחשוף מידע פנימי ב-API responses
> לפני כל שינוי ב-error handling או exception classes, ודא ש-`to_dict()` / response body לא מכילים: internal IDs, password hashes, stack traces, מזהי DB, או הודעות שגיאה באנגלית טכנית. החזר הודעה גנרית בעברית למשתמש.

### כלל 4: ולידציית קלט מספרי — בדוק NaN, Inf, ו-edge cases
> בכל validator מספרי, בדוק קודם `math.isnan()` ו-`math.isinf()` (Python) או `Number.isNaN()` ו-`!Number.isFinite()` (JS). NaN comparisons תמיד מחזירות False — ה-NaN יעבור כל בדיקת טווח.

### כלל 5: SQLAlchemy async — אל תיגע ב-attributes אחרי commit/close
> אחרי `db.commit()`, כל ה-attributes של model objects דורשים re-fetch. חלץ ערכים פרימיטיביים (IDs, strings) לפני ה-commit, ואז בצע `db.execute(select(...))` מחדש בתוך הלולאה. זה מונע MissingGreenlet errors.

### כלל 6: Escape של user-data בכל output formatter שיש לו סינטקס פעיל
> כשמטמיעים נתון מבחוץ (DB / API / user input) לתוך output עם סינטקס פעיל — HTML, mrkdwn, SQL, shell, ANSI — חובה escape. עדיף formatter נפרד פר-target (Telegram HTML, Slack mrkdwn) על format-string אחיד, כי כללי ה-escape שונים פר ספק וtemplate אחת תעבוד טוב על אחד ותשבור על האחר. דוגמה: `parse_mode=HTML` של Telegram דורש `html.escape`; Slack mrkdwn דורש escape של `& < >` בלבד. סובייקט "Price < $100" או שולח "AT&T" מספיקים לשבור את שני הספקים.

### כלל 7: SSRF — URL מ-user → allowlist origin, לא רק https
> כל endpoint שה-backend עושה אליו fetch/POST עם URL שמשתמש סיפק (webhooks, redirect URIs, image-proxy, file-download) חייב לאמת origin מול allowlist קבוע. הגבלת `https://` בלבד לא מספיקה — `https://169.254.169.254/` היא URL חוקי שמצביע ל-AWS metadata service. לדוגמה: Slack webhook → `https://hooks.slack.com/services/` בלבד.


# דפוסי Postgres / SQL 

1. **`col = NULL` הוא NULL, לא TRUE.** CAS / `UPDATE WHERE col=:val` לא תופס שורות `NULL`. הסתעפות בקוד אפליקציה: `col.is_(None)` כשהערך הוא `None`.

2. **`VARCHAR(N)` ≥ אורך ערך ה-enum המקסימלי** — מאומת על ידי טסט CI. SQLite (dev) לא אוכף אורך, Postgres כן.

3. **IDs חיצוניים צריכים `BigInteger`.** Telegram, Discord, Stripe, GitHub IDs חורגים מ-2³¹.

4. **כל `ORDER BY` משולב עם `LIMIT` / `OFFSET` / cursor צריך tiebreaker** — בדרך כלל `Model.id.desc()` אחרי השדה הסמנטי. אחרת דפדוף מכפיל / מדלג על שורות עם ערכים ראשיים זהים.

5. **`LIKE` על קלט משתמש:** `column.startswith(value, autoescape=True)` (SQLAlchemy) או escape ל-`_` ו-`%` ידנית + `LIKE :p ESCAPE '\'`. או השתמש ב-`=`.

6. **`ANY(:ids)` / `IN` cast של טיפוס:** Postgres לא יבצע cast מרומז ממערך מחרוזות ל-UUID. המר ב-Python או `cast(col, String) == any_(...)`.

7. **פעולות מחרוזת של Python (`.strip()`, `.lower()`) על `Column` הן no-ops ב-SQL.** השתמש ב-`func.trim(col)`, `func.lower(col)`.

8. **Truthy על מחרוזות DB:** רווח לבן `"  "` הוא truthy ב-Python אבל ריק ב-flow של עריכה. השתמש ב-`(val or "").strip()` לפני בדיקות.

9. **Migrations:** כל `Index` / `CheckConstraint` / `UniqueConstraint` ב-migration חייב לשקף ב-`__table_args__` של המודל. revision id של Alembic ≤ 30 chars. ל-MySQL אין `ADD COLUMN IF NOT EXISTS`. `DROP COLUMN` הולך ב-migration נפרד אחרי שהקוד הפסיק להתייחס לעמודה.

10. **`postgresql_ops` הוא למחלקות אופרטור, לא כיוון מיון.** השתמש ב-`desc("col")` ל-index יורד.
