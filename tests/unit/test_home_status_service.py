from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from direm.db.base import Base
from direm.db.models import Reminder
from direm.domain.constants import ReminderStatus, ScheduleType
from direm.repositories.reminders import ReminderRepository
from direm.repositories.users import UserRepository
from direm.services.home_status_service import HomeStatusService
from direm.services.user_service import TelegramUserProfile, UserService


@pytest.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield async_sessionmaker(engine, expire_on_commit=False)

    await engine.dispose()


async def create_user(session, telegram_user_id: int = 1001):
    return await UserService(UserRepository(session)).register_or_update_from_telegram(
        TelegramUserProfile(
            telegram_user_id=telegram_user_id,
            chat_id=telegram_user_id + 1000,
            username="ilya",
            first_name="Ilya",
            language_code="en",
        )
    )


def make_reminder(user_id: int, *, status: str, deleted: bool = False) -> Reminder:
    return Reminder(
        user_id=user_id,
        title="Morning focus",
        message_text="Return.",
        schedule_type=ScheduleType.INTERVAL.value,
        interval_minutes=30,
        timezone="UTC",
        status=status,
        next_run_at=datetime(2026, 5, 3, 9, 0, tzinfo=UTC),
        deleted_at=datetime(2026, 5, 3, 8, 0, tzinfo=UTC) if deleted else None,
    )


async def test_home_status_stats_are_scoped_and_exclude_deleted(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001)
        other_user = await create_user(session, 1002)
        session.add_all(
            [
                make_reminder(user.id, status=ReminderStatus.ACTIVE.value),
                make_reminder(user.id, status=ReminderStatus.PAUSED.value),
                make_reminder(user.id, status=ReminderStatus.ACTIVE.value, deleted=True),
                make_reminder(other_user.id, status=ReminderStatus.ACTIVE.value),
            ]
        )
        await session.flush()

        text = await HomeStatusService(ReminderRepository(session)).render_for_user(user)

        assert "Reminders: 2" in text
        assert "Active: 1" in text
        assert "Paused: 1" in text
