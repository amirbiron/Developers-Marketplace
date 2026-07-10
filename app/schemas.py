"""סכמות Pydantic — ולידציית קלט ועיצוב פלט (Spec §5).

עקרון פרטיות: אף סכמת פלט ציבורית לא כוללת את `whatsapp_e164`. המספר יוצא רק
דרך ReferralResponse (Spec §5.2).
"""

from __future__ import annotations

import math
import re
import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.constants import (
    AVAILABILITY_VALUES,
    HOURLY,
    INVOLVEMENT_VALUES,
    PRICING_MODELS,
    PROJECT_TYPE_CODES,
    TIMELINE_VALUES,
)

# E.164 בלי '+' — ספרה ראשונה 1-9, סה"כ 8–15 ספרות (Spec §2.1: 972501234567)
_E164_RE = re.compile(r"^[1-9]\d{7,14}$")

MAX_HOURLY_RATE = 100_000  # תקרת שפיות לתעריף שעתי (₪)


# --- עזרי ניקוי/ולידציה משותפים ---
def normalize_e164(value: str) -> str:
    """מנקה ומוודא מספר וואטסאפ בפורמט E.164. שומר ספרות בלבד, בלי '+'."""
    cleaned = re.sub(r"[\s\-()]", "", (value or "").strip())
    if cleaned.startswith("+"):
        cleaned = cleaned[1:]
    if not _E164_RE.match(cleaned):
        raise ValueError(
            "מספר וואטסאפ לא תקין — נדרש פורמט בינלאומי בלי '+', למשל 972501234567"
        )
    return cleaned


def _clean_tokens(items: list[str] | None) -> list[str]:
    """מנקה רשימת מחרוזות: strip + הסרת ריקים, שמירת סדר וייחוד."""
    seen: dict[str, None] = {}
    for item in items or []:
        token = (item or "").strip()
        if token and token not in seen:
            seen[token] = None
    return list(seen.keys())


def _clean_codes(items: list[str] | None) -> list[str]:
    """כמו _clean_tokens אך ל-codes מבוקרים — מוריד גם לאותיות קטנות."""
    seen: dict[str, None] = {}
    for item in items or []:
        token = (item or "").strip().lower()
        if token and token not in seen:
            seen[token] = None
    return list(seen.keys())


def _ensure_subset(values: list[str], allowed: frozenset[str], label_he: str) -> list[str]:
    invalid = [v for v in values if v not in allowed]
    if invalid:
        raise ValueError(f"{label_he}: ערכים לא חוקיים — {', '.join(invalid)}")
    return values


def validate_pricing_hourly(pricing_models: list[str], hourly_rate: int | None) -> None:
    """אינווריאנט משותף (Spec §5): hourly_rate מותר ורלוונטי רק אם pricing כולל hourly.

    נקרא גם מהראוטר אחרי מיזוג עדכון חלקי — מקור-אמת יחיד לכלל הזה.
    """
    if hourly_rate is not None and HOURLY not in (pricing_models or []):
        raise ValueError("hourly_rate מותר רק כאשר מודל התמחור כולל 'hourly'")


def _validate_hourly_rate_value(value: Any) -> int | None:
    """בודק תעריף שעתי: חוסם NaN/Inf קודם (דפוס CLAUDE.md 4), ואז טווח."""
    if value is None:
        return None
    # NaN/Inf עוברים כל בדיקת טווח (השוואות מחזירות False) — חוסמים קודם
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        raise ValueError("תעריף שעתי לא תקין")
    if isinstance(value, bool):  # bool הוא subclass של int — לא רוצים True→1
        raise ValueError("תעריף שעתי לא תקין")
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        raise ValueError("תעריף שעתי חייב להיות מספר שלם")
    if ivalue < 1 or ivalue > MAX_HOURLY_RATE:
        raise ValueError(f"תעריף שעתי חייב להיות בין 1 ל-{MAX_HOURLY_RATE}")
    return ivalue


