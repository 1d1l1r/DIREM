from datetime import UTC, datetime, time

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from direm.db.base import Base
from direm.domain.constants import ReminderStatus, ScheduleType
from direm.domain.errors import InvalidScheduleConfigError
from direm.repositories.reminders import ReminderRepository
from direm.repositories.users import UserRepository
from direm.services.reminder_service import CreateReminderRequest, ReminderService
from direm.services.user_service import TelegramUserProfile, UserService


@pytest.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield async_sessionmaker(engine, expire_on_commit=False)

    await engine.dispose()


async def create_user(session_factory, timezone: str = "Asia/Almaty"):
    async with session_factory() as session:
        user_service = UserService(UserRepository(session))
        user = await user_service.register_or_update_from_telegram(
            TelegramUserProfile(
                telegram_user_id=1001,
                chat_id=2001,
                username="ilya",
                first_name="Ilya",
            )
        )
        await user_service.update_timezone(user, timezone)
        await session.commit()
        return user.id


async def test_create_interval_reminder_uses_user_timezone_and_active_status(session_factory) -> None:
    await create_user(session_factory)

    async with session_factory() as session:
        user = await UserRepository(session).get_by_telegram_user_id(1001)
        assert user is not None
        service = ReminderService(ReminderRepository(session))

        created = await service.create_reminder(
            user,
            CreateReminderRequest(
                title="Morning focus",
                message_text="Return to the current step.",
                schedule_type=ScheduleType.INTERVAL.value,
                interval_minutes=45,
            ),
        )

        assert created.reminder.status == ReminderStatus.ACTIVE.value
        assert created.reminder.timezone == "Asia/Almaty"
        assert created.reminder.schedule_type == ScheduleType.INTERVAL.value
        assert created.reminder.interval_minutes == 45
        assert created.first_run_at_utc.tzinfo is not None
        assert created.first_run_at_utc > datetime.now(UTC)


async def test_create_daily_reminder_calculates_future_next_run(session_factory) -> None:
    await create_user(session_factory, timezone="UTC")

    async with session_factory() as session:
        user = await UserRepository(session).get_by_telegram_user_id(1001)
        assert user is not None
        service = ReminderService(ReminderRepository(session))

        created = await service.create_reminder(
            user,
            CreateReminderRequest(
                title="Evening check",
                message_text="What moved today?",
                schedule_type=ScheduleType.DAILY.value,
                daily_time=time(22, 0),
            ),
        )

        assert created.reminder.status == ReminderStatus.ACTIVE.value
        assert created.reminder.daily_time == time(22, 0)
        assert created.first_run_at_utc > datetime.now(UTC)


async def test_daily_reminder_outside_active_window_rejects(session_factory) -> None:
    await create_user(session_factory, timezone="UTC")

    async with session_factory() as session:
        user = await UserRepository(session).get_by_telegram_user_id(1001)
        assert user is not None
        service = ReminderService(ReminderRepository(session))

        with pytest.raises(InvalidScheduleConfigError):
            await service.create_reminder(
                user,
                CreateReminderRequest(
                    title="Late check",
                    message_text="Too late.",
                    schedule_type=ScheduleType.DAILY.value,
                    daily_time=time(22, 0),
                    active_from=time(10, 0),
                    active_to=time(18, 0),
                ),
            )


async def test_create_reminder_rejects_invalid_title_and_message(session_factory) -> None:
    await create_user(session_factory, timezone="UTC")

    async with session_factory() as session:
        user = await UserRepository(session).get_by_telegram_user_id(1001)
        assert user is not None
        service = ReminderService(ReminderRepository(session))

        with pytest.raises(InvalidScheduleConfigError):
            await service.create_reminder(
                user,
                CreateReminderRequest(
                    title="",
                    message_text="Message",
                    schedule_type=ScheduleType.INTERVAL.value,
                    interval_minutes=10,
                ),
            )

        with pytest.raises(InvalidScheduleConfigError):
            await service.create_reminder(
                user,
                CreateReminderRequest(
                    title="Title",
                    message_text="",
                    schedule_type=ScheduleType.INTERVAL.value,
                    interval_minutes=10,
                ),
            )
