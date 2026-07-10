"""טסטי אינטגרציה מול DB אמיתי (מדולגים אם אין TEST_DATABASE_URL).

מאמתים את החוזה של ה-API ובמיוחד את שמירת הפרטיות: whatsapp_e164 יוצא **רק**
דרך POST /referrals ובשום מקום אחר.
"""

from __future__ import annotations

import uuid

from tests.conftest import requires_db

VALID_DEV = {
    "full_name": "דנה כהן",
    "title": "Full-stack",
    "highlight": "בונה SaaS מהר ובאיכות",
    "bio": "מפתחת עם ניסיון בבניית מערכות מאפס",
    "whatsapp_e164": "972501234567",
    "project_types": ["saas", "webapp"],
    "stack": ["React", "FastAPI", "Supabase"],
    "ai_tools": ["Claude Code"],
    "pricing_models": ["hourly", "budget_friendly"],
    "hourly_rate": 350,
    "availability": "available",
    "portfolio_url": "https://dana.dev",
    "links": {"github": "https://github.com/dana"},
}


@requires_db
class TestDevelopersAPI:
    async def test_create_returns_no_whatsapp(self, client):
        resp = await client.post("/developers", json=VALID_DEV)
        assert resp.status_code == 201
        body = resp.json()
        assert "whatsapp_e164" not in body  # לא מודלף
        assert body["full_name"] == "דנה כהן"
        assert body["is_verified"] is False  # auto-publish בלי אימות (Spec §4.1)
        assert body["is_active"] is True

    async def test_get_returns_no_whatsapp(self, client):
        dev_id = (await client.post("/developers", json=VALID_DEV)).json()["id"]
        resp = await client.get(f"/developers/{dev_id}")
        assert resp.status_code == 200
        assert "whatsapp_e164" not in resp.json()

    async def test_cannot_set_is_verified(self, client):
        resp = await client.post("/developers", json={**VALID_DEV, "is_verified": True})
        assert resp.status_code == 422  # extra="forbid"

    async def test_hourly_rate_without_hourly_rejected(self, client):
        bad = {**VALID_DEV, "pricing_models": ["after_scoping"], "hourly_rate": 350}
        resp = await client.post("/developers", json=bad)
        assert resp.status_code == 422

    async def test_create_returns_edit_token(self, client):
        body = (await client.post("/developers", json=VALID_DEV)).json()
        assert isinstance(body.get("edit_token"), str) and body["edit_token"]
        # ה-token לא חוזר ב-GET הציבורי
        assert "edit_token" not in (await client.get(f"/developers/{body['id']}")).json()

    async def test_patch_requires_valid_token(self, client):
        created = (await client.post("/developers", json=VALID_DEV)).json()
        dev_id, token = created["id"], created["edit_token"]

        # בלי token → 403
        assert (await client.patch(f"/developers/{dev_id}", json={"is_active": False})).status_code == 403
        # token שגוי → 403
        bad = await client.patch(
            f"/developers/{dev_id}", json={"is_active": False}, headers={"X-Edit-Token": "nope"}
        )
        assert bad.status_code == 403

        # token נכון → 200 (השהיה עצמית)
        ok = await client.patch(
            f"/developers/{dev_id}", json={"is_active": False}, headers={"X-Edit-Token": token}
        )
        assert ok.status_code == 200
        assert ok.json()["is_active"] is False
        assert (await client.get(f"/developers/{dev_id}")).status_code == 404  # מושהה


@requires_db
class TestMatchAPI:
    async def test_returns_results_without_whatsapp(self, client):
        await client.post("/developers", json=VALID_DEV)
        resp = await client.post("/match", json={"project_type": "saas", "timeline": "weeks"})
        assert resp.status_code == 200
        body = resp.json()
        assert "request_id" in body
        assert len(body["results"]) == 1
        item = body["results"][0]
        assert "whatsapp_e164" not in item
        assert item["match_score"] > 0
        assert item["full_name"] == "דנה כהן"

    async def test_zero_results_is_200_empty(self, client):
        await client.post("/developers", json=VALID_DEV)  # saas/webapp בלבד
        resp = await client.post("/match", json={"project_type": "bot_voice", "timeline": "urgent"})
        assert resp.status_code == 200
        assert resp.json()["results"] == []

    async def test_exact_project_type_only(self, client):
        await client.post("/developers", json=VALID_DEV)
        resp = await client.post("/match", json={"project_type": "landing", "timeline": "weeks"})
        assert resp.json()["results"] == []

    async def test_portfolio_only_filter(self, client):
        no_pf = {**VALID_DEV, "whatsapp_e164": "972500000001", "portfolio_url": None}
        await client.post("/developers", json=no_pf)
        resp = await client.post(
            "/match",
            json={"project_type": "saas", "timeline": "weeks", "portfolio_only": True},
        )
        assert resp.json()["results"] == []

    async def test_budget_bonus_ranks_higher(self, client):
        budget_dev = {
            **VALID_DEV,
            "whatsapp_e164": "972500000002",
            "full_name": "מפתח נגיש",
            "pricing_models": ["budget_friendly"],
            "hourly_rate": None,
        }
        plain_dev = {
            **VALID_DEV,
            "whatsapp_e164": "972500000003",
            "full_name": "מפתח רגיל",
            "pricing_models": ["after_scoping"],
            "hourly_rate": None,
        }
        await client.post("/developers", json=budget_dev)
        await client.post("/developers", json=plain_dev)
        resp = await client.post(
            "/match",
            json={
                "project_type": "saas",
                "timeline": "weeks",
                "pricing_prefs": ["budget_friendly"],
            },
        )
        results = resp.json()["results"]
        assert results[0]["full_name"] == "מפתח נגיש"  # בונוס budget דוחף למעלה


@requires_db
class TestReferralAPI:
    async def test_referral_is_only_source_of_number(self, client):
        dev_id = (await client.post("/developers", json=VALID_DEV)).json()["id"]
        match_resp = await client.post(
            "/match", json={"project_type": "saas", "timeline": "weeks"}
        )
        request_id = match_resp.json()["request_id"]

        resp = await client.post(
            "/referrals", json={"request_id": request_id, "developer_id": dev_id}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["whatsapp_e164"] == "972501234567"  # המספר — רק כאן
        assert body["wa_link"].startswith("https://wa.me/972501234567?text=")

    async def test_referral_missing_request_404(self, client):
        dev_id = (await client.post("/developers", json=VALID_DEV)).json()["id"]
        resp = await client.post(
            "/referrals",
            json={"request_id": str(uuid.uuid4()), "developer_id": dev_id},
        )
        assert resp.status_code == 404

    async def test_referral_missing_developer_404(self, client):
        match_resp = await client.post(
            "/match", json={"project_type": "saas", "timeline": "weeks"}
        )
        request_id = match_resp.json()["request_id"]
        resp = await client.post(
            "/referrals",
            json={"request_id": request_id, "developer_id": str(uuid.uuid4())},
        )
        assert resp.status_code == 404


@requires_db
class TestMetaAPI:
    async def test_project_types_returns_ten(self, client):
        resp = await client.get("/meta/project-types")
        assert resp.status_code == 200
        # create_all לא זורע → fallback ל-constants (10 קטגוריות)
        assert len(resp.json()) == 10
        codes = [pt["code"] for pt in resp.json()]
        assert "saas" in codes
        assert "webapp" in codes
