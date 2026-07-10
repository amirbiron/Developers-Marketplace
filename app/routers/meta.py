"""GET /meta/project-types — רשימת סוגי פרויקט + תיאורים לתצוגה בפרונט (Spec §5)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import PROJECT_TYPES
from app.database import get_db
from app.models import ProjectType
from app.schemas import ProjectTypeOut

router = APIRouter(tags=["meta"])


@router.get("/meta/project-types", response_model=list[ProjectTypeOut])
async def list_project_types(db: AsyncSession = Depends(get_db)) -> list[ProjectTypeOut]:
    # ORDER BY עם tiebreaker על code (דפוס Postgres 4)
    stmt = (
        select(ProjectType)
        .where(ProjectType.is_active.is_(True))
        .order_by(ProjectType.sort_order, ProjectType.code)
    )
    rows = list((await db.execute(stmt)).scalars().all())
    if rows:
        return [ProjectTypeOut.model_validate(row) for row in rows]

    # fallback ל-constants אם הטבלה עוד לא נזרעה — כדי שהפרונט תמיד יקבל 10 קטגוריות
    return [
        ProjectTypeOut(
            code=pt["code"],
            label_he=pt["label_he"],
            description_he=pt["description_he"],
            sort_order=index + 1,
        )
        for index, pt in enumerate(PROJECT_TYPES)
    ]
