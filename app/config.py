"""הגדרות אפליקציה — נטענות ממשתני סביבה (או מקובץ .env בפיתוח)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # חיבור למסד הנתונים (Postgres של Supabase). ברירת מחדל מקומית לפיתוח.
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/marketplace"

    # Supabase Storage — להעלאת תמונות פרופיל
    supabase_url: str = ""
    supabase_service_key: str = ""
    avatar_bucket: str = "avatars"
    max_avatar_bytes: int = 5 * 1024 * 1024  # 5MB — גודל מקסימלי סביר לתמונת פרופיל

    # CORS — דומיינים מורשים לפרונט. פסיק מפריד, או "*" לכל המקורות.
    allowed_origins: str = "*"

    # טקסט פתיחה להודעת הוואטסאפ (מיתוג)
    wa_greeting: str = "היי! הגעתי דרך מרקטפלייס המפתחים."

    @property
    def cors_origins(self) -> list[str]:
        """הופך את המחרוזת מ-ALLOWED_ORIGINS לרשימת מקורות ל-CORS middleware."""
        # (val or "").strip() — רווח לבן הוא truthy ב-Python אבל ריק בפועל (דפוס Postgres 8)
        raw = (self.allowed_origins or "").strip()
        if not raw or raw == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """מוחזר singleton של ההגדרות (נטען פעם אחת)."""
    return Settings()
