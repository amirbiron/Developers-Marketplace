"""initial schema — developers, requests, referrals, project_types

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-10

הערה: נתוני ה-seed של project_types מוטמעים כאן במכוון (snapshot קפוא),
כדי שהמיגרציה תישאר עצמאית ולא תלויה בקוד האפליקציה שעלול להשתנות.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 10 הקטגוריות — snapshot לזריעה ראשונית (Spec §1 / §2.4)
_PROJECT_TYPES_SEED = [
    ("landing", "אתר תדמית", "אתר תדמית / דף נחיתה — נוכחות דיגיטלית, ללא משתמשים או התחברות.", 1),
    ("store", "חנות אונליין", "חנות אונליין — קטלוג מוצרים, עגלת קניות ותשלום.", 2),
    ("mobile", "אפליקציית מובייל", "אפליקציה טבעית לאנדרואיד / iOS.", 3),
    ("webapp", "Web App", "מערכת web עם משתמשים והתחברות — בלי מנוי חוזר.", 4),
    ("saas", "מערכת SaaS", "מערכת SaaS — עם מנוי ותשלום חוזר.", 5),
    ("automation", "אוטומציה ואינטגרציות", "אוטומציות, חיבור בין מערכות ו-APIs.", 6),
    ("bot_chat", "בוט צ'אט", "בוט טקסט ל-WhatsApp / Telegram.", 7),
    ("bot_voice", "בוט קולי", "בוט קולי / מענה טלפוני אוטומטי.", 8),
    ("ai_agents", "AI ואייג'נטים", "פתרונות מבוססי AI ואייג'נטים חכמים.", 9),
    ("other", "אחר", "משהו אחר שלא נכנס לקטגוריות שלמעלה.", 10),
]


def upgrade() -> None:
    # gen_random_uuid() — קיים ב-core מ-PG13, אבל pgcrypto מבטיח זמינות בכל מקרה.
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # --- developers ---
    op.create_table(
        "developers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column("full_name", sa.Text(), nullable=False),
        sa.Column("title", sa.Text()),
        sa.Column("bio", sa.Text()),
        sa.Column("highlight", sa.Text()),
        sa.Column("avatar_url", sa.Text()),
        sa.Column("whatsapp_e164", sa.Text(), nullable=False),
        sa.Column("project_types", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("stack", postgresql.ARRAY(sa.Text())),
        sa.Column("ai_tools", postgresql.ARRAY(sa.Text())),
        sa.Column("pricing_models", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("hourly_rate", sa.Integer()),
        sa.Column("availability", sa.Text(), nullable=False),
        sa.Column("portfolio_url", sa.Text()),
        sa.Column("links", postgresql.JSONB()),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "availability in ('available','limited','unavailable')",
            name="ck_developers_availability",
        ),
    )
    op.create_index(
        "ix_developers_project_types_gin", "developers", ["project_types"], postgresql_using="gin"
    )
    op.create_index("ix_developers_stack_gin", "developers", ["stack"], postgresql_using="gin")
    op.create_index("ix_developers_availability", "developers", ["availability"])
    op.create_index("ix_developers_is_active", "developers", ["is_active"])
    op.create_index("ix_developers_portfolio_url", "developers", ["portfolio_url"])

    # --- requests ---
    op.create_table(
        "requests",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column("project_type", sa.Text(), nullable=False),
        sa.Column("pricing_prefs", postgresql.ARRAY(sa.Text())),
        sa.Column("stack_pref", postgresql.ARRAY(sa.Text())),
        sa.Column("timeline", sa.Text()),
        sa.Column("involvement", sa.Text()),
        sa.Column("portfolio_only", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("description", sa.Text()),
        sa.Column("matched_dev_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True))),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # --- referrals ---
    op.create_table(
        "referrals",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "request_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("requests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "developer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("developers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("match_score", sa.Integer()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_referrals_request_id", "referrals", ["request_id"])
    op.create_index("ix_referrals_developer_id", "referrals", ["developer_id"])

    # --- project_types (lookup) ---
    op.create_table(
        "project_types",
        sa.Column("code", sa.Text(), primary_key=True),
        sa.Column("label_he", sa.Text(), nullable=False),
        sa.Column("description_he", sa.Text()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )

    # --- trigger ל-updated_at על developers ---
    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_developers_updated_at
        BEFORE UPDATE ON developers
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )

    # --- זריעת project_types ---
    project_types_table = sa.table(
        "project_types",
        sa.column("code", sa.Text),
        sa.column("label_he", sa.Text),
        sa.column("description_he", sa.Text),
        sa.column("sort_order", sa.Integer),
    )
    op.bulk_insert(
        project_types_table,
        [
            {
                "code": code,
                "label_he": label_he,
                "description_he": description_he,
                "sort_order": sort_order,
            }
            for code, label_he, description_he, sort_order in _PROJECT_TYPES_SEED
        ],
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_developers_updated_at ON developers")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at()")
    op.drop_table("referrals")
    op.drop_table("requests")
    op.drop_table("project_types")
    op.drop_table("developers")
