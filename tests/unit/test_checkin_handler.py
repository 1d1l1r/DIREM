from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from direm.bot.handlers.checkins import handle_checkin_callback
from direm.db.base import Base
from direm.db.models import Reminder, ReminderCheckIn
from direm.domain.constants import CheckInResponseType, DeliveryStatus, ReminderStatus, ScheduleType
from direm.repositories.deliveries import ReminderDeliveryRepository
from direm.repositories.users import UserRepository
from direm.services.user_service import TelegramUserProfile, UserService


class FakeMessage:
    def __init__(self, *, chat_id: int = 2001) -> None:
        self.chat = SimpleNamespace(id=chat_id)


class FakeCallback:
    def __init__(self, data: str, *, telegram_user_id: int = 1001, chat_id: int = 2001, language_code: str = "en") -> None:
        self.data = data
        self.from_user = SimpleNamespace(
            id=telegram_user_id,
            username=f"user{telegram_user_id}",
            first_name="User",
            language_code=language_code,
        )
        self.message = FakeMessage(chat_id=chat_id)
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


async def seed_user(session, *, telegram_user_id: int = 1001, chat_id: int = 2001, language_code: str = "en"):
    return await UserService(UserRepository(session)).register_or_update_from_telegram(
        TelegramUserProfile(
            telegram_user_id=telegram_user_id,
            chat_id=chat_id,
            username=f"user{telegram_user_id}",
            first_name="User",
            language_code=language_code,
        )
    )


async def seed_reminder(session, user):
    reminder = Reminder(
        user_id=user.id,
        title="Morning focus",
        message_text="Return.",
        schedule_type=ScheduleType.INTERVAL.value,
        interval_minutes=30,
        timezone=user.timezone,
        status=ReminderStatus.ACTIVE.value,
        next_run_at=datetime(2026, 5, 4, 9, 0, tzinfo=UTC),
    )
    session.add(reminder)
    await session.flush()
    return reminder


async def seed_delivery(session, user, reminder, *, status: str = DeliveryStatus.SENT.value):
    return await ReminderDeliveryRepository(session).create(
        reminder_id=reminder.id,
        user_id=user.id,
        scheduled_for=reminder.next_run_at,
        status=status,
        sent_at=datetime(2026, 5, 4, 9, 0, tzinfo=UTC) if status == DeliveryStatus.SENT.value else None,
    )


async def list_checkins(session) -> list[ReminderCheckIn]:
    result = await session.execute(select(ReminderCheckIn).order_by(ReminderCheckIn.id.asc()))
    return list(result.scalars().all())


async def test_checkin_callback_records_response_for_owned_sent_delivery(session_factory) -> None:
    async with session_factory() as session:
        user = await seed_user(session)
        reminder = await seed_reminder(session, user)
        delivery = await seed_delivery(session, user, reminder)
        callback = FakeCallback(f"checkin:{delivery.id}:done")

        await handle_checkin_callback(callback, session)

        checkins = await list_checkins(session)
        assert callback.answers == [("Marked: done.", None)]
        assert len(checkins) == 1
        assert checkins[0].user_id == user.id
        assert checkins[0].reminder_id == reminder.id
        assert checkins[0].reminder_delivery_id == delivery.id
        assert checkins[0].response_type == CheckInResponseType.DONE.value


async def test_checkin_callback_repeat_tap_updates_existing_response(session_factory) -> None:
    async with session_factory() as session:
        user = await seed_user(session)
        reminder = await seed_reminder(session, user)
        delivery = await seed_delivery(session, user, reminder)

        await handle_checkin_callback(FakeCallback(f"checkin:{delivery.id}:done"), session)
        await handle_checkin_callback(FakeCallback(f"checkin:{delivery.id}:later"), session)

        checkins = await list_checkins(session)
        assert len(checkins) == 1
        assert checkins[0].response_type == CheckInResponseType.LATER.value
        assert reminder.next_run_at == datetime(2026, 5, 4, 9, 0, tzinfo=UTC)


async def test_checkin_callback_rejects_foreign_delivery(session_factory) -> None:
    async with session_factory() as session:
        owner = await seed_user(session, telegram_user_id=1001, chat_id=2001)
        other = await seed_user(session, telegram_user_id=1002, chat_id=2002)
        reminder = await seed_reminder(session, owner)
        delivery = await seed_delivery(session, owner, reminder)
        callback = FakeCallback(f"checkin:{delivery.id}:done", telegram_user_id=other.telegram_user_id, chat_id=other.chat_id)

        await handle_checkin_callback(callback, session)

        assert callback.answers == [("This check-in action is no longer available.", True)]
        assert await list_checkins(session) == []


async def test_checkin_callback_rejects_pending_delivery(session_factory) -> None:
    async with session_factory() as session:
        user = await seed_user(session)
        reminder = await seed_reminder(session, user)
        delivery = await seed_delivery(session, user, reminder, status=DeliveryStatus.PENDING.value)
        callback = FakeCallback(f"checkin:{delivery.id}:done")

        await handle_checkin_callback(callback, session)

        assert callback.answers == [("This check-in action is no longer available.", True)]
        assert await list_checkins(session) == []


async def test_checkin_callback_rejects_invalid_data(session_factory) -> None:
    async with session_factory() as session:
        await seed_user(session)
        callback = FakeCallback("checkin:42:snooze")

        await handle_checkin_callback(callback, session)

        assert callback.answers == [("This check-in action is no longer available.", True)]
        assert await list_checkins(session) == []
