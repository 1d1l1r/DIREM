"""create reminder checkins

Revision ID: 20260503_005_reminder_checkins
Revises: 20260503_004_bunker_state
Create Date: 2026-05-03
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

from direm.domain.constants import CheckInResponseType


revision: str = "20260503_005_reminder_checkins"
down_revision: str | None = "20260503_004_bunker_state"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "reminder_checkins",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("reminder_id", sa.Integer(), nullable=False),
        sa.Column("reminder_delivery_id", sa.Integer(), nullable=False),
        sa.Column("response_type", sa.String(length=32), nullable=False),
        sa.Column("response_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            f"response_type in ({_quoted_values(CheckInResponseType)})",
            name="ck_reminder_checkins_response_type",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reminder_id"], ["reminders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reminder_delivery_id"], ["reminder_deliveries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reminder_delivery_id", name="uq_reminder_checkins_delivery_id"),
    )
    op.create_index("ix_reminder_checkins_user_id", "reminder_checkins", ["user_id"])
    op.create_index("ix_reminder_checkins_reminder_id", "reminder_checkins", ["reminder_id"])
    op.create_index("ix_reminder_checkins_reminder_delivery_id", "reminder_checkins", ["reminder_delivery_id"])
    op.create_index("ix_reminder_checkins_response_type", "reminder_checkins", ["response_type"])
    op.create_index("ix_reminder_checkins_user_created_at", "reminder_checkins", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_reminder_checkins_user_created_at", table_name="reminder_checkins")
    op.drop_index("ix_reminder_checkins_response_type", table_name="reminder_checkins")
    op.drop_index("ix_reminder_checkins_reminder_delivery_id", table_name="reminder_checkins")
    op.drop_index("ix_reminder_checkins_reminder_id", table_name="reminder_checkins")
    op.drop_index("ix_reminder_checkins_user_id", table_name="reminder_checkins")
    op.drop_table("reminder_checkins")


def _quoted_values(enum_type: type[CheckInResponseType]) -> str:
    return ", ".join(f"'{item.value}'" for item in enum_type)