# =========================================================================
# Developer — קלט
# =========================================================================
class DeveloperCreate(BaseModel):
    """POST /developers. שימו לב: is_verified לא ניתן להגדרה ע"י הלקוח (admin בלבד)."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    full_name: str = Field(min_length=1, max_length=120)
    title: str | None = Field(default=None, max_length=120)
    bio: str | None = Field(default=None, max_length=600)
    highlight: str | None = Field(default=None, max_length=280)
    avatar_url: str | None = Field(default=None, max_length=1000)
    whatsapp_e164: str
    project_types: list[str] = Field(min_length=1)
    stack: list[str] | None = None
    ai_tools: list[str] | None = None
    pricing_models: list[str] = Field(min_length=1)
    hourly_rate: int | None = None
    availability: str
    portfolio_url: str | None = Field(default=None, max_length=1000)
    links: dict[str, str] | None = None

    @field_validator("whatsapp_e164")
    @classmethod
    def _v_whatsapp(cls, v: str) -> str:
        return normalize_e164(v)

    @field_validator("hourly_rate", mode="before")
    @classmethod
    def _v_hourly(cls, v: Any) -> int | None:
        return _validate_hourly_rate_value(v)

    @field_validator("availability")
    @classmethod
    def _v_availability(cls, v: str) -> str:
        v = (v or "").strip().lower()
        if v not in AVAILABILITY_VALUES:
            raise ValueError(f"זמינות לא חוקית — מותר: {', '.join(sorted(AVAILABILITY_VALUES))}")
        return v

    @field_validator("project_types")
    @classmethod
    def _v_project_types(cls, v: list[str]) -> list[str]:
        codes = _clean_codes(v)
        if not codes:
            raise ValueError("חובה לבחור לפחות סוג פרויקט אחד")
        return _ensure_subset(codes, PROJECT_TYPE_CODES, "סוגי פרויקט")

    @field_validator("pricing_models")
    @classmethod
    def _v_pricing(cls, v: list[str]) -> list[str]:
        codes = _clean_codes(v)
        if not codes:
            raise ValueError("חובה לבחור לפחות מודל תמחור אחד")
        return _ensure_subset(codes, PRICING_MODELS, "מודלי תמחור")

    @field_validator("stack", "ai_tools")
    @classmethod
    def _v_free_lists(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        return _clean_tokens(v)

    @model_validator(mode="after")
    def _v_pricing_hourly(self) -> DeveloperCreate:
        validate_pricing_hourly(self.pricing_models, self.hourly_rate)
        return self


class DeveloperUpdate(BaseModel):
    """PATCH /developers/{id}. כל השדות אופציונליים. is_verified לא נכלל (admin בלבד).

    בדיקת העקביות pricing↔hourly נעשית בראוטר מול המצב הממוזג (create + עדכון).
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    full_name: str | None = Field(default=None, min_length=1, max_length=120)
    title: str | None = Field(default=None, max_length=120)
    bio: str | None = Field(default=None, max_length=600)
    highlight: str | None = Field(default=None, max_length=280)
    avatar_url: str | None = Field(default=None, max_length=1000)
    whatsapp_e164: str | None = None
    project_types: list[str] | None = Field(default=None, min_length=1)
    stack: list[str] | None = None
    ai_tools: list[str] | None = None
    pricing_models: list[str] | None = Field(default=None, min_length=1)
    hourly_rate: int | None = None
    availability: str | None = None
    portfolio_url: str | None = Field(default=None, max_length=1000)
    links: dict[str, str] | None = None
    is_active: bool | None = None  # השהיה עצמית (Spec §5)

    @field_validator("whatsapp_e164")
    @classmethod
    def _v_whatsapp(cls, v: str | None) -> str | None:
        return normalize_e164(v) if v is not None else None

    @field_validator("hourly_rate", mode="before")
    @classmethod
    def _v_hourly(cls, v: Any) -> int | None:
        return _validate_hourly_rate_value(v)

    @field_validator("availability")
    @classmethod
    def _v_availability(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip().lower()
        if v not in AVAILABILITY_VALUES:
            raise ValueError(f"זמינות לא חוקית — מותר: {', '.join(sorted(AVAILABILITY_VALUES))}")
        return v

    @field_validator("project_types")
    @classmethod
    def _v_project_types(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        codes = _clean_codes(v)
        if not codes:
            raise ValueError("חובה לבחור לפחות סוג פרויקט אחד")
        return _ensure_subset(codes, PROJECT_TYPE_CODES, "סוגי פרויקט")

    @field_validator("pricing_models")
    @classmethod
    def _v_pricing(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        codes = _clean_codes(v)
        if not codes:
            raise ValueError("חובה לבחור לפחות מודל תמחור אחד")
        return _ensure_subset(codes, PRICING_MODELS, "מודלי תמחור")

    @field_validator("stack", "ai_tools")
    @classmethod
    def _v_free_lists(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        return _clean_tokens(v)


# =========================================================================
# Developer — פלט (בלי whatsapp_e164 לעולם)
# =========================================================================
class DeveloperPublic(BaseModel):
    """פרופיל ציבורי — GET /developers/{id}. אין כאן whatsapp_e164."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    title: str | None = None
    bio: str | None = None
    highlight: str | None = None
    avatar_url: str | None = None
    project_types: list[str]
    stack: list[str] | None = None
    ai_tools: list[str] | None = None
    pricing_models: list[str]
    hourly_rate: int | None = None
    availability: str
    portfolio_url: str | None = None
    links: dict[str, Any] | None = None
    is_verified: bool
    is_active: bool


class DeveloperCreated(DeveloperPublic):
    """תשובת POST /developers — כוללת את אסימון העריכה. מוחזר **פעם אחת בלבד**;
    יש לשמור אותו כדי לערוך את הפרופיל בעתיד (PATCH דורש אותו ב-header X-Edit-Token)."""

    edit_token: str


# =========================================================================
# Match
# =========================================================================
class MatchRequest(BaseModel):
    """POST /match — תשובות הלקוח (Spec §5.1)."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    project_type: str
    pricing_prefs: list[str] | None = None
    timeline: str
    involvement: str | None = None
    portfolio_only: bool = False
    description: str | None = Field(default=None, max_length=1000)
    stack_pref: list[str] | None = None

    @field_validator("project_type")
    @classmethod
    def _v_project_type(cls, v: str) -> str:
        v = (v or "").strip().lower()
        if v not in PROJECT_TYPE_CODES:
            raise ValueError("סוג פרויקט לא חוקי")
        return v

    @field_validator("timeline")
    @classmethod
    def _v_timeline(cls, v: str) -> str:
        v = (v or "").strip().lower()
        if v not in TIMELINE_VALUES:
            raise ValueError(f"לו\"ז לא חוקי — מותר: {', '.join(sorted(TIMELINE_VALUES))}")
        return v

    @field_validator("involvement")
    @classmethod
    def _v_involvement(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip().lower()
        if v not in INVOLVEMENT_VALUES:
            raise ValueError("רמת מעורבות לא חוקית")
        return v

    @field_validator("pricing_prefs")
    @classmethod
    def _v_pricing_prefs(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        codes = _clean_codes(v)
        return _ensure_subset(codes, PRICING_MODELS, "העדפות תמחור")

    @field_validator("stack_pref")
    @classmethod
    def _v_stack_pref(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        return _clean_tokens(v)


class MatchResultItem(BaseModel):
    """כרטיס מפתח בתוצאות — בלי whatsapp_e164 (Spec §5.1)."""

    developer_id: uuid.UUID
    full_name: str
    title: str | None = None
    highlight: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    project_types: list[str]
    stack: list[str] | None = None
    ai_tools: list[str] | None = None
    pricing_models: list[str]
    hourly_rate: int | None = None
    availability: str
    portfolio_url: str | None = None
    links: dict[str, Any] | None = None
    is_verified: bool
    match_score: int


class MatchResponse(BaseModel):
    request_id: uuid.UUID
    results: list[MatchResultItem]


# =========================================================================
# Referral — choke point של הפרטיות (Spec §5.2)
# =========================================================================
class ReferralCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: uuid.UUID
    developer_id: uuid.UUID


class ReferralResponse(BaseModel):
    """התשובה היחידה במערכת שמכילה מספר וואטסאפ."""

    whatsapp_e164: str
    wa_link: str


# =========================================================================
# Avatar + Meta
# =========================================================================
class AvatarResponse(BaseModel):
    avatar_url: str


class ProjectTypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    label_he: str
    description_he: str | None = None
    sort_order: int
