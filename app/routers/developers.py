"""ניהול פרופיל מפתח (Spec §5).

⚠️ אבטחה — פער מודע: ה-Spec אינו מגדיר auth ל-POST/PATCH. המימוש נאמן ל-Spec,
אבל **בפרודקשן חובה** להוסיף שכבת בעלוּת/אימות: כרגע כל אחד יכול לערוך כל פרופיל
(כולל שינוי מספר הוואטסאפ). ראו README, סעיף אבטחה. is_verified לעולם לא ניתן
להגדרה מכאן — admin בלבד.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Developer
from app.schemas import DeveloperCreate, DeveloperPublic, DeveloperUpdate, validate_pricing_hourly

router = APIRouter(tags=["developers"])


@router.post("/developers", response_model=DeveloperPublic, status_code=201)
async def create_developer(
    payload: DeveloperCreate, db: AsyncSession = Depends(get_db)
) -> Developer:
    # auto-publish: הפרופיל חי מיד, is_verified=false (Spec §4.1)
    developer = Developer(**payload.model_dump())
    db.add(developer)
    await db.commit()
    # re-fetch — טוען server defaults (id, created_at, is_verified, is_active) (דפוס CLAUDE.md 5)
    await db.refresh(developer)
    return developer


@router.get("/developers/{developer_id}", response_model=DeveloperPublic)
async def get_developer(
    developer_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> Developer:
    developer = await db.get(Developer, developer_id)
    if developer is None or not developer.is_active:
        raise HTTPException(status_code=404, detail="המפתח לא נמצא")
    return developer


@router.patch("/developers/{developer_id}", response_model=DeveloperPublic)
async def update_developer(
    developer_id: uuid.UUID,
    payload: DeveloperUpdate,
    db: AsyncSession = Depends(get_db),
) -> Developer:
    developer = await db.get(Developer, developer_id)
    if developer is None:
        raise HTTPException(status_code=404, detail="המפתח לא נמצא")

    updates = payload.model_dump(exclude_unset=True)  # PATCH — רק שדות שנשלחו

    # בדיקת עקביות pricing↔hourly מול המצב הממוזג (קיים + עדכון) — מקור-אמת יחיד
    merged_pricing = updates.get("pricing_models", developer.pricing_models)
    merged_hourly = updates.get("hourly_rate", developer.hourly_rate)
    try:
        validate_pricing_hourly(merged_pricing, merged_hourly)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    for field, value in updates.items():
        setattr(developer, field, value)

    await db.commit()
    await db.refresh(developer)
    return developer
