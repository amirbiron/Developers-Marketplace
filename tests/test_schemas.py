"""טסטים לוולידציית הסכמות (Pydantic). בלי DB."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas import (
    DeveloperCreate,
    DeveloperPublic,
    DeveloperUpdate,
    MatchRequest,
    MatchResultItem,
    normalize_e164,
)


def valid_developer_kwargs(**overrides):
    base = dict(
        full_name="דנה כהן",
        whatsapp_e164="972501234567",
        project_types=["webapp", "saas"],
        pricing_models=["after_scoping"],
        availability="available",
    )
    base.update(overrides)
    return base


# =========================================================================
# E.164
# =========================================================================
class TestE164:
    def test_valid(self):
        assert normalize_e164("972501234567") == "972501234567"

    def test_normalizes_plus_and_separators(self):
        assert normalize_e164("+972-50-123-4567") == "972501234567"
        assert normalize_e164(" 972 50 123 4567 ") == "972501234567"

    @pytest.mark.parametrize(
        "bad",
        [
            "0501234567",  # מתחיל ב-0
            "12",  # קצר מדי
            "97250123456789012",  # ארוך מדי
            "972-50-ABC-4567",  # אותיות
            "",  # ריק
            "+",  # רק פלוס
        ],
    )
    def test_invalid(self, bad):
        with pytest.raises(ValueError):
            normalize_e164(bad)

    def test_developer_normalizes_on_create(self):
        dev = DeveloperCreate(**valid_developer_kwargs(whatsapp_e164="+972 50-123-4567"))
        assert dev.whatsapp_e164 == "972501234567"


# =========================================================================
# hourly_rate ↔ pricing_models
# =========================================================================
class TestHourlyRate:
    def test_hourly_rate_allowed_with_hourly(self):
        dev = DeveloperCreate(
            **valid_developer_kwargs(pricing_models=["hourly"], hourly_rate=350)
        )
        assert dev.hourly_rate == 350

    def test_hourly_rate_rejected_without_hourly(self):
        with pytest.raises(ValidationError):
            DeveloperCreate(
                **valid_developer_kwargs(pricing_models=["after_scoping"], hourly_rate=350)
            )

    def test_hourly_rate_zero_rejected(self):
        with pytest.raises(ValidationError):
            DeveloperCreate(**valid_developer_kwargs(pricing_models=["hourly"], hourly_rate=0))

    def test_hourly_rate_negative_rejected(self):
        with pytest.raises(ValidationError):
            DeveloperCreate(**valid_developer_kwargs(pricing_models=["hourly"], hourly_rate=-5))

    def test_hourly_rate_too_high_rejected(self):
        with pytest.raises(ValidationError):
            DeveloperCreate(
                **valid_developer_kwargs(pricing_models=["hourly"], hourly_rate=999_999)
            )

    def test_hourly_rate_nan_rejected(self):
        # דפוס CLAUDE.md 4 — NaN חייב להיחסם לפני כל בדיקת טווח
        with pytest.raises(ValidationError):
            DeveloperCreate(
                **valid_developer_kwargs(pricing_models=["hourly"], hourly_rate=float("nan"))
            )

    def test_hourly_rate_inf_rejected(self):
        with pytest.raises(ValidationError):
            DeveloperCreate(
                **valid_developer_kwargs(pricing_models=["hourly"], hourly_rate=float("inf"))
            )

    def test_hourly_rate_bool_rejected(self):
        # True הוא subclass של int — אסור שיתפרש כתעריף 1
        with pytest.raises(ValidationError):
            DeveloperCreate(
                **valid_developer_kwargs(pricing_models=["hourly"], hourly_rate=True)
            )


# =========================================================================
# enums / subsets
# =========================================================================
class TestEnums:
    def test_invalid_availability(self):
        with pytest.raises(ValidationError):
            DeveloperCreate(**valid_developer_kwargs(availability="maybe"))

    def test_invalid_project_type(self):
        with pytest.raises(ValidationError):
            DeveloperCreate(**valid_developer_kwargs(project_types=["webapp", "nonsense"]))

    def test_empty_project_types(self):
        with pytest.raises(ValidationError):
            DeveloperCreate(**valid_developer_kwargs(project_types=[]))

    def test_invalid_pricing_model(self):
        with pytest.raises(ValidationError):
            DeveloperCreate(**valid_developer_kwargs(pricing_models=["barter"]))

    def test_codes_are_lowercased(self):
        dev = DeveloperCreate(**valid_developer_kwargs(project_types=["WebApp", "SAAS"]))
        assert dev.project_types == ["webapp", "saas"]

    def test_stack_deduped_and_trimmed(self):
        dev = DeveloperCreate(
            **valid_developer_kwargs(stack=[" React ", "React", "FastAPI", "  "])
        )
        assert dev.stack == ["React", "FastAPI"]


# =========================================================================
# is_verified לא ניתן להגדרה ע"י הלקוח
# =========================================================================
class TestSecurityFields:
    def test_is_verified_forbidden_on_create(self):
        # extra="forbid" → ניסיון להגדיר is_verified נדחה
        with pytest.raises(ValidationError):
            DeveloperCreate(**valid_developer_kwargs(is_verified=True))

    def test_is_verified_forbidden_on_update(self):
        with pytest.raises(ValidationError):
            DeveloperUpdate(is_verified=True)

    def test_public_output_has_no_whatsapp(self):
        # הסכמה הציבורית לא כוללת בכלל את השדה
        assert "whatsapp_e164" not in DeveloperPublic.model_fields

    def test_match_result_has_no_whatsapp(self):
        assert "whatsapp_e164" not in MatchResultItem.model_fields


# =========================================================================
# MatchRequest
# =========================================================================
class TestMatchRequest:
    def test_minimal_valid(self):
        req = MatchRequest(project_type="saas", timeline="weeks")
        assert req.project_type == "saas"
        assert req.portfolio_only is False

    def test_project_type_required(self):
        with pytest.raises(ValidationError):
            MatchRequest(timeline="weeks")

    def test_timeline_required(self):
        with pytest.raises(ValidationError):
            MatchRequest(project_type="saas")

    def test_invalid_timeline(self):
        with pytest.raises(ValidationError):
            MatchRequest(project_type="saas", timeline="someday")

    def test_invalid_involvement(self):
        with pytest.raises(ValidationError):
            MatchRequest(project_type="saas", timeline="weeks", involvement="ghost")

    def test_full_valid(self):
        req = MatchRequest(
            project_type="saas",
            pricing_prefs=["hourly", "budget_friendly"],
            timeline="weeks",
            involvement="collaborative",
            portfolio_only=True,
            description="מערכת ניהול לקוחות עם דשבורד",
            stack_pref=["React", "Supabase"],
        )
        assert req.pricing_prefs == ["hourly", "budget_friendly"]
        assert req.stack_pref == ["React", "Supabase"]

    def test_description_too_long(self):
        with pytest.raises(ValidationError):
            MatchRequest(project_type="saas", timeline="weeks", description="א" * 1001)

    def test_invalid_pricing_pref(self):
        with pytest.raises(ValidationError):
            MatchRequest(project_type="saas", timeline="weeks", pricing_prefs=["free"])
