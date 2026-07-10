"""Fixtures לטסטי אינטגרציה מול Postgres אמיתי.

טסטים אלה מדולגים אוטומטית אם `TEST_DATABASE_URL` לא מוגדר — כך ה-CI נשאר ירוק
בלי DB, בעוד המנוע/הסכמות/whatsapp (שלא דורשים DB) רצים תמיד.

TEST_DATABASE_URL חייב להיות פורמט asyncpg, למשל:
    postgresql+asyncpg://postgres:postgres@localhost:5432/marketplace_test
"""

from __future__ import annotations

import os

import pytest

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "").strip()

# marker לשימוש בטסטי API — מדלג אם אין DB
requires_db = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="TEST_DATABASE_URL לא מוגדר — מדלגים על טסטי אינטגרציה מול DB",
)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


if TEST_DATABASE_URL:
    import pytest_asyncio
    from httpx import ASGITransport, AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy.pool import NullPool

    from app import models  # noqa: F401 — רישום המודלים ב-metadata
    from app.database import Base, get_db
    from app.main import app

    @pytest_asyncio.fixture
    async def db_engine():
        """יוצר סכמה נקייה לכל טסט (drop+create) ומנקה אחריו."""
        engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        yield engine
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    @pytest_asyncio.fixture
    async def client(db_engine):
        """AsyncClient שמדבר עם האפליקציה, כשה-get_db מוחלף ל-session של טסט."""
        session_factory = async_sessionmaker(
            db_engine, class_=AsyncSession, expire_on_commit=False
        )

        async def override_get_db():
            async with session_factory() as session:
                yield session

        app.dependency_overrides[get_db] = override_get_db
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as http_client:
            yield http_client
        app.dependency_overrides.clear()
