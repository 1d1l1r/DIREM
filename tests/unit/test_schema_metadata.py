from direm.db.base import Base
from direm.db.models import Reminder, ReminderDelivery, User, UserState


def test_domain_tables_are_registered() -> None:
    assert {"users", "reminders", "reminder_deliveries", "user_states"}.issubset(Base.metadata.tables)


def test_reminders_table_has_foundation_columns() -> None:
    columns = Reminder.__table__.columns

    for name in (
        "id",
        "user_id",
        "title",
        "message_text",
        "schedule_type",
        "interval_minutes",
        "daily_time",
        "active_from",
        "active_to",
        "timezone",
        "status",
        "next_run_at",
        "created_at",
        "updated_at",
        "deleted_at",
    ):
        assert name in columns


def test_delivery_table_has_foundation_columns() -> None:
    columns = ReminderDelivery.__table__.columns

    for name in (
        "id",
        "reminder_id",
        "user_id",
        "scheduled_for",
        "sent_at",
        "status",
        "error_message",
        "created_at",
    ):
        assert name in columns


def test_user_states_table_has_foundation_columns() -> None:
    columns = UserState.__table__.columns

    for name in ("id", "user_id", "state", "payload_json", "created_at", "updated_at"):
        assert name in columns


def test_relationships_are_declared_without_business_logic() -> None:
    assert Reminder.user.property.mapper.class_ is User
    assert ReminderDelivery.reminder.property.mapper.class_ is Reminder
    assert UserState.user.property.mapper.class_ is User
