"""add pending delivery status

Revision ID: 20260504_006_pending_status
Revises: 20260503_005_reminder_checkins
Create Date: 2026-05-04
"""
from collections.abc import Sequence

from alembic import op


revision: str = "20260504_006_pending_status"
down_revision: str | None = "20260503_005_reminder_checkins"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("reminder_deliveries", "status", server_default="pending")
    op.drop_constraint("ck_reminder_deliveries_status", "reminder_deliveries", type_="check")
    op.create_check_constraint(
        "ck_reminder_deliveries_status",
        "reminder_deliveries",
        "status in ('pending', 'sent', 'failed', 'skipped')",
    )


def downgrade() -> None:
    op.alter_column("reminder_deliveries", "status", server_default="skipped")
    op.drop_constraint("ck_reminder_deliveries_status", "reminder_deliveries", type_="check")
    op.create_check_constraint(
        "ck_reminder_deliveries_status",
        "reminder_deliveries",
        "status in ('sent', 'failed', 'skipped')",
    )
