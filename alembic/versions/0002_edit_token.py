"""add edit_token_hash to developers — בעלוּת על פרופיל

Revision ID: 0002_edit_token
Revises: 0001_initial
Create Date: 2026-07-10
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_edit_token"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # nullable — שורות קיימות (seed) לא נערכות דרך ה-API (אין להן אסימון)
    op.add_column("developers", sa.Column("edit_token_hash", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("developers", "edit_token_hash")
