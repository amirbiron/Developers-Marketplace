"""מנוע ההתאמה — הלב של המערכת (Spec §3).

דטרמיניסטי לחלוטין: אותו קלט מחזיר תמיד אותה תוצאה. אין LLM, אין I/O.
כל הפונקציות טהורות ועובדות על dataclasses פשוטים — מנותקות מ-SQLAlchemy כדי
שאפשר יהיה לבדוק את כל ההיגיון בלי מסד נתונים.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import datetime

from app.constants import AVAILABILITY_AVAILABLE, AVAILABILITY_UNAVAILABLE, BUDGET_FRIENDLY

# --- משקלים (Spec §3.2) ---
PROJECT_MAX = 50.0
STACK_MAX = 30.0
AVAILABILITY_MAX = 20.0
BUDGET_BONUS = 10.0

# כמה תוצאות להחזיר — קצר וממוקד עדיף על ארוך (Spec §3.3: top-5 עד top-8)
DEFAULT_MAX_RESULTS = 8


@dataclass(frozen=True)
class Candidate:
    """התוצר המצומצם של שורת developer שנחוץ לניקוד. הראוטר בונה זאת משורת ה-ORM."""

    id: str
    project_types: Sequence[str]
    availability: str
    is_active: bool
    updated_at: datetime
    is_verified: bool = False
    stack: Sequence[str] = field(default_factory=tuple)
    pricing_models: Sequence[str] = field(default_factory=tuple)
    portfolio_url: str | None = None


@dataclass(frozen=True)
class MatchQuery:
    """תשובות הלקוח שנכנסות למנוע (רק מה שרלוונטי לניקוד)."""

    project_type: str
    timeline: str | None = None
    pricing_prefs: Sequence[str] = field(default_factory=tuple)
    stack_pref: Sequence[str] = field(default_factory=tuple)
    portfolio_only: bool = False


@dataclass(frozen=True)
class ScoreBreakdown:
    """פירוט הניקוד — שקוף וניתן לדיבוג (Spec §3: "ניתן לדיבוג")."""

    project: float
    stack: float
    availability: float
    stack_active: bool
    budget_bonus: float
    base_normalized: float
    final: float  # לפני clamp — משמש למיון כדי שהבונוס יבדיל גם בצמרת
    display: int  # 0..100 — הציון שמוצג ללקוח ("94% מתאים")


@dataclass(frozen=True)
class MatchResult:
    """מפתח + הניקוד שלו, ממוין."""

    candidate: Candidate
    score: ScoreBreakdown


# --- עזרי נורמליזציה ---
def _norm(value: str | None) -> str:
    """נרמול טוקן להשוואה: strip + lower. רווח לבן נחשב ריק (דפוס Postgres 8)."""
    return (value or "").strip().lower()


def _norm_set(items: Iterable[str] | None) -> set[str]:
    """קבוצת טוקנים מנורמלים, בלי ריקים."""
    return {token for token in (_norm(item) for item in (items or [])) if token}


# --- שלב 1: סינון מקדים (Spec §3.1) ---
def prefilter(candidates: Iterable[Candidate], query: MatchQuery) -> list[Candidate]:
    """מסנן החוצה מי שלא רלוונטי לפני ניקוד.

    המנוע אוכף את כל כללי הסינון בעצמו (גם אם ה-SQL כבר סינן חלק) — כך ההיגיון
    נשאר במקום אחד וניתן לבדיקה בלי DB.
    """
    wanted_type = _norm(query.project_type)
    passed: list[Candidate] = []
    for candidate in candidates:
        # לא פעיל או לא זמין → החוצה
        if not candidate.is_active:
            continue
        if _norm(candidate.availability) == AVAILABILITY_UNAVAILABLE:
            continue
        # התאמת סוג פרויקט מדויקת — בינארית, אין חפיפה חלקית (Spec §1)
        if wanted_type not in _norm_set(candidate.project_types):
            continue
        # פילטר הלקוח "רק עם תיק עבודות"
        if query.portfolio_only and not (candidate.portfolio_url or "").strip():
            continue
        passed.append(candidate)
    return passed


# --- שלב 2: ניקוד לכל גורם (Spec §3.2) ---
def availability_timeline_score(availability: str, timeline: str | None) -> float:
    """ניקוד זמינות+לו"ז לפי הטבלה ב-Spec §3.2 (0–20)."""
    avail = _norm(availability)
    tl = _norm(timeline)

    if avail == AVAILABILITY_AVAILABLE:
        # זמין: דחוף = 20, אחרת (weeks/flexible) = 18
        return 20.0 if tl == "urgent" else 18.0

    if avail == "limited":
        if tl == "flexible":
            return 14.0
        if tl == "weeks":
            return 10.0
        if tl == "urgent":
            return 5.0
        return 10.0  # ברירת מחדל ניטרלית (timeline חובה — לא אמור לקרות)

    # unavailable — סונן ב-prefilter, אבל מחזירים 0 להגנה
    return 0.0


