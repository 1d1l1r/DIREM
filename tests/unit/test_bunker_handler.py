from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from direm.bot.handlers.bunker import (
    handle_bunker_activate,
    handle_bunker_command,
    handle_bunker_deactivate,
    handle_bunker_reply_toggle,
    handle_stale_bunker_callback,
)
from direm.db.base import Base
from direm.db.models import Reminder, ReminderDelivery
from direm.domain.constants import ReminderStatus, ScheduleType
from direm.repositories.users import UserRepository
from direm.services.bunker_service import BunkerService
from direm.services.user_service import TelegramUserProfile, UserService


class FakeMessage:
    def __init__(self, *, language_code: str = "en") -> None:
        self.from_user = SimpleNamespace(id=1001, username="ilya", first_name="Ilya", language_code=language_code)
        self.chat = SimpleNamespace(id=2001)
        self.answers: list[tuple[str, object | None]] = []

    async def answer(self, text: str, **kwargs) -> None:
        self.answers.append((text, kwargs.get("reply_markup")))


class FakeCallback:
    def __init__(self, data: str, *, language_code: str = "en") -> None:
        self.data = data
        self.from_user = SimpleNamespace(id=1001, username="ilya", first_name="Ilya", language_code=language_code)
        self.message = FakeMessage(language_code=language_code)
        self.answers: list[tuple[str | None, bool | None]] = []

    async def answer(self, text: str | None = None, show_alert: bool | None = None) -> None:
        self.answers.append((text, show_alert))


@pytest.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield async_sessionmaker(engine, expire_on_commit=False)

    await engine.dispose()


async def seed_user(session, *, language_code: str = "en"):
    return await UserService(UserRepository(session)).register_or_update_from_telegram(
        TelegramUserProfile(
            telegram_user_id=1001,
            chat_id=2001,
            username="ilya",
            first_name="Ilya",
            language_code=language_code,
        )
    )


async def test_bunker_command_renders_inactive_state(session_factory) -> None:
    async with session_factory() as session:
        await seed_user(session)
        message = FakeMessage(language_code="en")

        await handle_bunker_command(message, session)

    assert "Bunker is off." in message.answers[0][0]
    assert message.answers[0][1].inline_keyboard[0][0].callback_data == "bunker:activate"
    assert message.answers[1][1].keyboard[0][0].text == "Bunker OFF"


async def test_bunker_command_renders_active_state(session_factory) -> None:
    async with session_factory() as session:
        user = await seed_user(session)
        await BunkerService(UserRepository(session), clock=lambda: datetime(2026, 5, 3, 9, 0, tzinfo=UTC)).activate(user)
        message = FakeMessage(language_code="en")

        await handle_bunker_command(message, session)

    assert "Bunker is active." in message.answers[0][0]
    assert message.answers[0][1].inline_keyboard[0][0].callback_data == "bunker:deactivate"
    assert message.answers[1][1].keyboard[0][0].text == "Bunker ON"


async def test_bunker_activate_callback_sets_state_without_rescheduling(session_factory) -> None:
    due_at = datetime(2026, 5, 3, 8, 0, tzinfo=UTC)
    async with session_factory() as session:
        user = await seed_user(session)
        reminder = Reminder(
            user_id=user.id,
            title="Morning focus",
            message_text="Return.",
            schedule_type=ScheduleType.INTERVAL.value,
            interval_minutes=30,
            timezone=user.timezone,
            status=ReminderStatus.ACTIVE.value,
            next_run_at=due_at,
        )
        session.add(reminder)
        await session.flush()
        callback = FakeCallback("bunker:activate", language_code="en")

        await handle_bunker_activate(callback, session)

        assert user.bunker_active is True
        assert reminder.next_run_at == due_at
        assert reminder.status == ReminderStatus.ACTIVE.value


async def test_bunker_deactivate_callback_reschedules_without_delivery_records(session_factory) -> None:
    due_at = datetime.now(UTC)
    async with session_factory() as session:
        user = await seed_user(session)
        reminder = Reminder(
            user_id=user.id,
            title="Morning focus",
            message_text="Return.",
            schedule_type=ScheduleType.INTERVAL.value,
            interval_minutes=30,
            timezone=user.timezone,
            status=ReminderStatus.ACTIVE.value,
            next_run_at=due_at,
        )
        session.add(reminder)
        await session.flush()
        await BunkerService(UserRepository(session)).activate(user)
        callback = FakeCallback("bunker:deactivate", language_code="en")

        await handle_bunker_deactivate(callback, session)

        deliveries = (await session.execute(select(ReminderDelivery))).scalars().all()
        assert user.bunker_active is False
        assert user.bunker_activated_at is None
        assert reminder.next_run_at > due_at
        assert deliveries == []
        assert "Bunker turned off." in callback.message.answers[0][0]
        assert "DIREM is active." in callback.message.answers[1][0]
        assert callback.message.answers[1][1].keyboard[0][0].text == "Bunker OFF"


async def test_stale_bunker_callback_does_not_crash(session_factory) -> None:
    async with session_factory() as session:
        await seed_user(session)
        callback = FakeCallback("bunker:stale", language_code="en")

        await handle_stale_bunker_callback(callback, session)

    assert callback.answers == [("This Bunker action is stale. Open /bunker again.", True)]


async def test_bunker_reply_button_activates_directly(session_factory) -> None:
    async with session_factory() as session:
        user = await seed_user(session)
        message = FakeMessage(language_code="en")
        message.text = "Bunker OFF"

        await handle_bunker_reply_toggle(message, session)

        assert user.bunker_active is True
        assert "Bunker activated." in message.answers[0][0]
        assert "DIREM is active." in message.answers[1][0]
        assert message.answers[1][1].keyboard[0][0].text == "Bunker ON"


async def test_bunker_reply_button_deactivates_and_reschedules_directly(session_factory) -> None:
    due_at = datetime.now(UTC)
    async with session_factory() as session:
        user = await seed_user(session)
        reminder = Reminder(
            user_id=user.id,
            title="Morning focus",
            message_text="Return.",
            schedule_type=ScheduleType.INTERVAL.value,
            interval_minutes=30,
            timezone=user.timezone,
            status=ReminderStatus.ACTIVE.value,
            next_run_at=due_at,
        )
        session.add(reminder)
        await session.flush()
        await BunkerService(UserRepository(session)).activate(user)
        message = FakeMessage(language_code="en")
        message.text = "Bunker ON"

        await handle_bunker_reply_toggle(message, session)

        deliveries = (await session.execute(select(ReminderDelivery))).scalars().all()
        assert user.bunker_active is False
        assert reminder.next_run_at > due_at
        assert deliveries == []
        assert "Bunker turned off." in message.answers[0][0]
        assert message.answers[1][1].keyboard[0][0].text == "Bunker OFF"
