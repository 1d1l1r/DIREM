"""add user language code

Revision ID: 20260429_003_add_user_language_code
Revises: 20260425_002_domain_model
Create Date: 2026-04-29
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260429_003_add_user_language_code"
down_revision: str | None = "20260425_002_domain_model"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("language_code", sa.String(length=8), nullable=False, server_default="ru"),
    )
    op.create_check_constraint(
        "ck_users_language_code",
        "users",
        "language_code in ('ru', 'kk', 'en')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_users_language_code", "users", type_="check")
    op.drop_column("users", "language_code")
