"""חיבור async למסד הנתונים — engine, session factory, ו-dependency ל-FastAPI."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# pool_pre_ping — מוודא שהחיבור חי לפני שימוש (חשוב מול Supabase/PgBouncer).
# create_async_engine עצל: לא מתחבר עד השאילתה הראשונה, אז import לא נכשל בלי DB.
engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
)

# expire_on_commit=False — מונע MissingGreenlet כשניגשים ל-attributes אחרי commit
# (דפוס CLAUDE.md 5). עדיין נחלץ ערכים פרימיטיביים במפורש היכן שקריטי.
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """בסיס לכל המודלים של SQLAlchemy."""


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency של FastAPI — פותח session לכל בקשה וסוגר בסוף."""
    async with AsyncSessionLocal() as session:
        yield session
