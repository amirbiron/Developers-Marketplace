"""POST /avatars — העלאת תמונת פרופיל ל-Supabase Storage (Spec §2.5 / §5)."""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import get_settings
from app.schemas import AvatarResponse
from app.services.storage import AvatarUploadError, upload_avatar

router = APIRouter(tags=["avatars"])

_CHUNK_SIZE = 64 * 1024


@router.post("/avatars", response_model=AvatarResponse)
async def create_avatar(file: UploadFile = File(...)) -> AvatarResponse:
    max_bytes = get_settings().max_avatar_bytes

    # קריאה ב-chunks עם עצירה מוקדמת — לא טוענים קובץ ענק שלם לזיכרון (הגנת DoS).
    chunks: list[bytes] = []
    total = 0
    while chunk := await file.read(_CHUNK_SIZE):
        total += len(chunk)
        if total > max_bytes:
            max_mb = max_bytes / (1024 * 1024)
            raise HTTPException(status_code=400, detail=f"הקובץ גדול מדי — מקסימום {max_mb:.0f}MB")
        chunks.append(chunk)

    try:
        # content_type מהלקוח מועבר לתיעוד בלבד — הזיהוי בפועל לפי magic bytes
        url = await upload_avatar(b"".join(chunks), file.content_type)
    except AvatarUploadError as exc:
        raise HTTPException(status_code=400, detail=exc.message)
    return AvatarResponse(avatar_url=url)
