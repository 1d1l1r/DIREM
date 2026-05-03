from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from direm.db.base import Base
from direm.db.models import Reminder, ReminderDelivery
from direm.domain.constants import ReminderStatus, ScheduleType
from direm.domain.errors import InvalidScheduleConfigError
from direm.repositories.reminders import ReminderRepository
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


async def test_deactivate_and_reschedule_is_atomic_success_path(session_factory) -> None:
    activated_at = datetime(2026, 5, 3, 9, 0, tzinfo=UTC)
    exit_at = datetime(2026, 5, 3, 10, 0, tzinfo=UTC)
    due_at = datetime(2026, 5, 3, 8, 0, tzinfo=UTC)
    async with session_factory() as session:
        user = await create_user(session)
        reminder = Reminder(
            user_id=user.id,
            title="Morning focus",
            message_text="Return to intent.",
            schedule_type=ScheduleType.INTERVAL.value,
            interval_minutes=30,
            timezone=user.timezone,
            status=ReminderStatus.ACTIVE.value,
            next_run_at=due_at,
        )
        session.add(reminder)
        await session.flush()
        await BunkerService(UserRepository(session), clock=lambda: activated_at).activate(user)

        result = await BunkerService(
            UserRepository(session),
            ReminderRepository(session),
            clock=lambda: exit_at,
        ).deactivate_and_reschedule(user)

        assert result.state.active is False
        assert result.rescheduled_count == 1
        assert user.bunker_active is False
        assert user.bunker_activated_at is None
        assert reminder.status == ReminderStatus.ACTIVE.value
        assert reminder.next_run_at == datetime(2026, 5, 3, 10, 30, tzinfo=UTC)


async def test_deactivate_and_reschedule_failure_keeps_bunker_active(session_factory) -> None:
    activated_at = datetime(2026, 5, 3, 9, 0, tzinfo=UTC)
    exit_at = datetime(2026, 5, 3, 10, 0, tzinfo=UTC)
    due_at = datetime(2026, 5, 3, 8, 0, tzinfo=UTC)
    async with session_factory() as session:
        user = await create_user(session)
        reminder = Reminder(
            user_id=user.id,
            title="Broken",
            message_text="Return to intent.",
            schedule_type=ScheduleType.INTERVAL.value,
            interval_minutes=None,
            timezone=user.timezone,
            status=ReminderStatus.ACTIVE.value,
            next_run_at=due_at,
        )
        session.add(reminder)
        await session.flush()
        await BunkerService(UserRepository(session), clock=lambda: activated_at).activate(user)

        with pytest.raises(InvalidScheduleConfigError):
            await BunkerService(
                UserRepository(session),
                ReminderRepository(session),
                clock=lambda: exit_at,
            ).deactivate_and_reschedule(user)

        assert user.bunker_active is True
        assert user.bunker_activated_at == activated_at
        assert reminder.next_run_at == due_at
        assert reminder.status == ReminderStatus.ACTIVE.value


async def test_deactivate_when_inactive_does_not_reschedule(session_factory) -> None:
    exit_at = datetime(2026, 5, 3, 10, 0, tzinfo=UTC)
    due_at = datetime(2026, 5, 3, 8, 0, tzinfo=UTC)
    async with session_factory() as session:
        user = await create_user(session)
        reminder = Reminder(
            user_id=user.id,
            title="Morning focus",
            message_text="Return to intent.",
            schedule_type=ScheduleType.INTERVAL.value,
            interval_minutes=30,
            timezone=user.timezone,
            status=ReminderStatus.ACTIVE.value,
            next_run_at=due_at,
        )
        session.add(reminder)
        await session.flush()

        result = await BunkerService(
            UserRepository(session),
            ReminderRepository(session),
            clock=lambda: exit_at,
        ).deactivate_and_reschedule(user)

        assert result.was_already_inactive is True
        assert result.rescheduled_count == 0
        assert reminder.next_run_at == due_at


async def test_deactivate_reschedule_leaves_paused_deleted_and_deliveries_untouched(session_factory) -> None:
    activated_at = datetime(2026, 5, 3, 9, 0, tzinfo=UTC)
    exit_at = datetime(2026, 5, 3, 10, 0, tzinfo=UTC)
    due_at = datetime(2026, 5, 3, 8, 0, tzinfo=UTC)
    async with session_factory() as session:
        user = await create_user(session)
        active = Reminder(
            user_id=user.id,
            title="Active",
            message_text="Return to intent.",
            schedule_type=ScheduleType.INTERVAL.value,
            interval_minutes=30,
            timezone=user.timezone,
            status=ReminderStatus.ACTIVE.value,
            next_run_at=due_at,
        )
        paused = Reminder(
            user_id=user.id,
            title="Paused",
            message_text="Return to intent.",
            schedule_type=ScheduleType.INTERVAL.value,
            interval_minutes=30,
            timezone=user.timezone,
            status=ReminderStatus.PAUSED.value,
            next_run_at=due_at,
        )
        deleted = Reminder(
            user_id=user.id,
            title="Deleted",
            message_text="Return to intent.",
            schedule_type=ScheduleType.INTERVAL.value,
            interval_minutes=30,
            timezone=user.timezone,
            status=ReminderStatus.ACTIVE.value,
            next_run_at=due_at,
            deleted_at=datetime(2026, 5, 3, 9, 30, tzinfo=UTC),
        )
        session.add_all([active, paused, deleted])
        await session.flush()
        await BunkerService(UserRepository(session), clock=lambda: activated_at).activate(user)

        result = await BunkerService(
            UserRepository(session),
            ReminderRepository(session),
            clock=lambda: exit_at,
        ).deactivate_and_reschedule(user)

        deliveries = (await session.execute(select(ReminderDelivery))).scalars().all()
        assert result.rescheduled_count == 1
        assert active.next_run_at == datetime(2026, 5, 3, 10, 30, tzinfo=UTC)
        assert active.status == ReminderStatus.ACTIVE.value
        assert paused.next_run_at == due_at
        assert paused.status == ReminderStatus.PAUSED.value
        assert deleted.next_run_at == due_at
        assert deleted.status == ReminderStatus.ACTIVE.value
        assert deliveries == []
