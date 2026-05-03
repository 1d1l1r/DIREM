"""add user bunker state

Revision ID: 20260503_004_bunker_state
Revises: 20260429_003_user_language
Create Date: 2026-05-03
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260503_004_bunker_state"
down_revision: str | None = "20260429_003_user_language"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("bunker_active", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "users",
        sa.Column("bunker_activated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "bunker_activated_at")
    op.drop_column("users", "bunker_active")
