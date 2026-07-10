"""טסטים למנוע ההתאמה — הליבה. בלי DB, טהור לחלוטין.

מכסה: סינון מקדים, ניקוד לכל גורם, נורמליזציה, בונוס budget, שבירת שוויון,
תקרת תוצאות, תוצאה ריקה, ודטרמיניזם.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.engine import (
    Candidate,
    MatchQuery,
    MatchResult,
    ScoreBreakdown,
    _sort_key,
    availability_timeline_score,
    match,
    prefilter,
    score,
    stack_score,
)

OLD = datetime(2026, 1, 1, tzinfo=timezone.utc)
NEW = datetime(2026, 6, 1, tzinfo=timezone.utc)


def _fake_result(
    id: str,
    *,
    final: float = 100.0,
    is_verified: bool = False,
    availability: str = "available",
    updated_at: datetime = OLD,
) -> MatchResult:
    """בונה MatchResult עם final נתון — לבדיקה ישירה של לוגיקת המיון/שבירת-שוויון."""
    sb = ScoreBreakdown(
        project=50.0,
        stack=0.0,
        availability=0.0,
        stack_active=False,
        budget_bonus=0.0,
        base_normalized=final,
        final=final,
        display=round(min(final, 100.0)),
    )
    cand = make_candidate(
        id=id, is_verified=is_verified, availability=availability, updated_at=updated_at
    )
    return MatchResult(candidate=cand, score=sb)


def make_candidate(
    *,
    id: str = "dev-1",
    project_types=("webapp",),
    availability: str = "available",
    is_active: bool = True,
    updated_at: datetime = OLD,
    is_verified: bool = False,
    stack=(),
    pricing_models=(),
    portfolio_url: str | None = None,
) -> Candidate:
    return Candidate(
        id=id,
        project_types=project_types,
        availability=availability,
        is_active=is_active,
        updated_at=updated_at,
        is_verified=is_verified,
        stack=stack,
        pricing_models=pricing_models,
        portfolio_url=portfolio_url,
    )


# =========================================================================
# סינון מקדים (prefilter)
# =========================================================================
class TestPrefilter:
    def test_inactive_excluded(self):
        cand = make_candidate(is_active=False)
        assert prefilter([cand], MatchQuery(project_type="webapp")) == []

    def test_unavailable_excluded(self):
        cand = make_candidate(availability="unavailable")
        assert prefilter([cand], MatchQuery(project_type="webapp")) == []

    def test_limited_passes(self):
        cand = make_candidate(availability="limited")
        assert len(prefilter([cand], MatchQuery(project_type="webapp"))) == 1

    def test_exact_project_type_match_required(self):
        # מפתח שסימן webapp לא יתאים ללקוח שביקש saas (אין חפיפה חלקית, Spec §1)
        cand = make_candidate(project_types=("webapp",))
        assert prefilter([cand], MatchQuery(project_type="saas")) == []
        assert len(prefilter([cand], MatchQuery(project_type="webapp"))) == 1

    def test_webapp_and_saas_are_separate(self):
        webapp_dev = make_candidate(id="w", project_types=("webapp",))
        saas_dev = make_candidate(id="s", project_types=("saas",))
        passed = prefilter([webapp_dev, saas_dev], MatchQuery(project_type="saas"))
        assert [c.id for c in passed] == ["s"]

    def test_multiple_project_types_on_developer(self):
        cand = make_candidate(project_types=("webapp", "saas", "automation"))
        assert len(prefilter([cand], MatchQuery(project_type="automation"))) == 1

    def test_portfolio_only_filters_out_empty(self):
        no_portfolio = make_candidate(id="np", portfolio_url=None)
        whitespace = make_candidate(id="ws", portfolio_url="   ")  # רווח לבן = ריק
        with_portfolio = make_candidate(id="wp", portfolio_url="https://x.com")
        query = MatchQuery(project_type="webapp", portfolio_only=True)
        passed = prefilter([no_portfolio, whitespace, with_portfolio], query)
        assert [c.id for c in passed] == ["wp"]

    def test_project_type_match_case_insensitive(self):
        cand = make_candidate(project_types=("WebApp",))
        assert len(prefilter([cand], MatchQuery(project_type="webapp"))) == 1


# =========================================================================
# ניקוד זמינות + לו"ז — כל 5 השורות של טבלת Spec §3.2
# =========================================================================
class TestAvailabilityTimelineScore:
    @pytest.mark.parametrize(
        "availability,timeline,expected",
        [
            ("available", "urgent", 20.0),
            ("available", "weeks", 18.0),
            ("available", "flexible", 18.0),
            ("limited", "flexible", 14.0),
            ("limited", "weeks", 10.0),
            ("limited", "urgent", 5.0),
        ],
    )
    def test_table(self, availability, timeline, expected):
        assert availability_timeline_score(availability, timeline) == expected


# =========================================================================
# ניקוד stack
# =========================================================================
class TestStackScore:
    def test_no_pref_is_inactive(self):
        points, active = stack_score([], ["React", "FastAPI"])
        assert points == 0.0
        assert active is False

    def test_full_overlap(self):
        points, active = stack_score(["React", "Supabase"], ["React", "Supabase", "FastAPI"])
        assert points == 30.0
        assert active is True

    def test_partial_overlap(self):
        points, active = stack_score(["React", "Vue"], ["React"])
        assert points == pytest.approx(15.0)
        assert active is True

    def test_zero_overlap_still_active(self):
        points, active = stack_score(["Angular"], ["React"])
        assert points == 0.0
        assert active is True  # פעיל אבל 0 — המפתח לא נפסל, רק מקבל 0 בגורם הזה

    def test_case_insensitive(self):
        points, _ = stack_score(["react", "SUPABASE"], ["React", "supabase"])
        assert points == 30.0


# =========================================================================
# ניקוד כולל + נורמליזציה + בונוס
# =========================================================================
class TestScore:
    def test_full_match_no_stack_pref_available_urgent_is_100(self):
        cand = make_candidate(availability="available")
        sb = score(cand, MatchQuery(project_type="webapp", timeline="urgent"))
        # project 50 + avail 20, active_max=70 → 70/70=100
        assert sb.display == 100
        assert sb.stack_active is False

    def test_no_stack_pref_available_weeks_normalizes(self):
        cand = make_candidate(availability="available")
        sb = score(cand, MatchQuery(project_type="webapp", timeline="weeks"))
        # (50+18)/70*100 = 97.14 → 97. הלקוח הלא-טכני לא נענש על היעדר stack.
        assert sb.base_normalized == pytest.approx(97.142857, rel=1e-4)
        assert sb.display == 97

    def test_stack_pref_full_available_urgent_is_100(self):
        cand = make_candidate(stack=("React", "Supabase"))
        sb = score(
            cand,
            MatchQuery(project_type="webapp", timeline="urgent", stack_pref=["React", "Supabase"]),
        )
        # active_max=100, raw=50+30+20=100
        assert sb.display == 100
        assert sb.stack_active is True

    def test_stack_pref_half(self):
        cand = make_candidate(stack=("React",))
        sb = score(
            cand,
            MatchQuery(project_type="webapp", timeline="weeks", stack_pref=["React", "Vue"]),
        )
        # raw = 50 + 15 + 18 = 83, active_max=100 → 83
        assert sb.display == 83

    def test_budget_bonus_applied(self):
        cand = make_candidate(pricing_models=("budget_friendly", "after_scoping"))
        sb = score(
            cand,
            MatchQuery(
                project_type="webapp", timeline="weeks", pricing_prefs=["budget_friendly"]
            ),
        )
        # base 97.14 + 10 = 107.14 → clamp ל-100 בתצוגה, אבל final נשמר לצורך מיון
        assert sb.budget_bonus == 10.0
        assert sb.final == pytest.approx(107.142857, rel=1e-4)
        assert sb.display == 100

    def test_budget_bonus_not_applied_when_client_did_not_ask(self):
        cand = make_candidate(pricing_models=("budget_friendly",))
        sb = score(cand, MatchQuery(project_type="webapp", timeline="weeks"))
        assert sb.budget_bonus == 0.0

    def test_budget_bonus_not_applied_when_dev_not_budget(self):
        cand = make_candidate(pricing_models=("hourly",))
        sb = score(
            cand,
            MatchQuery(
                project_type="webapp", timeline="weeks", pricing_prefs=["budget_friendly"]
            ),
        )
        assert sb.budget_bonus == 0.0

    def test_budget_bonus_lifts_ranking_below_cap(self):
        # שני מפתחים עם בסיס 83; רק אחד budget → מקבל 93, מדורג מעל
        base_query = dict(project_type="webapp", timeline="weeks", stack_pref=["React", "Vue"])
        plain = make_candidate(id="plain", stack=("React",))
        budget = make_candidate(id="budget", stack=("React",), pricing_models=("budget_friendly",))
        q = MatchQuery(**base_query, pricing_prefs=["budget_friendly"])
        assert score(plain, q).display == 83
        assert score(budget, q).display == 93


# =========================================================================
# match — מיון, שבירת שוויון, תקרה, ריק, דטרמיניזם
# =========================================================================
class TestMatch:
    def test_empty_when_nobody_passes(self):
        cand = make_candidate(project_types=("landing",))
        assert match([cand], MatchQuery(project_type="saas")) == []

    def test_tiebreak_verified_before_unverified(self):
        # כולם ציון 100 (available+urgent, בלי stack_pref)
        verified = make_candidate(id="v", is_verified=True, updated_at=OLD)
        unverified = make_candidate(id="u", is_verified=False, updated_at=NEW)
        results = match([unverified, verified], MatchQuery(project_type="webapp", timeline="urgent"))
        assert [r.candidate.id for r in results] == ["v", "u"]

    def test_tiebreak_available_before_limited_at_same_score(self):
        # זמינות נכנסת לציון עצמו, אז "ציון זהה עם זמינות שונה" קשה לייצר דרך score().
        # לכן בודקים את לוגיקת המיון ישירות: אותו final, זמינות שונה → available קודם.
        available = _fake_result("av", availability="available")
        limited = _fake_result("lim", availability="limited")
        ordered = sorted([limited, available], key=_sort_key)
        assert [r.candidate.id for r in ordered] == ["av", "lim"]

    def test_tiebreak_updated_at_more_recent_first(self):
        old = make_candidate(id="old", is_verified=True, updated_at=OLD)
        new = make_candidate(id="new", is_verified=True, updated_at=NEW)
        results = match([old, new], MatchQuery(project_type="webapp", timeline="urgent"))
        assert [r.candidate.id for r in results] == ["new", "old"]

    def test_tiebreak_full_order(self):
        # C: verified+new, A: verified+old, B: unverified+new → C, A, B
        a = make_candidate(id="a", is_verified=True, updated_at=OLD)
        b = make_candidate(id="b", is_verified=False, updated_at=NEW)
        c = make_candidate(id="c", is_verified=True, updated_at=NEW)
        results = match([a, b, c], MatchQuery(project_type="webapp", timeline="urgent"))
        assert [r.candidate.id for r in results] == ["c", "a", "b"]

    def test_tiebreak_id_stable_last(self):
        # זהים לחלוטין חוץ מ-id → מיון לפי id עולה
        x = make_candidate(id="bbb", is_verified=True, updated_at=NEW)
        y = make_candidate(id="aaa", is_verified=True, updated_at=NEW)
        results = match([x, y], MatchQuery(project_type="webapp", timeline="urgent"))
        assert [r.candidate.id for r in results] == ["aaa", "bbb"]

    def test_higher_score_ranks_first(self):
        # מפתח עם התאמת stack מלאה מדורג מעל מי בלי — כשהלקוח ציין stack
        strong = make_candidate(id="strong", stack=("React", "Supabase"))
        weak = make_candidate(id="weak", stack=("PHP",))
        q = MatchQuery(project_type="webapp", timeline="urgent", stack_pref=["React", "Supabase"])
        results = match([weak, strong], q)
        assert [r.candidate.id for r in results] == ["strong", "weak"]

    def test_caps_at_eight(self):
        cands = [make_candidate(id=f"d{i}") for i in range(12)]
        results = match(cands, MatchQuery(project_type="webapp", timeline="urgent"))
        assert len(results) == 8

    def test_returns_fewer_than_five_when_few_pass(self):
        cands = [make_candidate(id=f"d{i}") for i in range(3)]
        results = match(cands, MatchQuery(project_type="webapp", timeline="urgent"))
        assert len(results) == 3  # לא ממציאים מפתחים

    def test_deterministic_same_output_regardless_of_input_order(self):
        a = make_candidate(id="a", is_verified=True, updated_at=NEW)
        b = make_candidate(id="b", is_verified=True, updated_at=NEW)
        c = make_candidate(id="c", is_verified=False, updated_at=OLD)
        query = MatchQuery(project_type="webapp", timeline="urgent")
        order1 = [r.candidate.id for r in match([a, b, c], query)]
        order2 = [r.candidate.id for r in match([c, b, a], query)]
        order3 = [r.candidate.id for r in match([b, a, c], query)]
        assert order1 == order2 == order3 == ["a", "b", "c"]

    def test_deterministic_scores_repeatable(self):
        cand = make_candidate(stack=("React",))
        q = MatchQuery(project_type="webapp", timeline="weeks", stack_pref=["React", "Vue"])
        first = score(cand, q)
        second = score(cand, q)
        assert first == second
