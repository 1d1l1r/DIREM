from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from direm.db.base import Base
from direm.db.models import Reminder
from direm.domain.constants import ReminderStatus, ScheduleType
from direm.repositories.users import UserRepository
from direm.services.bunker_service import BunkerService
from direm.services.user_service import TelegramUserProfile, UserService


@pytest.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield async_sessionmaker(engine, expire_on_commit=False)

    await engine.dispose()


async def create_user(session):
    return await UserService(UserRepository(session)).register_or_update_from_telegram(
        TelegramUserProfile(
            telegram_user_id=1001,
            chat_id=2001,
            username="first",
            first_name="First",
            language_code="en",
        )
    )


async def test_new_user_defaults_to_bunker_inactive(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session)
        state = await BunkerService(UserRepository(session)).get_current_state(user)

        assert user.bunker_active is False
        assert user.bunker_activated_at is None
        assert state.active is False
        assert state.activated_at is None


async def test_activate_sets_active_state_and_utc_timestamp(session_factory) -> None:
    now = datetime(2026, 5, 3, 9, 0, tzinfo=UTC)
    async with session_factory() as session:
        user = await create_user(session)
        service = BunkerService(UserRepository(session), clock=lambda: now)

        state = await service.activate(user)

        assert state.active is True
        assert state.activated_at == now
        assert state.activated_at.tzinfo == UTC
        assert user.bunker_active is True
        assert user.bunker_activated_at == now


async def test_activate_is_idempotent_and_keeps_original_timestamp(session_factory) -> None:
    first = datetime(2026, 5, 3, 9, 0, tzinfo=UTC)
    second = datetime(2026, 5, 3, 10, 0, tzinfo=UTC)
    async with session_factory() as session:
        user = await create_user(session)
        service = BunkerService(UserRepository(session), clock=lambda: first)
        await service.activate(user)

        service = BunkerService(UserRepository(session), clock=lambda: second)
        state = await service.activate(user)

        assert state.active is True
        assert state.activated_at == first
        assert user.bunker_activated_at == first


async def test_activate_repairs_active_state_without_timestamp(session_factory) -> None:
    now = datetime(2026, 5, 3, 9, 0, tzinfo=UTC)
    async with session_factory() as session:
        user = await create_user(session)
        user.bunker_active = True
        user.bunker_activated_at = None
        service = BunkerService(UserRepository(session), clock=lambda: now)

        state = await service.activate(user)

        assert state.active is True
        assert state.activated_at == now


async def test_deactivate_clears_active_state_and_timestamp(session_factory) -> None:
    now = datetime(2026, 5, 3, 9, 0, tzinfo=UTC)
    async with session_factory() as session:
        user = await create_user(session)
        service = BunkerService(UserRepository(session), clock=lambda: now)
        await service.activate(user)

        state = await service.deactivate(user)

        assert state.active is False
        assert state.activated_at is None
        assert user.bunker_active is False
        assert user.bunker_activated_at is None


async def test_deactivate_is_idempotent(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session)
        service = BunkerService(UserRepository(session))

        first = await service.deactivate(user)
        second = await service.deactivate(user)

        assert first.active is False
        assert first.activated_at is None
        assert second.active is False
        assert second.activated_at is None
        assert user.bunker_active is False
        assert user.bunker_activated_at is None


async def test_repeated_start_preserves_bunker_state(session_factory) -> None:
    now = datetime(2026, 5, 3, 9, 0, tzinfo=UTC)
    async with session_factory() as session:
        user_service = UserService(UserRepository(session))
        user = await create_user(session)
        await user_service.update_timezone(user, "Asia/Almaty")
        await user_service.update_language(user, "kk")
        await BunkerService(UserRepository(session), clock=lambda: now).activate(user)

        updated = await user_service.register_or_update_from_telegram(
            TelegramUserProfile(
                telegram_user_id=1001,
                chat_id=3001,
                username="second",
                first_name="Second",
                language_code="ru",
            )
        )

        assert updated.id == user.id
        assert updated.chat_id == 3001
        assert updated.timezone == "Asia/Almaty"
        assert updated.language_code == "kk"
        assert updated.bunker_active is True
        assert updated.bunker_activated_at == now


async def test_bunker_service_does_not_mutate_reminder_status(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session)
        reminder = Reminder(
            user_id=user.id,
            title="Morning focus",
            message_text="Return to intent.",
            schedule_type=ScheduleType.INTERVAL.value,
            interval_minutes=30,
            timezone=user.timezone,
            status=ReminderStatus.PAUSED.value,
            next_run_at=datetime(2026, 5, 3, 9, 30, tzinfo=UTC),
        )
        session.add(reminder)
        await session.flush()

        service = BunkerService(UserRepository(session))
        await service.activate(user)
        await service.deactivate(user)

        assert reminder.status == ReminderStatus.PAUSED.value
