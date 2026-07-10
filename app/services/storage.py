"""העלאת תמונת פרופיל ל-Supabase Storage (Spec §2.5 / §5).

ולידציה: לא סומכים על ה-Content-Type או שם הקובץ מהמשתמש — מזהים את סוג
התמונה מה-magic bytes בפועל, ומייצרים שם אובייקט אקראי (מונע path traversal).
"""

from __future__ import annotations

import uuid

import httpx

from app.config import get_settings

# סוגי תמונה נתמכים → סיומת קובץ
ALLOWED_IMAGE_TYPES: dict[str, str] = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}


class AvatarUploadError(Exception):
    """שגיאת העלאת תמונה — נושאת הודעה ידידותית בעברית להצגה ללקוח."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def detect_image_type(data: bytes) -> str | None:
    """מזהה סוג תמונה מה-magic bytes. מחזיר MIME type או None אם לא מזוהה."""
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    # WebP: "RIFF" ....(4 bytes) "WEBP"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def validate_avatar(data: bytes, *, max_bytes: int) -> tuple[str, str]:
    """ולידציה טהורה של תמונת פרופיל. מחזיר (content_type, סיומת). זורק AvatarUploadError."""
    if not data:
        raise AvatarUploadError("הקובץ ריק")
    if len(data) > max_bytes:
        max_mb = max_bytes / (1024 * 1024)
        raise AvatarUploadError(f"הקובץ גדול מדי — מקסימום {max_mb:.0f}MB")
    detected = detect_image_type(data)
    if detected is None:
        raise AvatarUploadError("סוג קובץ לא נתמך — יש להעלות PNG, JPEG או WebP")
    return detected, ALLOWED_IMAGE_TYPES[detected]


async def upload_avatar(data: bytes, content_type: str | None = None) -> str:
    """מעלה תמונה ל-bucket הציבורי ומחזיר URL ציבורי. content_type מהלקוח מתעלמים ממנו.

    הערה: משתמשים ב-service key בצד השרת בלבד — הוא לעולם לא נחשף ללקוח.
    """
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_key:
        raise AvatarUploadError("העלאת תמונות אינה מוגדרת בשרת")

    detected, ext = validate_avatar(data, max_bytes=settings.max_avatar_bytes)

    # שם אקראי — לא סומכים על שם הקובץ של המשתמש (מונע התנגשויות ו-path traversal)
    object_path = f"{uuid.uuid4().hex}{ext}"
    base = settings.supabase_url.rstrip("/")
    upload_url = f"{base}/storage/v1/object/{settings.avatar_bucket}/{object_path}"
    headers = {
        "Authorization": f"Bearer {settings.supabase_service_key}",
        "Content-Type": detected,
        "x-upsert": "true",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(upload_url, content=data, headers=headers)
    except httpx.HTTPError:
        raise AvatarUploadError("העלאת התמונה נכשלה — נסו שוב מאוחר יותר")

    if response.status_code not in (200, 201):
        raise AvatarUploadError("העלאת התמונה נכשלה")

    return f"{base}/storage/v1/object/public/{settings.avatar_bucket}/{object_path}"