def stack_score(stack_pref: Sequence[str], dev_stack: Sequence[str]) -> tuple[float, bool]:
    """ניקוד stack (0–30) + האם הגורם פעיל.

    הלקוח לא ציין stack_pref → (0, False): הגורם לא פעיל, וה-30 מתחלקים
    פרופורציונלית דרך הנורמליזציה ב-score() (Spec §3.2).
    הלקוח ציין → ציון לפי יחס החפיפה: כמה מהטכנולוגיות שביקש נמצאות אצל המפתח.
    """
    pref = _norm_set(stack_pref)
    if not pref:
        return 0.0, False
    dev = _norm_set(dev_stack)
    overlap = len(pref & dev)
    return (overlap / len(pref)) * STACK_MAX, True


def score(candidate: Candidate, query: MatchQuery) -> ScoreBreakdown:
    """מחשב את ציון ההתאמה של מפתח יחיד. דטרמיניסטי."""
    # עבר prefilter → התאמת סוג פרויקט מדויקת → מלוא 50 (Spec §3.2)
    project_pts = PROJECT_MAX
    stack_pts, stack_active = stack_score(query.stack_pref, candidate.stack)
    availability_pts = availability_timeline_score(candidate.availability, query.timeline)

    # נורמליזציה: כשאין stack_pref הגורם לא פעיל וה-active_max קטן ב-30, כך
    # שהניקוד מנורמל חזרה ל-0..100 — "30 הנקודות מתחלקות פרופורציונלית" (Spec §3.2).
    active_max = PROJECT_MAX + (STACK_MAX if stack_active else 0.0) + AVAILABILITY_MAX
    raw = project_pts + stack_pts + availability_pts
    base_normalized = raw / active_max * 100.0

    # בונוס budget_friendly — רק אם גם הלקוח וגם המפתח סימנו (Spec §3.2). +10 מעל הבסיס.
    budget_match = (
        BUDGET_FRIENDLY in _norm_set(query.pricing_prefs)
        and BUDGET_FRIENDLY in _norm_set(candidate.pricing_models)
    )
    budget_bonus = BUDGET_BONUS if budget_match else 0.0

    final = base_normalized + budget_bonus
    # מיון לפי final (לפני clamp) כדי שהבונוס יבדיל גם ליד 100; תצוגה חסומה ל-100.
    display = round(min(final, 100.0))

    return ScoreBreakdown(
        project=project_pts,
        stack=stack_pts,
        availability=availability_pts,
        stack_active=stack_active,
        budget_bonus=budget_bonus,
        base_normalized=base_normalized,
        final=final,
        display=display,
    )


# --- שלב 3: מיון, שבירת שוויון והחזרה (Spec §3.3) ---
def _sort_key(result: MatchResult) -> tuple:
    """מפתח מיון. Python ממיין עולה, אז שדות "גבוה קודם" מקבלים סימן שלילי/היפוך.

    סדר: final ↓ → is_verified ↓ → available ↓ → updated_at ↓ → id ↑ (tiebreaker יציב).
    """
    candidate = result.candidate
    updated_ts = candidate.updated_at.timestamp() if candidate.updated_at else 0.0
    return (
        -result.score.final,  # ציון גבוה קודם
        0 if candidate.is_verified else 1,  # מאומת קודם
        0 if _norm(candidate.availability) == AVAILABILITY_AVAILABLE else 1,  # זמין קודם
        -updated_ts,  # עדכני יותר קודם
        str(candidate.id),  # tiebreaker דטרמיניסטי אחרון (דפוס Postgres 4)
    )


def match(
    candidates: Iterable[Candidate],
    query: MatchQuery,
    *,
    max_results: int = DEFAULT_MAX_RESULTS,
) -> list[MatchResult]:
    """מריץ את המנוע המלא: סינון → ניקוד → מיון → top-N.

    אם אף מפתח לא עבר את הסינון → רשימה ריקה (הראוטר יחזיר מסך ריק, לא תוצאות מזויפות).
    """
    passed = prefilter(candidates, query)
    scored = [MatchResult(candidate=c, score=score(c, query)) for c in passed]
    scored.sort(key=_sort_key)
    return scored[:max_results]
