"""add domain model tables

Revision ID: 20260425_002_domain_model
Revises: 20260425_001_create_users
Create Date: 2026-04-25
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

from direm.domain.constants import DeliveryStatus, ReminderStatus, ScheduleType


revision: str = "20260425_002_domain_model"
down_revision: str | None = "20260425_001_create_users"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "reminders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message_text", sa.Text(), nullable=False),
        sa.Column("schedule_type", sa.String(length=32), nullable=False),
        sa.Column("interval_minutes", sa.Integer(), nullable=True),
        sa.Column("daily_time", sa.Time(timezone=False), nullable=True),
        sa.Column("active_from", sa.Time(timezone=False), nullable=True),
        sa.Column("active_to", sa.Time(timezone=False), nullable=True),
        sa.Column("timezone", sa.String(length=64), nullable=False, server_default="UTC"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default=ReminderStatus.ACTIVE.value),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            f"schedule_type in ({_quoted_values(ScheduleType)})",
            name="ck_reminders_schedule_type",
        ),
        sa.CheckConstraint(
            f"status in ({_quoted_values(ReminderStatus)})",
            name="ck_reminders_status",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reminders_user_id", "reminders", ["user_id"])
    op.create_index("ix_reminders_status", "reminders", ["status"])
    op.create_index("ix_reminders_next_run_at", "reminders", ["next_run_at"])
    op.create_index("ix_reminders_deleted_at", "reminders", ["deleted_at"])
    op.create_index("ix_reminders_due_lookup", "reminders", ["status", "next_run_at"])

    op.create_table(
        "reminder_deliveries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reminder_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default=DeliveryStatus.SKIPPED.value),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            f"status in ({_quoted_values(DeliveryStatus)})",
            name="ck_reminder_deliveries_status",
        ),
        sa.ForeignKeyConstraint(["reminder_id"], ["reminders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reminder_deliveries_reminder_id", "reminder_deliveries", ["reminder_id"])
    op.create_index("ix_reminder_deliveries_user_id", "reminder_deliveries", ["user_id"])
    op.create_index("ix_reminder_deliveries_scheduled_for", "reminder_deliveries", ["scheduled_for"])
    op.create_index("ix_reminder_deliveries_status", "reminder_deliveries", ["status"])

    op.create_table(
        "user_states",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(length=128), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )


def downgrade() -> None:
    op.drop_table("user_states")
    op.drop_index("ix_reminder_deliveries_status", table_name="reminder_deliveries")
    op.drop_index("ix_reminder_deliveries_scheduled_for", table_name="reminder_deliveries")
    op.drop_index("ix_reminder_deliveries_user_id", table_name="reminder_deliveries")
    op.drop_index("ix_reminder_deliveries_reminder_id", table_name="reminder_deliveries")
    op.drop_table("reminder_deliveries")
    op.drop_index("ix_reminders_due_lookup", table_name="reminders")
    op.drop_index("ix_reminders_deleted_at", table_name="reminders")
    op.drop_index("ix_reminders_next_run_at", table_name="reminders")
    op.drop_index("ix_reminders_status", table_name="reminders")
    op.drop_index("ix_reminders_user_id", table_name="reminders")
    op.drop_table("reminders")


def _quoted_values(enum_type: type[ScheduleType] | type[ReminderStatus] | type[DeliveryStatus]) -> str:
    return ", ".join(f"'{item.value}'" for item in enum_type)
