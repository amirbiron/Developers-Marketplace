"""מיפוי בין שורות ה-ORM לבין אובייקטי המנוע וסכמות הפלט.

מרוכז כאן כדי ש-/match ו-/referrals ישתמשו באותה המרה בדיוק (מקור-אמת יחיד).
"""

from __future__ import annotations

from app.engine import Candidate, MatchQuery
from app.models import Developer, Request
from app.schemas import MatchResultItem


def developer_to_candidate(row: Developer) -> Candidate:
    """שורת developer → מועמד לניקוד (רק השדות הרלוונטיים למנוע)."""
    return Candidate(
        id=str(row.id),
        project_types=row.project_types or [],
        availability=row.availability,
        is_active=row.is_active,
        updated_at=row.updated_at,
        is_verified=row.is_verified,
        stack=row.stack or [],
        pricing_models=row.pricing_models or [],
        portfolio_url=row.portfolio_url,
    )


def developer_to_result_item(row: Developer, match_score: int) -> MatchResultItem:
    """שורת developer + ציון → כרטיס תוצאה (בלי whatsapp_e164)."""
    return MatchResultItem(
        developer_id=row.id,
        full_name=row.full_name,
        title=row.title,
        highlight=row.highlight,
        bio=row.bio,
        avatar_url=row.avatar_url,
        project_types=row.project_types or [],
        stack=row.stack,
        ai_tools=row.ai_tools,
        pricing_models=row.pricing_models or [],
        hourly_rate=row.hourly_rate,
        availability=row.availability,
        portfolio_url=row.portfolio_url,
        links=row.links,
        is_verified=row.is_verified,
        match_score=match_score,
    )


def request_to_query(row: Request) -> MatchQuery:
    """שורת request → שאילתת מנוע — לשחזור דטרמיניסטי של הציון ב-/referrals."""
    return MatchQuery(
        project_type=row.project_type,
        timeline=row.timeline,
        pricing_prefs=row.pricing_prefs or [],
        stack_pref=row.stack_pref or [],
        portfolio_only=row.portfolio_only,
    )
