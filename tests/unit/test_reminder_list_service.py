from datetime import UTC, datetime, time

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from direm.db.base import Base
from direm.domain.constants import ReminderStatus, ScheduleType
from direm.repositories.reminders import ReminderRepository
from direm.repositories.users import UserRepository
from direm.services.reminder_list_service import ReminderListService
from direm.services.reminder_service import CreateReminderRequest, ReminderService
from direm.services.user_service import TelegramUserProfile, UserService


@pytest.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield async_sessionmaker(engine, expire_on_commit=False)

    await engine.dispose()


async def create_user(session, telegram_user_id: int, timezone: str):
    user_service = UserService(UserRepository(session))
    user = await user_service.register_or_update_from_telegram(
        TelegramUserProfile(
            telegram_user_id=telegram_user_id,
            chat_id=telegram_user_id + 1000,
            username=f"user{telegram_user_id}",
            first_name="User",
        )
    )
    await user_service.update_timezone(user, timezone)
    return user


async def test_list_empty_state(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001, "UTC")
        service = ReminderListService(ReminderRepository(session))

        items = await service.list_for_user(user)

        assert items == []
        assert service.render_for_user(items) == "No reminders yet.\nCreate one with /new."


async def test_list_only_current_user_reminders(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001, "UTC")
        other_user = await create_user(session, 1002, "UTC")
        reminder_service = ReminderService(ReminderRepository(session))

        await reminder_service.create_reminder(
            user,
            CreateReminderRequest(
                title="Mine",
                message_text="My message",
                schedule_type=ScheduleType.INTERVAL.value,
                interval_minutes=30,
            ),
        )
        await reminder_service.create_reminder(
            other_user,
            CreateReminderRequest(
                title="Other",
                message_text="Other message",
                schedule_type=ScheduleType.INTERVAL.value,
                interval_minutes=30,
            ),
        )

        items = await ReminderListService(ReminderRepository(session)).list_for_user(user)

        assert [item.title for item in items] == ["Mine"]


async def test_list_active_reminders_first(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001, "UTC")
        repository = ReminderRepository(session)

        paused = await repository.create(
            user_id=user.id,
            title="Paused",
            message_text="Paused message",
            schedule_type=ScheduleType.INTERVAL.value,
            interval_minutes=60,
            daily_time=None,
            active_from=None,
            active_to=None,
            timezone=user.timezone,
            status=ReminderStatus.PAUSED.value,
            next_run_at=datetime(2026, 4, 25, 10, tzinfo=UTC),
        )
        active = await repository.create(
            user_id=user.id,
            title="Active",
            message_text="Active message",
            schedule_type=ScheduleType.INTERVAL.value,
            interval_minutes=60,
            daily_time=None,
            active_from=None,
            active_to=None,
            timezone=user.timezone,
            status=ReminderStatus.ACTIVE.value,
            next_run_at=datetime(2026, 4, 25, 11, tzinfo=UTC),
        )
        assert paused.id is not None
        assert active.id is not None

        items = await ReminderListService(repository).list_for_user(user)

        assert [item.title for item in items] == ["Active", "Paused"]


async def test_list_formats_schedule_window_and_next_run_in_user_timezone(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001, "Asia/Almaty")
        await ReminderRepository(session).create(
            user_id=user.id,
            title="Daily pulse",
            message_text="Check in.",
            schedule_type=ScheduleType.DAILY.value,
            interval_minutes=None,
            daily_time=time(10, 0),
            active_from=time(9, 0),
            active_to=time(18, 0),
            timezone=user.timezone,
            status=ReminderStatus.ACTIVE.value,
            next_run_at=datetime(2026, 4, 25, 5, tzinfo=UTC),
        )

        service = ReminderListService(ReminderRepository(session))
        items = await service.list_for_user(user)
        rendered = service.render_for_user(items)

        assert items[0].schedule == "daily at 10:00"
        assert items[0].active_window == "09:00-18:00"
        assert "2026-04-25 10:00" in items[0].next_run_at
        assert "Daily pulse" in rendered
        assert "Status: active" in rendered
