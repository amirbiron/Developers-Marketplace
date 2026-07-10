"""מודלים של SQLAlchemy — ארבע טבלאות (Spec §2).

הערה: כל Index / CheckConstraint שמופיע כאן משוקף גם ב-migration (דפוס CLAUDE.md 9).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Developer(Base):
    """פרופיל מפתח. `whatsapp_e164` לעולם לא יוצא ל-client חוץ מ-POST /referrals."""

    __tablename__ = "developers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str | None] = mapped_column(Text)  # תפקיד חופשי
    bio: Mapped[str | None] = mapped_column(Text)  # תיאור כללי (~280 תווים)
    highlight: Mapped[str | None] = mapped_column(Text)  # משפט בידול — "במה אני טוב במיוחד"
    avatar_url: Mapped[str | None] = mapped_column(Text)
    # E.164 בלבד (972501234567). לא מוצג בפומבי — נחשף רק דרך /referrals.
    whatsapp_e164: Mapped[str] = mapped_column(Text, nullable=False)
    # מתוך 10 הקטגוריות, בלי תקרה. נכנס למנוע (חברוּת בינארית).
    project_types: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    stack: Mapped[list[str] | None] = mapped_column(ARRAY(Text))  # נכנס למנוע במשקל מלא
    ai_tools: Mapped[list[str] | None] = mapped_column(ARRAY(Text))  # תצוגה בלבד — לא במנוע
    # hourly / after_scoping / budget_friendly. רק budget_friendly נכנס למנוע.
    pricing_models: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    hourly_rate: Mapped[int | None] = mapped_column(Integer)  # ₪ לשעה — תצוגה בלבד
    availability: Mapped[str] = mapped_column(Text, nullable=False)  # enum, ראה CheckConstraint
    portfolio_url: Mapped[str | None] = mapped_column(Text)  # בסיס לפילטר "רק עם תיק עבודות"
    links: Mapped[dict | None] = mapped_column(JSONB)  # {"linkedin": "...", "github": "..."}
    is_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "availability in ('available','limited','unavailable')",
            name="ck_developers_availability",
        ),
        # GIN לחיפוש חברוּת מהיר במערכים (Spec §2.1)
        Index("ix_developers_project_types_gin", "project_types", postgresql_using="gin"),
        Index("ix_developers_stack_gin", "stack", postgresql_using="gin"),
        # B-tree לפילטרים של הסינון המקדים
        Index("ix_developers_availability", "availability"),
        Index("ix_developers_is_active", "is_active"),
        Index("ix_developers_portfolio_url", "portfolio_url"),
    )


class Request(Base):
    """פנייה של לקוח — נשמרת לכל חיפוש, גם בלי פנייה (Spec §2.2)."""

    __tablename__ = "requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    project_type: Mapped[str] = mapped_column(Text, nullable=False)  # הבחירה המרכזית
    pricing_prefs: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    # stack_pref — אחת מתשובות הלקוח (Spec §5.1). נשמר כדי לשחזר את הציון המדויק
    # שהוצג ב-/referrals, וגם ל-analytics על ביקוש טכנולוגי.
    stack_pref: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    timeline: Mapped[str | None] = mapped_column(Text)
    involvement: Mapped[str | None] = mapped_column(Text)  # מטא-דאטה לפנייה — לא במנוע
    portfolio_only: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    description: Mapped[str | None] = mapped_column(Text)  # לניסוח הפנייה, לא למנוע
    matched_dev_ids: Mapped[list[uuid.UUID] | None] = mapped_column(ARRAY(UUID(as_uuid=True)))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class Referral(Base):
    """כל לחיצה על "פנה בוואטסאפ" — analytics + bootstrap ל-reputation (Spec §2.3)."""

    __tablename__ = "referrals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("requests.id", ondelete="CASCADE"), nullable=False
    )
    developer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("developers.id", ondelete="CASCADE"), nullable=False
    )
    match_score: Mapped[int | None] = mapped_column(Integer)  # הציון שהוצג באותו רגע
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("ix_referrals_request_id", "request_id"),
        Index("ix_referrals_developer_id", "developer_id"),
    )


class ProjectType(Base):
    """lookup לסוגי פרויקט — מאפשר לשנות טקסט קטגוריה בלי deploy (Spec §2.4)."""

    __tablename__ = "project_types"

    code: Mapped[str] = mapped_column(Text, primary_key=True)
    label_he: Mapped[str] = mapped_column(Text, nullable=False)
    description_he: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
