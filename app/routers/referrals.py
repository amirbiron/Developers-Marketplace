"""POST /referrals — ה-choke point של הפרטיות (Spec §5.2).

זו הנקודה **היחידה** במערכת שמחזירה מספר וואטסאפ. חשיפת המספר והרישום של
הפנייה קורים באותה טרנזקציה — אי אפשר לקבל מספר בלי שהפנייה נרשמה (דפוס CLAUDE.md 2).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.engine import score as score_developer
from app.mappers import developer_to_candidate, request_to_query
from app.models import Developer, Referral, Request
from app.schemas import ReferralCreate, ReferralResponse
from app.services.whatsapp import build_wa_link

router = APIRouter(tags=["referrals"])


@router.post("/referrals", response_model=ReferralResponse)
async def create_referral(
    payload: ReferralCreate, db: AsyncSession = Depends(get_db)
) -> ReferralResponse:
    request_row = await db.get(Request, payload.request_id)
    if request_row is None:
        raise HTTPException(status_code=404, detail="הפנייה לא נמצאה")

    developer = await db.get(Developer, payload.developer_id)
    if developer is None or not developer.is_active:
        raise HTTPException(status_code=404, detail="המפתח לא נמצא")

    # שחזור דטרמיניסטי של הציון שהוצג — אותה נוסחה בדיוק כמו ב-/match
    match_score = score_developer(
        developer_to_candidate(developer), request_to_query(request_row)
    ).display

    # חילוץ ערכים פרימיטיביים לפני commit (דפוס CLAUDE.md 5)
    whatsapp = developer.whatsapp_e164
    description = request_row.description
    involvement = request_row.involvement

    # רישום הפנייה — קורה לפני שהמספר מוחזר. אם ה-commit נכשל → אין חשיפה.
    referral = Referral(
        request_id=request_row.id,
        developer_id=developer.id,
        match_score=match_score,
    )
    db.add(referral)
    await db.commit()

    wa_link = build_wa_link(whatsapp, description=description, involvement=involvement)
    return ReferralResponse(whatsapp_e164=whatsapp, wa_link=wa_link)
