"""POST /match — הלב. שומר את הפנייה, מריץ את המנוע, מחזיר top-N (בלי מספרי וואטסאפ)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import AVAILABILITY_UNAVAILABLE
from app.database import get_db
from app.engine import MatchQuery
from app.engine import match as run_match
from app.mappers import developer_to_candidate, developer_to_result_item
from app.models import Developer, Request
from app.schemas import MatchRequest, MatchResponse

router = APIRouter(tags=["match"])


@router.post("/match", response_model=MatchResponse)
async def create_match(payload: MatchRequest, db: AsyncSession = Depends(get_db)) -> MatchResponse:
    # --- 1. שליפת מועמדים: הסינון המקדים נדחף ל-SQL (מנצל אינדקסים) ---
    # project_types @> ARRAY[type] — חברוּת מדויקת, נתמך ב-GIN index.
    stmt = select(Developer).where(
        Developer.is_active.is_(True),
        Developer.availability != AVAILABILITY_UNAVAILABLE,
        Developer.project_types.contains([payload.project_type]),
    )
    if payload.portfolio_only:
        # func.trim (לא .strip של Python — no-op ב-SQL, דפוס Postgres 7)
        stmt = stmt.where(
            Developer.portfolio_url.isnot(None),
            func.length(func.trim(Developer.portfolio_url)) > 0,
        )
    rows = list((await db.execute(stmt)).scalars().all())

    # --- 2. ניקוד ומיון בזיכרון (המנוע גם אוכף שוב את הסינון — defense-in-depth) ---
    query = MatchQuery(
        project_type=payload.project_type,
        timeline=payload.timeline,
        pricing_prefs=payload.pricing_prefs or [],
        stack_pref=payload.stack_pref or [],
        portfolio_only=payload.portfolio_only,
    )
    results = run_match((developer_to_candidate(r) for r in rows), query)
    matched_uuids = [uuid.UUID(res.candidate.id) for res in results]

    # --- 3. שמירת ה-request תמיד (גם 0 תוצאות) — analytics ביקוש↔היצע (Spec §2.2) ---
    request_row = Request(
        project_type=payload.project_type,
        pricing_prefs=payload.pricing_prefs,
        stack_pref=payload.stack_pref,
        timeline=payload.timeline,
        involvement=payload.involvement,
        portfolio_only=payload.portfolio_only,
        description=payload.description,
        matched_dev_ids=matched_uuids,
    )
    db.add(request_row)
    await db.flush()
    request_id = request_row.id  # חילוץ פרימיטיבי לפני commit (דפוס CLAUDE.md 5)
    await db.commit()

    # --- 4. בניית התשובה מהשורות שכבר בזיכרון (בלי whatsapp) ---
    rows_by_id = {str(r.id): r for r in rows}
    items = [
        developer_to_result_item(rows_by_id[res.candidate.id], res.score.display)
        for res in results
    ]
    return MatchResponse(request_id=request_id, results=items)
