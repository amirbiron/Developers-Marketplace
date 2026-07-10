"""POST /avatars — העלאת תמונת פרופיל ל-Supabase Storage (Spec §2.5 / §5)."""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas import AvatarResponse
from app.services.storage import AvatarUploadError, upload_avatar

router = APIRouter(tags=["avatars"])


@router.post("/avatars", response_model=AvatarResponse)
async def create_avatar(file: UploadFile = File(...)) -> AvatarResponse:
    data = await file.read()
    try:
        # content_type מהלקוח מועבר לתיעוד בלבד — הזיהוי בפועל לפי magic bytes
        url = await upload_avatar(data, file.content_type)
    except AvatarUploadError as exc:
        raise HTTPException(status_code=400, detail=exc.message)
    return AvatarResponse(avatar_url=url)
