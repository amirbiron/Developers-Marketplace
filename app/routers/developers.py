"""ניהול פרופיל מפתח (Spec §5).

בעלוּת: POST מחזיר `edit_token` חד-פעמי; PATCH דורש אותו ב-header `X-Edit-Token`.
כך רק מי שיצר את הפרופיל יכול לערוך אותו (כולל שינוי מספר הוואטסאפ).
`is_verified` לעולם לא ניתן להגדרה מכאן — admin בלבד (לא נכלל בסכמות הקלט).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Developer
from app.schemas import (
    DeveloperCreate,
    DeveloperCreated,
    DeveloperPublic,
    DeveloperUpdate,
    validate_pricing_hourly,
)
from app.security import generate_edit_token, verify_edit_token

router = APIRouter(tags=["developers"])


@router.post("/developers", response_model=DeveloperCreated, status_code=201)
async def create_developer(
    payload: DeveloperCreate, db: AsyncSession = Depends(get_db)
) -> DeveloperCreated:
    # auto-publish: הפרופיל חי מיד, is_verified=false (Spec §4.1)
    token, token_hash = generate_edit_token()
    developer = Developer(**payload.model_dump(), edit_token_hash=token_hash)
    db.add(developer)
    await db.commit()
    # re-fetch — טוען server defaults (id, created_at, is_verified, is_active) (דפוס CLAUDE.md 5)
    await db.refresh(developer)
    public = DeveloperPublic.model_validate(developer)
    # ה-edit_token מוחזר פעם אחת בלבד — לא נשמר כטקסט גלוי ולא חוזר ב-GET
    return DeveloperCreated(**public.model_dump(), edit_token=token)


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
    x_edit_token: str | None = Header(default=None, alias="X-Edit-Token"),
) -> Developer:
    developer = await db.get(Developer, developer_id)
    if developer is None:
        raise HTTPException(status_code=404, detail="המפתח לא נמצא")

    # אימות בעלוּת — רק בעל האסימון רשאי לערוך
    if not verify_edit_token(x_edit_token, developer.edit_token_hash):
        raise HTTPException(status_code=403, detail="אין הרשאה לערוך פרופיל זה")

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
